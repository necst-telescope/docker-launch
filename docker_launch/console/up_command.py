from cleo import Command

from ..launch import launch_containers


class UpCommand(Command):
    """
    Create and launch docker containers on multiple hosts

    up
        {config : Path to launch configuration file}
    """

    def handle(self) -> int:
        config_file_path = self.argument("config")
        launch_containers(config_file_path)
        return 0
