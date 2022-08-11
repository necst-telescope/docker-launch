from cleo import Application

from docker_launch import __version__
from .check_command import CheckCommand
from .up_command import UpCommand


def main():
    app = Application("docker-launch", __version__)
    app.add(CheckCommand())
    app.add(UpCommand())

    app.run()
