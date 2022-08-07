from pathlib import Path

import pytest

from docker_launch.config_parser import _substitute_command, _groupby, parse


@pytest.fixture
def sample_dir():
    return Path(__file__).parent / "sample"


def test__substitute_command():
    assert _substitute_command("ls", {}) == "ls"
    assert _substitute_command("ls", [{}]) == ["ls"]
    assert _substitute_command("ls", [{}, {}]) == ["ls", "ls"]

    assert _substitute_command("ls", {"a": "./"}) == "ls"
    assert _substitute_command("ls", [{"a": "./"}]) == ["ls"]
    assert _substitute_command("ls", [{"a": "./"}, {"a": "../"}]) == ["ls", "ls"]

    assert _substitute_command("ls {a}", {"a": "./"}) == "ls ./"
    assert _substitute_command("ls {a}", [{"a": "./"}]) == ["ls ./"]
    assert _substitute_command("ls {a}", [{"a": "./"}, {"a": "../"}]) == [
        "ls ./",
        "ls ../",
    ]

    assert _substitute_command("ls {a} {b}", {"a": "./"}) == "ls ./ "
    assert _substitute_command("ls {a} {b}", [{"a": "./"}]) == ["ls ./ "]
    assert _substitute_command("ls {a} {b}", [{"a": "./"}, {"b": "../"}]) == [
        "ls ./ ",
        "ls  ../",
    ]

    assert _substitute_command("ls {a} {b}", {"a": "-l", "b": "./"}) == "ls -l ./"
    assert _substitute_command("ls {a} {b}", [{"a": "-l", "b": "./"}]) == ["ls -l ./"]
    assert _substitute_command(
        "ls {a} {b}", [{"a": "-l", "b": "./"}, {"a": "-l", "b": "../"}]
    ) == ["ls -l ./", "ls -l ../"]


def test__groupby():
    assert _groupby([{"k": 1}], "k") == {1: [{"k": 1}]}
    assert _groupby([{"k": 1, "l": 2}], "k") == {1: [{"k": 1, "l": 2}]}
    assert _groupby([{"k": 1}, {"k": 1, "l": 2}], "k") == {
        1: [{"k": 1}, {"k": 1, "l": 2}]
    }
    assert _groupby([{"l": 1}, {"k": 1, "l": 2}], "k") == {
        "": [{"l": 1}],
        1: [{"k": 1, "l": 2}],
    }


class TestParse:
    def test_parse(self, sample_dir):
        assert parse(sample_dir / "config.toml") == {
            "localhost": [
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run run-some-nodes.exec.py",
                    "machine": "localhost",
                }
            ],
            "user@192.168.1.2": [
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run run-other-nodes.exec.py",
                    "machine": "user@192.168.1.2",
                }
            ],
            None: [
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run run-other-nodes.exec.py",
                    "machine": None,
                }
            ],
        }

    def test_parse_multiple_samebase(self, sample_dir):
        assert parse(sample_dir / "config_multiple_samebase.toml") == {
            "localhost": [
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run run-some-nodes.exec.py",
                    "machine": "localhost",
                },
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run some_node.py",
                    "machine": "localhost",
                },
            ],
            "user@192.168.1.2": [
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run run-other-nodes.exec.py",
                    "machine": "user@192.168.1.2",
                },
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run other_node.py",
                    "machine": "user@192.168.1.2",
                },
            ],
            None: [
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run run-other-nodes.exec.py",
                    "machine": None,
                },
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run unknown_node.py",
                    "machine": None,
                },
            ],
        }

    def test_parse_multiple_differentbase(self, sample_dir):
        assert parse(sample_dir / "config_multiple_differentbase.toml") == {
            "localhost": [
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run run-some-nodes.exec.py",
                    "machine": "localhost",
                },
                {
                    "image": "ros:foxy-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run some_node.py",
                    "machine": "localhost",
                },
            ],
            "user@192.168.1.2": [
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run run-other-nodes.exec.py",
                    "machine": "user@192.168.1.2",
                },
                {
                    "image": "ros:foxy-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run other_node.py",
                    "machine": "user@192.168.1.2",
                },
            ],
            None: [
                {
                    "image": "ros:humble-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run run-other-nodes.exec.py",
                    "machine": None,
                },
                {
                    "image": "ros:foxy-ros-base",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 run unknown_node.py",
                    "machine": None,
                },
            ],
        }

    @pytest.mark.skip(reason="Not supported yet.")
    def test_parse_include_samebase(self, sample_dir):
        assert parse(sample_dir / "config_include_samebase.toml")

    @pytest.mark.skip(reason="Not supported yet.")
    def test_parse_include_differentbase(self, sample_dir):
        assert parse(sample_dir / "config_include_differentbase.toml")
