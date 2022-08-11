from pathlib import Path
from unittest.mock import patch

import pytest
from cleo import CommandTester


@pytest.fixture
def tester(command_tester_factory) -> CommandTester:
    return command_tester_factory("check")


@pytest.fixture
def tmp_home_dir(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("user")


@pytest.fixture
def tmp_home_dir_with_default_ssh_key_pair(tmp_home_dir: Path) -> Path:
    (tmp_home_dir / ".ssh").mkdir()
    (tmp_home_dir / ".ssh" / "id_rsa").touch(0o600)
    (tmp_home_dir / ".ssh" / "id_rsa.pub").touch(0o644)
    return tmp_home_dir


@pytest.fixture
def tmp_home_dir_with_default_ssh_public_key_only(tmp_home_dir: Path) -> Path:
    (tmp_home_dir / ".ssh").mkdir()
    (tmp_home_dir / ".ssh" / "id_rsa.pub").touch(0o644)
    return tmp_home_dir


@pytest.fixture
def tmp_home_dir_with_default_ssh_private_key_only(tmp_home_dir: Path) -> Path:
    (tmp_home_dir / ".ssh").mkdir()
    (tmp_home_dir / ".ssh" / "id_rsa").touch(0o600)
    return tmp_home_dir


@pytest.fixture
def tmp_home_dir_with_no_default_ssh_key(tmp_home_dir: Path) -> Path:
    (tmp_home_dir / ".ssh").mkdir()
    return tmp_home_dir


@pytest.mark.usefixtures("mock_ssh_connection")
def test_check_pass_interactive(tester):
    tester.execute("user@172.29.0.1")
    assert tester.io.fetch_output() == "OK\n"
    assert tester.status_code == 0


@pytest.mark.usefixtures("mock_ssh_connection")
def test_check_pass_noninteractive(tester):
    tester.execute("user@172.29.0.1", interactive=False)
    assert tester.io.fetch_output() == "OK\n"
    assert tester.status_code == 0


@pytest.mark.usefixtures("mock_ssh_connection")
def test_check_fail_interactive(tester):
    tester.execute("me@172.29.0.1")
    assert tester.io.fetch_error() == "Cannot connect. Use --setup flag to set-up.\n"
    assert tester.status_code == 1


@pytest.mark.usefixtures("mock_ssh_connection")
def test_check_fail_noninteractive(tester):
    tester.execute("me@172.29.0.1", interactive=False)
    assert tester.io.fetch_error() == "Cannot connect. Use --setup flag to set-up.\n"
    assert tester.status_code == 1


@pytest.mark.usefixtures("mock_successful_ssh_copy_id")
def test_check_setup_no_key_found_interactive(
    tester, tmp_home_dir_with_no_default_ssh_key
):
    private_key = tmp_home_dir_with_no_default_ssh_key / ".ssh" / "id_rsa"
    public_key = tmp_home_dir_with_no_default_ssh_key / ".ssh" / "id_rsa.pub"
    assert not private_key.exists()
    assert not public_key.exists()

    with patch(
        "docker_launch.console.check_command.SSH_DIR",
        tmp_home_dir_with_no_default_ssh_key / ".ssh",
    ):
        tester.execute("me@172.29.0.1 -s")

    assert "Default RSA key" in tester.io.fetch_output()
    assert "generated." in tester.io.fetch_output()
    assert (
        "Successfully copied public key to remote host 'me@172.29.0.1'."
        in tester.io.fetch_output()
    )
    assert "Connection OK!" in tester.io.fetch_output()

    assert private_key.exists()
    assert public_key.exists()

    assert tester.status_code == 0


@pytest.mark.usefixtures("mock_successful_ssh_copy_id")
def test_check_setup_only_public_key_found_interactive(
    tester, tmp_home_dir_with_default_ssh_public_key_only
):
    private_key = tmp_home_dir_with_default_ssh_public_key_only / ".ssh" / "id_rsa"
    public_key = tmp_home_dir_with_default_ssh_public_key_only / ".ssh" / "id_rsa.pub"
    assert not private_key.exists()
    assert public_key.exists()

    with patch(
        "docker_launch.console.check_command.SSH_DIR",
        tmp_home_dir_with_default_ssh_public_key_only / ".ssh",
    ):
        tester.execute("me@172.29.0.1 -s")

    assert (
        "Successfully copied public key to remote host 'me@172.29.0.1'."
        in tester.io.fetch_output()
    )
    assert "Connection OK!" in tester.io.fetch_output()

    assert private_key.exists()
    assert public_key.exists()

    assert tester.status_code == 0


@pytest.mark.usefixtures("mock_successful_ssh_copy_id")
def test_check_setup_only_private_key_found_interactive(
    tester, tmp_home_dir_with_default_ssh_private_key_only
):
    private_key = tmp_home_dir_with_default_ssh_private_key_only / ".ssh" / "id_rsa"
    public_key = tmp_home_dir_with_default_ssh_private_key_only / ".ssh" / "id_rsa.pub"
    assert private_key.exists()
    assert not public_key.exists()

    with patch(
        "docker_launch.console.check_command.SSH_DIR",
        tmp_home_dir_with_default_ssh_private_key_only / ".ssh",
    ):
        tester.execute("me@172.29.0.1 -s")

    assert (
        "Successfully copied public key to remote host 'me@172.29.0.1'."
        in tester.io.fetch_output()
    )
    assert "Connection OK!" in tester.io.fetch_output()

    assert private_key.exists()
    assert public_key.exists()

    assert tester.status_code == 0


@pytest.mark.usefixtures("mock_successful_ssh_copy_id")
def test_check_setup_default_key_pair_found_interactive(
    tester, tmp_home_dir_with_default_ssh_key_pair
):
    private_key = tmp_home_dir_with_default_ssh_key_pair / ".ssh" / "id_rsa"
    public_key = tmp_home_dir_with_default_ssh_key_pair / ".ssh" / "id_rsa.pub"
    assert private_key.exists()
    assert public_key.exists()

    with patch(
        "docker_launch.console.check_command.SSH_DIR",
        tmp_home_dir_with_default_ssh_key_pair / ".ssh",
    ):
        tester.execute("me@172.29.0.1 -s")

    assert (
        "Successfully copied public key to remote host 'me@172.29.0.1'."
        in tester.io.fetch_output()
    )
    assert "Connection OK!" in tester.io.fetch_output()

    assert private_key.exists()
    assert public_key.exists()

    assert tester.status_code == 0


@pytest.mark.usefixtures(
    "mock_ssh_copy_id_has_no_effect_identity_changed", "mock_ssh_key_not_locked"
)
def test_check_setup_identity_changed_interactive(
    tester, tmp_home_dir_with_default_ssh_key_pair
):
    with patch(
        "docker_launch.console.check_command.SSH_DIR",
        tmp_home_dir_with_default_ssh_key_pair / ".ssh",
    ):
        tester.execute("me@172.29.0.1 -s")

    assert "ssh keygen -R 172.29.0.1" in tester.io.fetch_output()
    assert tester.status_code == 2


@pytest.mark.usefixtures("mock_ssh_copy_id_has_no_effect", "mock_ssh_key_locked")
def test_check_setup_locked_key_interactive(
    tester, tmp_home_dir_with_default_ssh_key_pair
):
    with patch(
        "docker_launch.console.check_command.SSH_DIR",
        tmp_home_dir_with_default_ssh_key_pair / ".ssh",
    ):
        tester.execute("me@172.29.0.1 -s")

    assert "This error may originates from locked key." in tester.io.fetch_output()
    assert tester.status_code == 3


@pytest.mark.usefixtures("mock_ssh_copy_id_has_no_effect", "mock_ssh_key_not_locked")
def test_check_setup_unknown_failure_interactive(
    tester, tmp_home_dir_with_default_ssh_key_pair
):
    with patch(
        "docker_launch.console.check_command.SSH_DIR",
        tmp_home_dir_with_default_ssh_key_pair / ".ssh",
    ):
        tester.execute("me@172.29.0.1 -s")

    assert "Unknown error." in tester.io.fetch_output()
    assert tester.status_code == 4
