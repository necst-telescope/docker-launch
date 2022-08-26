import docker
import pytest

from docker_launch import launch_containers, check_docker_available
from docker_launch.launch import Containers

DOCKER_NOT_AVAILABLE = not check_docker_available()
skip_if_docker_not_available = pytest.mark.skipif(
    DOCKER_NOT_AVAILABLE, reason="Docker isn't available in this environment."
)


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


@skip_if_docker_not_available
@config_file_names
@pytest.mark.usefixtures("mock_docker_client")
class TestContainers:
    def test_start(self, sample_dir, config_file_name):
        c = Containers(sample_dir / config_file_name)
        _ = c.start(remove=True)
        assert len(c.containers_list) == len(c._flatten(c.config))
        for container in c.containers_list:
            container.reload()
            assert container.status == "running"
            container.stop()

    def test_stop(self, sample_dir, config_file_name):
        c = Containers(sample_dir / config_file_name)
        _ = c.start()
        c.stop()

        for container in c.containers_list:
            container.reload()
            assert container.status == "exited"
            container.remove()

    def test_remove(self, sample_dir, config_file_name):
        c = Containers(sample_dir / config_file_name)
        _ = c.start()
        c.stop()
        c.remove()

        for container in c.containers_list:
            with pytest.raises(docker.errors.NotFound):
                container.reload()

    def test_ping(self, sample_dir, config_file_name):
        c = Containers(sample_dir / config_file_name)
        _ = c.start()
        result = c.ping()
        assert result == {}

        c.containers_list[0].stop()
        result = c.ping()
        assert len(result["exited"]) == 1

        c.stop()
        c.remove()

    @pytest.mark.usefixtures("keyboardinterrupt_on_sleep")
    def test_watch(self, sample_dir, config_file_name):
        c = Containers(sample_dir / config_file_name)
        _ = c.start()
        c.watch()
        for container in c.containers_list:
            container.reload()
            container.status == "exited"
        c.remove()


@pytest.mark.skip(reason="No idea how to test this.")
@skip_if_docker_not_available
@config_file_names
@pytest.mark.usefixtures("mock_docker_client", "keyboardinterrupt_on_sleep")
def test_launch_containers(sample_dir, config_file_name):
    _ = launch_containers(sample_dir / config_file_name, remove=True)
