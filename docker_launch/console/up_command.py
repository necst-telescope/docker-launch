from typing import Dict, List, Union

from cleo import Command

from ..launch import launch_containers


class UpCommand(Command):
    """
    Create and launch docker containers on multiple hosts

    up
        {config : Path to launch configuration file}
        {--add-host=* : *Add custom host-to-IP mapping (host:ip)}
        {--blkio-weight=? :
            *Block IO (relative weight), between 10 and 1000, or 0 to disable
            (default 0)}
        {--blkio-weight-device=* :
            *Block IO weight (relative device weight), device_path:weight}
        {--cap-add=* : Add Linux capabilities}
        {--cap-drop=* : Drop Linux capabilities}
        {--cgroup-parent=? : *Optional parent cgroup for the container}
        {--cpu-count=? : *CPU count (Windows only)}
        {--cpu-percent=? : *CPU percent (Windows only)}
        {--cpu-period=? : *Limit CPU CFS (Completely Fair Scheduler) period}
        {--cpu-quota=? : *Limit CPU CFS (Completely Fair Scheduler) quota}
        {--cpu-rt-period=? : *Limit CPU real-time period in microseconds}
        {--cpu-rt-runtime=? : *Limit CPU real-time runtime in microseconds}
        {--c|cpu-shares=? : *CPU shares (relative weight)}
        {--cpuset-cpus=? : *CPUs in which to allow execution (0-3, 0,1)}
        {--cpuset-mems=? : *MEMs in which to allow execution (0-3, 0,1)}
        {--device=* : *Add a host device to the container}
        {--device-cgroup-rule=* : *Add a rule to the cgroup allowed devices list}
        {--device-read-bps=* : *Limit read rate (bytes per second) from a device}
        {--device-read-iops=* : *Limit read rate (IO per second) from a device}
        {--device-write-bps=* : *Limit write rate (bytes per second) to a device}
        {--device-write-iops=* : *Limit write rate (IO per second) to a device}
        {--dns=* : *Set custom DNS servers}
        {--dns-opt=* : *Set DNS options}
        {--dns-option=* : *Set DNS options}
        {--dns-search=* : *Set custom DNS search domains}
        {--domainname=* : *Container NIS domain name}
        {--entrypoint=* : *Overwrite the default ENTRYPOINT of the image}
        {--e|env=* : *Set environment variables}
        {--group-add=* : *Add additional groups to join}
        {--health-cmd=? : *Command to run to check health}
        {--health-interval=? : *Time between running the check (ms|s|m|h) (default 0s)}
        {--health-retries=? : *Consecutive failures needed to report unhealthy}
        {--health-start-period=? :
            *Start period for the container to initialize before starting health-retries
            countdown (ms|s|m|h) (default 0s)}
        {--health-timeout=? :
            *Maximum time to allow one check to run (ms|s|m|h) (default 0s)}
        {--hostname=? : *Container host name}
        {--init :
            *Run an init inside the container that forwards signals and reaps processes}
        {--ipc=? : *IPC mode to use}
        {--isolation=? : *Container isolation technology}
        {--kernel-memory=? : *Kernel memory limit}
        {--l|label=* : *Set meta data on a container}
        {--link=* : *Add link to another container}
        {--mac-address=? : *Container MAC address (e.g., 92:d0:c6:0a:29:33)}
        {--m|memory=? : *Memory limit}
        {--memory-reservation=? : *Memory soft limit}
        {--memory-swap=? :
            *Swap limit equal to memory plus swap: '-1' to enable unlimited swap}
        {--memory-swappiness=? : *Tune container memory swappiness (0 to 100)}
        {--name=? : *Assign a name to the container}
        {--net=? : Conenct a container to a network}
        {--network=? : Connect a container to a network}
        {--oom-kill-disable : *Disable OOM killer}
        {--oom-score-adj=? : *Tune host's OOM preferences (-1000 to 1000)}
        {--pid=? : *PID namespace to use}
        {--pids-limit=? : *Tune container pids limit (set -1 for unlimited)}
        {--platform=? : *Set platform if server is multi-platform capable}
        {--privileged : *Give extended privileges to this container}
        {--p|publish=* : *Publish a container's port(s) to the host}
        {--P|publish-all : *Publish all exposed ports to random ports}
        {--read-only : *Mount the container's root filesystem as read only}
        {--restart=? : *Restart policy to apply when a container exits}
        {--rm : Automatically remove the container when it exits}
        {--runtime=? : *Runtime to use for this container}
        {--security-opt=* : *Security options}
        {--shm-size=? : *Size of /dev/shm}
        {--stop-signal=? : *Signal to stop a container}
        {--storage-opt=* : *Storage driver options for the container}
        {--sysctl=* : *Sysctl options}
        {--tmpfs=* : *Mount a tmpfs directory}
        {--t|tty : *Allocate a pseudo-TTY}
        {--u|user=? : *Username or UID (format: <name:uid>[:<group|gid>])}
        {--userns=? : *User namespace to use}
        {--uts=? : *UTS namespace to use}
        {--volume=* : *Bind mount a volume}
        {--volume-driver=? : *Optional volume driver for the container}
        {--volumes-from=* : *Mount volumes from the specified container(s)}
        {--w|workdir=? : *Working directory inside the container}
    """

    # All options are globally applied.
    # Options whose explanation starts with asterisk are experimental, so may be buggy.

    def handle(self) -> int:
        config_file_path = self.argument("config")

        options = {
            "blkio_weight": self._parse_int(self.option("blkio-weight")),
            "blkio_weight_device": self._parse_keyword_mapping(
                self.option("blkio-weight-device"), "Path", "Weight"
            ),
            "cap_add": self._parse_list(self.option("cap-add")),
            "cap_drop": self._parse_list(self.option("cap-drop")),
            "cgroup_parent": self.option("cgroup-parent"),
            "cpu_count": self._parse_int(self.option("cpu-count")),
            "cpu_percent": self._parse_int(self.option("cpu-percent")),
            "cpu_period": self._parse_int(self.option("cpu-period")),
            "cpu_quota": self._parse_int(self.option("cpu-quota")),
            "cpu_rt_period": self._parse_int(self.option("cpu-rt-period")),
            "cpu_rt_runtime": self._parse_int(self.option("cpu-rt-runtime")),
            "cpu_shares": self._parse_int(self.option("cpu-shares")),
            "cpuset_cpus": self.option("cpuset-cpus"),
            "cpuset_mems": self.option("cpuset-mems"),
            "device_cgroup_rules": self._parse_list(self.option("device-cgroup-rule")),
            "device_read_bps": self._parse_keyword_mapping(
                self.option("device-read-bps"), "Path", "Rate"
            ),
            "device_read_iops": self._parse_keyword_mapping(
                self.option("device-read-iops"), "Path", "Rate"
            ),
            "device_write_bps": self._parse_keyword_mapping(
                self.option("device-write-bps"), "Path", "Rate"
            ),
            "device_write_iops": self._parse_keyword_mapping(
                self.option("device-write-iops"), "Path", "Rate"
            ),
            "devices": self._parse_mapping(self.option("device")),
            "dns": self._parse_list(self.option("dns")),
            "dns_opt": self._parse_list(
                self.option("dns-opt"), self.option("dns-option")
            ),
            "dns_search": self._parse_list(self.option("dns-search")),
            "domainname": self._parse_list(self.option("domainname")),
            "entrypoint": self._parse_list(self.option("entrypoint")),
            "environment": self._parse_mapping(self.option("env"), sep="="),
            "extra_hosts": self._parse_mapping(self.option("add-host")),
            "group_add": self._parse_list(self.option("group-add")),
            "healthcheck": self._parse_scattered_mapping(
                [
                    self.option("health-cmd"),
                    self.option("health-interval"),
                    self.option("health-retries"),
                    self.option("health-start-period"),
                    self.option("health-timeout"),
                ],
                ["Test", "Interval", "Retries", "StartPeriod", "Timeout"],
            ),
            "hostname": self.option("hostname"),
            "init": self.option("init"),
            "ipc_mode": self.option("ipc"),
            "isolation": self.option("isolation"),
            "kernel_memory": self.option("kernel-memory"),
            "labels": self._parse_mapping(self.option("label"), sep="="),
            "links": self._parse_mapping(self.option("link")),
            "mac_address": self.option("mac-address"),
            "mem_limit": self.option("memory"),
            "mem_reservasion": self.option("memory-reservation"),
            "mem_swappiness": self._parse_int(self.option("memory-swappiness")),
            "memswap_limit": self.option("memory-swap"),
            "name": self.option("name"),
            "network_mode": self._parse_network(
                self.option("net"), self.option("network")
            ),
            "oom_kill_disable": self.option("oom-kill-disable"),
            "oom_score_adj": self._parse_int(self.option("oom-score-adj")),
            "pid_mode": self.option("pid"),
            "pids_limit": self._parse_int(self.option("pids-limit")),
            "platform": self.option("platform"),
            "ports": self._parse_ports(self.option("publish")),
            "privileged": self.option("privileged"),
            "publish_all_ports": self.option("publish-all"),
            "read_only": self.option("read-only"),
            "remove": self.option("rm"),
            "restart_policy": self._parse_keyword_mapping(
                [self.option("restart")], "Name", "MaximumRetryCount"
            ),
            "runtime": self.option("runtime"),
            "security_opt": self._parse_list(self.option("security-opt")),
            "shm_size": self.option("shm-size"),
            "stop_signal": self.option("stop-signal"),
            "storage_opt": self._parse_mapping(self.option("storage-opt")),
            "sysctls": self._parse_mapping(self.option("sysctl")),
            "tmpfs": self._parse_mapping(self.option("tmpfs")),
            "tty": self.option("tty"),
            "user": self._parse_int_if_possible(self.option("user")),
            "userns_mode": self.option("userns"),
            "uts_mode": self.option("uts"),
            "volume_driver": self.option("volume-driver"),
            "volumes": self._parse_list(self.option("volume")),
            "volumes_from": self.option("volumes-from"),
            "working_dir": self.option("workdir"),
        }
        options = dict(filter(lambda x: x[1] is not None, options.items()))
        self.line(str(options))

        launch_containers(config_file_path, **options)
        return 0

    @staticmethod
    def _parse_int(expr: str) -> int:
        try:
            return int(expr)
        except TypeError:
            return

    @staticmethod
    def _parse_list(expr: List[str], *additional_expr) -> List[str]:
        for e in additional_expr:
            expr += e
        return expr if len(expr) > 0 else None

    @staticmethod
    def _parse_mapping(expr: List[str], sep: str = ":") -> Dict[str, str]:
        try:
            expr_splitted = [e.split(sep, 1) for e in expr]
            ret = {k: v for k, v in expr_splitted}
            return ret if len(ret) > 0 else None
        except ValueError:
            raise ValueError("Mapping should be given in 'key:value' form")
        except AttributeError:
            return None

    @staticmethod
    def _parse_keyword_mapping(
        expr: List[str], *keys, sep: str = ":"
    ) -> List[Dict[str, str]]:
        try:
            expr_splitted = [e.split(sep, 1) for e in expr]
            ret = [{k: v for k, v in zip(keys, e)} for e in expr_splitted]
            return ret if len(ret) > 0 else None
        except ValueError:
            raise ValueError("Mapping should be given in 'key:value' form")
        except AttributeError:
            return None

    @staticmethod
    def _parse_scattered_mapping(expr: List[str], keys: List[str]) -> Dict[str, str]:
        ret = {k: v for k, v in zip(keys, expr)}
        return ret if any([e is not None for e in ret.values()]) else None

    @staticmethod
    def _parse_ports(expr: List[str]) -> Dict[str, str]:
        expr_splitted = [e.rsplit(":", 1) for e in expr]
        # TODO: Support (address, port) syntax for host
        ret = {container: int(host) for host, container in expr_splitted}
        return ret if len(ret) > 0 else None

    def _parse_network(self, expr1: str, expr2: str) -> str:
        supported = ["bridge", "none", "host"]
        expr = expr1 or expr2
        if expr is None:
            return None
        if expr in supported:
            return expr
        if expr.find(":") != -1:
            # Might be container:<name|id> format
            return expr
        self.line(f"Unsupported network type '{expr}'")

    @staticmethod
    def _parse_int_if_possible(expr: str) -> Union[int, str]:
        try:
            return int(expr)
        except (ValueError, TypeError):
            return expr
