#!/usr/bin/env python3
"""
Mixrunner - GUI Launcher
Quick launcher for the graphical interface
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.control_panel import MixreadyControlPanel
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


def main():
    """Launch the GUI"""
    print("=" * 70)
    print("Mixrunner - Ableton Live Session Optimizer")
    print("=" * 70)
    print("\nStarting GUI...")

    try:
        app = MixreadyControlPanel()
        app.run()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
