from unittest.mock import patch

import pytest

from docker_launch import check_connection
from docker_launch.ssh import _parse_address

from .conftest import connect


def test__parse_address():
    assert _parse_address("172.29.1.1", "user") == ("172.29.1.1", "user")
    assert _parse_address("user@172.29.1.1") == ("172.29.1.1", "user")
    assert _parse_address("user@172.29.1.1", "user") == ("172.29.1.1", "user")
    with pytest.raises(ValueError):
        _parse_address("user@172.29.1.1", "me")


@patch("paramiko.SSHClient.connect", connect)
def test_check_connection():
    assert check_connection("me@172.29.0.1") is True
    assert check_connection("172.29.0.1", username="me") is True
    assert check_connection("me@172.29.0.1", username="me") is True

    assert check_connection("you@172.29.0.1") is False
    assert check_connection("172.29.0.1", username="you") is False
    assert check_connection("you@172.29.0.1", username="you") is False

    assert check_connection("me@172.29.0.11") is False
    assert check_connection("172.29.0.11", username="me") is False
    assert check_connection("me@172.29.0.11", username="me") is False

    assert check_connection("me@172.29.0.1", port=21) is False
    assert check_connection("172.29.0.1", username="me", port=21) is False
    assert check_connection("me@172.29.0.1", username="me", port=21) is False
