# Mixrunner - Project Overview

Complete technical overview of the Mixrunner system for Logic Pro.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
│  ┌──────────────┐              ┌─────────────────────┐      │
│  │  GUI (Tkinter)│              │  CLI / Python API   │      │
│  └───────┬──────┘              └──────────┬──────────┘      │
│          │                                 │                 │
│          └─────────────┬───────────────────┘                 │
└────────────────────────┼─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│              Mix Readiness Engine (Core)                     │
│  • Session orchestration                                     │
│  • Workflow management                                       │
│  • Configuration handling                                    │
└────────┬─────────┬──────────┬───────────┬────────────────────┘
         │         │          │           │
    ┌────▼───┐ ┌──▼────┐ ┌───▼─────┐ ┌──▼────────┐
    │ Logic  │ │  AI   │ │Analyzers│ │Processors │
    │Interface│ │Engine │ │         │ │           │
    └────┬───┘ └───┬───┘ └────┬────┘ └─────┬─────┘
         │         │          │            │
         ▼         ▼          ▼            ▼
    ┌────────────────────────────────────────────┐
    │         Logic Pro (via AppleScript)        │
    └────────────────────────────────────────────┘
```

## Core Components

### 1. Logic Interface Layer (`src/logic_interface/`)

**Purpose**: Communication with Logic Pro via AppleScript

**Components**:
- **LogicController**: Main interface for Logic Pro commands
  - Track manipulation (create, delete, move, rename)
  - Property modification (color, mute, solo)
  - Project management (save, export)

- **SessionReader**: Reads Logic Pro session data
  - Parses .logicx package format
  - Extracts track information
  - Analyzes audio files
  - Detects unused files

- **TrackManager**: High-level track operations
  - Track organization and reordering
  - Color scheme application
  - Naming conventions
  - Bus/aux creation

**Key Technologies**:
- AppleScript via subprocess
- macOS ScriptingBridge (PyObjC)
- File system analysis

### 2. AI Engine (`src/ai_engine/`)

**Purpose**: Intelligent track classification using ML and heuristics

**Components**:
- **TrackClassifier**: Multi-method classification
  - Name-based classification (keyword matching)
  - Audio-based classification (ML features)
  - Hybrid classification (combined approach)
  - Batch processing

- **AudioFeatureExtractor**: Feature extraction for ML
  - MFCC (Mel-frequency cepstral coefficients)
  - Spectral features (centroid, rolloff, bandwidth)
  - Temporal features (ZCR, RMS)
  - Rhythm features (tempo, beat strength)
  - Harmonic features (chroma)

**Classification Categories**:
- Drums (kick, snare, hi-hat, etc.)
- Bass (electric, synth, 808)
- Guitars (electric, acoustic)
- Keys (piano, synth, organ, pads)
- Vocals (lead, background, harmonies)
- Strings, Brass, Woodwinds
- FX and Ambience

**Algorithms**:
- Random Forest Classifier (sklearn)
- Feature normalization (StandardScaler)
- Confidence scoring
- Fallback to rule-based classification

### 3. Analyzers (`src/analyzers/`)

**Purpose**: Technical audio analysis

**Components**:

#### PhaseAnalyzer
- Stereo phase correlation analysis
- Frequency-dependent phase detection
- Mono compatibility checking
- Issue detection and correction suggestions

**Methods**:
- Cross-correlation analysis
- Bandpass filtering (6 frequency bands)
- Phase coherence measurement

#### GainAnalyzer
- Peak level measurement (dBFS)
- RMS level analysis
- Integrated loudness (LUFS) using ITU-R BS.1770
- Crest factor calculation
- Dynamic range estimation
- Clipping detection
- Headroom analysis

**Technologies**:
- pyloudnorm (LUFS measurement)
- soundfile (audio I/O)
- NumPy (DSP)

#### FrequencyAnalyzer
- Spectral analysis via FFT/STFT
- Frequency band energy measurement
- Spectral centroid and rolloff
- Brightness calculation
- Low-end balance analysis
- Issue detection (muddiness, harshness, etc.)
- EQ suggestions

**Frequency Bands**:
- Sub-bass: 20-60 Hz
- Bass: 60-250 Hz
- Low-mids: 250-500 Hz
- Mids: 500-2000 Hz
- High-mids: 2000-6000 Hz
- Presence: 6000-12000 Hz
- Brilliance: 12000-20000 Hz

### 4. Processors (`src/processors/`)

**Purpose**: Apply corrections and optimizations

**Components**:

#### SessionCleaner
- Empty track removal
- Muted track cleanup (optional)
- Unused file detection
- Duplicate file analysis
- Take folder consolidation
- Automation cleanup

#### AudioNormalizer
- Peak normalization
- LUFS-based loudness normalization
- RMS normalization
- Batch level matching
- Safety limiting (anti-clip)
- Automatic backup creation

**Normalization Methods**:
1. **Peak**: Normalize to target peak level
2. **Loudness**: Normalize to target LUFS
3. **RMS**: Normalize to target RMS
4. **Batch Matching**: Match all files to median level

### 5. Mix Readiness Engine (`src/mixrunner_engine.py`)

**Purpose**: Main orchestrator that coordinates all components

**Workflow**:
```
1. Connect to Logic Pro
   ↓
