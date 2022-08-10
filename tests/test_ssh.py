import pytest

from docker_launch import check_connection
from docker_launch.ssh import _parse_address


def test__parse_address():
    assert _parse_address("172.29.1.1", "user") == ("172.29.1.1", "user")
    assert _parse_address("user@172.29.1.1") == ("172.29.1.1", "user")
    assert _parse_address("user@172.29.1.1", "user") == ("172.29.1.1", "user")
    with pytest.raises(ValueError):
        _parse_address("user@172.29.1.1", "me")


@pytest.mark.usefixtures("mock_ssh_connection")
def test_check_connection_to_verified_host():
    assert check_connection("user@172.29.0.1") is True
    assert check_connection("172.29.0.1", username="user") is True
    assert check_connection("user@172.29.0.1", username="user") is True


@pytest.mark.usefixtures("mock_ssh_connection")
def test_check_connection_to_different_user():
    assert check_connection("you@172.29.0.1") is False
    assert check_connection("172.29.0.1", username="you") is False
    assert check_connection("you@172.29.0.1", username="you") is False


@pytest.mark.usefixtures("mock_ssh_connection")
def test_check_connection_to_different_host():
    assert check_connection("user@172.29.0.11") is False
    assert check_connection("172.29.0.11", username="user") is False
    assert check_connection("user@172.29.0.11", username="user") is False


@pytest.mark.usefixtures("mock_ssh_connection")
def test_check_connection_to_different_port():
    assert check_connection("user@172.29.0.1", port=21) is False
    assert check_connection("172.29.0.1", username="user", port=21) is False
    assert check_connection("user@172.29.0.1", username="user", port=21) is False
