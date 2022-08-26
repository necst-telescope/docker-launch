from collections import defaultdict
from ipaddress import ip_address
from typing import Any, Dict, Hashable, List, Tuple

Object = Dict[Hashable, Any]


def groupby(objects: List[Object], key: Hashable) -> Dict[Hashable, List[Object]]:
    """Group list of dictionaries by values of its specific key.

    You can safely specify possibly missing key. See the example below.

    Examples
    --------
    >>> groupby([{"a": 1, "b": 2}, {"a": 5, "b": 2}, {"a": 1, "b": 7}], "a")
    {1: [{"a": 1, "b": 2},  {"a": 1, "b": 7}], 5: [{"a": 5, "b": 2}]}
    >>> groupby([{"a": 1, "b": 2}, {"b": 2}, {"a": 1, "b": 7}], "a")
    {"": [{"b": 2}], 1: [{"a": 1, "b": 2}, {"a": 1, "b": 7}]}
    >>> groupby([{"a": 1, "b": 2}, {"a": 5, "b": 2}, {"a": 1, "b": 7}], "c")
    {"": [{"a": 1, "b": 2}, {"a": 5, "b": 2}, {"a": 1, "b": 7}]}

    """
    grouped = defaultdict(lambda: [])
    for obj in objects:
        group_name = obj.get(key, "")
        grouped[group_name].append(obj)
    return dict(grouped)


def parse_address(address: str, username: str = None) -> Tuple[str, str]:
    """Parse IP address, either in format user@ipaddr or separately provided.

    Raises
    ------
    ValueError
        If address is given in username@ipaddr format but inconsistent username is given
        as separate argument.

    Examples
    --------
    >>> parse_address("user@172.29.0.0")
    ("172.29.0.0", "user")
    >>> parse_address("172.29.0.0", "user")
    ("172.29.0.0", "user")
    >>> parse_address("172.29.0.0")
    ("172.29.0.0", None)

    """
    _username, ipaddr = username, address
    if address.find("@") != -1:
        _username, ipaddr = address.split("@", 1)

    if (username is not None) and (_username != username):
        raise ValueError("Inconsistent username.")
    return (ipaddr, _username)


def is_ip_address(address: str) -> bool:
    """Check if the input is IP address or not.

    Examples
    --------
    >>> is_ip_address("172.29.0.0")
    True
    >>> is_ip_address("user@172.29.0.0")
    True
    >>> is_ip_address("localhost")
    False

    """
    if not isinstance(address, str):
        return False

    try:
        ip_addr, _ = parse_address(address)
        ip_address(ip_addr)
        return True
    except ValueError:
        return False


def resolve_base_url(machine: str = None) -> str:
    """Base URL for Docker client.

    Examples
    --------
    >>> _resolve_base_url("user@172.29.0.0")
    'ssh://user@172.29.0.0'
    >>> _resolve_base_url("localhost")
    None

    """
    if machine in ["host", "localhost"]:
        return None
    if machine is None:
        # TODO: Possibly be arbitrary host, if load balance can be handled
        return None
    if is_ip_address(machine):
        return f"ssh://{machine}"
    raise ValueError(f"Cannot interpret machine specification : '{machine}'")
