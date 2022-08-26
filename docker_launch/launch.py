"""Start, watch and terminate distributed containers.

Most of launch functionalities involve network communications, so they are run
concurrently in multi-threads.

"""

import concurrent.futures
import time
from typing import Any, Dict, Hashable, List, Tuple

import docker

from docker_launch import logger
from . import utils
from .config_parser import LaunchConfiguration, parse
from .exceptions import LaunchError
from .typing import PathLike


class Containers:
    def __init__(self, config_path: PathLike) -> None:
        self.config_path = config_path
        self.containers_list = []
        self.last_ping = int(time.time())

    @property
    def config(self) -> Dict[Hashable, List[LaunchConfiguration]]:
        return parse(self.config_path)

    @staticmethod
    def _flatten(dict_of_lists: Dict[Any, List]) -> List:
        ret = []
        _ = [ret.extend(elem) for elem in dict_of_lists.values()]
        return ret

    def start(
        self, **docker_run_kwargs
    ) -> Dict[str, List[docker.client.ContainerCollection]]:
        if len(self.containers_list) > 0:
            raise LaunchError("This process is already running a launch group.")

        def _start(
            client: docker.DockerClient, image: str, command: str, **kwargs
        ) -> docker.client.ContainerCollection:
            container = client.containers.run(image, command, detach=True, **kwargs)
            _base_url = client.api.base_url.split("//")[-1]
            logger.info(
                f"Container '{container.name}' ({container.short_id}) started "
                f"on '{_base_url}'"
            )
            return container

        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            futures = []

            for machine, conf in self.config.items():
                daemon_url = utils.resolve_base_url(machine)
                client = docker.DockerClient(base_url=daemon_url)
                img_and_cmd = list(map(lambda x: (x["image"], x["cmd"]), conf))
                _futures = [
                    executor.submit(_start, client, img, cmd, **docker_run_kwargs)
                    for img, cmd in img_and_cmd
                ]
                futures.extend(_futures)

            _futures = concurrent.futures.as_completed(futures, timeout=60)
            _futures = map(lambda x: x.result(), _futures)
            self.containers_list.extend(_futures)
        return self.containers_list

    def stop(self) -> None:
        def _stop(container: docker.client.ContainerCollection) -> None:
            try:
                container.stop(timeout=3)  # Escalate to SIGKILL after 3 sec.
                logger.info(f"Container {container} has stopped.")
            except Exception as e:
                logger.warning(str(e))

        logger.info("Gracefully stopping containers, may take time.")
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            futures = [executor.submit(_stop, c) for c in self.containers_list]
            _ = concurrent.futures.as_completed(futures, timeout=30)

    def remove(self) -> None:
        def _remove(container: docker.client.ContainerCollection) -> None:
            try:
                container.remove()
                logger.info(f"Container {container} successfully removed.")
            except Exception as e:
                logger.warning(str(e))

        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            futures = [executor.submit(_remove, c) for c in self.containers_list]
            _ = concurrent.futures.as_completed(futures, timeout=30)

    def ping(self) -> Dict[str, List[docker.client.ContainerCollection]]:
        now = int(time.time())

        def _ping(
            container: docker.client.ContainerCollection,
        ) -> Tuple[docker.client.ContainerCollection, str]:
            try:
                container.reload()
                logs = container.logs(timestamps=True, since=self.last_ping, until=now)
                if logs:
                    base_url = container.client.api.base_url
                    info = f"{container.short_id}@{base_url} : {logs.decode('utf-8')}"
                    logger.info(info)
                return container, container.status
            except docker.errors.APIError:
                return container, "not found"

        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            futures = [executor.submit(_ping, c) for c in self.containers_list]
            futures = concurrent.futures.as_completed(futures, timeout=30)

        self.last_ping = now
        result = [f.result() for f in futures]
        info = [{"container": c, "status": s} for c, s in result if s != "running"]
        return utils.groupby(info, "status")

    def watch(self):
        try:
            while True:
                not_running = self.ping()
                if not_running:
                    logger.info(str(not_running))
                time.sleep(1)
        except Exception as e:
            logger.error(e)
            self.stop()

    @classmethod
    def launch(cls, config_path: PathLike, **kwargs) -> None:
        """Launch containers described in config_path.

        .. warning::

            To stop all the containers, press Ctrl+C. Killing the process will leave the
            launched containers unmanaged.

        """
        c = cls(config_path)
        c.start(**kwargs)
        try:
            c.watch()
        finally:
            c.stop()


launch_containers = Containers.launch
