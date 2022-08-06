from unittest.mock import Mock

import paramiko
import pytest

from docker_launch import check_key_ssh
from docker_launch.ssh import _parse_address


def test__parse_address():
    assert _parse_address("192.168.1.1", "user") == ("192.168.1.1", "user")
    assert _parse_address("user@192.168.1.1") == ("192.168.1.1", "user")
    assert _parse_address("user@192.168.1.1", "user") == ("192.168.1.1", "user")
    with pytest.raises(ValueError):
        _parse_address("user@192.168.1.1", "me")


def test_check_key_ssh():
    def _mock_connect(addr, *, username, port):
        if (addr == "192.168.0.1") and (username == "me") and (port == 22):
            return
        else:
            raise paramiko.AuthenticationException

    paramiko.SSHClient.connect = Mock(side_effect=_mock_connect)

    assert check_key_ssh("me@192.168.0.1") is True
    assert check_key_ssh("192.168.0.1", username="me") is True
    assert check_key_ssh("me@192.168.0.1", username="me") is True

    assert check_key_ssh("you@192.168.0.1") is False
    assert check_key_ssh("192.168.0.1", username="you") is False
    assert check_key_ssh("you@192.168.0.1", username="you") is False

    assert check_key_ssh("me@192.168.0.11") is False
    assert check_key_ssh("192.168.0.11", username="me") is False
    assert check_key_ssh("me@192.168.0.11", username="me") is False

    assert check_key_ssh("me@192.168.0.1", port=21) is False
    assert check_key_ssh("192.168.0.1", username="me", port=21) is False
    assert check_key_ssh("me@192.168.0.1", username="me", port=21) is False


@pytest.mark.skip(reason="Not implemented yet.")
def test_interactively_check_key_ssh():
    ...
