from ipaddress import ip_address
from typing import List

import docker

from .config_parser import parse
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

    def start(self, **kwargs) -> List[docker.models.containers.Container]:
        config = parse(self.config_path)

        containers = {}
        for machine, conf in config.items():
            daemon_url = _resolve_base_url(machine)
            client = docker.DockerClient(base_url=daemon_url)

            img_and_cmd = list(map(lambda x: (x["image"], x["cmd"]), conf))
            _containers = [
                client.containers.run(image, command, detach=True, **kwargs)
                for image, command in img_and_cmd
            ]  # TODO: Possibly multi-thread?
            containers[machine] = _containers
        return containers

    def stop(self):
        raise NotImplementedError

    def ping(self):
        raise NotImplementedError

    @classmethod
    def launch(
        cls, config_path: PathLike, **kwargs
    ) -> List[docker.models.containers.Container]:
        return cls(config_path).start(**kwargs)


launch_containers = Containers.launch