2. Analyze Session
   • Read project data
   • Classify tracks
   • Analyze audio files
   • Detect issues
   ↓
3. Generate Report
   • Track breakdown
   • Issues found
   • Recommendations
   ↓
4. Apply Cleanup
   • Remove empty tracks
   • Find unused files
   ↓
5. Organize Tracks
   • Reorder by type
   • Apply colors
   • Rename tracks
   • Create buses
   ↓
6. Technical Normalization
   • Gain staging
   • Phase correction
   • Level matching
   ↓
7. Export/Save
   • Save Logic project
   • Generate final report
```

**Configuration Options**:
- Target levels (LUFS, peak)
- Organization preferences
- Cleanup options
- Normalization settings
- Color schemes
- Naming templates

### 6. User Interface (`src/ui/`)

**Purpose**: Graphical control panel

**Features**:
- Connection status monitoring
- Configuration panel
- Action buttons (individual + full workflow)
- Real-time output log
- Status bar
- Threading for non-blocking operations

**Built with**:
- Tkinter (Python's standard GUI library)
- ttk (themed widgets)
- Threading (async operations)

## Data Flow

### Analysis Phase
```
Logic Pro Project
    ↓
SessionReader reads .logicx
    ↓
Extract track info + audio files
    ↓
TrackClassifier analyzes tracks
    ↓
Analyzers process audio files
    ↓
Aggregate results
    ↓
Generate report
```

### Processing Phase
```
Analysis Results
    ↓
SessionCleaner removes unused items
    ↓
TrackManager organizes tracks
    ↓
AudioNormalizer processes audio
    ↓
LogicController applies changes
    ↓
