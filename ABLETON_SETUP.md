# Ableton Live Setup Guide

This guide will help you set up Mixrunner with Ableton Live 12.

## Prerequisites

- Ableton Live 12 (Suite, Standard, or Intro)
- Python 3.11 or later
- Windows 10/11 or macOS 10.15+

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Install MIDI Remote Script (Optional but Recommended)

For full Ableton Live integration, you'll need a MIDI Remote Script that enables OSC communication.

### Option A: Using AbletonOSC

1. Download AbletonOSC from: https://github.com/ideoforms/AbletonOSC
2. Copy the `AbletonOSC` folder to your Ableton Remote Scripts directory:
   - **macOS**: `~/Music/Ableton/User Library/Remote Scripts/`
   - **Windows**: `%USERPROFILE%\Documents\Ableton\User Library\Remote Scripts\`

3. Restart Ableton Live
4. Go to Preferences → Link/Tempo/MIDI → Control Surface
5. Select "AbletonOSC" from the dropdown

### Option B: Using LiveOSC (Alternative)

1. Download LiveOSC from: https://github.com/ideoforms/LiveOSC
2. Follow the same installation steps as above

## Step 3: Configure Mixrunner

1. Set your API key in `config/api_keys.yaml`:
   ```yaml
   anthropic:
     api_key: "your-api-key-here"
   ```

2. (Optional) Adjust OSC settings if using a custom port:
   - Edit `src/ableton_interface/ableton_controller.py`
   - Change the default `port` parameter (default: 11000)

## Step 4: Launch Mixrunner

```bash
python run_gui.py
```

## Step 5: Connect to Ableton Live

1. Make sure Ableton Live is running
2. Click "⚡ Connect to Ableton Live" in Mixrunner
3. You should see a green connection indicator

## Troubleshooting

### Connection Issues

**Problem**: "Could not connect to Ableton Live"

**Solutions**:
- Verify Ableton Live is running
- Check that the MIDI Remote Script is installed correctly
- Ensure no firewall is blocking UDP port 11000
- Restart both Ableton Live and Mixrunner

### OSC Communication Not Working

**Problem**: Commands not reaching Ableton Live

**Solutions**:
- Verify the MIDI Remote Script is selected in Ableton Preferences
- Check that OSC is enabled in the Remote Script settings
- Try using a different port (edit both the Remote Script and Mixrunner)

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'ableton_interface'`

**Solution**: Make sure you're running from the project root directory

## Features Available

With Ableton Live connected, you can:

- ✅ Analyze your current session
- ✅ Get AI recommendations for EQ, compression, and effects
- ✅ Import and analyze individual tracks
- ✅ Organize tracks by type
- ✅ Normalize audio levels
- ✅ Apply color schemes
- ✅ Create return tracks (buses)
- ✅ Set track volumes and panning

## Alternative: Manual Control Mode

If you prefer not to use the MIDI Remote Script, Mixrunner can still:

- Import and analyze audio files
- Generate AI mixing recommendations
- Provide detailed reports

However, direct Ableton control features will be limited.

## Next Steps

- Read the [Usage Guide](USAGE_GUIDE.md) for detailed examples
- Check out [NEW_FEATURES.md](NEW_FEATURES.md) for LLM integration details
- Explore the example scripts in the `examples/` directory
