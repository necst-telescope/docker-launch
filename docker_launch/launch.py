import concurrent.futures
import time
from collections import defaultdict
from ipaddress import ip_address
from typing import Any, Dict, Hashable, List

import docker

from docker_launch import logger
from . import utils
from .config_parser import LaunchConfiguration, parse
from .exceptions import LaunchError
from .ssh import _parse_address
from .typing import PathLike


def _is_ip_address(address: str) -> bool:
    if not isinstance(address, str):
        return False

    try:
        ip_addr, _ = _parse_address(address)
        ip_address(ip_addr)
        return True
    except ValueError:
        return False


def _resolve_base_url(machine: str = None) -> str:
    if machine in ["host", "localhost"]:
        return None
    if machine is None:
        # TODO: Possibly be arbitrary host, if load balance can be handled
        return None
    if _is_ip_address(machine):
        return f"ssh://{machine}"
    raise ValueError(f"Cannot interpret machine specification : '{machine}'")


class Containers:
    def __init__(self, config_path: PathLike) -> None:
        self.config_path = config_path
        self.containers = defaultdict(lambda: [])

    @property
    def config(self) -> Dict[Hashable, List[LaunchConfiguration]]:
        return parse(self.config_path)

    @staticmethod
    def _flatten(dict_of_lists: Dict[Any, List]) -> List:
        ret = []
        _ = [ret.extend(elem) for elem in dict_of_lists.values()]
        return ret

    @property
    def containers_list(self) -> List[docker.client.ContainerCollection]:
        """List of containers, i.e. not grouped by machines they're running on."""
        return self._flatten(self.containers)

    def start(
        self, **docker_run_kwargs
    ) -> Dict[str, List[docker.client.ContainerCollection]]:
        if len(self.containers_list) > 0:
            raise LaunchError("This process is already running a launch group.")

        def _start(
            client: docker.DockerClient, image: str, command: str, **kwargs
        ) -> docker.client.ContainerCollection:
            return client.containers.run(image, command, detach=True, **kwargs)

        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            futures = {}

            for machine, conf in self.config.items():
                daemon_url = _resolve_base_url(machine)
                client = docker.DockerClient(base_url=daemon_url)
                img_and_cmd = list(map(lambda x: (x["image"], x["cmd"]), conf))
                _futures = [
                    executor.submit(_start, client, img, cmd, **docker_run_kwargs)
                    for img, cmd in img_and_cmd
                ]
                futures[machine] = _futures

            for machine, future in futures.items():
                _future = concurrent.futures.as_completed(future, timeout=30)
                _future = map(lambda x: x.result(), _future)
                self.containers[machine].extend(_future)
        return self.containers

    def stop(self) -> None:
        def _stop(container: docker.client.ContainerCollection) -> None:
            try:
                container.stop()
                logger.info(f"Container {container} successfully stopped.")
            except Exception as e:
                logger.warning(str(e))

        logger.info("Gracefully stopping containers. This will take ~10s.")
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
        def _ping(container: docker.client.ContainerCollection) -> None:
            container.reload()
            return container, container.status

        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            futures = [executor.submit(_ping, c) for c in self.containers_list]
            futures = concurrent.futures.as_completed(futures, timeout=30)

        result = [f.result() for f in futures]
        info = [{"container": c, "status": s} for c, s in result if s != "running"]
        return utils._groupby(info, "status")

    def watch(self):
        try:
            while True:
                not_running = self.ping()
                if not_running:
                    logger.info(str(not_running))
                time.sleep(0.5)
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
