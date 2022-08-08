from unittest.mock import patch

import docker
import pytest

from docker_launch import launch_containers, check_docker_available
from docker_launch.launch import _is_ip_address, _resolve_base_url, Containers

DOCKER_NOT_AVAILABLE = not check_docker_available()


def test__is_ip_address():
    assert _is_ip_address("172.29.1.1") is True
    assert _is_ip_address("user@172.29.1.1") is True
    assert _is_ip_address("localhost") is False
    assert _is_ip_address(None) is False


def test__resolve_base_url():
    assert _resolve_base_url("host") is None
    assert _resolve_base_url("localhost") is None
    assert _resolve_base_url(None) is None  # TODO: May change
    assert _resolve_base_url("user@172.29.1.1") == "ssh://user@172.29.1.1"
    assert _resolve_base_url("172.29.1.1") == "ssh://172.29.1.1"


config_file_names = pytest.mark.parametrize(
    "config_file_name",
    [
        "config.toml",
        pytest.param(
            "config_include_differentbase.toml",
            marks=pytest.mark.xfail(reason="Not implemented yet."),
        ),
        pytest.param(
            "config_include_samebase.toml",
            marks=pytest.mark.xfail(reason="Not implemented yet."),
        ),
        "config_multiple_differentbase.toml",
        "config_multiple_samebase.toml",
    ],
)


OriginalDockerClient = docker.DockerClient


def LocalhostDockerClient(base_url=None, **kwargs):
    kwargs.update({"base_url": None})
    return OriginalDockerClient(**kwargs)


@patch("docker.DockerClient", LocalhostDockerClient)
@pytest.mark.skipif(
    DOCKER_NOT_AVAILABLE, reason="Docker isn't available in this environment."
)
class TestContainers:
    @config_file_names
    def test_start(self, sample_dir, config_file_name):
        c = Containers(sample_dir / config_file_name)
        started = c.start(remove=True)
        print(c, started)
        for group in started.values():
            for container in group:
                container.reload()
                assert container.status == "running"
                container.stop()

    @config_file_names
    @pytest.mark.skip(reason="Not implemented yet.")
    def test_stop(self, sample_dir, config_file_name):
        _ = Containers(sample_dir / config_file_name)

    @config_file_names
    @pytest.mark.skip(reason="Not implemented yet.")
    def test_ping(self, sample_dir, config_file_name):
        _ = Containers(sample_dir / config_file_name)


@patch("docker.DockerClient", LocalhostDockerClient)
@config_file_names
@pytest.mark.skip(reason="Not implemented yet.")
def test_launch_containers(sample_dir, config_file_name):
    _ = launch_containers(sample_dir / config_file_name, remove=True)
