# PyCraft Alpha 4 🎮⛏️

A 2D Minecraft-inspired game built with Python and Pygame, featuring procedural world generation, survival mechanics, and multiplayer support.

## 🚀 Features

### Core Gameplay
- **Procedural World Generation**: Infinite worlds with multiple biomes (Plains, Desert, Forest, Snow, Swamp, etc.)
- **Survival Mechanics**: Health, hunger, and oxygen systems
- **Day/Night Cycle**: Dynamic lighting with hostile mob spawning at night
- **Combat System**: Fight zombies, skeletons, creepers, spiders, endermen, and more
- **Creative & Survival Modes**: Build freely or survive the elements

### Advanced Features
- **Elytra Gliding**: Press SPACE while falling to glide through the air
- **Ice Boat Speed**: 1.5x speed boost when riding boats on ice
- **Help System**: Press H for comprehensive controls guide
- **Multiplayer Support**: Play with friends over LAN
- **Bug Reporting**: Built-in bug tracker in launcher (admins can manage reports)

### World Features
- **20+ Biomes**: Including Crimson Forest, Warped Forest, Soul Sand Valley, and more
- **Structures**: Villages, pillager outposts, witch huts, desert temples, strongholds
- **Liquid Physics**: Water and lava flow naturally downward and horizontally
- **150+ Block Types**: Including ores, wood, stone, decorative blocks
- **45+ Mob Types**: Passive animals, hostile monsters, and rare bosses

### Player Features
- **Crafting System**: Craft tools, weapons, armor, and items
- **Enchanting & Anvils**: Enhance your gear with magical properties
- **Achievement System**: Track your progress with 20+ achievements
- **Skin Selection**: Choose from 9 different player skins
- **Armor & Tools**: Full progression from wood to diamond

## 📋 Requirements

- Python 3.8 or higher
- Pygame 2.5.0 or higher
- Streamlit 1.28.0 or higher (for launcher)

## 🔧 Installation

1. **Clone the repository**
```bash
git clone https://github.com/Syed-Ameer/akram-pygame-minecraft.git
cd akram-pygame-minecraft
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the launcher**
```bash
streamlit run launcher.py
```

Or run the game directly:
```bash
cd Alpha
python "Alpha 4 Overworld.py"
```

## 🎮 Controls

### Basic Controls
- **WASD** - Move around
- **SPACE** - Jump / Swim up
- **SHIFT** - Sneak / Climb down
- **E** - Open inventory
- **1-9** - Select hotbar slot
- **Q** - Drop item
- **R** - Sprint (2x speed)
- **ESC** - Pause menu
- **H** - Show help overlay

### Mouse Controls
- **Left Click** - Break blocks / Attack
- **Right Click** - Place blocks / Use items
- **Middle Click** - Pick block (Creative)
- **Scroll Wheel** - Change hotbar slot

### Advanced Controls
- **F5** - Change camera view (First/Third person)
- **Z** - Block with shield
- **SPACE** (while falling with Elytra) - Activate gliding
- **Right Click** (on animal) - Ride/Tame
- **T** - Open chat (Multiplayer)
- **C** - Toggle fly mode (Creative)
- **/** - Command mode (Creative)

## 🌍 Game Versions

- **Alpha 4 Overworld** - Main survival world with full feature set
- **Alpha 4 End** - End dimension with ender dragon boss
- **Alpha 4 Nether** - Nether dimension with unique biomes and mobs
- **Multiplayer Support** - Play with friends via LAN

## 🐛 Bug Reporting

The launcher includes a built-in bug reporting system:
- All players can view and submit bug reports
- Admins can edit status and manage reports
- Reports are saved in `bugs.json`
- Admin usernames are stored in `admins.txt`

## 👥 Accounts System

- Create a username on first launch
- Select from 9 different player skins
- Accounts saved in `accounts.json`
- Data persists across sessions

## 🎨 Texture System

Toggle between modern textures and classic "Programming Art" style:
- Press the Textures button in pause menu
- All mobs and blocks have texture support
- Textures located in `Textures/` folder

## 🔊 Sound System

- Background music for menu, gameplay, and dimensions
- Sound effects for blocks, mobs, and player actions
- Adjustable volume in settings
- Music files in `Sounds/` folder

## 📦 Project Structure

```
PyGame/
├── Alpha/
│   ├── Alpha 4 Overworld.py    # Main game file
│   ├── Alpha 4 End.py           # End dimension
│   ├── pycraft_nether.py        # Nether dimension
│   ├── pycraft_network.py       # Multiplayer system
│   └── saves/                   # World save files
├── Textures/                    # Block and mob textures
├── Sounds/                      # Music and sound effects
├── launcher.py                  # Streamlit launcher UI
├── sound_manager.py             # Audio system
├── requirements.txt             # Python dependencies
└── bugs.json                    # Bug report database
```

## 🚧 Known Issues

- Save/load system may not preserve all mob states
- Liquid physics can cause lag in very large pools
- Some texture files may be missing

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is open source and available for educational purposes.

## 👨‍💻 Authors

- **Syed Ameer** - Initial work and development
- Contributors welcome!

## 🙏 Acknowledgments

- Inspired by Minecraft (Mojang Studios)
- Built with Pygame
- UI powered by Streamlit
- Community feedback and testing

## 📞 Support

For bugs and feature requests:
- Use the in-game bug reporter
- Open an issue on GitHub
- Contact the development team

---

**Enjoy building and surviving in PyCraft!** 🎮⛏️✨
