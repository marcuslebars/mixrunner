# Installation Guide - Mixrunner

Complete installation instructions for macOS.

## System Requirements

### Required
- **Operating System**: macOS 10.15 (Catalina) or later
- **Logic Pro**: Version 10.8 or later
- **Python**: Version 3.11 or later
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 500MB for installation + space for your projects

### Optional
- **Xcode Command Line Tools**: For building native dependencies
- **Virtual Environment**: Recommended for isolation

## Installation Steps

### 1. Install Python 3.11+

Check if Python is installed:
```bash
python3 --version
```

If not installed or version is older than 3.11:

**Option A: Using Homebrew (Recommended)**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

**Option B: Download from Python.org**
- Visit https://www.python.org/downloads/
- Download Python 3.11 or later
- Run the installer

### 2. Install Xcode Command Line Tools

Required for some native dependencies:
```bash
xcode-select --install
```

Click "Install" in the popup dialog.

### 3. Download Mixrunner

**Option A: Clone from Git**
```bash
git clone https://github.com/yourusername/mixrunner.git
cd mixrunner
```

**Option B: Download ZIP**
- Download the ZIP file
- Extract to your preferred location
- Open Terminal and navigate to the folder:
```bash
cd /path/to/mixrunner
```

### 4. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

To deactivate later:
```bash
deactivate
```

### 5. Install Dependencies

```bash
# Make sure you're in the project directory
cd mixrunner

# Install all dependencies
pip install -r requirements.txt
```

This will install:
- Audio processing libraries (librosa, soundfile)
- Machine learning tools (scikit-learn, tensorflow)
- macOS integration (pyobjc)
- UI framework (tkinter - usually included with Python)
- Utilities (pyyaml, loguru, etc.)

**Note**: This may take 5-10 minutes depending on your connection.

### 6. Install the Package

```bash
# Install in development mode
python setup.py develop

# OR for regular installation
python setup.py install
```

### 7. Grant Automation Permissions

Mixrunner needs permission to control Logic Pro:

1. Open **System Preferences** → **Security & Privacy**
2. Click the **Privacy** tab
3. Select **Automation** from the left sidebar
4. When you first run the tool, macOS will prompt you to allow access
5. Check the box next to **Logic Pro**

### 8. Verify Installation

Test the installation:

```bash
# Test CLI
mix-readiness --help

# Test import
python -c "from src.mixrunner_engine import MixReadinessEngine; print('Success!')"
```

If you see "Success!" - you're ready to go!

### 9. Run the GUI

```bash
# Launch graphical interface
python run_gui.py

# OR if installed globally
mix-readiness-gui
```

## Troubleshooting Installation

### Problem: "command not found: python3"

**Solution**: Install Python 3.11+ (see Step 1 above)

### Problem: "No module named 'numpy'"

**Solution**: Dependencies not installed
```bash
pip install -r requirements.txt
```

### Problem: "Permission denied"

**Solution**: Use virtual environment or install with --user
```bash
pip install --user -r requirements.txt
```

### Problem: "ERROR: Could not build wheels for pyobjc"

**Solution**: Install Xcode Command Line Tools
```bash
xcode-select --install
```

### Problem: "librosa installation failed"

**Solution**: Install system audio libraries first
```bash
brew install libsndfile
pip install librosa
```

### Problem: "tkinter not found"

**Solution**: Reinstall Python with tkinter support
```bash
brew reinstall python-tk@3.11
```

### Problem: Dependencies conflict

**Solution**: Use a fresh virtual environment
```bash
# Remove old environment
rm -rf venv

# Create new one
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Updating

To update to the latest version:

```bash
cd mixrunner

# Pull latest changes (if using git)
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Reinstall
python setup.py develop
```

## Uninstalling

To remove Mixrunner:

```bash
# Uninstall package
pip uninstall mixrunner

# Remove directory
rm -rf /path/to/mixrunner

# Remove virtual environment
rm -rf venv
```

## Alternative Installation Methods

### Using pip (if published to PyPI)

```bash
pip install mixrunner
```

### Using conda

```bash
# Create conda environment
conda create -n mixready python=3.11
conda activate mixready

# Install dependencies
pip install -r requirements.txt
```

## Docker Installation (Advanced)

For isolated environment:

```bash
# Build Docker image
docker build -t mixrunner .

# Run container
docker run -it --rm \
  -v /path/to/projects:/projects \
  mixrunner
```

**Note**: Docker installation has limitations with Logic Pro integration.

## Verifying Audio Libraries

Test audio processing capabilities:

```bash
python -c "
import librosa
import soundfile as sf
import pyloudnorm as pyln
print('Audio libraries OK!')
"
```

## Performance Optimization

### For faster processing:

1. **Install optimized NumPy**:
```bash
pip uninstall numpy
pip install numpy --no-binary numpy
```

2. **Use TensorFlow Lite** (smaller footprint):
```bash
pip install tensorflow-lite
```

3. **Limit analysis duration** in config:
```yaml
performance:
  analysis_duration: 15.0  # Instead of 30.0
```

## Development Installation

For contributing or development:

```bash
# Clone repository
git clone https://github.com/yourusername/mixrunner.git
cd mixrunner

# Install dev dependencies
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .

# Install pre-commit hooks
pre-commit install
```

## Next Steps

After installation:

1. Read the [Quick Start Guide](QUICKSTART.md)
2. Review the [Usage Guide](USAGE_GUIDE.md)
3. Try the [examples](examples/basic_usage.py)
4. Configure [settings](config/settings.yaml)

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting-installation) section above
2. Review the [FAQ](USAGE_GUIDE.md#troubleshooting)
3. Open an issue on GitHub
4. Contact support@example.com

---

**Installation complete!** Ready to optimize your Logic Pro sessions. 🎵
