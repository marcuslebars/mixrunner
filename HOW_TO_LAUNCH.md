# 🚀 How to Launch Mixrunner

Quick guide to get Mixrunner running on your system.

## ✅ Prerequisites Check

Before launching, make sure you have:
1. ✅ Logic Pro installed and working
2. ✅ Python 3.11+ installed
3. ✅ Dependencies installed

## 📦 One-Time Setup (First Time Only)

Open Terminal and run:

```bash
# Navigate to the Mixrunner folder
cd "/c/Users/marcu/Desktop/chance studio"

# Install dependencies
pip install -r requirements.txt
```

**This only needs to be done once!**

## 🎯 Launching Mixrunner

### Method 1: GUI (Recommended - Easiest!)

```bash
# Make sure you're in the project folder
cd "/c/Users/marcu/Desktop/chance studio"

# Launch the GUI
python run_gui.py
```

**Then:**
1. Open Logic Pro with your project
2. Click "Connect to Logic Pro" button
3. Click "Full Workflow" button
4. Done! ✅

### Method 2: Command Line

```bash
cd "/c/Users/marcu/Desktop/chance studio"
python run_cli.py
```

This will automatically run the full optimization workflow.

### Method 3: Python API (Advanced)

```bash
cd "/c/Users/marcu/Desktop/chance studio"
python
```

Then in Python:
```python
from src.mixrunner_engine import MixrunnerEngine

engine = MixrunnerEngine()
engine.connect_to_logic()
engine.run_full_workflow()
```

## 🎨 What Happens When You Run It

1. **Analyzes** your Logic Pro session
2. **Classifies** all tracks (drums, bass, vocals, etc.)
3. **Removes** empty tracks
4. **Organizes** tracks in logical order
5. **Colors** tracks by instrument type
6. **Renames** tracks with consistent naming
7. **Normalizes** audio levels
8. **Checks** for phase and technical issues
9. **Saves** your optimized session

Total time: **2-5 minutes** ⚡

## ⚠️ Important Notes

### Before Running:
- ✅ **Open Logic Pro** with your project loaded
- ✅ **Save your project** first (just in case)
- ✅ **Close any modal dialogs** in Logic Pro

### First Time Running:
- macOS will ask for **Automation permissions**
- Click **OK** to allow Mixrunner to control Logic Pro
- This only happens once

## 🐛 Troubleshooting

### "Can't find python"
```bash
# Try python3 instead
python3 run_gui.py
```

### "Can't connect to Logic Pro"
- Make sure Logic Pro is actually running
- Open a project in Logic Pro
- Try quitting and reopening Logic Pro

### "Module not found"
```bash
# Re-run the setup
pip install -r requirements.txt
```

### "Permission denied"
```bash
# Make the scripts executable
chmod +x run_gui.py run_cli.py
```

## 📝 Example Session

```bash
# 1. Navigate to folder
cd "/c/Users/marcu/Desktop/chance studio"

# 2. Launch GUI
python run_gui.py

# 3. In the GUI that opens:
#    - Click "Connect to Logic Pro"
#    - Click "Full Workflow"
#    - Watch the magic happen!
```

## 🎯 Quick Tips

- **Use the GUI** if you're new - it's the easiest
- **Read the log output** - it shows exactly what's happening
- **Check the report** - it tells you what changes were made
- **Start with a copy** of your project if you're nervous

## 📚 Next Steps

Once you're comfortable launching:
- Read [USAGE_GUIDE.md](USAGE_GUIDE.md) for all features
- Check [examples/basic_usage.py](examples/basic_usage.py) for code examples
- Customize [config/settings.yaml](config/settings.yaml) for your workflow

---

**Ready to optimize your Logic Pro sessions!** 🎚️✨
