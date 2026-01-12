# AbletonOSC Configuration Check

## Default AbletonOSC Ports

According to the AbletonOSC documentation, the default configuration is:

- **Receive from client (your app)**: Port **11000**
- **Send to client (your app)**: Port **11001**

However, some versions use different defaults:
- Older versions: Port **9000** (receive) / **9001** (send)
- Some forks: Port **11001** (receive) / **11000** (send) - REVERSED!

## How to Check AbletonOSC Configuration

1. **Find the AbletonOSC folder:**
   ```
   %USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\AbletonOSC\
   ```

2. **Open `__init__.py`** and look for port configuration:
   ```python
   OSC_LISTEN_PORT = 11000  # Port AbletonOSC listens on
   OSC_SEND_PORT = 11001    # Port AbletonOSC sends to
   ```

3. **Check if there's a config file** like `config.py` or `settings.py`

## Current Issue

Your test shows:
- Mixrunner sends TO port 11000 ✓
- Mixrunner listens ON port 11001 ✓
- AbletonOSC is NOT responding

This means one of:
1. AbletonOSC isn't running/loaded in Ableton
2. AbletonOSC is using different ports
3. AbletonOSC requires a different message format

## Next Steps

Please check:

1. **Is AbletonOSC visible in Ableton's Control Surface dropdown?**
   - If NO: AbletonOSC isn't installed correctly
   - If YES but not selected: Select it and restart Ableton

2. **Check Ableton's Log.txt:**
   ```
   %APPDATA%\Ableton\Live 12\Preferences\Log.txt
   ```
   Look for lines containing "AbletonOSC" or "OSC" - they'll show if it loaded successfully

3. **Find the actual port numbers:**
   Open: `%USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\AbletonOSC\__init__.py`

   Look for lines like:
   ```python
   OSC_LISTEN_PORT = ?
   OSC_SEND_PORT = ?
   ```

Once you find the actual port numbers in the file, let me know and I'll update the code!
