from pathlib import Path

import pytest
from cleo import CommandTester

from docker_launch import check_docker_available

DOCKER_NOT_AVAILABLE = not check_docker_available()
pytestmark = pytest.mark.skipif(
    DOCKER_NOT_AVAILABLE, reason="Docker isn't available in this environment."
)


@pytest.fixture
def tester(command_tester_factory) -> CommandTester:
    return command_tester_factory("up")


@pytest.fixture
def tmp_volume(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("volume")


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


@pytest.mark.skip(reason="Still experimental")
def test_up_add_host():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_blkio_weight():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_blkio_weight_device():
    ...


@pytest.mark.usefixtures("keyboardinterrupt_on_sleep", "mock_docker_client")
class TestUpCapAdd:
    def test_equal(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --cap-add=SYS_RAWIO --rm")
        assert tester.status_code == 0

    def test_whitespace(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --cap-add SYS_RAWIO --rm")
        assert tester.status_code == 0

    def test_multiple(self, tester, sample_dir):
        tester.execute(
            f"{sample_dir / 'config.toml'} --cap-add=SYS_RAWIO --cap-add SYS_ADMIN --rm"
        )
        assert tester.status_code == 0


@pytest.mark.usefixtures("keyboardinterrupt_on_sleep", "mock_docker_client")
class TestUpCapDrop:
    def test_equal(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --cap-drop=MKNOD --rm")
        assert tester.status_code == 0

    def test_whitespace(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --cap-drop MKNOD --rm")
        assert tester.status_code == 0

    def test_multiple(self, tester, sample_dir):
        tester.execute(
            f"{sample_dir / 'config.toml'} --cap-drop=MKNOD --cap-drop SYS_ADMIN --rm"
        )
        assert tester.status_code == 0


@pytest.mark.skip(reason="Still experimental")
def test_up_cgroup_parent():
    ...


@pytest.mark.skip(reason="Still experimental, and OS specific")
def test_up_cpu_count():
    ...


@pytest.mark.skip(reason="Still experimental, and OS specific")
def test_up_cpu_percent():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_cpu_period():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_cpu_quota():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_cpu_rt_period():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_cpu_rt_runtime():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_cpu_shares():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_cpuset_cpus():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_cpuset_mems():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_device():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_device_cgroup_rule():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_device_read_bps():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_device_read_iops():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_device_write_bps():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_device_write_iops():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_dns():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_dns_opt():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_dns_option():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_dns_search():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_domainname():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_entrypoint():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_env():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_group_add():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_health_cmd():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_health_interval():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_health_retries():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_health_start_period():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_health_timeout():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_hostname():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_init():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_ipc():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_isolation():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_kernel_memory():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_label():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_link():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_mac_address():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_memory():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_memory_reservation():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_memory_swap():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_memory_swappiness():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_name():
    ...


@pytest.mark.usefixtures("keyboardinterrupt_on_sleep", "mock_docker_client")
class TestUpNet:
    def test_equal(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --net=host --rm")
        assert tester.status_code == 0
        assert "Unsupported network type." not in tester.io.fetch_error()

    def test_whitespace(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --net host --rm")
        assert tester.status_code == 0
        assert "Unsupported network type." not in tester.io.fetch_error()

    def test_not_supported(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --net=custom --rm")
        assert tester.status_code == 0
        assert "Unsupported network type." in tester.io.fetch_error()


@pytest.mark.usefixtures("keyboardinterrupt_on_sleep", "mock_docker_client")
class TestUpNetwork:
    def test_equal(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --network=host --rm")
        assert tester.status_code == 0
        assert "Unsupported network type." not in tester.io.fetch_error()

    def test_whitespace(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --network host --rm")
        assert tester.status_code == 0
        assert "Unsupported network type." not in tester.io.fetch_error()

    def test_not_supported(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --network=custom --rm")
        assert tester.status_code == 0
        assert "Unsupported network type." in tester.io.fetch_error()


@pytest.mark.skip(reason="Still experimental")
def test_up_oom_kill_disable():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_oom_score_adj():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_pid():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_pids_limit():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_platform():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_privileged():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_publish():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_publish_all():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_read_only():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_restart():
    ...


@pytest.mark.usefixtures("keyboardinterrupt_on_sleep", "mock_docker_client")
@config_file_names
def test_up_rm(tester, sample_dir, config_file_name):
    tester.execute(f"{sample_dir / config_file_name} --rm")
    assert tester.status_code == 0


@pytest.mark.skip(reason="Still experimental")
def test_up_runtime():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_security_opt():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_shm_size():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_stop_signal():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_storage_opt():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_sysctl():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_tmpfs():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_tty():
    ...


@pytest.mark.usefixtures("keyboardinterrupt_on_sleep", "mock_docker_client")
class TestUpUser:
    def test_username_long_equal(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --rm --user=root")
        assert tester.status_code == 0
        assert "Group/GID isn't supported." not in tester.io.fetch_error()

    def test_username_long_whitespace(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --rm --user root")
        assert tester.status_code == 0
        assert "Group/GID isn't supported." not in tester.io.fetch_error()

    def test_username_short_equal(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --rm -u=root")
        assert tester.status_code == 0
        assert "Group/GID isn't supported." not in tester.io.fetch_error()

    def test_username_short_whitespace(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --rm -u root")
        assert tester.status_code == 0
        assert "Group/GID isn't supported." not in tester.io.fetch_error()

    def test_username_groupname(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --rm -u=root:root")
        assert tester.status_code == 0
        assert "Group/GID isn't supported." in tester.io.fetch_error()

    def test_uid(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --rm -u=0")
        assert tester.status_code == 0
        assert "Group/GID isn't supported." not in tester.io.fetch_error()

    def test_uid_gid(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --rm -u=0:0")
        assert tester.status_code == 0
        assert "Group/GID isn't supported." in tester.io.fetch_error()

    def test_username_gid(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --rm -u=root:0")
        assert tester.status_code == 0
        assert "Group/GID isn't supported." in tester.io.fetch_error()

    def test_uid_groupname(self, tester, sample_dir):
        tester.execute(f"{sample_dir / 'config.toml'} --rm -u=0:root")
        assert tester.status_code == 0
        assert "Group/GID isn't supported." in tester.io.fetch_error()


@pytest.mark.skip(reason="Still experimental")
def test_up_userns():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_uts():
    ...


@pytest.mark.usefixtures("keyboardinterrupt_on_sleep", "mock_docker_client")
class TestUpVolume:
    def test_equal(self, tester, sample_dir, tmp_volume):
        tester.execute(
            f"{sample_dir / 'config.toml'} --rm --volume={tmp_volume}:/home/volume"
        )
        assert tester.status_code == 0
        assert "Anonymous volume isn't supported." not in tester.io.fetch_error()

    def test_whitespace(self, tester, sample_dir, tmp_volume):
        tester.execute(
            f"{sample_dir / 'config.toml'} --rm --volume {tmp_volume}:/home/volume"
        )
        assert tester.status_code == 0
        assert "Anonymous volume isn't supported." not in tester.io.fetch_error()

    def test_multiple(self, tester, sample_dir, tmp_volume):
        tester.execute(
            f"{sample_dir / 'config.toml'} --rm --volume {tmp_volume}:/home/volume1"
            f"--volume={tmp_volume}:/home/volume2"
        )
        assert tester.status_code == 0
        assert "Anonymous volume isn't supported." not in tester.io.fetch_error()

    def test_option_ro(self, tester, sample_dir, tmp_volume):
        tester.execute(
            f"{sample_dir / 'config.toml'} --rm --volume {tmp_volume}:/home/volume:ro"
        )
        assert tester.status_code == 0
        assert "Anonymous volume isn't supported." not in tester.io.fetch_error()

    def test_option_rw(self, tester, sample_dir, tmp_volume):
        tester.execute(
            f"{sample_dir / 'config.toml'} --rm --volume {tmp_volume}:/home/volume:rw"
        )
        assert tester.status_code == 0
        assert "Anonymous volume isn't supported." not in tester.io.fetch_error()

    def test_anonymous(self, tester, sample_dir, tmp_volume):
        tester.execute(f"{sample_dir / 'config.toml'} --rm --volume /home/volume")
        assert tester.status_code == 0
        assert "Anonymous volume isn't supported." in tester.io.fetch_error()

    def test_anonymous_with_option(self, tester, sample_dir, tmp_volume):
        tester.execute(f"{sample_dir / 'config.toml'} --rm --volume /home/volume:rw")
        assert tester.status_code == 0
        assert "Anonymous volume isn't supported." in tester.io.fetch_error()


@pytest.mark.skip(reason="Still experimental")
def test_up_volume_driver():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_volumes_from():
    ...


@pytest.mark.skip(reason="Still experimental")
def test_up_workdir():
    ...
