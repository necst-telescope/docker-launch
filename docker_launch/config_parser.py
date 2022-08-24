from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Dict, Hashable, List, overload

from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile

from . import utils
from .exceptions import ConfigFileError
from .typing import Literal, PathLike


Substitution = Dict[str, str]
LaunchConfiguration = Dict[Literal["image", "cmd", "machine"], str]


@overload
def _substitute_command(template: str, values: Substitution) -> str:
    ...


def _substitute_command(template: str, values: List[Substitution]) -> List[str]:
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

    def _read(self, path: PathLike) -> TOMLDocument:
        return TOMLFile(path).read()

    def _validate(self, content: TOMLDocument) -> None:
        _content = deepcopy(content)
        for k, v in _content.items():
            if k in self.SpecialTopLevelKeys:
                continue
            if not isinstance(v, dict):
                raise ConfigFileError(f"Value of '{k}' should be table, got {type(v)}.")
            _ = [v.pop(_k, None) for _k in self.SpecialInTableKeys]
            if len(v) > 0:
                raise ConfigFileError(f"{v.keys()} is not supported.")

    @classmethod
    def parse(cls, config_path: PathLike) -> Dict[Hashable, List[LaunchConfiguration]]:
        parsed = cls(config_path)._parse()
        return utils._groupby(parsed, "machine")

    def _resolve_path(self, path: PathLike, parent: Path) -> Path:
        return Path(path) if Path(path).is_absolute() else parent / path

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
            image = group.get("baseimg", "ubuntu:latest")
            command_template = group.get("command", "")
            targets = group.get("targets", [])

            _config = self._generate_config(image, command_template, targets)
            launch_config.extend(_config)
        return launch_config

    def _generate_config(
        self, image: str, command_template: str, targets: List[Substitution]
    ) -> List[LaunchConfiguration]:
        commands = _substitute_command(command_template, targets)
        machines = [t.get("__machine__", None) for t in targets]
        return [
            {"image": image, "cmd": cmd, "machine": machine}
            for cmd, machine in zip(commands, machines)
        ]


parse = ConfigFileParser.parse
