import pytest

from docker_launch.config_parser import _substitute_command, parse
from docker_launch.exceptions import ConfigFileError


class TestSubstituteCommand:
    def test_no_placeholder_empty_target(self):
        assert _substitute_command("ls", {}) == "ls"
        assert _substitute_command("ls", [{}]) == ["ls"]
        assert _substitute_command("ls", [{}, {}]) == ["ls", "ls"]

    def test_no_placeholder_redundant_target(self):
        assert _substitute_command("ls", {"a": "./"}) == "ls"
        assert _substitute_command("ls", [{"a": "./"}]) == ["ls"]
        assert _substitute_command("ls", [{"a": "./"}, {"a": "../"}]) == ["ls", "ls"]

    def test_single_substitution(self):
        assert _substitute_command("ls {a}", {"a": "./"}) == "ls ./"
        assert _substitute_command("ls {a}", [{"a": "./"}]) == ["ls ./"]
        assert _substitute_command("ls {a}", [{"a": "./"}, {"a": "../"}]) == [
            "ls ./",
            "ls ../",
        ]

    def test_multiple_substitutions_with_missing_key(self):
        assert _substitute_command("ls {a} {b}", {"a": "./"}) == "ls ./ "
        assert _substitute_command("ls {a} {b}", [{"a": "./"}]) == ["ls ./ "]
        assert _substitute_command("ls {a} {b}", [{"a": "./"}, {"b": "../"}]) == [
            "ls ./ ",
            "ls  ../",
        ]

    def test_multiple_substitutions(self):
        assert _substitute_command("ls {a} {b}", {"a": "-l", "b": "./"}) == "ls -l ./"
        assert _substitute_command("ls {a} {b}", [{"a": "-l", "b": "./"}]) == [
            "ls -l ./"
        ]
        assert _substitute_command(
            "ls {a} {b}", [{"a": "-l", "b": "./"}, {"a": "-l", "b": "../"}]
        ) == ["ls -l ./", "ls -l ../"]


class TestParse:
    def test_parse(self, sample_dir):
        assert parse(sample_dir / "config.toml") == {
            "localhost": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub first std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "localhost",
                }
            ],
            "user@172.29.1.2": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub /second std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "user@172.29.1.2",
                }
            ],
            None: [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub third std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": None,
                }
            ],
        }

    def test_parse_multiple_samebase(self, sample_dir):
        assert parse(sample_dir / "config_multiple_samebase.toml") == {
            "localhost": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub first std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "localhost",
                },
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub first std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "localhost",
                },
            ],
            "user@172.29.1.2": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub /second std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "user@172.29.1.2",
                },
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub /second std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "user@172.29.1.2",
                },
            ],
            None: [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub third std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": None,
                },
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub third std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": None,
                },
            ],
        }

    def test_parse_multiple_differentbase(self, sample_dir):
        assert parse(sample_dir / "config_multiple_differentbase.toml") == {
            "localhost": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub first std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "localhost",
                },
                {
                    "image": "ros:foxy-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub first std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "localhost",
                },
            ],
            "user@172.29.1.2": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub /second std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "user@172.29.1.2",
                },
                {
                    "image": "ros:foxy-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub /second std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "user@172.29.1.2",
                },
            ],
            None: [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub third std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": None,
                },
                {
                    "image": "ros:foxy-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub third std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": None,
                },
            ],
        }

    def test_parse_include_samebase(self, sample_dir):
        assert parse(sample_dir / "config_include_samebase.toml") == {
            "localhost": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub first std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "localhost",
                },
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub first std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "localhost",
                },
            ],
            "user@172.29.1.2": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub /second std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "user@172.29.1.2",
                },
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub /second std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "user@172.29.1.2",
                },
            ],
            None: [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub third std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": None,
                },
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub third std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": None,
                },
            ],
        }

    def test_parse_include_differentbase(self, sample_dir):
        assert parse(sample_dir / "config_include_differentbase.toml") == {
            "localhost": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub first std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "localhost",
                },
                {
                    "image": "ros:foxy-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub first std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "localhost",
                },
            ],
            "user@172.29.1.2": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub /second std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "user@172.29.1.2",
                },
                {
                    "image": "ros:foxy-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub /second std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "user@172.29.1.2",
                },
            ],
            None: [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub third std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": None,
                },
                {
                    "image": "ros:foxy-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub third std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": None,
                },
            ],
        }

    def test_not_grouped(self, sample_dir):
        with pytest.raises(ConfigFileError):
            parse(sample_dir / "config_not_grouped.toml")

    def test_recursive(self, sample_dir):
        assert parse(sample_dir / "config_recursive.toml") == {
            "localhost": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub first std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "localhost",
                }
            ],
            "user@172.29.1.2": [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub /second std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": "user@172.29.1.2",
                }
            ],
            None: [
                {
                    "image": "ros:humble-ros-core",
                    "cmd": "env ROS_DOMAIN_ID=1 ros2 topic pub third std_msgs/msg/Float64 '{data: 123.45}'",  # noqa: E501
                    "machine": None,
                }
            ],
        }
