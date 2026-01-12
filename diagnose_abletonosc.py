#!/usr/bin/env python3
"""
Complete AbletonOSC Diagnostic Tool
Checks all common issues and provides specific fixes
"""

import os
import sys
from pathlib import Path
import socket

print("=" * 70)
print("AbletonOSC Diagnostic Tool")
print("=" * 70)
print()

issues_found = []
fixes_suggested = []

# Check 1: Is AbletonOSC installed?
print("[1/6] Checking if AbletonOSC is installed...")

user_profile = os.environ.get('USERPROFILE', '')
remote_scripts_path = Path(user_profile) / "Documents" / "Ableton" / "User Library" / "Remote Scripts"
abletonosc_path = remote_scripts_path / "AbletonOSC"

if not remote_scripts_path.exists():
    print(f"  [WARN] Remote Scripts folder not found:")
    print(f"         {remote_scripts_path}")
    issues_found.append("Remote Scripts folder doesn't exist")
    fixes_suggested.append("Create the folder manually or run Ableton Live once")
elif not abletonosc_path.exists():
    print(f"  [FAIL] AbletonOSC NOT installed")
    print(f"         Expected at: {abletonosc_path}")
    issues_found.append("AbletonOSC not installed")
    fixes_suggested.append(f"""
    Install AbletonOSC:
    1. Download from: https://github.com/ideoforms/AbletonOSC
    2. Extract the ZIP
    3. Copy the 'AbletonOSC' folder to:
       {remote_scripts_path}
    4. Restart Ableton Live
    """)
