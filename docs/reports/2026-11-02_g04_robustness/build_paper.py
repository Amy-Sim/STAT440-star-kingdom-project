"""Build the canonical English PDF and editable Word report.

Compatibility entry point; use build_detailed.py directly for the same outputs.
"""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("build_detailed.py")), run_name="__main__")
