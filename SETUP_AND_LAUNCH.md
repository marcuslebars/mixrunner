# 🚀 Setup and Launch Mixrunner

## ⚡ Quick Setup (Do This First!)

### Step 1: Install Dependencies (REQUIRED - First Time Only)

Open Terminal/Command Prompt and run:

```bash
cd "/c/Users/marcu/Desktop/chance studio"
pip install -r requirements.txt
```

**This will take ~5 minutes.** Wait for it to complete!

You'll see output like:
```
Collecting librosa...
Collecting numpy...
Installing collected packages: ...
Successfully installed ...
```

---

## 🎯 Launch Mixrunner

After dependencies are installed, you can launch:

### Option 1: Double-Click (Windows)
📁 Double-click: `LAUNCH_GUI.bat`

### Option 2: Terminal
```bash
cd "/c/Users/marcu/Desktop/chance studio"
python run_gui.py
```

---

## ✅ What You'll See

When it works correctly:
```
======================================================================
🎚️  Mixrunner - Logic Pro Session Optimizer
======================================================================

Starting GUI...
```

A window will open with the Mixrunner interface!

---

## ❌ Common Errors & Fixes

### Error: "ModuleNotFoundError: No module named 'loguru'"

**Fix:** Dependencies not installed. Run:
```bash
pip install -r requirements.txt
```

### Error: "python: command not found"

**Fix:** Try python3 instead:
```bash
python3 run_gui.py
```

Or install Python 3.11+ from [python.org](https://python.org)

### Error: "pip: command not found"

**Fix:** Install Python properly with pip included, or try:
```bash
python -m pip install -r requirements.txt
```

---

## 📋 Full Installation Checklist

- [ ] Python 3.11+ installed
- [ ] In the correct folder (`cd "/c/Users/marcu/Desktop/chance studio"`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Logic Pro is open with a project loaded
- [ ] Run: `python run_gui.py`

---

## 🎨 Using Mixrunner

Once the GUI opens:

1. **Click "Connect to Logic Pro"**
   - Status turns green ✅

2. **Click "Full Workflow"**
   - Sits back and watches! ☕

3. **Done!** Your session is optimized 🎉

---

## 🆘 Still Having Issues?

Read the detailed guides:
- [HOW_TO_LAUNCH.md](HOW_TO_LAUNCH.md)
- [INSTALLATION.md](INSTALLATION.md)
- [QUICKSTART.md](QUICKSTART.md)

---

**Ready? Install dependencies first, then launch!** 🚀
