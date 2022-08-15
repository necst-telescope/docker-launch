# docker-launch

[![PyPI](https://img.shields.io/pypi/v/docker-launch.svg?label=PyPI&style=flat-square)](https://pypi.org/pypi/docker-launch/)
[![Python](https://img.shields.io/pypi/pyversions/docker-launch.svg?label=Python&color=yellow&style=flat-square)](https://pypi.org/pypi/docker-launch/)
[![Test](https://img.shields.io/github/workflow/status/necst-telescope/docker-launch/Test?logo=github&label=Test&style=flat-square)](https://github.com/necst-telescope/docker-launch/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?label=License&style=flat-square)](https://github.com/necst-telescope/docker-launch/blob/main/LICENSE)

Create and launch docker containers on multiple hosts.

## Features

This library provides:

- SSH public key authentication checker and its set-up command
- Launch multiple Docker containers on arbitrary host(s), via command line or Python script

## Installation

```shell
pip install docker-launch
```

## Usage

To check if SSH public key authentication to `user@192.168.1.1` is enabled or not, run

```python
>>> from docker_launch import check_connection
>>> check_connection("user@192.168.1.1")
True
```

or from command line,

```shell
$ docker-launch check user@192.168.1.1
OK
```

If the authentication hasn't been set-up, you can configure it via

```shell
$ docker-launch check user@192.168.1.1 --setup
```

Once the authentication is set-up, let's prepare configuration file `path/to/config.toml`

```toml
[ros_topics]
baseimg = "ros:humble-ros-core"
command = "env ROS_DOMAIN_ID=1 ros2 topic pub {a} std_msgs/msg/Float64 '{{data: 123.45}}'"
targets = [
    { a = "first", __machine__ = "localhost" },
    { a = "/second", __machine__ = "user@172.29.1.2" },
]
```

This will spawn

- [`ros:humble-ros-core`](https://hub.docker.com/_/ros) container on the host machine, executing command `env ROS_DOMAIN_ID=1 ros2 topic pub first std_msgs/msg/Float64 '{data: 123.45}'`
- [`ros:humble-ros-core`](https://hub.docker.com/_/ros) container on `user@172.29.1.2`, executing command `env ROS_DOMAIN_ID=1 ros2 topic pub /second std_msgs/msg/Float64 '{data: 123.45}'`

by running

```python
>>> from docker_launch import launch_containers
>>> launch_containers("path/to/config.toml", remove=True)
```

or

```shell
$ docker-launch up path/to/config.toml --rm
```

For the details of the options, see [docker run documentation](https://docs.docker.com/engine/reference/commandline/run/) and [Docker SDK's documentation](https://docker-py.readthedocs.io/en/stable/containers.html#docker.models.containers.ContainerCollection.run).

<details><summary>Options of <code>docker run</code> command which <code>docker-launch</code> command and <code>docker_launch.launch_containers()</code> function doesn't support</summary>

- `--attach`, `-a`
- `--cgroupns`
- `--cidfile`
- `--detach`, `-d` (always `True`)
- `--detach-keys`
- `--disable-content-trust`
- `--env-file`
- `--expose`
- `--gpus`
- `-h` (use `--hostname` instead)
- `--interactive`, `-i`
- `--ip`
- `--ip6`
- `--label-file`
- `--link-local-ip`
- `--log-driver`
- `--log-opt`
- `--mount`
- `--net`
- `--net-alias`
- `--network`
- `--network-alias`
- `--no-healthcheck`
- `--pull`
- `--sig-proxy`
- `--stop-timeout`
- `--ulimit`
- `-v` (use `--volume` instead)

</details>
<details><summary>Options of Docker SDK's <code>docker.containers.run</code> function which <code>docker-launch</code> command doesn't support (<code>docker_launch.launch_containers()</code> function supports them)</summary>

- `auto_remove`
- `device_requests`
- `init_path`
- `log_config`
- `lxc_conf`
- `mounts`
- `nano_cpus`
- `network`
- `network_disabled`
- `network_mode`
- `stdin_open`
- `stdout`
- `stderr`
- `stream`
- `ulimits`
- `use_config_proxy`
- `version`

</details>

## Configuration File Spec

The configuration is described in [TOML](https://toml.io/en/) format.  
Required fields are:

- `baseimg` (string) - Name of the image from which the containers are created
- `command` (string) - Command template to execute in each containers, with [Python style placeholder](https://docs.python.org/3/library/string.html#format-string-syntax) (positional placeholder e.g. `{0}` isn't supported)
- `targets` (array of table) - List of parameter tables for each containers, and special parameter `__machine__`

The fields above must be grouped in a table.

```toml
[table-name]
baseimg = "docker:image-name"
command = "command template with {placeholder}"
targets = [
    { placeholder = "this", __machine__ = "user@172.29.1.2" },
    { placeholder = "that" },
]
```

A configuration file can have multiple tables

```toml
[table-1]
baseimg = "docker:image-name"
command = "command template with {placeholder}"
targets = [
    { placeholder = "this", __machine__ = "user@172.29.1.2" },
    { placeholder = "that" },
]

[table-2]
baseimg = "docker:other-image"
command = "other command {parameter} with curly braces {{escaped}}"
targets = [
    { parameter = 100, __machine__ = "user@172.29.1.2" },
    { parameter = 200 },
]
```

Following option is to be implemented soon.

- `include` (array of string) - Paths to additional configuration files

The instruction must be declared at top level (not inside tables).

```toml
include = ["path/to/other/config.toml", "path/to/another/config.toml"]

[table-name]
baseimg = "docker:image-name"
command = "command template with {placeholder}"
targets = [
    { placeholder = "this", __machine__ = "user@172.29.1.2" },
    { placeholder = "that" },
]
```

---

This library is using [Semantic Versioning](https://semver.org).
