"""
Realtime Hairbrush SDK - A middleware and CLI for controlling the airbrush plotter.

This package provides a real-time interactive control system for the dual-airbrush plotter
machine, with support for both serial and HTTP connections to the Duet board.
"""

__version__ = "0.1.0"
__author__ = "Semantic GCode Team"

# Import main components for easier access
from realtime_hairbrush.config.manager import ConfigManager
from realtime_hairbrush.execution.engine import ExecutionEngine
# High-level airbrush operations are implemented in realtime_hairbrush/operations/high_level.py
