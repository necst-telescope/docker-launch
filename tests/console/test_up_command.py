import pytest
from cleo import CommandTester


@pytest.fixture
def tester(command_tester_factory) -> CommandTester:
    return command_tester_factory("up")


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


@pytest.mark.usefixtures("keyboardinterrupt_on_sleep", "mock_docker_client")
@config_file_names
def test_up(tester, sample_dir, config_file_name):
    tester.execute(str(sample_dir / config_file_name))
    assert tester.status_code == 0
