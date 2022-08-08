from unittest.mock import patch

import paramiko
import pytest

from docker_launch import check_key_ssh
from docker_launch.ssh import _parse_address


def test__parse_address():
    assert _parse_address("172.29.1.1", "user") == ("172.29.1.1", "user")
    assert _parse_address("user@172.29.1.1") == ("172.29.1.1", "user")
    assert _parse_address("user@172.29.1.1", "user") == ("172.29.1.1", "user")
    with pytest.raises(ValueError):
        _parse_address("user@172.29.1.1", "me")


def _mock_connect(self, addr, *, username, port):
    if (addr == "172.29.0.1") and (username == "me") and (port == 22):
        return
    else:
        raise paramiko.AuthenticationException


@patch("paramiko.SSHClient.connect", _mock_connect)
def test_check_key_ssh():
    # paramiko.SSHClient.connect = Mock(side_effect=_mock_connect)

    assert check_key_ssh("me@172.29.0.1") is True
    assert check_key_ssh("172.29.0.1", username="me") is True
    assert check_key_ssh("me@172.29.0.1", username="me") is True

    assert check_key_ssh("you@172.29.0.1") is False
    assert check_key_ssh("172.29.0.1", username="you") is False
    assert check_key_ssh("you@172.29.0.1", username="you") is False

    assert check_key_ssh("me@172.29.0.11") is False
    assert check_key_ssh("172.29.0.11", username="me") is False
    assert check_key_ssh("me@172.29.0.11", username="me") is False

    assert check_key_ssh("me@172.29.0.1", port=21) is False
    assert check_key_ssh("172.29.0.1", username="me", port=21) is False
    assert check_key_ssh("me@172.29.0.1", username="me", port=21) is False


@pytest.mark.skip(reason="Not implemented yet.")
def test_interactively_check_key_ssh():
    ...
