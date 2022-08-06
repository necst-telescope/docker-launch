from typing import Tuple

import paramiko


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


def check_key_ssh(address: str, *, username: str = None, port: int = 22) -> bool:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    ipaddr, username = _parse_address(address, username)
    try:
        client.connect(ipaddr, username=username, port=port)
        client.close()
        return True
    except paramiko.AuthenticationException:
        return False


def interactively_check_key_ssh():
    raise NotImplementedError
