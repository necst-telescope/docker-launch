import os
from collections import defaultdict
from typing import Dict, Hashable, List, Union

from tomlkit.toml_file import TOMLFile

from . import utils
from .typing import Literal


Substitution = Dict[str, str]
LaunchConfiguration = Dict[Literal["image", "cmd", "machine"], str]


def _substitute_command(
    template: str, values: Union[List[Substitution], Substitution]
) -> List[str]:
    if isinstance(values, dict):
        return template.format_map(defaultdict(lambda: "", values))

    return [template.format_map(defaultdict(lambda: "", v)) for v in values]


def parse(config_path: os.PathLike) -> Dict[Hashable, List[LaunchConfiguration]]:
    config = TOMLFile(config_path).read()

    additional_config_files = config.pop("include", [])
    if additional_config_files:  # TODO: Implement.
        raise NotImplementedError

    groups = [v for v in config.values() if isinstance(v, dict)]

    launch_config = []
    for group in groups:
        command_template = group.get("command", "")
        substitution_values = group.get("targets", [])
        commands = _substitute_command(command_template, substitution_values)

        image = group.get("baseimg", "ubuntu:latest")
        machines = [subst.get("__machine__", None) for subst in substitution_values]
        _ = [
            launch_config.append({"image": image, "cmd": command, "machine": machine})
            for command, machine in zip(commands, machines)
        ]
    return utils._groupby(launch_config, "machine")
