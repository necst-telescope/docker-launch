from typing import Tuple

import paramiko

from docker_launch import logger


def _parse_address(address: str, username: str = None) -> Tuple[str, str]:
    """Parse IP address, either in format user@ipaddr or separately provided.

    Parameters
    ----------
    address
        IP address or username@ipaddr.
    username
        User name.

    Returns
    -------
    tuple[str, str]
        Parsed (IP address, user name).

    Raises
    ------
    ValueError
        If address is given in username@ipaddr format but inconsistent username is given
        as separate argument.

    """
    _username, ipaddr = username, address
    if address.find("@") != -1:
        _username, ipaddr = address.split("@", 1)

    if (username is not None) and (_username != username):
        raise ValueError("Inconsistent username.")
    return (ipaddr, _username)


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

    ipaddr, username = _parse_address(address, username)
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
