#!/usr/bin/env python3
"""
Clean up stuck OSC server ports
Run this if you get "port already in use" errors
"""

import socket
import sys

def test_port(port):
    """Test if a port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True, "Available"
    except OSError as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("OSC Port Cleanup Utility")
    print("=" * 70)
    print()

    ports_to_check = [11000, 11001, 9000, 9001]

    print("Checking ports...")
    for port in ports_to_check:
        available, msg = test_port(port)
        status = "[OK]" if available else "[IN USE]"
        print(f"  Port {port}: {status} - {msg}")

    print()
    print("If ports are in use:")
    print("1. Close any running Python scripts or GUI windows")
    print("2. Restart your terminal/command prompt")
    print("3. If issue persists, restart your computer")
    print()
    print("The application now uses SO_REUSEADDR to handle this automatically.")
    print("=" * 70)

if __name__ == '__main__':
    main()
