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

# Initialize accounts system
ACCOUNTS_FILE = base_dir / "accounts.json"

def load_accounts():
    """Load saved accounts"""
    if ACCOUNTS_FILE.exists():
        try:
            with open(ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_accounts(accounts):
    """Save accounts to file"""
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

def add_account(username):
    """Add or update account"""
    accounts = load_accounts()
    accounts[username] = {
        "created": datetime.now().isoformat(),
        "last_login": datetime.now().isoformat(),
        "play_count": accounts.get(username, {}).get("play_count", 0)
    }
    save_accounts(accounts)
    return True

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
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

# Login System
if not st.session_state.logged_in:
    st.markdown('<p class="subtitle">Login or Create Account</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "➕ Create Account"])
    
    with tab1:
        st.markdown("### Login to Existing Account")
        accounts = load_accounts()
        
        if accounts:
            account_names = list(accounts.keys())
            selected_account = st.selectbox("Select Account:", account_names)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🎮 Login", type="primary", use_container_width=True):
                    st.session_state.logged_in = True
                    st.session_state.username = selected_account
                    # Update last login
                    accounts[selected_account]["last_login"] = datetime.now().isoformat()
                    save_accounts(accounts)
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Delete Account", use_container_width=True):
                    del accounts[selected_account]
                    save_accounts(accounts)
                    st.success(f"Account '{selected_account}' deleted!")
                    st.rerun()
        else:
            st.info("No accounts found. Create a new account in the 'Create Account' tab!")
    
    with tab2:
        st.markdown("### Create New Account")
        new_username = st.text_input("Username:", placeholder="Enter your username")
        if st.button("✅ Create Account", type="primary", use_container_width=True):
            if new_username:
                if len(new_username) < 3:
                    st.error("Username must be at least 3 characters!")
                elif new_username in accounts:
                    st.error("Username already exists!")
                elif new_username.lower() in ["player", "example", "testuser", ""]:
                    st.error("Please choose a unique username!")
                else:
                    add_account(new_username)
                    st.session_state.logged_in = True
                    st.session_state.username = new_username
                    st.success(f"Welcome, {new_username}! 🎉")
                    st.balloons()
                    st.rerun()
            else:
                st.error("Please enter a username!")
    
    # Show existing accounts preview
    if accounts:
        st.markdown("---")
        st.markdown("### 👥 Existing Accounts")
        for username, data in accounts.items():
            if username.lower() in ["player", "example", "testuser", ""]:
                continue
            last_login = data.get('last_login', 'Never')
            if last_login != 'Never':
                try:
                    last_login = datetime.fromisoformat(last_login).strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            st.text(f"👤 {username} - Last login: {last_login}")
    
    st.stop()

# User is logged in
st.markdown(f'<p class="subtitle">Welcome back, <strong>{st.session_state.username}</strong>! 🎮</p>', unsafe_allow_html=True)

# Logout button in sidebar
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.username}")
    accounts = load_accounts()
    if st.session_state.username in accounts:
        account_data = accounts[st.session_state.username]
        st.text(f"Play Count: {account_data.get('play_count', 0)}")
        try:
            created = datetime.fromisoformat(account_data.get('created', datetime.now().isoformat()))
            st.text(f"Member since: {created.strftime('%Y-%m-%d')}")
        except:
            st.text(f"Member since: Unknown")
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

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

# Version selector with prominent play button
selected_version = st.selectbox(
    "🎮 Select Game Version:",
    options=dropdown_options,
    index=default_index
)

# BIG PLAY BUTTON
play_col1, play_col2, play_col3 = st.columns([1, 3, 1])
with play_col2:
    launch_button = st.button(
        "🚀 PLAY SINGLEPLAYER",
        use_container_width=True,
        type="primary",
        help=f"Launch {selected_version}"
    )

# Display version info
if selected_version:
    st.caption(f"📦 {selected_version} | 👤 {st.session_state.username}")

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

# ===== FEATURE POLL =====
st.markdown("---")
st.markdown("### 📊 Vote for Next Update!")

# Initialize poll vote if not exists
if 'feature_vote' not in st.session_state:
    st.session_state.feature_vote = None

# Load existing votes from file
poll_file = base_dir / "feature_poll.json"
if poll_file.exists():
    try:
        with open(poll_file, 'r') as f:
            poll_data = json.load(f)
    except:
        poll_data = {"option1": 0, "option2": 0, "option3": 0, "option4": 0, "voters": []}
else:
    poll_data = {"option1": 0, "option2": 0, "option3": 0, "option4": 0, "voters": []}

# Feature options
poll_col1, poll_col2 = st.columns([3, 1])

with poll_col1:
    st.markdown("""
    **Choose what we add next:**
    - 🐱 **Option 1: Cats & Mod Support** - Tameable cats, mod loading system
    - 🌾 **Option 2: Farms & Bug Fixes** - Automated farms, performance improvements
    - 🌳 **Option 3: Mangrove Swamps & Alligators** - New biome, swamp mobs
    - 🏰 **Option 4: Structure Update** - More villages, dungeons, strongholds
    """)

with poll_col2:
    # Check if user already voted
    username = st.session_state.username
    has_voted = username in poll_data.get("voters", [])
    
    if not has_voted:
        vote_option = st.radio(
            "Your Vote:",
            ["🐱 Cats & Mods", "🌾 Farms & Fixes", "🌳 Mangroves & Alligators", "🏰 Structures"],
            label_visibility="collapsed"
        )
        
        if st.button("✅ Submit Vote", use_container_width=True, type="primary"):
            # Map vote to option
            vote_map = {
                "🐱 Cats & Mods": "option1",
                "🌾 Farms & Fixes": "option2",
                "🌳 Mangroves & Alligators": "option3",
                "🏰 Structures": "option4"
            }
            
            chosen_option = vote_map[vote_option]
            poll_data[chosen_option] += 1
            poll_data.setdefault("voters", []).append(username)
            
            # Save votes
            with open(poll_file, 'w') as f:
                json.dump(poll_data, f, indent=2)
            
            st.session_state.feature_vote = vote_option
            st.success(f"✅ Vote recorded for: {vote_option}")
            st.balloons()
            st.rerun()
    else:
        st.info("✅ You already voted!")

# Show poll results
total_votes = poll_data.get("option1", 0) + poll_data.get("option2", 0) + poll_data.get("option3", 0) + poll_data.get("option4", 0)
if total_votes > 0:
    st.markdown("**Current Results:**")
    
    option1_pct = (poll_data.get("option1", 0) / total_votes) * 100
    option2_pct = (poll_data.get("option2", 0) / total_votes) * 100
    option3_pct = (poll_data.get("option3", 0) / total_votes) * 100
    option4_pct = (poll_data.get("option4", 0) / total_votes) * 100
    
    st.progress(option1_pct / 100, text=f"🐱 Cats & Mods: {option1_pct:.1f}% ({poll_data.get('option1', 0)} votes)")
    st.progress(option2_pct / 100, text=f"🌾 Farms & Fixes: {option2_pct:.1f}% ({poll_data.get('option2', 0)} votes)")
    st.progress(option3_pct / 100, text=f"🌳 Mangroves & Alligators: {option3_pct:.1f}% ({poll_data.get('option3', 0)} votes)")
    st.progress(option4_pct / 100, text=f"🏰 Structures: {option4_pct:.1f}% ({poll_data.get('option4', 0)} votes)")
    
    st.caption(f"Total votes: {total_votes}")

# ===== BUG REPORT SYSTEM =====
st.markdown("---")
st.markdown("### 🐛 Bug Reports")

# Helper functions for bug reports
def load_bugs():
    """Load bug reports from file"""
    bugs_file = base_dir / "bugs.json"
    if bugs_file.exists():
        try:
            with open(bugs_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_bugs(bugs):
    """Save bug reports to file"""
    bugs_file = base_dir / "bugs.json"
    with open(bugs_file, 'w') as f:
        json.dump(bugs, f, indent=2)

def is_admin(username):
    """Check if user is an admin"""
    admins_file = base_dir / "admins.txt"
    if admins_file.exists():
        try:
            with open(admins_file, 'r') as f:
                admins = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('#')]
                return username in admins
        except:
            return False
    return False

# Load bugs
bugs = load_bugs()
user_is_admin = is_admin(st.session_state.username)

# Tab system for viewing and reporting
bug_tab1, bug_tab2 = st.tabs(["📋 View Reports", "➕ Report Bug"])

with bug_tab1:
    st.markdown("#### All Bug Reports")
    
    if bugs:
        # Filter options
        status_filter = st.selectbox("Filter by status:", ["All", "Open", "In Progress", "Fixed", "Closed"], key="bug_filter")
        
        # Apply filter
        filtered_bugs = bugs
        if status_filter != "All":
            filtered_bugs = [b for b in bugs if b.get("status", "Open") == status_filter]
        
        # Display bugs
        for i, bug in enumerate(filtered_bugs):
            bug_id = bug.get("id", i)
            title = bug.get("title", "Untitled Bug")
            description = bug.get("description", "No description")
            reporter = bug.get("reporter", "Anonymous")
            status = bug.get("status", "Open")
            date = bug.get("date", "Unknown")
            version = bug.get("version", "Unknown")
            
            # Color code by status
            status_colors = {
                "Open": "🔴",
                "In Progress": "🟡",
                "Fixed": "🟢",
                "Closed": "⚪"
            }
            status_icon = status_colors.get(status, "🔵")
            
            with st.expander(f"{status_icon} **#{bug_id}**: {title} - *by {reporter}*"):
                st.markdown(f"**Description:** {description}")
                st.text(f"Version: {version} | Reported: {date}")
                st.text(f"Status: {status}")
                
                # Admin controls
                if user_is_admin:
                    st.markdown("---")
                    st.markdown("**Admin Controls:**")
                    
                    admin_col1, admin_col2, admin_col3 = st.columns(3)
                    
                    with admin_col1:
                        new_status = st.selectbox(
                            "Change Status:",
                            ["Open", "In Progress", "Fixed", "Closed"],
                            index=["Open", "In Progress", "Fixed", "Closed"].index(status),
                            key=f"status_{bug_id}"
                        )
                    
                    with admin_col2:
                        if st.button("💾 Save Status", key=f"save_{bug_id}"):
                            # Find and update bug
                            for b in bugs:
                                if b.get("id") == bug_id:
                                    b["status"] = new_status
                                    b["last_updated"] = datetime.now().isoformat()
                                    b["updated_by"] = st.session_state.username
                                    break
                            save_bugs(bugs)
                            st.success(f"Bug #{bug_id} status updated to {new_status}!")
                            st.rerun()
                    
                    with admin_col3:
                        if st.button("🗑️ Delete", key=f"delete_{bug_id}"):
                            bugs = [b for b in bugs if b.get("id") != bug_id]
                            save_bugs(bugs)
                            st.success(f"Bug #{bug_id} deleted!")
                            st.rerun()
        
        st.caption(f"Showing {len(filtered_bugs)} of {len(bugs)} reports")
    else:
        st.info("📭 No bug reports yet. Be the first to report!")

with bug_tab2:
    st.markdown("#### Submit a Bug Report")
    
    bug_form_col1, bug_form_col2 = st.columns([2, 1])
    
    with bug_form_col1:
        bug_title = st.text_input("Bug Title:", placeholder="Brief description of the bug")
        bug_description = st.text_area(
            "Detailed Description:",
            placeholder="Provide steps to reproduce, what happened vs. what should happen, etc.",
            height=150
        )
    
    with bug_form_col2:
        bug_version = st.selectbox(
            "Affected Version:",
            ["Alpha v1.0 Overworld", "Alpha v1.0 End", "Alpha v1.0 Nether", 
             "Alpha 4 Overworld", "Alpha 4 End", "Alpha 4 Nether", 
             "Alpha 3", "Classic", "Indev", "Bedrock Mobile", "Other"]
        )
        bug_severity = st.selectbox(
            "Severity:",
            ["Low", "Medium", "High", "Critical"]
        )
    
    if st.button("📤 Submit Bug Report", type="primary", use_container_width=True):
        if bug_title and bug_description:
            # Generate bug ID
            bug_id = len(bugs) + 1
            
            # Create bug report
            new_bug = {
                "id": bug_id,
                "title": bug_title,
                "description": bug_description,
                "reporter": st.session_state.username,
                "version": bug_version,
                "severity": bug_severity,
                "status": "Open",
                "date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            bugs.append(new_bug)
            save_bugs(bugs)
            
            st.success(f"✅ Bug report #{bug_id} submitted successfully!")
            st.balloons()
            st.info("Thank you for helping improve PyCraft! 🎮")
            st.rerun()
        else:
            st.error("⚠️ Please fill in both the title and description fields.")

# Multiplayer options (lower priority now)
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

# Meme of the Month Section
st.markdown("---")
st.markdown("### 😂 Meme of the Month")

# Get current month and display appropriate meme
current_month = datetime.now().month
meme_files = {
    2: "meme_february.jpg",
    3: "meme_march.jpg"
}

# Default to February if month not found
meme_file = meme_files.get(current_month, "meme_february.jpg")
meme_path = base_dir / "Assets" / meme_file

if meme_path.exists():
    try:
        meme_col1, meme_col2, meme_col3 = st.columns([1, 2, 1])
        with meme_col2:
            st.image(str(meme_path), caption=f"Meme of the Month - {datetime.now().strftime('%B')}", use_container_width=True)
    except Exception as e:
        st.info("😅 Meme not available this month!")
else:
    st.info("😅 Meme not available this month!")

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
        
        # Show loading message
        with st.spinner(f"🎮 Launching {selected_version}..."):
            try:
                # Get the directory of the game file
                game_dir = str(Path(game_path).parent)
                game_file = Path(game_path).name
                
                # Use the same Python interpreter that's running this launcher
                python_exe = sys.executable
                
                # Launch the game as a subprocess
                if os.name == 'nt':  # Windows
                    # Use start command to keep window open
                    subprocess.Popen(
                        f'start cmd /k "cd /d {game_dir} && "{python_exe}" "{game_file}""',
                        shell=True
                    )
                else:  # Linux/Mac
                    subprocess.Popen(
                        [python_exe, game_path],
                        cwd=game_dir
                    )
                
                # Update play count
                accounts = load_accounts()
                if st.session_state.username in accounts:
                    accounts[st.session_state.username]["play_count"] = accounts[st.session_state.username].get("play_count", 0) + 1
                    save_accounts(accounts)
                
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
    '<p style="text-align: center; color: #999; font-size: 0.9rem;">PyCraft Launcher v2.0 | Account System & Realms</p>',
    unsafe_allow_html=True
)
