# 🎮 PyCraft - Desktop Edition

## 🚀 Quick Start (Easiest Way)

### For Windows:
1. **Double-click `PLAY.bat`**
2. Press ENTER when prompted
3. Select your game and click PLAY!

### For Mac/Linux:
```bash
python desktop_install.py
```

---

## 📦 What You Need

**Only 1 Requirement:**
- Python 3.7+ installed
- That's it! The launcher will auto-install pygame

**No Internet Required After First Install!**

---

## 🎯 Features

### ✅ Desktop Launcher Benefits:
- **Works Offline** - No web browser needed
- **Fast Loading** - Pure Pygame, instant startup
- **All 25 Games** - Complete collection in one launcher
- **Simple Controls** - Arrow keys + ENTER
- **No Account Needed** - Just play!
- **Cross-Platform** - Windows, Mac, Linux

### ❌ What's Removed (For Simplicity):
- Meme of the Month (requires download)
- Online features (voting, accounts)
- Streamlit dependency
- Web browser requirement

---

## 🎮 Available Games

### Pre-Classic (1)
- Pre-Classic

### Classic (7)
- Classic 1-7 (Beginning through Complete)

### Indev (7)
- Indev 1-7 (Basics through Dimensions)

### Alpha (9)
- Alpha 1 & 2
- Alpha 3, 4, v1.0 Overworld
- Alpha 4 & v1.0 End
- Alpha 4-snapshot & v1.0 Nether

### Experimental (1)
- Experimental builds

**Total: 25 Desktop Games**

---

## 🎯 How to Use

### Method 1: One-Click Launch (Recommended)
```
1. Double-click PLAY.bat (Windows)
2. Press ENTER
3. Done!
```

### Method 2: Manual Launch
```bash
# Install pygame (only needed once)
pip install pygame

# Launch the desktop launcher
python desktop_launcher.py

# OR launch any game directly
python "Classic/Classic 5.py"
python "Alpha/Alpha v1.0 Overworld.py"
```

---

## 🕹️ Controls

**In Launcher:**
- ↑↓ Arrow Keys: Select game
- ENTER or Click: Launch game
- Mouse Wheel: Scroll list
- ESC: Exit launcher

**In Game:**
- Controls vary by version
- Most use WASD + Mouse + E for inventory

---

## 📂 File Structure

```
PyCraft/
├── PLAY.bat                    # Windows quick launcher
├── desktop_launcher.py         # Main desktop launcher
├── desktop_install.py          # Auto-installer
├── Classic/                    # Classic games (1-7)
├── Indev/                      # Indev games (1-7)
├── Alpha/                      # Alpha games (complete)
└── Pre-Classic.py             # First version
```

---

## 🔧 Troubleshooting

### "Pygame not found"
```bash
pip install pygame
```

### "Game file not found"
- Make sure all game folders are in the same directory as the launcher
- Check that files haven't been renamed

### Game crashes on launch
- Some versions have specific requirements
- Try a different version (Classic 5 is most stable)

### Launcher won't start
```bash
# Try running directly
python desktop_launcher.py

# Check Python version
python --version  # Should be 3.7+
```

---

## 🆚 Desktop vs Web Version

### Desktop Launcher (PLAY.bat)
✅ Works offline  
✅ No browser needed  
✅ Faster loading  
✅ Direct access to all games  
❌ No memes/voting  
❌ No online features  

### Web/Streamlit Launcher (launcher.py)
✅ Meme of the month  
✅ Feature voting  
✅ User accounts  
✅ Web browser interface  
❌ Requires Streamlit  
❌ Needs internet for memes  

**Choose Desktop for:**
- Offline play
- Simple quick access
- School/work computers
- No admin access

**Choose Web for:**
- Online features
- Meme voting
- User accounts
- Browser-based play

---

## 📝 For Developers

### Running Specific Games:
```bash
# Classic series
python "Classic/Classic 5.py"

# Alpha Overworld (full features)
python "Alpha/Alpha v1.0 Overworld.py"

# Alpha Nether
python "Alpha/Alpha v1.0 Nether.py"

# Alpha End
python "Alpha/Alpha v1.0 End.py"
```

### Modifying the Launcher:
Edit `desktop_launcher.py` to:
- Change colors/theme
- Add more games
- Customize layout
- Add custom features

---

## 🌐 Want the Web Version Instead?

If you prefer the web launcher with memes and voting:

```bash
# Install additional requirements
pip install streamlit

# Launch web version
streamlit run launcher.py
```

---

## 💾 Save Files

All games save to:
- `saves/` folder for worlds
- Individual game folders for settings

Saves are compatible across desktop and web versions!

---

## 🎉 Enjoy!

No internet, no web browser, no accounts - just pure Minecraft-style gaming!

**To start playing:**
1. Double-click `PLAY.bat`
2. Select a game
3. Click PLAY
4. Have fun! ⛏️

---

## 📧 Support

If you encounter issues:
1. Check this README
2. Try a different game version
3. Make sure pygame is installed
4. Check Python version is 3.7+

**Have fun mining and crafting!** 🎮⛏️
