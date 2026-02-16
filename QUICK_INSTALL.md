# 🚀 Quick Install Guide

## One-Click Installation

### Windows
Just double-click:
```
INSTALL_AND_PLAY.bat
```
or
```
PLAY.bat
```

Both will automatically:
1. ✅ Check Python installation
2. ✅ Install all required packages
3. ✅ Launch the game launcher

### Linux/Mac
Run:
```bash
python3 install_and_play.py
```

## Manual Installation

If automatic installation doesn't work:

```bash
# 1. Install Python 3.8+ from python.org

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
streamlit run launcher.py
```

## What Gets Installed?

The auto-installer will install:
- **pygame** (2.5.0+) - Game engine
- **streamlit** (1.28.0+) - Launcher UI
- **pyvirtualdisplay** (3.0+) - Cloud support
- **pillow** (10.0+) - Image processing

All installations are automatic and handled for you!

## Features

✨ **Zero Configuration** - Just run and play!
🔧 **Auto-Repair** - Missing packages? We install them!
🎮 **One Command** - Everything installs automatically
☁️ **Cloud Ready** - Works on Streamlit Cloud too

## Troubleshooting

**"Python not found"**
→ Install Python 3.8+ from [python.org](https://python.org)

**"pip not found"**
→ Reinstall Python with "Add to PATH" checked

**Packages fail to install**
→ Run: `python -m pip install --upgrade pip`
→ Then try again

## That's It!

No complex setup. No manual commands. Just double-click and play! 🎮
