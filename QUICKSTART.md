# Quick Start Guide - Mixrunner

Get up and running in 5 minutes!

## Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. That's it! No additional setup needed.
```

## Usage

### Option 1: Graphical Interface (Easiest)

```bash
# Launch the GUI
python run_gui.py
```

**Then:**
1. Open Logic Pro with your project
2. Click "Connect to Logic Pro"
3. Click "Full Workflow"
4. Done! Your session is optimized.

### Option 2: Command Line

```bash
# Make sure Logic Pro is open with your project
python run_cli.py
```

That's it!

## What It Does

The tool automatically:

1. **Analyzes** your session and classifies all tracks
2. **Cleans up** by removing empty tracks and finding unused files
3. **Organizes** tracks in a logical mixing order
4. **Color codes** tracks by instrument type
5. **Renames** tracks with consistent naming
6. **Normalizes** audio levels for optimal gain staging
7. **Checks** for phase issues and technical problems

## Example Output

```
======================================================================
MIX READINESS ANALYSIS REPORT
======================================================================

Project: My Song
Sample Rate: 48000 Hz
Total Tracks: 24
Audio Files: 87

----------------------------------------------------------------------
TRACK CLASSIFICATION
----------------------------------------------------------------------
  Drums: 8
  Bass: 2
  Guitar: 4
  Vocals: 6
  Keys: 3

----------------------------------------------------------------------
ISSUES DETECTED
----------------------------------------------------------------------
  ⚠ Empty tracks: 3
  ⚠ Files with gain issues: 5
  ⚠ Files with phase issues: 2

======================================================================
```

## Configuration

Edit `config/settings.yaml` to customize:

```yaml
target_lufs: -18.0      # Loudness target
target_peak: -6.0       # Peak headroom
auto_organize: true     # Reorder tracks
auto_color: true        # Color-code tracks
normalize_audio: true   # Apply gain staging
```

## Common Issues

### "Can't connect to Logic Pro"
- Make sure Logic Pro is running
- Open a project in Logic Pro first
- Grant automation permissions in System Preferences

### "Module not found"
```bash
# Make sure you're in the project directory
cd mixrunner
pip install -r requirements.txt
```

## Next Steps

- Read the full [Usage Guide](USAGE_GUIDE.md) for detailed information
- See [examples/basic_usage.py](examples/basic_usage.py) for code examples
- Check [README.md](README.md) for complete documentation

## Support

Having issues? Check the [Troubleshooting](USAGE_GUIDE.md#troubleshooting) section in the Usage Guide.

---

**Ready to mix!** 🎚️🎵
