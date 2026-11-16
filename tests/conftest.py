import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

__all__ = ["ROOT", "EXAMPLE_DIR"]

EXAMPLE_DIR =ROOT / "examples" / "sample-ppm-task-listing"
