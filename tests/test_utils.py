import pytest

from docker_launch.utils import groupby, parse_address, is_ip_address, resolve_base_url


def test_groupby():
    assert groupby([{"k": 1}], "k") == {1: [{"k": 1}]}
    assert groupby([{"k": 1, "l": 2}], "k") == {1: [{"k": 1, "l": 2}]}
    assert groupby([{"k": 1}, {"k": 1, "l": 2}], "k") == {
        1: [{"k": 1}, {"k": 1, "l": 2}]
    }
    assert groupby([{"l": 1}, {"k": 1, "l": 2}], "k") == {
        "": [{"l": 1}],
        1: [{"k": 1, "l": 2}],
    }


def test_parse_address():
    assert parse_address("172.29.1.1", "user") == ("172.29.1.1", "user")
    assert parse_address("user@172.29.1.1") == ("172.29.1.1", "user")
    assert parse_address("user@172.29.1.1", "user") == ("172.29.1.1", "user")
    assert parse_address("172.29.1.1") == ("172.29.1.1", None)
    with pytest.raises(ValueError):
        parse_address("user@172.29.1.1", "me")


def test_is_ip_address():
    assert is_ip_address("172.29.1.1") is True
    assert is_ip_address("user@172.29.1.1") is True
    assert is_ip_address("localhost") is False
    assert is_ip_address(None) is False


def test_resolve_base_url():
    assert resolve_base_url("host") is None
    assert resolve_base_url("localhost") is None
    assert resolve_base_url(None) is None  # TODO: May change
    assert resolve_base_url("user@172.29.1.1") == "ssh://user@172.29.1.1"
    assert resolve_base_url("172.29.1.1") == "ssh://172.29.1.1"
