"""fubon-cli: CLI tool for Fubon Neo trading API."""

try:
    from fubon_cli._version import __version__
except ImportError:
    __version__ = "0.1.0"

__author__ = "Mofesto.Cui"
__email__ = "mofesto.cui@gmail.com"
__license__ = "MIT"

__all__ = ["__version__", "__author__", "__email__", "__license__"]
