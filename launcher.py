import streamlit as st
import subprocess
import os
from pathlib import Path
import base64

# Set page config
st.set_page_config(
    page_title="PyCraft Launcher",
    page_icon="⛏️",
    layout="centered"
)

# Get the base directory
base_dir = Path(__file__).parent

# Function to load background image
def get_base64_image(image_path):
    """Convert image to base64 string."""
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
st.markdown('<p class="subtitle">Select a version and start playing!</p>', unsafe_allow_html=True)

# Define game versions organized by category
def get_game_versions():
    """Scan directories and get all available game versions."""
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

# Find default selection (Alpha 3 Overwold)
default_index = 0
for i, option in enumerate(dropdown_options):
    if "Alpha 3 Overwold" in option:
        default_index = i
        break

# Create dropdown
st.markdown("### 🎮 Select Game Version")
selected_version = st.selectbox(
    "Choose a version to play:",
    options=dropdown_options,
    index=default_index,
    label_visibility="collapsed"
)

# Display version info
if selected_version:
    st.info(f"📦 Selected: **{selected_version}**")

# Launch button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    launch_button = st.button(
        "🚀 LAUNCH",
        use_container_width=True,
        type="primary"
    )

# Handle launch
if launch_button:
    if selected_version in version_map:
        game_path = version_map[selected_version]
        
        # Show loading message
        with st.spinner(f"🎮 Launching {selected_version}..."):
            try:
                # Get the directory of the game file
                game_dir = str(Path(game_path).parent)
                game_file = Path(game_path).name
                
                # Launch the game as a subprocess with proper working directory
                if os.name == 'nt':  # Windows
                    # Use start command to keep window open
                    subprocess.Popen(
                        f'start cmd /k "cd /d {game_dir} && python "{game_file}""',
                        shell=True
                    )
                else:  # Linux/Mac
                    subprocess.Popen(
                        ["python", game_path],
                        cwd=game_dir
                    )
                
                st.success(f"✅ {selected_version} launched successfully!")
                st.balloons()
                st.info("💡 The game is running in a separate window. You can close this launcher or launch another version.")
                
            except Exception as e:
                st.error(f"❌ Error launching game: {str(e)}")
                st.error(f"Path: {game_path}")
    else:
        st.error("❌ Selected version not found!")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #999; font-size: 0.9rem;">PyCraft Launcher v1.0 | Made with Streamlit</p>',
    unsafe_allow_html=True
)
