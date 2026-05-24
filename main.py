"""Compatibility wrapper for running the analyzer as ``python main.py``."""

from __future__ import annotations

import sys

from ran_kpi_analyzer.cli import main

if __name__ == "__main__":
    sys.exit(main())
