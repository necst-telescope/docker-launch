from cleo import Application

from docker_launch import __version__
from .check_command import CheckCommand

# from .launch_command import LaunchCommand


def main():
    app = Application("docker-launch", __version__)
    app.add(CheckCommand())
    # app.add(LaunchCommand())

    app.run()
