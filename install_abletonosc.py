#!/usr/bin/env python3
"""
Download and install complete AbletonOSC from GitHub
"""

import os
import shutil
import urllib.request
import zipfile
from pathlib import Path

print("=" * 70)
print("AbletonOSC Installer")
print("=" * 70)
print()

# Paths
user_profile = os.environ.get('USERPROFILE', os.environ.get('HOME', ''))
remote_scripts_path = Path(user_profile) / "Documents" / "Ableton" / "User Library" / "Remote Scripts"
abletonosc_path = remote_scripts_path / "AbletonOSC"
temp_zip = Path("abletonosc_temp.zip")
temp_extract = Path("abletonosc_temp")

print(f"Target directory: {abletonosc_path}")
print()

# Step 1: Backup existing installation
if abletonosc_path.exists():
    print("[1/5] Backing up existing AbletonOSC...")
    backup_path = remote_scripts_path / "AbletonOSC_backup"
    if backup_path.exists():
        shutil.rmtree(backup_path)
    shutil.move(str(abletonosc_path), str(backup_path))
    print(f"  Backed up to: {backup_path}")
else:
    print("[1/5] No existing installation found")
print()

# Step 2: Download from GitHub
print("[2/5] Downloading AbletonOSC from GitHub...")
github_url = "https://github.com/ideoforms/AbletonOSC/archive/refs/heads/master.zip"

try:
    urllib.request.urlretrieve(github_url, temp_zip)
    print(f"  Downloaded: {temp_zip} ({temp_zip.stat().st_size / 1024:.1f} KB)")
except Exception as e:
    print(f"  [ERROR] Failed to download: {e}")
    print()
    print("Please manually download from: https://github.com/ideoforms/AbletonOSC")
    exit(1)
print()

# Step 3: Extract
print("[3/5] Extracting archive...")
try:
    with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_extract)
    print(f"  Extracted to: {temp_extract}")
except Exception as e:
    print(f"  [ERROR] Failed to extract: {e}")
    exit(1)
print()

# Step 4: Move to Remote Scripts
print("[4/5] Installing to Remote Scripts...")
try:
    # The extracted folder will be "AbletonOSC-master"
    extracted_folder = temp_extract / "AbletonOSC-master"

    if not extracted_folder.exists():
        print(f"  [ERROR] Extracted folder not found: {extracted_folder}")
        exit(1)

    # Ensure target directory exists
    remote_scripts_path.mkdir(parents=True, exist_ok=True)

    # Move the folder
    shutil.move(str(extracted_folder), str(abletonosc_path))
    print(f"  Installed to: {abletonosc_path}")
except Exception as e:
    print(f"  [ERROR] Failed to install: {e}")
    exit(1)
print()

# Step 5: Verify installation
print("[5/5] Verifying installation...")
required_files = [
    "__init__.py",
    "manager.py",
    "abletonosc",  # This should be a directory
]

all_good = True
for item in required_files:
    item_path = abletonosc_path / item
    if item_path.exists():
        if item == "abletonosc":
            # Check it's a directory
            if item_path.is_dir():
                print(f"  [OK] {item}/ (directory)")
            else:
                print(f"  [FAIL] {item} is not a directory!")
                all_good = False
        else:
            print(f"  [OK] {item}")
    else:
        print(f"  [FAIL] Missing: {item}")
        all_good = False

# Cleanup
try:
    if temp_zip.exists():
        temp_zip.unlink()
    if temp_extract.exists():
        shutil.rmtree(temp_extract)
except:
    pass

print()
print("=" * 70)
if all_good:
    print("SUCCESS! AbletonOSC is now installed correctly.")
    print()
    print("Next steps:")
    print("1. RESTART Ableton Live completely (quit and reopen)")
    print("2. Go to Preferences -> Link / Tempo / MIDI")
    print("3. Select 'AbletonOSC' in Control Surface dropdown")
    print("4. Look for message: 'AbletonOSC: Listening for OSC on port 11000'")
    print("5. Run: python test_osc_connection.py")
else:
    print("INSTALLATION INCOMPLETE!")
    print("Some files are missing. Please check the errors above.")
print("=" * 70)
