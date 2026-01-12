# Troubleshooting OSC Connection

## Current Situation

You're seeing:
```
[OK] Connection established
[DEBUG] No response for /live/song/get/num_tracks
Track count: 0
```

This means:
- ✅ OSC client and server are running
- ✅ No errors sending messages
- ❌ **AbletonOSC is not responding**

## Root Cause Analysis

The OSC server is starting successfully, but AbletonOSC isn't sending responses back. This happens when:

### 1. AbletonOSC Isn't Running (Most Likely)

**Check:**
- Open Ableton Live
- Go to Preferences (Ctrl+,)
- Click "Link · Tempo · MIDI"
- Look at Control Surface dropdowns

**What you should see:**
- "AbletonOSC" should appear in the dropdown list
- One of the dropdowns should have "AbletonOSC" selected

**If AbletonOSC is NOT in the list:**
- It's not installed correctly
- Check: `%USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\AbletonOSC\`
- Should contain: `__init__.py` and other Python files

**If AbletonOSC is in the list but not selected:**
- Select it in an empty Control Surface slot
- **RESTART Ableton Live completely** (important!)

### 2. Wrong Port Numbers

**Default ports for AbletonOSC:**
- Receives from you: **11000**
- Sends to you: **11001**

But some versions use:
- Port 9000/9001 instead
- Or the ports are reversed

**To find the correct ports:**

1. Navigate to:
   ```
   %USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\AbletonOSC\
   ```

2. Open `__init__.py` in a text editor

3. Look for lines like:
   ```python
   OSC_LISTEN_PORT = 11000
   OSC_SEND_PORT = 11001
   ```

4. These are the actual port numbers being used

### 3. AbletonOSC Not Loaded

**Check Ableton's log file:**

1. Open: `%APPDATA%\Ableton\Live 12\Preferences\Log.txt`

2. Search for "AbletonOSC" or "OSC"

3. You should see:
   ```
   RemoteScriptLoader: Loading AbletonOSC
   AbletonOSC: Initialized on port 11000
   ```

4. If you see errors like:
   ```
   RemoteScriptLoader: Error loading AbletonOSC
   ```
   Then the Remote Script has a problem

### 4. Firewall Blocking UDP

Windows Firewall might be blocking UDP ports 11000-11001.

**Solution:**
1. Open Windows Defender Firewall
2. "Allow an app through firewall"
3. Allow Python and Ableton Live through both Private and Public networks

## Quick Diagnostic Tests

### Test 1: Simple Sender (Visual Confirmation)

Run this test while watching Ableton:
```bash
python test_osc_simple.py
```

This will try to:
- Change tempo to 150 BPM (you'll see it if it works!)
- Change it back to 120 BPM
- Rename a track to "OSC_TEST"

**If you see ANY changes in Ableton:**
- OSC is working! Note which port number worked.

**If you see NO changes:**
- AbletonOSC isn't receiving messages

### Test 2: Check What's Using Ports

In Command Prompt:
```cmd
netstat -an | findstr "11000"
netstat -an | findstr "11001"
```

You should see:
```
UDP    127.0.0.1:11001        *:*
```

This means our receiver is running.

If you see Ableton listening on 11000:
```
UDP    127.0.0.1:11000        *:*
```

That's good - it means AbletonOSC is listening!

## Most Common Fix

**90% of the time, this is the issue:**

1. AbletonOSC is installed
2. But it's NOT selected in Preferences
3. Or Ableton wasn't restarted after installation

**Solution:**
1. Close Ableton Live completely
2. Open Ableton Live
3. Preferences → Link · Tempo · MIDI
4. Find empty Control Surface dropdown
5. Select "AbletonOSC"
6. **RESTART Ableton Live again**
7. Try the test again

## Alternative: Try LiveOSC Instead

If AbletonOSC doesn't work, try LiveOSC:

1. Download: https://github.com/ideoforms/LiveOSC
2. Install same way as AbletonOSC
3. Select "LiveOSC" in Control Surface
4. Restart Ableton
5. Test again

## Still Not Working?

If none of this works, we need to:

1. **Verify the Remote Script loads:**
   - Check Log.txt for errors
   - Share any AbletonOSC-related error messages

2. **Try a known-working Remote Script:**
   - Install "Push" or another built-in script
   - If those work but AbletonOSC doesn't, there's an issue with AbletonOSC itself

3. **Check Python version compatibility:**
   - Ableton Live uses Python 2.7 internally
   - Some newer Remote Scripts might not be compatible

## Next Steps

1. **Run the simple test:**
   ```bash
   python test_osc_simple.py
   ```

2. **Watch Ableton Live for any visible changes**

3. **Report back:**
   - Did anything change in Ableton?
   - What does Log.txt say about AbletonOSC?
   - Is AbletonOSC in the Control Surface dropdown?
   - What port numbers are in AbletonOSC's `__init__.py`?
