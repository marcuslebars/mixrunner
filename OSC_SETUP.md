# OSC Connection Setup for Ableton Live

This guide explains how to set up OSC communication between Mixrunner and Ableton Live using AbletonOSC.

## What is OSC?

OSC (Open Sound Control) is a protocol for communication between computers, synthesizers, and multimedia devices. It's the standard way to control Ableton Live remotely.

## Prerequisites

1. **Ableton Live 12** (any edition)
2. **Python 3.11+** with all requirements installed
3. **AbletonOSC** MIDI Remote Script

## Step 1: Install AbletonOSC

### Download AbletonOSC

1. Go to: https://github.com/ideoforms/AbletonOSC
2. Click the green "Code" button → Download ZIP
3. Extract the ZIP file

### Install the Remote Script

1. **Locate your Ableton Remote Scripts folder:**
   - **Windows**: `%USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\`
   - **macOS**: `~/Music/Ableton/User Library/Remote Scripts/`

2. **Copy the AbletonOSC folder:**
   - From the extracted ZIP, copy the `AbletonOSC` folder
   - Paste it into the Remote Scripts folder
   - The path should look like: `Remote Scripts\AbletonOSC\__init__.py`

3. **Restart Ableton Live** completely (quit and reopen)

## Step 2: Enable AbletonOSC in Ableton

1. Open Ableton Live
2. Go to **Preferences** (Ctrl+, or Cmd+,)
3. Click on **Link · Tempo · MIDI**
4. In the **Control Surface** section:
   - Find an empty dropdown
   - Select **AbletonOSC**
   - Leave Input and Output as "None"
5. Close Preferences

## Step 3: Verify Installation

### Check AbletonOSC is Active

In Ableton Live's Log.txt file, you should see messages from AbletonOSC when it loads.

**Log file location:**
- **Windows**: `%APPDATA%\Ableton\Live 12\Preferences\Log.txt`
- **macOS**: `~/Library/Preferences/Ableton/Live 12/Log.txt`

### Test OSC Connection

Run the test script:

```bash
cd "c:\Users\marcu\Desktop\chance studio"
python test_osc_connection.py
```

This will:
1. Connect to Ableton Live on port 11000
2. Listen for responses on port 11001
3. Query track count, tempo, and project info
4. Display track information

**Expected output:**
```
[OK] Connection established
Track count: 5
Tempo: 120.0 BPM
Project path: C:\Users\...\MyProject.als
Track 0: {'name': 'Audio 1', 'muted': False, ...}
```

## How OSC Communication Works

### Port Configuration

- **Send Port (11000)**: Mixrunner sends commands to Ableton
- **Receive Port (11001)**: Mixrunner receives responses from Ableton

### OSC Message Format

Mixrunner sends OSC messages like:
```
/live/song/get/tempo
/live/track/get/name [track_index]
/live/track/set/volume [track_index, volume_value]
```

AbletonOSC receives these messages and sends back responses.

## Troubleshooting

### Problem: "Could not connect to Ableton Live"

**Solutions:**
1. Verify Ableton Live is running
2. Check AbletonOSC is installed correctly:
   - Folder path: `Remote Scripts\AbletonOSC\__init__.py`
3. Confirm AbletonOSC is selected in Preferences → Link · Tempo · MIDI
4. Restart Ableton Live after installing AbletonOSC
5. Check Windows Firewall isn't blocking UDP ports 11000-11001

### Problem: "No response from Ableton"

**Solutions:**
1. Check AbletonOSC is enabled in Preferences
2. Look at Ableton's Log.txt for error messages
3. Try different port numbers (edit both Mixrunner and AbletonOSC config)
4. Restart both Ableton Live and Mixrunner

### Problem: "Track count: 0" but tracks exist

**Solutions:**
1. Make sure you have an actual project open (not just blank session)
2. AbletonOSC might be loading - wait a few seconds and retry
3. Check the OSC implementation matches AbletonOSC's API

### Problem: ImportError for python-osc

**Solution:**
```bash
pip install python-osc
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

## Alternative: Using LiveOSC

If AbletonOSC doesn't work, you can try LiveOSC instead:

1. Download from: https://github.com/ideoforms/LiveOSC
2. Install using the same process as AbletonOSC
3. Select "LiveOSC" in Ableton Preferences instead

Note: LiveOSC and AbletonOSC have similar but slightly different APIs.

## Firewall Configuration

If you have firewall issues:

### Windows Firewall
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Click "Change settings"
4. Click "Allow another app"
5. Browse to your Python executable
6. Allow both Private and Public networks

### Port Forwarding
OSC uses UDP (not TCP), so make sure UDP ports 11000-11001 are open.

## Advanced Configuration

### Custom Ports

To use different ports, edit both:

1. **Mixrunner** - in your code:
   ```python
   controller = AbletonController(
       port=12000,        # Send port
       receive_port=12001 # Receive port
   )
   ```

2. **AbletonOSC** - edit `AbletonOSC/__init__.py`:
   ```python
   OSC_LISTEN_PORT = 12000
   OSC_SEND_PORT = 12001
   ```

### Network Configuration

By default, OSC uses localhost (127.0.0.1). To control Ableton Live over a network:

1. Find the computer's IP address running Ableton
2. Update Mixrunner:
   ```python
   controller = AbletonController(host="192.168.1.100")
   ```
3. Configure firewall to allow remote connections

## Next Steps

Once OSC is working:

1. Run the main GUI: `python run_gui.py`
2. Click "Connect to Ableton Live"
3. Start analyzing and optimizing your sessions!

## Resources

- **AbletonOSC GitHub**: https://github.com/ideoforms/AbletonOSC
- **OSC Protocol Spec**: https://opensoundcontrol.stanford.edu/spec-1_0.html
- **Ableton Remote Scripts Documentation**: https://docs.cycling74.com/max8/vignettes/live_object_model

## Need Help?

If you're still having issues:

1. Check Ableton's Log.txt for error messages
2. Run `test_osc_connection.py` with DEBUG logging
3. Verify AbletonOSC is loaded in Log.txt
4. Try the simpler test: send `/live/test` message and check for response
