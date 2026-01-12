#!/usr/bin/env python3
"""
Simple OSC sender - just sends messages without waiting for response
Use this to verify AbletonOSC receives messages
"""

from pythonosc import udp_client
import time

print("=" * 70)
print("Simple OSC Sender Test")
print("=" * 70)
print()

# Test different port combinations
port_configs = [
    {"name": "Standard", "send": 11000, "desc": "AbletonOSC default"},
    {"name": "Reversed", "send": 11001, "desc": "Some AbletonOSC versions"},
    {"name": "Legacy", "send": 9000, "desc": "Older versions"},
    {"name": "Alt", "send": 9001, "desc": "Alternative config"},
]

print("This test will send OSC messages to different ports.")
print("Watch Ableton Live for any response or activity.")
print()
print("IMPORTANT: Keep Ableton Live visible while running this test")
print("Look for: Track names changing, tempo jumping, or any reaction")
print()
input("Press Enter to start...")
print()

for config in port_configs:
    print(f"Testing {config['name']} config (port {config['send']}) - {config['desc']}")

    try:
        client = udp_client.SimpleUDPClient("127.0.0.1", config['send'])

        # Send a tempo change command (visible if it works!)
        print(f"  -> Sending tempo change to 150 BPM...")
        client.send_message("/live/song/set/tempo", [150.0])
        time.sleep(0.5)

        # Send it back to original
        print(f"  -> Sending tempo back to 120 BPM...")
        client.send_message("/live/song/set/tempo", [120.0])
        time.sleep(0.5)

        # Try renaming track 1 (if it exists)
        print(f"  -> Trying to rename track 0 to 'OSC_TEST'...")
        client.send_message("/live/track/set/name", [0, "OSC_TEST"])
        time.sleep(0.5)

        print()

    except Exception as e:
        print(f"  [ERROR] {e}")
        print()

print("=" * 70)
print("Did you see ANY changes in Ableton Live?")
print("=" * 70)
print()
print("If YES - note which port worked and let me know!")
print("If NO - AbletonOSC might not be running. Check:")
print("  1. Ableton Preferences -> Control Surface -> AbletonOSC selected")
print("  2. Ableton Live was restarted after installing AbletonOSC")
print("  3. Log.txt in %APPDATA%\\Ableton\\Live 12\\Preferences\\")
print()
