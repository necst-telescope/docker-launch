from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from cleo import Application, CommandTester
from docker import DockerClient as OriginalDockerClient

from docker_launch.console.check_command import CheckCommand

# from docker_launch.console.up_command import UpCommand


@pytest.fixture
def sample_dir():
    return Path(__file__).parent / "sample"


@pytest.fixture
def app():
    _app = Application()
    _app.add(CheckCommand())
    # _app.add(UpCommand())
    return _app


@pytest.fixture
def command_tester_factory(app):
    def create_tester(command: str):
        command = app.find(command)
        return CommandTester(command)

    return create_tester


@pytest.fixture
def mock_ssh_connection():
    def connect(self, hostname, port=22, username=None, **kwargs) -> None:
        import paramiko

        if (hostname, username, port) == ("172.29.0.1", "user", 22):
            return
        if port == 22:
            raise paramiko.AuthenticationException
        if username == "user":
            raise paramiko.BadHostKeyException
        raise paramiko.SSHException

    with patch("paramiko.SSHClient.connect", connect):
        yield


@pytest.fixture
def mock_docker_client():
    def LocalhostDockerClient(**kwargs):
        kwargs.update({"base_url": None})
        return OriginalDockerClient(**kwargs)

    with patch("docker.DockerClient", LocalhostDockerClient):
        yield


@pytest.fixture
def mock_ssh_copy_id_pass():
    with patch(
        "docker_launch.console.check_command.CheckCommand._ssh_copy_id", lambda *args: 0
    ):
        yield


@pytest.fixture
def mock_successful_ssh_copy_id(mock_ssh_copy_id_pass):
    import paramiko

    class connect:
        count = 0

        def __new__(cls, hostname, port=22, username=None, **kwargs) -> None:
            cls.count += 1
            if cls.count > 1:  # After second attempt
                return
            raise paramiko.AuthenticationException  # Before running ssh-copy-id

    with patch("paramiko.SSHClient.connect", connect):
        yield


@pytest.fixture
def mock_ssh_copy_id_has_no_effect(mock_ssh_copy_id_pass):
    import paramiko

    def connect(self, hostname, port=22, username=None, **kwargs) -> None:
        raise paramiko.AuthenticationException

    with patch("paramiko.SSHClient.connect", connect):
        yield


@pytest.fixture
def mock_ssh_copy_id_has_no_effect_identity_changed(mock_ssh_copy_id_pass):
    import paramiko

    def connect(self, hostname, port=22, username=None, **kwargs) -> None:
        key_obj = SimpleNamespace(get_base64=lambda: "...")
        raise paramiko.BadHostKeyException(hostname, key_obj, key_obj)

    with patch("paramiko.SSHClient.connect", connect):
        yield


@pytest.fixture
def mock_ssh_key_locked():
    with patch(
        "docker_launch.console.check_command.CheckCommand._check_if_key_is_locked",
        lambda self, key_path: True,
    ):
        yield


@pytest.fixture
def mock_ssh_key_not_locked():
    with patch(
        "docker_launch.console.check_command.CheckCommand._check_if_key_is_locked",
        lambda self, key_path: False,
    ):
        yield
