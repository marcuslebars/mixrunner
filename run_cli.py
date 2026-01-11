#!/usr/bin/env python3
"""
Mixrunner - CLI Launcher
Quick launcher for command-line interface
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.mix_readiness_engine import MixrunnerEngine
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


def main():
    """Run CLI workflow"""
    print("=" * 70)
    print("Mixrunner - Logic Pro Session Optimizer")
    print("=" * 70)

    print("\nInitializing engine...")
    engine = MixrunnerEngine()

    print("\nMake sure Logic Pro is open with your project loaded.")
    input("Press Enter to continue...")

    try:
        # Run full workflow
        success = engine.run_full_workflow()

        if success:
            print("\n" + "=" * 70)
            print("SUCCESS! Your session is ready for mixing.")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("Workflow completed with errors. Check the output above.")
            print("=" * 70)

    except KeyboardInterrupt:
        print("\n\nWorkflow cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