Save project
```

## File Structure

```
mixrunner/
├── src/
│   ├── logic_interface/          # Logic Pro communication
│   │   ├── logic_controller.py   # AppleScript interface
│   │   ├── session_reader.py     # Session parsing
│   │   └── track_manager.py      # Track operations
│   │
│   ├── ai_engine/                 # ML classification
│   │   ├── track_classifier.py   # Track classification
│   │   └── audio_feature_extractor.py  # Feature extraction
│   │
│   ├── analyzers/                 # Audio analysis
│   │   ├── phase_analyzer.py     # Phase analysis
│   │   ├── gain_analyzer.py      # Level analysis
│   │   └── frequency_analyzer.py # Spectral analysis
│   │
│   ├── processors/                # Audio processing
│   │   ├── session_cleaner.py    # Cleanup operations
│   │   └── audio_normalizer.py   # Normalization
│   │
│   ├── ui/                        # User interface
│   │   └── control_panel.py      # GUI application
│   │
│   └── mixrunner_engine.py   # Main engine
│
├── config/
│   └── settings.yaml              # Configuration
│
├── models/                        # ML models (optional)
│
├── presets/                       # User presets
│
├── examples/
│   └── basic_usage.py            # Usage examples
│
├── tests/                         # Test suite
│
├── run_gui.py                     # GUI launcher
├── run_cli.py                     # CLI launcher
├── setup.py                       # Installation
├── requirements.txt               # Dependencies
├── README.md                      # Project overview
├── QUICKSTART.md                  # Quick start
├── USAGE_GUIDE.md                 # Detailed guide
└── PROJECT_OVERVIEW.md            # This file
```

## Technologies & Dependencies

### Core Libraries
- **NumPy**: Numerical computing and DSP
- **SciPy**: Signal processing (filtering, etc.)
- **librosa**: Audio analysis and feature extraction
- **soundfile**: Audio file I/O
- **pyloudnorm**: LUFS loudness measurement

### Machine Learning
- **scikit-learn**: ML algorithms (Random Forest)
- **TensorFlow/PyTorch**: Optional deep learning
- **pandas**: Data manipulation

### macOS Integration
- **PyObjC**: macOS Objective-C bridge
- **subprocess**: AppleScript execution

### UI
- **Tkinter**: GUI framework
- **ttk**: Themed widgets

### Utilities
- **PyYAML**: Configuration files
- **loguru**: Logging
- **click**: CLI framework
- **tqdm**: Progress bars
- **colorama**: Terminal colors

## Performance Considerations

### Optimization Strategies
1. **Lazy Loading**: Only analyze files when needed
2. **Batch Processing**: Process multiple files together
3. **Threading**: Non-blocking UI operations
4. **Caching**: Cache analysis results
5. **Downsampling**: Analyze at lower sample rates
6. **Time Limiting**: Analyze only first N seconds

### Typical Performance
- Track classification: ~0.1s per track (name-based)
- Audio analysis: ~2-5s per file (30s audio)
- Session analysis: ~30s (50 tracks, 100 files)
- Full workflow: ~2-5 minutes (typical session)

## Extensibility

### Adding New Track Categories
```python
# In track_classifier.py
TRACK_CATEGORIES.append('new_category')

# In settings.yaml
colors:
  new_category: 15  # Logic Pro color index

naming:
  templates:
    new_category: "NEW"
```

### Adding Custom Analyzers
```python
from src.analyzers.base_analyzer import BaseAnalyzer

class CustomAnalyzer(BaseAnalyzer):
    def analyze_file(self, audio_path):
        # Your analysis code
        return results
```

### Custom Presets
Create YAML files in `presets/` directory with custom configurations.

## Future Enhancements

### Planned Features
1. **Advanced ML Models**: Deep learning for better classification
2. **Plugin Analysis**: Detect and optimize plugin usage
3. **Routing Automation**: Automatic bus routing and sends
4. **Mastering Prep**: Preparation for mastering stage
5. **Batch Session Processing**: Process multiple projects
6. **Cloud Integration**: Cloud-based ML models
7. **Collaboration Features**: Share presets and templates
8. **Real-time Monitoring**: Live session monitoring

### API Improvements
1. **REST API**: Web service interface
2. **WebSocket**: Real-time updates
3. **Plugin Support**: VST/AU plugin integration
4. **MIDI Scripting**: Enhanced Logic Pro control

## Security & Privacy

### Data Handling
- All processing is local (no cloud uploads)
- No telemetry or tracking
- Session data never leaves your machine
- Backup files created for safety

### Permissions Required
- **Automation**: Control Logic Pro via AppleScript
- **File System**: Read/write audio files
- **No Network**: No internet connection needed

## Testing

### Test Coverage
```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction
3. **End-to-End Tests**: Full workflow testing
4. **Performance Tests**: Speed and efficiency

## Contributing

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black src/
isort src/

# Type checking
mypy src/
```

### Code Style
- PEP 8 compliance
- Type hints throughout
- Comprehensive docstrings
- Logging for debugging

## License

MIT License - Free for commercial and personal use

## Credits

Built with:
- librosa (Audio Analysis)
- scikit-learn (Machine Learning)
- ITU-R BS.1770 (Loudness Standards)
- Logic Pro (Apple Inc.)

---

For questions or support, see the main README.md