else:
    init_file = abletonosc_path / "__init__.py"
    if init_file.exists():
        print(f"  [OK] AbletonOSC found at: {abletonosc_path}")

        # Try to read port configuration
        try:
            with open(init_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Look for port definitions
            listen_port = None
            send_port = None

            for line in content.split('\n'):
                if 'OSC_LISTEN_PORT' in line or 'LISTEN_PORT' in line:
                    if '=' in line and not line.strip().startswith('#'):
                        try:
                            listen_port = int(line.split('=')[1].split('#')[0].strip())
                        except:
                            pass
                if 'OSC_SEND_PORT' in line or 'SEND_PORT' in line:
                    if '=' in line and not line.strip().startswith('#'):
                        try:
                            send_port = int(line.split('=')[1].split('#')[0].strip())
                        except:
                            pass

            if listen_port:
                print(f"       AbletonOSC listens on port: {listen_port}")
            if send_port:
                print(f"       AbletonOSC sends to port: {send_port}")

            if listen_port and listen_port != 11000:
                issues_found.append(f"AbletonOSC uses non-standard port {listen_port} (expected 11000)")
                fixes_suggested.append(f"""
                Update Mixrunner to use port {listen_port}:
                Edit ableton_controller.py, change:
                    port={listen_port}
                """)

        except Exception as e:
            print(f"  [WARN] Could not read port config: {e}")
    else:
        print(f"  [FAIL] AbletonOSC folder exists but __init__.py missing")
        issues_found.append("AbletonOSC installation incomplete")
        fixes_suggested.append("Reinstall AbletonOSC from GitHub")

print()

# Check 2: Check Ableton Log for AbletonOSC
print("[2/6] Checking Ableton Live log file...")

appdata = os.environ.get('APPDATA', '')
log_path = Path(appdata) / "Ableton" / "Live 12" / "Preferences" / "Log.txt"

if not log_path.exists():
    # Try Live 11
    log_path = Path(appdata) / "Ableton" / "Live 11" / "Preferences" / "Log.txt"

if log_path.exists():
    print(f"  [OK] Log file found: {log_path}")
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()

        if 'AbletonOSC' in log_content:
            print(f"  [OK] AbletonOSC mentioned in log file")

            # Look for specific messages
            for line in log_content.split('\n'):
                if 'AbletonOSC' in line:
                    print(f"       {line.strip()}")

            if 'error' in log_content.lower() and 'abletonosc' in log_content.lower():
                issues_found.append("AbletonOSC has errors in log file")
                fixes_suggested.append("Check the log file for specific error messages")
        else:
            print(f"  [WARN] AbletonOSC not mentioned in log")
            issues_found.append("AbletonOSC not loaded by Ableton")
            fixes_suggested.append("""
            Enable AbletonOSC:
            1. Open Ableton Live
            2. Preferences -> Link · Tempo · MIDI
            3. Control Surface -> Select 'AbletonOSC'
            4. Restart Ableton Live
            """)
    except Exception as e:
        print(f"  [WARN] Could not read log: {e}")
else:
    print(f"  [WARN] Log file not found at: {log_path}")
    print(f"        (Ableton may not have been run yet)")

print()

# Check 3: Are ports available?
print("[3/6] Checking if OSC ports are available...")

def check_port(port, name):
    """Check if a UDP port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True, "Available"
    except OSError as e:
        if e.errno == 10048:  # Windows: Port already in use
            return False, "Already in use (might be AbletonOSC!)"
        return False, str(e)

port_11000_avail, port_11000_msg = check_port(11000, "Send port")
port_11001_avail, port_11001_msg = check_port(11001, "Receive port")

print(f"  Port 11000 (send): {port_11000_msg}")
print(f"  Port 11001 (receive): {port_11001_msg}")

if not port_11000_avail:
    print(f"  [GOOD] Port 11000 in use - might be AbletonOSC listening!")
else:
    print(f"  [WARN] Port 11000 is free - AbletonOSC might not be running")

print()

# Check 4: Python version
print("[4/6] Checking Python version...")
python_version = sys.version
print(f"  Current Python: {python_version}")
if sys.version_info >= (3, 11):
    print(f"  [OK] Python 3.11+ detected")
else:
    print(f"  [WARN] Old Python version")

print()

# Check 5: Is python-osc installed?
print("[5/6] Checking if python-osc is installed...")
try:
    import pythonosc
    print(f"  [OK] python-osc is installed")
except ImportError:
    print(f"  [FAIL] python-osc NOT installed")
    issues_found.append("python-osc library missing")
    fixes_suggested.append("Run: pip install python-osc")

print()

# Check 6: Is Ableton Live running?
print("[6/6] Checking if Ableton Live is running...")

# Check for Ableton processes (Windows)
if sys.platform == 'win32':
    import subprocess
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        if 'Ableton' in result.stdout:
            print(f"  [OK] Ableton Live is running")
        else:
            print(f"  [WARN] Ableton Live not detected in running processes")
            issues_found.append("Ableton Live might not be running")
            fixes_suggested.append("Start Ableton Live before testing OSC connection")
    except:
        print(f"  [WARN] Could not check running processes")

print()
print("=" * 70)
print("DIAGNOSIS SUMMARY")
print("=" * 70)
print()

if not issues_found:
    print("[SUCCESS] No obvious issues found!")
    print()
    print("If OSC still doesn't work:")
    print("1. Make sure a project is open in Ableton (not just blank session)")
    print("2. Try restarting Ableton Live")
    print("3. Check Windows Firewall settings")
    print("4. Try running: python test_osc_simple.py")
else:
    print(f"Found {len(issues_found)} issue(s):")
    print()
    for i, issue in enumerate(issues_found, 1):
        print(f"{i}. {issue}")
    print()
    print("=" * 70)
    print("SUGGESTED FIXES")
    print("=" * 70)
    print()
    for i, fix in enumerate(fixes_suggested, 1):
        print(f"Fix #{i}:")
        print(fix)
        print()

print("=" * 70)
print("Next steps:")
print("  1. Apply the suggested fixes above")
print("  2. Restart Ableton Live completely")
print("  3. Run: python test_osc_simple.py")
print("=" * 70)
