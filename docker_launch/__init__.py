try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

try:
    __version__ = version("docker-launch")
except:  # noqa: E722
    __version__ = "0.0.0"

# Aliases
from .launch import launch_containers  # noqa: F401
from .ssh import check_key_ssh  # noqa: F401
