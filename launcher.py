import streamlit as st
import subprocess
import sys
import os
from pathlib import Path
import base64
import json
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="PyCraft Launcher",
    page_icon="⛏️",
    layout="centered"
)

# Get the base directory
base_dir = Path(__file__).parent

# Simplified launcher - no accounts needed
# Initialize session state
if 'show_realm_selector' not in st.session_state:
    st.session_state.show_realm_selector = False

# Function to load background image
@st.cache_data(show_spinner=False)
def get_base64_image(image_path):
    """Convert image to base64 string (cached)."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Try to load background image from Assets folder
background_path = base_dir / "Assets" / "Background_launcher.png"
if background_path.exists():
    bg_base64 = get_base64_image(str(background_path))
    if bg_base64:
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bg_base64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """, unsafe_allow_html=True)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2E8B57;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .subtitle {
        text-align: center;
        color: #fff;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    }
    .stSelectbox, .stButton {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">⛏️ PyCraft Launcher</h1>', unsafe_allow_html=True)

# Download section at top (for new users)
st.markdown("---")

# Check if running on Streamlit Cloud
is_cloud = os.path.exists('/mount/src') or os.environ.get('STREAMLIT_SHARING_MODE') or 'streamlit.app' in os.environ.get('HOSTNAME', '')

if is_cloud:
    # CLOUD MODE - Browser play available!
    st.success("🌐 **Streamlit Cloud Mode** - Click play buttons to launch in browser!")
    st.markdown("---")
    st.markdown("### 📥 Or Download for Offline Play (Optional)")
    st.markdown("**Want to play offline? Download the full version:**")
else:
    # LOCAL MODE - Show download for new users
    st.markdown("### 📥 First Time Here? Download PyCraft")
    st.markdown("**If you haven't downloaded PyCraft yet**, click below for one-click installation:")

# Create installer script for download
installer_script = """'''
PyCraft One-Click Installer
Downloads and installs PyCraft automatically
'''
import os
import sys
import subprocess
import urllib.request
import zipfile

def main():
    print(\"\"\"
    ⛏️  PyCraft One-Click Installer
    ================================
    This will automatically:
    1. Download PyCraft from GitHub
    2. Install dependencies (pygame, streamlit, ursina)
    3. Launch the game launcher
    
    Press Enter to continue or Ctrl+C to cancel...
    \"\"\")
    input()
    
    # Download repository
    print("\\n📥 Downloading PyCraft from GitHub...")
    repo_url = "https://github.com/Syed-Ameer/akram-pygame-minecraft/archive/refs/heads/feature-texture-v1.zip"
    zip_path = "pycraft.zip"
    
    try:
        urllib.request.urlretrieve(repo_url, zip_path)
        print("✅ Download complete!")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        input("\\nPress Enter to exit...")
        return
    
    # Extract ZIP
    print("\\n📂 Extracting files...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        os.remove(zip_path)
        extracted_folder = "akram-pygame-minecraft-feature-texture-v1"
        if os.path.exists(extracted_folder):
            os.chdir(extracted_folder)
            print(f"✅ Extracted to: {os.getcwd()}")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        input("\\nPress Enter to exit...")
        return
    
    # Install dependencies
    print("\\n📦 Installing dependencies...")
    for package in ["pygame", "streamlit", "ursina"]:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        print(f"✅ {package} installed!")
    
    # Create launch shortcut
    print("\\n🎯 Creating game launcher shortcut...")
    if sys.platform == 'win32':
        play_script = "@echo off\\n"
        play_script += "title PyCraft Launcher\\n"
        play_script += "echo Launching PyCraft...\\n"
        play_script += f'"{sys.executable}" -m streamlit run launcher.py\\n'
        play_script += "pause"
        with open("PLAY_PYCRAFT.bat", "w") as f:
            f.write(play_script)
        print("✅ Created PLAY_PYCRAFT.bat")
    else:
        play_script = "#!/bin/bash\\n"
        play_script += 'echo "Launching PyCraft..."\\n'
        play_script += f'"{sys.executable}" -m streamlit run launcher.py'
        with open("play_pycraft.sh", "w") as f:
            f.write(play_script)
        os.chmod("play_pycraft.sh", 0o755)
        print("✅ Created play_pycraft.sh")
    
    # Launch
    print("\\n🚀 Launching PyCraft...")
    print("The launcher will open at http://localhost:8501")
    print("Press Ctrl+C to stop\\n")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "launcher.py"])
    except KeyboardInterrupt:
        print("\\n\\n👋 Thanks for playing PyCraft!")
        print(f"\\n💡 To play again, run: PLAY_PYCRAFT.bat")
        print(f"   Located at: {os.getcwd()}")
    
    input("\\nPress Enter to exit...")

if __name__ == "__main__":
    main()
'''"""

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.download_button(
        label="⬇️ DOWNLOAD INSTALLER",
        data=installer_script,
        file_name="install_pycraft.py",
        mime="text/x-python",
        use_container_width=True,
        type="primary"
    )

with st.expander("ℹ️ How to install (click to expand)"):
    st.markdown("""
    **After downloading:**
    1. Run: `python install_pycraft.py`
    2. Wait for automatic setup (downloads, installs dependencies)
    3. Double-click **PLAY_PYCRAFT.bat** anytime to play!
    
    The installer creates a permanent launcher shortcut in your game folder.
    """)

st.markdown("#### 🛠️ Manual Installation")
with st.expander("Prefer manual setup? Click here"):
    st.markdown("""
    **Manual Download & Setup:**
    
    1. **Get the code:**
    """)
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.link_button(
            "📦 Download ZIP from GitHub",
            "https://github.com/Syed-Ameer/akram-pygame-minecraft/archive/refs/heads/feature-texture-v1.zip",
            use_container_width=True
        )
    with col_b:
        st.link_button(
            "🔗 Visit GitHub Repository",
            "https://github.com/Syed-Ameer/akram-pygame-minecraft",
            use_container_width=True
        )
    
    st.markdown("""
    2. **Extract the ZIP file** to a folder
    
    3. **Install dependencies:**
    """)
    st.code("pip install pygame streamlit ursina", language="bash")
    
    st.markdown("""
    4. **Launch the launcher:**
    """)
    st.code("streamlit run launcher.py", language="bash")
    
    st.markdown("""
    5. **Or run games directly:**
    """)
    st.code('python "Alpha/Alpha v1.0 Overworld.py"', language="bash")
    
    st.success("✅ That's it! The launcher will open in your browser.")

st.markdown("---")

# Show download reminder for cloud users
is_cloud = os.path.exists('/mount/src') or os.environ.get('STREAMLIT_SHARING_MODE') or 'streamlit.app' in os.environ.get('HOSTNAME', '')
if is_cloud:
    st.info("💡 **Browsing on Streamlit Cloud?** Download the installer above to play on your computer. You can still explore the launcher features below!")

# Show launcher for everyone
st.markdown("### 🎮 Game Launcher")
st.markdown('<p class="subtitle">Select your game and start playing! No account needed. 🎮</p>', unsafe_allow_html=True)

# Define game versions organized by category
@st.cache_data(show_spinner=False)
def get_game_versions():
    """Scan directories and get all available game versions (cached)."""
    versions = {}
    
    # Pre-Classic
    pre_classic_path = base_dir / "Pre-Classic.py"
    if pre_classic_path.exists():
        versions["Pre-Classic"] = [("Pre-Classic", str(pre_classic_path))]
    else:
        versions["Pre-Classic"] = []
    
    # Classic versions
    classic_dir = base_dir / "Classic"
    if classic_dir.exists():
        classic_files = sorted([f for f in classic_dir.glob("*.py")])
        versions["Classic"] = [(f.stem, str(f)) for f in classic_files]
    else:
        versions["Classic"] = []
    
    # Indev versions
    indev_dir = base_dir / "Indev"
    if indev_dir.exists():
        indev_files = sorted([f for f in indev_dir.glob("*.py")])
        versions["Indev"] = [(f.stem, str(f)) for f in indev_files]
    else:
        versions["Indev"] = []
    
    # Alpha versions
    alpha_dir = base_dir / "Alpha"
    if alpha_dir.exists():
        alpha_files = sorted([f for f in alpha_dir.glob("*.py")])
        versions["Alpha"] = [(f.stem, str(f)) for f in alpha_files]
    else:
        versions["Alpha"] = []
    
    # Bedrock Edition (Mobile/Tablet)
    bedrock_path = base_dir / "Alpha" / "pycraft_bedrock_mobile.py"
    if bedrock_path.exists():
        versions["Bedrock Edition"] = [("Bedrock Mobile/Tablet", str(bedrock_path))]
    else:
        versions["Bedrock Edition"] = []
    
    # Experimental
    experimental_path = base_dir / "Experimental.py"
    if experimental_path.exists():
        versions["Experimental"] = [("Experimental", str(experimental_path))]
    else:
        versions["Experimental"] = []
    
    return versions

# Get all versions
all_versions = get_game_versions()

# Create a flat list for dropdown with category prefixes
dropdown_options = []
version_map = {}

for category, versions in all_versions.items():
    for version_name, version_path in versions:
        display_name = f"{category} → {version_name}"
        dropdown_options.append(display_name)
        version_map[display_name] = version_path

# Find default selection (Alpha v1.0 Overworld is prioritized)
default_index = 0
for i, option in enumerate(dropdown_options):
    if "Alpha v1.0 Overworld" in option:
        default_index = i
        break
    elif "Alpha 4 Overworld" in option:
        default_index = i
    elif "Alpha 3 Overworld" in option and default_index == 0:
        default_index = i

# ===== QUICK PLAY SECTION - MOST PROMINENT =====
st.markdown("### 🎮 Quick Play")

# Show total available versions
total_versions = len(dropdown_options)
st.success(f"✅ **{total_versions} Game Versions Available** - All Launchable from this Launcher!")

# Check if on cloud
is_cloud_env = os.path.exists('/mount/src') or os.environ.get('STREAMLIT_SHARING_MODE') or 'streamlit.app' in os.environ.get('HOSTNAME', '')

# Version selector with prominent play button
selected_version = st.selectbox(
    "🎮 Select Game Version:",
    options=dropdown_options,
    index=default_index,
    help=f"Choose any of the {total_versions} available versions!"
)

# BIG PLAY BUTTON
play_col1, play_col2, play_col3 = st.columns([1, 3, 1])
with play_col2:
    if is_cloud_env:
        # On cloud - offer multiple options
        cloud_play_option = st.radio(
            "Choose play mode:",
            ["🖼️ Play in Streamlit (Experimental)", "🌐 Play in Browser (Full Version)", "📥 Download Only"],
            label_visibility="collapsed",
            horizontal=True
        )
        
        if cloud_play_option == "🖼️ Play in Streamlit (Experimental)":
            play_button_streamlit = st.button(
                "🎮 PLAY IN STREAMLIT",
                use_container_width=True,
                type="primary",
                help=f"Run {selected_version} right here in Streamlit!"
            )
            
            if play_button_streamlit:
                st.session_state.game_mode = "streamlit"
                st.session_state.selected_game = selected_version
                st.rerun()
        
        elif cloud_play_option == "🌐 Play in Browser (Full Version)":
            play_button_cloud = st.button(
                "🚀 OPEN IN NEW WINDOW",
                use_container_width=True,
                type="primary",
                help=f"Launch full browser version"
            )
            
            if play_button_cloud:
                browser_url = "https://syed-ameer.github.io/akram-pygame-minecraft/"
                st.markdown(f"""
                    <script>
                        window.open('{browser_url}', '_blank');
                    </script>
                """, unsafe_allow_html=True)
                st.success(f"🎮 Opening browser launcher...")
                st.info("💡 A new window should open. If blocked, click the link below:")
                st.markdown(f"[🌐 Click here to play]({browser_url})", unsafe_allow_html=True)
        
        else:  # Download only
            st.info("📥 Use the download section below to get the full version")
        
        launch_button = False
    else:
        # Local - show both desktop and browser options
        st.markdown("**Choose Launch Mode:**")
        launch_mode = st.radio(
            "Select how to play:",
            ["🖥️ Desktop (Launch Real Game)", "🌐 Browser (Web Version)"],
            label_visibility="collapsed"
        )
        
        if launch_mode.startswith("🖥️"):
            launch_button = st.button(
                "🚀 LAUNCH DESKTOP GAME",
                use_container_width=True,
                type="primary",
                help=f"Launch {selected_version} in new window - Full featured desktop version!"
            )
        else:
            launch_button = False
            if st.button(
                "🌐 OPEN BROWSER VERSION",
                use_container_width=True,
                type="secondary",
                help="Play in browser"
            ):
                browser_url = "https://syed-ameer.github.io/akram-pygame-minecraft/"
                st.markdown(f'<script>window.open("{browser_url}", "_blank");</script>', unsafe_allow_html=True)
                st.success("🎮 Opening browser launcher...")
                st.markdown(f"[🌐 Click here if it didn't open]({browser_url})")


# Display version info
if selected_version:
    st.caption(f"📦 {selected_version}")

# Handle Streamlit gameplay mode
if 'game_mode' in st.session_state and st.session_state.game_mode == "streamlit":
    st.markdown("---")
    
    try:
        from streamlit_pygame_runner import run_pygame_in_streamlit
        
        # Get the game path
        selected_game = st.session_state.selected_game
        game_path = version_map.get(selected_game, None)
        
        # Run the game
        run_pygame_in_streamlit(selected_game, game_path)
        
    except Exception as e:
        st.error(f"❌ Error loading game: {e}")
        st.info("💡 Try the browser version instead!")
        if st.button("🌐 Open Browser Version"):
            st.session_state.game_mode = None
            st.rerun()
    
    st.stop()  # Don't show rest of launcher

# ===== BROWSER PLAY OPTION =====
st.markdown("---")
st.markdown("### 🌐 Play in Browser (Web Version)")

st.info("🎮 **Pygbag Web Edition** - Play in your browser without installation!")

browser_col1, browser_col2 = st.columns([3, 1])

with browser_col1:
    st.markdown("""
    **Browser Edition Features:**
    - ✨ All 27 versions in interactive web launcher
    - 🌐 Works on any device with a browser
    - 🎮 Use ← → arrow keys to browse versions
    - ⌨️ Press ENTER to launch selected game
    - 💾 No installation required
    - 🚀 Powered by Pygbag WebAssembly
    
    *Classic 5 fully playable now, more versions being added!*
    """)

with browser_col2:
    st.markdown("")  # Spacing
    st.markdown("")  # Spacing
    # Button to launch web version
    if st.button(
        "🌐 Launch Browser Game",
        use_container_width=True,
        type="primary",
        help="Opens the Pygbag web version in your browser"
    ):
        browser_url = "https://syed-ameer.github.io/akram-pygame-minecraft/"
        
        # Open in browser
        import webbrowser
        try:
            webbrowser.open(browser_url)
            st.success("✅ Opening web launcher in browser...")
            st.info("🎮 Use ← → arrows to browse games, press ENTER to launch")
        except Exception as e:
            st.warning("⚠️ Couldn't auto-open browser")
        
        # Also show link
        st.markdown(f"[🌐 Click here if browser didn't open]({browser_url})")


# Optional: Show screenshot or info about desktop launcher
with st.expander("ℹ️ About Desktop Launcher"):
    st.markdown("""
    The **Desktop Launcher** is a beautiful Pygame interface that lets you:
    
    - 📋 Browse all game versions with smooth carousel navigation
    - ✅ See which games are playable vs coming soon
    - 🎨 Enjoy gradient backgrounds and professional UI
    - 🚀 Launch games instantly in separate windows
    - 🔄 Return to launcher after closing games
    
    **Perfect for:**
    - Installing once and playing anytime
    - Offline gameplay
    - Best performance (native Python)
    - Full game features without browser limits
    """)

# Show all available versions organized by category
with st.expander("📋 View All Available Versions"):
    st.markdown("### 🎮 Complete Version List")
    st.markdown("*All versions below are launchable from the dropdown above!*")
    
    for category, versions in all_versions.items():
        if versions:  # Only show categories that have versions
            st.markdown(f"**{category}:** ({len(versions)} versions)")
            for version_name, version_path in versions:
                # Check if file exists
                exists = "✅" if Path(version_path).exists() else "❌"
                st.text(f"  {exists} {version_name}")
            st.markdown("")  # Spacing

# ===== AKRAM DLC TOGGLE =====
st.markdown("---")
st.markdown("### 🔥 Akram DLC Features")

# Initialize DLC state if not exists
if 'akram_dlc_enabled' not in st.session_state:
    st.session_state.akram_dlc_enabled = True  # Default enabled for enhanced experience

# Create toggle with nice styling
dlc_col1, dlc_col2 = st.columns([3, 1])

with dlc_col1:
    st.markdown("""
    **Akram DLC** adds custom features beyond Minecraft:
    - 🦌 **Custom Animals**: Deer, Bear, Elephant, Narwhal, Turtle, Panda, Fox, Penguin, Camel
    - 🏺 **Custom Items**: Deer Horn, Narwhal Horn, custom spawn eggs
    - 🎨 **Enhanced Textures**: Custom animal textures and sprites
    - 🌊 **Ocean Life**: Whale, Dolphin, Shark, Nautilus creatures
    - 🐾 **Wildlife Variety**: Expanded animal ecosystem beyond vanilla Minecraft
    
    *All standard Minecraft features (portals, enchanting, combat, etc.) remain enabled*
    
    *Disable for pure vanilla Minecraft animal roster*
    """)

with dlc_col2:
    # Toggle button
    if st.session_state.akram_dlc_enabled:
        dlc_button_text = "🔥 DLC: ON"
        dlc_button_type = "primary"
        dlc_help_text = "Custom animals and content enabled - Enhanced wildlife!"
    else:
        dlc_button_text = "⚪ DLC: OFF"
        dlc_button_type = "secondary" 
        dlc_help_text = "Vanilla animals only - Standard Minecraft creatures"
    
    if st.button(dlc_button_text, use_container_width=True, type=dlc_button_type, help=dlc_help_text):
        st.session_state.akram_dlc_enabled = not st.session_state.akram_dlc_enabled
        st.rerun()

# Show current DLC status
if st.session_state.akram_dlc_enabled:
    st.success("🔥 **Akram DLC ENABLED** - Custom animals and wildlife active!")
else:
    st.warning("⚪ **Vanilla Mode** - Standard Minecraft animals only")

# Voting system removed for simplified launcher

# Multiplayer options
st.markdown("---")
st.markdown("### 🌐 Multiplayer Options")

with st.expander("🎮 Host or Join Multiplayer Server"):
    # Server IP input for joining
    server_ip = st.text_input("Server IP Address", value="127.0.0.1", help="Enter the server IP to connect to")
    server_port = st.number_input("Port", value=5555, min_value=1024, max_value=65535, help="Server port (default 5555)")
    
    mp_col1, mp_col2 = st.columns(2)
    
    with mp_col1:
        start_server_button = st.button(
            "🖥️ Host Server",
            use_container_width=True,
            help="Start a multiplayer server for others to join"
        )
    
    with mp_col2:
        join_server_button = st.button(
            "🌍 Join Server",
            use_container_width=True,
            help="Connect to a multiplayer server"
        )

# Meme of the month removed - doesn't work on foreign computers

# --- Handle button actions ---

# Handle server hosting
if start_server_button:
    server_path = base_dir / "Alpha" / "multiplayer_server.py"
    
    if server_path.exists():
        with st.spinner("🖥️ Starting multiplayer server..."):
            try:
                server_dir = str(server_path.parent)
                python_exe = sys.executable
                
                if os.name == 'nt':  # Windows
                    subprocess.Popen(
                        f'start cmd /k "cd /d {server_dir} && "{python_exe}" multiplayer_server.py --port {int(server_port)}"',
                        shell=True
                    )
                else:
                    subprocess.Popen(
                        [python_exe, str(server_path), "--port", str(int(server_port))],
                        cwd=server_dir
                    )
                
                # Get local IP
                import socket
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect(("8.8.8.8", 80))
                    local_ip = s.getsockname()[0]
                    s.close()
                except Exception:
                    local_ip = "127.0.0.1"
                
                st.success(f"✅ Server started on port {int(server_port)}!")
                st.info(f"💡 Share this IP with friends: **{local_ip}**")
                st.code(f"IP: {local_ip}\nPort: {int(server_port)}")
            except Exception as e:
                st.error(f"❌ Error starting server: {str(e)}")
    else:
        st.error("❌ Multiplayer server file not found!")

# Handle Join Server
if join_server_button:
    if selected_version in version_map:
        game_path = version_map[selected_version]
        with st.spinner(f"🌍 Connecting to {server_ip}:{int(server_port)}..."):
            try:
                game_dir = str(Path(game_path).parent)
                game_file = Path(game_path).name
                python_exe = sys.executable
                
                if os.name == 'nt':
                    subprocess.Popen(
                        f'start cmd /k "cd /d {game_dir} && "{python_exe}" "{game_file}""',
                        shell=True
                    )
                else:
                    subprocess.Popen(
                        [python_exe, game_path],
                        cwd=game_dir
                    )
                
                st.success(f"✅ Joining server at {server_ip}:{int(server_port)}!")
                st.info("💡 The game is connecting in a separate window.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.error("❌ Select a game version first!")

# Handle launch
if launch_button:
    if selected_version in version_map:
        game_path = version_map[selected_version]
        
        # Verify game file exists
        if not Path(game_path).exists():
            st.error(f"❌ Game file not found: {game_path}")
            st.warning("💡 Make sure you've extracted all files from the ZIP!")
        else:
            # Show loading message
            with st.spinner(f"🎮 Launching {selected_version}..."):
                try:
                    # Get the directory of the game file
                    game_dir = str(Path(game_path).parent.resolve())
                    game_file = Path(game_path).name
                    
                    # Use the same Python interpreter that's running this launcher
                    python_exe = sys.executable
                    
                    # Debug info
                    st.info(f"📂 Game directory: {game_dir}")
                    st.info(f"📄 Game file: {game_file}")
                    st.info(f"🐍 Python: {python_exe}")
                    
                    # Launch the game as a subprocess
                    if os.name == 'nt':  # Windows
                        # Create launch command
                        cmd = f'cd /d "{game_dir}" && "{python_exe}" "{game_file}"'
                        st.code(f"Running: {cmd}", language="bash")
                        
                        # Use start command to keep window open
                        subprocess.Popen(
                            f'start cmd /k "{cmd}"',
                            shell=True,
                            cwd=game_dir
                        )
                    else:  # Linux/Mac
                        subprocess.Popen(
                            [python_exe, game_file],
                            cwd=game_dir
                        )
                    
                    st.success(f"✅ {selected_version} launched successfully!")
                    st.balloons()
                    st.info("💡 The game window should open in 2-5 seconds. Check your taskbar!")
                    st.warning("⚠️ If nothing happens, check the command window that opened for error messages.")
                    
                except Exception as e:
                    st.error(f"❌ Error launching game: {str(e)}")
                    st.error(f"Path: {game_path}")
                    st.code(f"Python: {sys.executable}\nGame Dir: {game_dir}\nGame File: {game_file}")
    else:
        st.error("❌ Selected version not found!")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #999; font-size: 0.9rem;">PyCraft Launcher v2.0 | Account System & Realms</p>',
    unsafe_allow_html=True
)
