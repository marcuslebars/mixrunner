# Mixrunner - Usage Guide

Complete guide to using the Mixrunner tool for Logic Pro.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [GUI Usage](#gui-usage)
4. [Command Line Usage](#command-line-usage)
5. [Features](#features)
6. [Configuration](#configuration)
7. [Workflow Examples](#workflow-examples)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- macOS 10.15 or later
- Logic Pro 10.8 or later
- Python 3.11 or later
- Xcode Command Line Tools

### Install Steps

```bash
# Clone or download the repository
cd mixrunner

# Install dependencies
pip install -r requirements.txt

# Install the package
python setup.py install
```

### Verify Installation

```bash
# Test CLI
mix-readiness --help

# Launch GUI
mix-readiness-gui
```

---

## Quick Start

### Using the GUI (Recommended for Beginners)

1. **Open Logic Pro** with your project
2. **Launch the GUI**:
   ```bash
   mix-readiness-gui
   ```
3. **Click "Connect to Logic Pro"**
4. **Click "Full Workflow"** to run complete optimization
5. **Review the output log** for results

### Using the Command Line

```bash
# Make sure Logic Pro is open with your project
mix-readiness
```

---

## GUI Usage

### Main Window Sections

#### 1. Logic Pro Connection
- **Connect Button**: Establishes connection to Logic Pro
- **Status Indicator**: Shows connection status (green = connected)

#### 2. Configuration Panel
Options to customize the workflow:

- **Remove empty tracks**: Delete tracks with no audio/MIDI data
- **Auto-organize tracks**: Reorder tracks by instrument type
- **Apply color scheme**: Color-code tracks by category
- **Normalize audio levels**: Apply gain staging to audio files

**Level Targets:**
- **Target LUFS**: Integrated loudness target (default: -18.0)
- **Target Peak**: Peak level headroom (default: -6.0 dB)

#### 3. Action Buttons

**Individual Actions:**
- **Analyze Session**: Scan and classify tracks without making changes
- **Clean Up**: Remove empty tracks and find unused files
- **Organize Tracks**: Reorder and color-code tracks
- **Normalize Audio**: Apply gain staging to audio files

**Combined Actions:**
- **Full Workflow**: Run all steps automatically
- **Generate Report**: Show detailed analysis report

#### 4. Output Log
Real-time feedback showing:
- Progress updates
- Classification results
- Issues detected
- Actions performed

---

## Command Line Usage

### Basic Commands

```bash
# Run full workflow on current Logic Pro project
mix-readiness

# Use custom configuration
mix-readiness --config /path/to/config.yaml

# Analyze only (no changes)
mix-readiness --analyze-only
```

### Python API

```python
from src.mixrunner_engine import MixReadinessEngine

# Initialize
engine = MixReadinessEngine()

# Connect to Logic Pro
engine.connect_to_logic()

# Analyze session
results = engine.analyze_session()

# Generate report
print(engine.generate_report())

# Apply optimizations
engine.apply_cleanup()
engine.organize_tracks()
engine.normalize_technical()

# Save
engine.export_session()
```

---

## Features

### 1. AI-Powered Track Classification

The tool automatically identifies track types:

**Instrument Categories:**
- Drums (kick, snare, hi-hat, overheads, etc.)
- Bass (bass guitar, synth bass, 808, etc.)
- Guitars (electric, acoustic, rhythm, lead)
- Keys (piano, synth, organ, pads)
- Vocals (lead, background, harmonies)
- Strings, Brass, Woodwinds
- FX and Ambience

**Classification Methods:**
1. **Name-based**: Fast keyword matching (90%+ accuracy)
2. **Audio-based**: ML analysis of audio features (optional)
3. **Hybrid**: Combines both methods for best results

### 2. Session Cleanup

**Automatically Detects and Removes:**
- Empty audio tracks (no regions)
- Empty MIDI tracks (no notes)
- Unused audio files in project folder
- Duplicate or similar files

**Optional Cleanup:**
- Muted tracks (disabled by default for safety)
- Unused automation data
- Consolidated take folders

### 3. Track Organization

**Automatic Organization:**
- Reorders tracks by instrument type
- Groups similar instruments together
- Follows industry-standard mixing order

**Standard Order:**
1. Drums (kick → snare → hi-hats → cymbals → room mics)
2. Bass
3. Guitars
4. Keys/Synths
5. Strings/Orchestral
6. Vocals (lead → harmonies → backgrounds)
7. FX
8. Buses/Auxes

### 4. Color Coding

Automatically applies Logic Pro colors by instrument:

- **Red**: Drums (kick, snare)
- **Orange**: Percussion, toms
- **Purple**: Bass
- **Orange/Yellow**: Guitars
- **Yellow/Green**: Keys, synths
- **Green**: Strings, pads
- **Pink**: Vocals
- **Blue**: FX
- **Gray**: Buses/Auxes

### 5. Intelligent Renaming

**Naming Conventions:**
- Consistent prefixes (KICK, SNR, GTR, VOX, etc.)
- Automatic numbering (GTR 1, GTR 2, etc.)
- Preserves descriptive terms (Lead, Rhythm, Close, Room)

**Examples:**
- `audio 1` → `KICK`
- `Guitar_Track_01` → `GTR 1 - Rhythm`
- `vox lead take 3` → `LEAD VOX`

### 6. Technical Normalization

**Gain Staging:**
- Peak normalization with headroom
- LUFS-based loudness matching
- RMS energy optimization

**Phase Analysis (Stereo Files):**
- Detects phase cancellation
- Measures phase correlation
- Frequency-dependent phase analysis
- Suggests corrections

**Frequency Analysis:**
- Spectral balance assessment
- Detects problematic frequencies
- Suggests EQ corrections

**Issues Detected:**
- Clipping/distortion
- Insufficient headroom
- Phase problems
- Excessive sub-bass
- Muddy low-mids
- Harsh high frequencies

---

## Configuration

### Configuration File

Edit `config/settings.yaml` to customize:

```yaml
# Target levels
target_lufs: -18.0
target_peak: -6.0

# Organization
organization:
  auto_organize: true
  auto_color: true
  auto_rename: true

# Cleanup
cleanup:
  remove_empty_tracks: true
  remove_muted_tracks: false
  find_unused_files: true

# Normalization
normalization:
  enabled: true
  method: "loudness"  # or "peak"
  match_levels: true
  create_backup: true
```

### Custom Color Schemes

```yaml
colors:
  kick: 1      # Logic Pro color index
  snare: 1
  guitar: 9
  vocal: 18
  # ... etc
```

### Custom Naming Templates

```yaml
naming:
  templates:
    kick: "BD"        # Instead of "KICK"
    snare: "SD"       # Instead of "SNR"
    guitar: "GUITAR"  # Instead of "GTR"
```

---

## Workflow Examples

### Example 1: Basic Mix Prep

**Scenario**: You received a session and need to prepare it for mixing.

```python
from src.mixrunner_engine import MixReadinessEngine

engine = MixReadinessEngine()
engine.connect_to_logic()

# Full automatic workflow
engine.run_full_workflow()
```

**Result**:
- Empty tracks removed
- Tracks organized by type
- Color coding applied
- Levels normalized
- Ready to mix!

### Example 2: Analysis Only

**Scenario**: You want to understand the session before making changes.

```python
engine = MixReadinessEngine()
engine.connect_to_logic()

# Analyze without changes
engine.analyze_session()
print(engine.generate_report())
```

**Output**:
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
  Other: 1

----------------------------------------------------------------------
ISSUES DETECTED
----------------------------------------------------------------------
  ⚠ Empty tracks: 3
  ⚠ Files with gain issues: 5
  ⚠ Files with phase issues: 2
```

### Example 3: Custom Workflow

**Scenario**: You want fine control over each step.

```python
engine = MixReadinessEngine()
engine.connect_to_logic()

# Step 1: Analyze
engine.analyze_session()

# Step 2: Review and clean
engine.apply_cleanup()

# Step 3: Organize (but skip normalization)
engine.config['normalize_audio'] = False
engine.organize_tracks()

# Step 4: Save
engine.export_session()
```

### Example 4: Batch Audio Processing

**Scenario**: Normalize audio files before importing.

```python
from src.processors.audio_normalizer import AudioNormalizer
from pathlib import Path

normalizer = AudioNormalizer(target_lufs=-18.0, target_peak=-6.0)

# Get audio files
audio_files = list(Path('path/to/audio').glob('*.wav'))

# Normalize with level matching
normalizer.normalize_batch(audio_files, match_levels=True)
```

---

## Troubleshooting

### Connection Issues

**Problem**: Can't connect to Logic Pro

**Solutions**:
1. Ensure Logic Pro is running
2. Open a project in Logic Pro
3. Grant automation permissions in macOS System Preferences → Security & Privacy → Automation
4. Restart Logic Pro and try again

### Track Organization Not Working

**Problem**: Tracks aren't being organized

**Solutions**:
1. Check that `auto_organize` is enabled in config
2. Ensure tracks have names (unnamed tracks may not classify correctly)
3. Run analysis first to verify classifications
4. Check output log for errors

### Audio Normalization Issues

**Problem**: Audio files sound different or distorted

**Solutions**:
1. Check that backups were created (`.backup` files)
2. Restore from backup if needed
3. Adjust target LUFS/peak levels
4. Use `match_levels=False` for independent normalization

### Performance/Speed Issues

**Problem**: Analysis takes too long

**Solutions**:
1. Reduce `max_audio_files_analyze` in config
2. Reduce `analysis_duration` (default: 30 seconds)
3. Disable audio-based classification (use name-only)
4. Close other applications

### AppleScript Errors

**Problem**: AppleScript timeout or errors

**Solutions**:
1. Increase timeout in `logic_controller.py`
2. Reduce number of tracks processed at once
3. Simplify Logic Pro project (freeze tracks, bounce in place)
4. Update Logic Pro to latest version

---

## Advanced Usage

### Creating Custom Presets

Create preset files in `presets/` directory:

```yaml
# presets/rock-mix.yaml
name: "Rock Mix Template"

organization:
  track_order:
    - drums
    - bass
    - guitar
    - vocals

colors:
  drums: 1   # Red
  bass: 6    # Purple
  guitar: 9  # Orange
  vocal: 19  # Pink

naming:
  templates:
    drums: "DRUMS"
    bass: "BASS"
    guitar: "GTR"
```

Load preset:
```python
import yaml

with open('presets/rock-mix.yaml') as f:
    preset = yaml.safe_load(f)

engine = MixReadinessEngine(config=preset)
```

### Training Custom AI Models

For better track classification, train on your own sessions:

```python
from src.ai_engine.track_classifier import TrackClassifier
from sklearn.ensemble import RandomForestClassifier

# Prepare training data (features + labels)
# ... your training code ...

# Train model
classifier = RandomForestClassifier()
classifier.fit(X_train, y_train)

# Save model
track_classifier = TrackClassifier()
track_classifier.classifier = classifier
track_classifier.save_model(Path('models/my_model.pkl'))
```

---

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/yourusername/mixrunner/issues
- Documentation: https://mixrunner.readthedocs.io
- Email: support@example.com

---

## License

MIT License - see LICENSE file for details
