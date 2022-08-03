from pathlib import Path

try:
    version_path = Path(__file__).parent / "VERSION"
    version = version_path.read_text().strip()
    del version_path
except FileNotFoundError:
    version = "0.0.0"

__version__ = version
del version
del Path

# submods to include in *
from . import api
from . import beam
from . import tracing
from . import utils

# top level everything
from .api import *

__all__ = [
    # submods
    "api",
    "beam",
    "trace",
    "utils",
]
