import pytest

from docker_launch import launch_containers, check_docker_available  # noqa: F401
from docker_launch.launch import _is_ip_address, _resolve_base_url, Containers

DOCKER_NOT_AVAILABLE = check_docker_available()


def test__is_ip_address():
    assert _is_ip_address("192.168.1.1") is True
    assert _is_ip_address("user@192.168.1.1") is True
    assert _is_ip_address("localhost") is False
    assert _is_ip_address(None) is False


def test__resolve_base_url():
    assert _resolve_base_url("host") is None
    assert _resolve_base_url("localhost") is None
    assert _resolve_base_url(None) is None  # TODO: Not fixed yet
    assert _resolve_base_url("user@192.168.1.1") == "ssh://user@192.168.1.1"
    assert _resolve_base_url("192.168.1.1") == "ssh://192.168.1.1"


config_file_names = pytest.mark.parametrize(
    "config_file_name",
    [
        "config.toml",
        "config_include_differentbase.toml",
        "config_include_samebase.toml",
        "config_multiple_differentbase.toml",
        "config_multiple_samebase.toml",
    ],
)


@pytest.mark.skipif(
    DOCKER_NOT_AVAILABLE, reason="Docker isn't available in this environment."
)
class TestContainers:
    @config_file_names
    def test_start(self, sample_dir, config_file_name):
        _ = Containers(sample_dir / config_file_name)

    @config_file_names
    @pytest.mark.skip(reason="Not implemented yet.")
    def test_stop(self, sample_dir, config_file_name):
        _ = Containers(sample_dir / config_file_name)

    @config_file_names
    @pytest.mark.skip(reason="Not implemented yet.")
    def test_ping(self, sample_dir, config_file_name):
        _ = Containers(sample_dir / config_file_name)


@config_file_names
@pytest.mark.skipif(
    DOCKER_NOT_AVAILABLE, reason="Docker isn't available in this environment."
)
def test_launch_containers(sample_dir, config_file_name):
    _ = launch_containers(sample_dir / config_file_name, remove=True, network="host")
