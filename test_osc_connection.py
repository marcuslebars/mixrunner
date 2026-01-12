#!/usr/bin/env python3
"""
Test OSC connection to Ableton Live with AbletonOSC
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ableton_interface import AbletonController
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="DEBUG"
)

def test_connection():
    """Test Ableton Live OSC connection"""
    print("=" * 70)
    print("Testing Ableton Live OSC Connection")
    print("=" * 70)
    print()

    print("IMPORTANT: Make sure:")
    print("1. Ableton Live is running")
    print("2. AbletonOSC is installed in Remote Scripts folder")
    print("3. AbletonOSC is selected in Preferences -> MIDI")
    print()
    input("Press Enter when ready...")
    print()

    # Initialize controller
    print("[1/5] Initializing OSC controller...")
    controller = AbletonController()

    # Connect
    print("[2/5] Connecting to Ableton Live...")
    if controller.connect():
        print("  [OK] Connection established")
    else:
        print("  [FAILED] Could not connect")
        return

    time.sleep(0.5)

    # Test basic commands
    print("[3/5] Testing basic commands...")

    # Get track count
    track_count = controller.get_track_count()
    print(f"  Track count: {track_count}")

    # Get tempo
    tempo = controller.get_tempo()
    print(f"  Tempo: {tempo} BPM")

    # Get project path
    project_path = controller.get_current_project_path()
    print(f"  Project path: {project_path}")

    # Test track info
    print("[4/5] Testing track info...")
    if track_count > 0:
        for i in range(min(3, track_count)):
            track_info = controller.get_track_info(i)
            print(f"  Track {i}: {track_info}")
    else:
        print("  No tracks found (create some tracks in Ableton Live)")

    # Disconnect
    print("[5/5] Disconnecting...")
    controller.disconnect()

    print()
    print("=" * 70)
    print("Test complete!")
    print("=" * 70)

if __name__ == '__main__':
    test_connection()
