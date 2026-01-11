# Mixrunner - Logic Pro Session Optimizer

An intelligent AI-powered tool that automatically prepares Logic Pro sessions for mixing by cleaning, organizing, and technically normalizing tracks.

## Features

### 🧹 Automatic Session Cleanup
- Removes empty tracks and unused regions
- Consolidates duplicate plugins
- Cleans up unused automation
- Removes silent audio files
- Optimizes take folders

### 🎯 AI-Powered Track Organization
- Intelligent track categorization (drums, bass, vocals, etc.)
- Automatic color coding by instrument type
- Smart track ordering and grouping
- Bus/Aux creation and routing
- VCA/summing stack setup

### ⚙️ Technical Normalization
- Phase alignment detection and correction
- Gain staging optimization
- Peak normalization with headroom preservation
- Stereo width analysis and correction
- Latency compensation verification

### 🎨 Mix Template Application
- Auto-creates organized track stacks
- Sets up send/return effects
- Applies naming conventions
- Configures output routing
- Generates session notes

## Project Structure

```
mixrunner/
├── src/
│   ├── logic-interface/     # Logic Pro scripting and API
│   ├── ai-engine/           # ML models for track classification
│   ├── analyzers/           # Audio analysis algorithms
│   ├── processors/          # Session modification engines
│   ├── ui/                  # User interface components
│   └── utils/               # Helper functions
├── models/                  # Pre-trained AI models
├── presets/                 # Mix templates and configurations
├── scripts/                 # Logic Pro scripts
└── tests/                   # Test suite
```

## Technology Stack

- **Core**: Python 3.11+
- **Audio Analysis**: librosa, essentia, pyloudnorm
- **AI/ML**: TensorFlow/PyTorch for track classification
- **Logic Pro Interface**: AppleScript/JXA, MIDI scripting
- **UI**: Tkinter/PyQt for control panel
- **Config**: YAML for settings and presets

## Installation

```bash
pip install -r requirements.txt
python setup.py install
```

## Quick Start

```python
from mixrunner import MixReadinessEngine

# Initialize the engine
engine = MixReadinessEngine()

# Analyze and prepare session
engine.analyze_session("/path/to/project.logicx")
report = engine.generate_report()

# Apply optimizations
engine.apply_cleanup()
engine.organize_tracks()
engine.normalize_technical()

# Export results
engine.export_session()
```

## Configuration

Edit `config/settings.yaml` to customize:
- Track organization rules
- Color schemes
- Naming conventions
- Headroom targets
- Bus templates

## Supported Logic Pro Versions

- Logic Pro 10.8+
- Logic Pro 11.x

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.
