from pathlib import Path

try:
    version_path = Path(__file__).parent / "VERSION"
    version = version_path.read_text().strip()
except FileNotFoundError:
    version = "0.0.0"

__version__ = version
del version

from .profiling import *
from .utils import *

__all__ = [
    # submods
    "profiling",
    "utils",
]
