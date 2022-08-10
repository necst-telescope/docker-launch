from pathlib import Path

import pytest
from cleo import Application, CommandTester

from docker_launch.console.check_command import CheckCommand

# from docker_launch.console.up_command import UpCommand


@pytest.fixture
def sample_dir():
    return Path(__file__).parent / "sample"


@pytest.fixture
def app():
    _app = Application()
    _app.add(CheckCommand)
    # _app.add(UpCommand)
    return _app


@pytest.fixture
def command_tester_factory(app):
    def create_tester(command: str):
        command = app.find(command)
        return CommandTester(command)

    return create_tester


def connect(self, hostname, port=22, username=None, **kwargs) -> None:
    import paramiko

    if (hostname, username, port) == ("172.29.0.1", "me", 22):
        return
    else:
        raise paramiko.AuthenticationException


def LocalhostDockerClient(**kwargs):
    from docker import DockerClient

    kwargs.update({"base_url": None})
    return DockerClient(**kwargs)
