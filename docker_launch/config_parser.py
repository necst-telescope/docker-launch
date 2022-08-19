from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Dict, Hashable, List, Union

from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile

from . import utils
from .exceptions import ConfigFileError
from .typing import Literal, PathLike


Substitution = Dict[str, str]
LaunchConfiguration = Dict[Literal["image", "cmd", "machine"], str]


def _substitute_command(
    template: str, values: Union[List[Substitution], Substitution]
) -> List[str]:
    if isinstance(values, dict):
        return template.format_map(defaultdict(lambda: "", values))

    return [template.format_map(defaultdict(lambda: "", v)) for v in values]


class ConfigFileParser:

    SpecialTopLevelKeys = ["include"]
    SpecialInTableKeys = ["baseimg", "command", "targets"]

    def __init__(self, config_path: PathLike):
        self.config_path = Path(config_path)

    @property
    def raw_content(self) -> TOMLDocument:
        return self._read(self.config_path)

    @staticmethod
    def _read(path: PathLike) -> TOMLDocument:
        return TOMLFile(path).read()

    def _validate(self, content: TOMLDocument) -> None:
        _content = deepcopy(content)
        for k, v in _content.items():
            if k in self.SpecialTopLevelKeys:
                continue
            if not isinstance(v, dict):
                raise ConfigFileError(f"Value of '{k}' should be table-type.")
            _ = [v.pop(_k, None) for _k in self.SpecialInTableKeys]
            if len(v) > 0:
                raise ConfigFileError(f"In-table data {v.keys()} are not supported.")

    @classmethod
    def parse(cls, config_path: PathLike) -> Dict[Hashable, List[LaunchConfiguration]]:
        parsed = cls(config_path)._parse()
        return utils._groupby(parsed, "machine")

    @staticmethod
    def _resolve_path(path: PathLike, parent: Path):
        return path if Path(path).is_absolute() else parent / path

    def _parse(
        self, path: Path = None, already_parsed: List[Path] = []
    ) -> List[LaunchConfiguration]:
        if path is None:
            path = self.config_path
            already_parsed = []
            # XXX: Somehow this list shares its values across instances

        if path in already_parsed:
            return {}
        already_parsed.append(path)

        config = self._read(path)
        self._validate(config)

        launch_config = []

        additional_config_files = config.pop("include", [])
        for _path in additional_config_files:
            _path = self._resolve_path(_path, path.parent)
            parsed = self._parse(_path, already_parsed)
            launch_config.extend(parsed)

        for group in config.values():
            _command_template = group.get("command", "")
            _substitution_values = group.get("targets", [])
            commands = _substitute_command(_command_template, _substitution_values)

            image = group.get("baseimg", "ubuntu:latest")
            machines = [s.get("__machine__", None) for s in _substitution_values]
            for command, machine in zip(commands, machines):
                _config = {"image": image, "cmd": command, "machine": machine}
                launch_config.append(_config)
        return launch_config


parse = ConfigFileParser.parse
