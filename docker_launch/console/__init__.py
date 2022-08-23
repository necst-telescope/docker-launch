"""docker-launch command-line tool.

Building a command-line tool using cleo (https://cleo.readthedocs.io/en/latest/).
This file constructs the "application" which defines `docker-launch` command. Individual
sub-"commands" are implemented in submodules.

The `main` function below, an application runner, is referenced from entrypoint
definition `[tool.poetry.scripts]` in "pyproject.toml".

"""

from cleo import Application

from docker_launch import __version__
from .check_command import CheckCommand
from .up_command import UpCommand


def main():
    app = Application("docker-launch", __version__)
    app.add(CheckCommand())
    app.add(UpCommand())

    app.run()
