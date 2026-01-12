# 🎚️ Mixrunner - AI-Powered Mixing Assistant

Professional mixing engineer powered by Claude, GPT, or Gemini AI for Ableton Live 12.

## 🤖 LLM-Powered Mixing

- **Claude/GPT/Gemini**: AI analyzes tracks and provides expert mixing advice
- **Smart Recommendations**: EQ, compression, panning, effects
- **Complete Workflows**: Step-by-step mixing plans

## ✨ Key Features

### Import & Analyze
- Import individual tracks with AI analysis
- Scan current Ableton Live workspace
- Get instant mixing recommendations

### AI Mixing Tasks
- **EQ**: Frequency analysis and precise adjustments
- **Dynamics**: Compression/limiting recommendations
- **Panning**: Optimal stereo placement
- **Effects**: Reverb/delay suggestions
- **Automation**: AI-generated parameter curves
- **Bus Processing**: Automatic routing and grouping

## 🚀 Quick Start

```bash
# Install
pip install -r requirements.txt

# Set API key (choose one)
export ANTHROPIC_API_KEY="your-key"  # Claude
export OPENAI_API_KEY="your-key"     # GPT-4
export GOOGLE_API_KEY="your-key"     # Gemini

# Launch
python run_gui.py
```

## 💡 Usage

```python
from src.mixing_features import TrackImporter
from src.llm_integration import MixingAgent, LLMProvider

# Import and analyze track
importer = TrackImporter(use_ai=True, llm_provider=LLMProvider.CLAUDE)
result = importer.import_track("vocal.wav", analyze=True)

# Get AI recommendations
print(result['ai_analysis']['ai_recommendations'])

# Scan Ableton Live workspace
workspace = importer.get_current_workspace_info()
print(f"Connected to {workspace['track_count']} tracks")
```

## 📚 Documentation

- [Installation Guide](INSTALLATION.md)
- [Usage Guide](USAGE_GUIDE.md)
- [Project Overview](PROJECT_OVERVIEW.md)

## 🔑 Get API Keys

- **Claude**: https://console.anthropic.com/
- **GPT-4**: https://platform.openai.com/api-keys
- **Gemini**: https://makersuite.google.com/app/apikey

## ⚙️ Requirements

- Windows 10/11 or macOS 10.15+
- Python 3.11+
- Ableton Live 12
- LLM API key
- MIDI Remote Script (for OSC communication)

## 📝 License

MIT License
