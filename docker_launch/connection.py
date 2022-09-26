"""Connection checker."""

import paramiko

from docker_launch import logger
from . import utils


def _get_ssh_client() -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
    except UnicodeDecodeError:
        logger.warning("Host key file found, but it may be corrupted.")
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    return client


def check_connection(
    address: str, *, username: str = None, port: int = 22, timeout: float = 3
) -> bool:
    client = _get_ssh_client()

    ipaddr, username = utils.parse_address(address, username)
    try:
        client.connect(ipaddr, username=username, port=port, timeout=timeout)
        client.close()
        return True
    except Exception as e:
        logger.error(
            f"Cannot establish SSH connection with '{username}@{ipaddr}', "
            f"got {e.__class__}.\nUse ``docker-launch check`` to debug this."
        )
        return False
