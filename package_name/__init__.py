try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

try:
    __version__ = version("package-name")
except:
    __version__ = "0.0.0"
