# 🔧 Quick Fix for Import Error

## The Problem

The class name in `mixrunner_engine.py` is still `MixReadinessEngine` but the imports are looking for `MixrunnerEngine`.

---

## ✅ **Quick Fix (2 minutes)**

Run these commands on the Mac:

```bash
cd /Users/m1/Documents/mixrunner

# Fix the class name in the main engine file
sed -i '' 's/class MixReadinessEngine/class MixrunnerEngine/g' src/mixrunner_engine.py

# Verify it worked
grep "class Mixrunner" src/mixrunner_engine.py
# Should show: class MixrunnerEngine:
```

Then try running again:
```bash
python3 run_gui.py
```

---

## 🔄 **Alternative: Re-download from Windows**

If the above doesn't work, the files may not have transferred completely.

### **On Windows:**

1. **Commit the new fix files:**
   ```bash
   cd "/c/Users/marcu/Desktop/chance studio"
   git add -A
   git commit -m "Fix import errors for macOS"
   git push
   ```

2. **Push to GitHub** (if you haven't already):
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/mixrunner.git
   git push -u origin main
   ```

### **On Mac:**

```bash
cd /Users/m1/Documents
rm -rf mixrunner  # Remove incomplete version
git clone https://github.com/YOUR_USERNAME/mixrunner.git
cd mixrunner
pip3 install -r requirements.txt
pip3 install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-ScriptingBridge
python3 run_gui.py
```

---

## 📝 **Manual Fix (if sed doesn't work)**

Edit the file manually:

```bash
cd /Users/m1/Documents/mixrunner
nano src/mixrunner_engine.py
```

Find the line (around line 17):
```python
class MixReadinessEngine:
```

Change it to:
```python
class MixrunnerEngine:
```

Save (Ctrl+O, Enter, Ctrl+X) and run:
```bash
python3 run_gui.py
```

---

## ✨ **Should Work Now!**

After the fix, you should see:
```
======================================================================
Mixrunner - Logic Pro Session Optimizer
======================================================================

Starting GUI...
```

And the GUI window opens! 🎉
