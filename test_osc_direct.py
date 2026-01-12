#!/usr/bin/env python3
"""
Direct OSC test - sends raw OSC messages to debug AbletonOSC
"""

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import threading
import time

print("=" * 70)
print("Direct OSC Test for AbletonOSC")
print("=" * 70)
print()

# Global response tracker
responses = []

def handle_message(address, *args):
    """Handle any incoming OSC message"""
    print(f"  <- RECEIVED: {address} {args}")
    responses.append({'address': address, 'args': args})

# Set up receiver
print("[1] Setting up OSC receiver on port 11001...")
dispatcher = Dispatcher()
dispatcher.set_default_handler(handle_message)

server = ThreadingOSCUDPServer(("127.0.0.1", 11001), dispatcher)
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()
print("  [OK] Listening on 127.0.0.1:11001")
print()

# Set up sender
print("[2] Setting up OSC sender to port 11000...")
client = udp_client.SimpleUDPClient("127.0.0.1", 11000)
print("  [OK] Ready to send to 127.0.0.1:11000")
print()

print("[3] Sending test messages to AbletonOSC...")
print()

# Test 1: Basic ping
print("Test 1: Basic ping")
print("  -> SENDING: /live/test")
responses.clear()
client.send_message("/live/test", [])
time.sleep(0.5)
if responses:
    print(f"  [OK] Got response!")
else:
    print(f"  [FAIL] No response")
print()

# Test 2: Get tempo
print("Test 2: Get tempo")
print("  -> SENDING: /live/song/get/tempo")
responses.clear()
client.send_message("/live/song/get/tempo", [])
time.sleep(0.5)
if responses:
    print(f"  [OK] Tempo: {responses[0]}")
else:
    print(f"  [FAIL] No response")
print()

# Test 3: Get track count
print("Test 3: Get track count")
print("  -> SENDING: /live/song/get/num_tracks")
responses.clear()
client.send_message("/live/song/get/num_tracks", [])
time.sleep(0.5)
if responses:
    print(f"  [OK] Track count: {responses[0]}")
else:
    print(f"  [FAIL] No response")
print()

# Test 4: Alternative API paths (some OSC implementations use different paths)
alternative_paths = [
    "/live/tempo",
    "/live/song/tempo",
    "/tempo",
    "/song/get/tempo",
]

print("Test 4: Trying alternative API paths...")
for path in alternative_paths:
    print(f"  -> SENDING: {path}")
    responses.clear()
    client.send_message(path, [])
    time.sleep(0.3)
    if responses:
        print(f"    [OK] Got response: {responses[0]}")
        break
else:
    print(f"  [FAIL] No alternative paths worked")
print()

print("=" * 70)
print("Diagnosis:")
print("=" * 70)

if not any([responses]):
    print("""
AbletonOSC is NOT responding to any OSC messages.

Possible causes:
1. AbletonOSC is not installed or not enabled in Ableton preferences
2. AbletonOSC is using different port numbers
3. Ableton Live is not running
4. Firewall is blocking UDP communication

SOLUTIONS:

1. Verify AbletonOSC is installed:
   - Check: %USERPROFILE%\\Documents\\Ableton\\User Library\\Remote Scripts\\AbletonOSC\\
   - Should contain: __init__.py, _Framework folder, etc.

2. Enable in Ableton:
   - Preferences -> Link/Tempo/MIDI
   - Control Surface -> Select "AbletonOSC"
   - Restart Ableton Live

3. Check Ableton's Log file:
   - Location: %APPDATA%\\Ableton\\Live 12\\Preferences\\Log.txt
   - Look for AbletonOSC loading messages or errors

4. Try different ports (if AbletonOSC is configured differently):
   - Edit this script to use ports 9000/9001 instead of 11000/11001
""")
else:
    print("""
SUCCESS! AbletonOSC is responding.

The working API path is: [check output above]
""")

# Keep server alive for a moment
time.sleep(1)
server.shutdown()
