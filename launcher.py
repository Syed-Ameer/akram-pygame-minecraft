import streamlit as st
import subprocess
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

# Initialize file paths
ACCOUNTS_FILE = base_dir / "accounts.json"
REALMS_FILE = base_dir / "realms.json"
BUGS_FILE = base_dir / "bugs.json"
POLL_FILE = base_dir / "feature_poll.json"

def load_accounts():
    """Load saved accounts"""
    if ACCOUNTS_FILE.exists():
        with open(ACCOUNTS_FILE, 'r') as f:
            return json.load(f)
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

def load_poll():
    """Load feature poll data"""
    if POLL_FILE.exists():
        with open(POLL_FILE, 'r') as f:
            return json.load(f)
    return {"option1": 0, "option2": 0, "option3": 0, "option4": 0, "voters": []}

def save_poll(poll_data):
    """Save poll data"""
    with open(POLL_FILE, 'w') as f:
        json.dump(poll_data, f, indent=2)

def load_bugs():
    """Load bug reports"""
    if BUGS_FILE.exists():
        with open(BUGS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_bugs(bugs):
    """Save bug reports"""
    with open(BUGS_FILE, 'w') as f:
        json.dump(bugs, f, indent=2)

def load_realms():
    """Load saved realms"""
    if REALMS_FILE.exists():
        with open(REALMS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_realms(realms):
    """Save realms"""
    with open(REALMS_FILE, 'w') as f:
        json.dump(realms, f, indent=2)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_realm_selector' not in st.session_state:
    st.session_state.show_realm_selector = False

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
        new_username = st.text_input("Username:", placeholder="Enter your username (e.g., AkramSyed2014!)")
        
        if st.button("✅ Create Account", type="primary", use_container_width=True):
            if new_username:
                if len(new_username) < 3:
                    st.error("Username must be at least 3 characters!")
                elif new_username in load_accounts():
                    st.error("Username already exists!")
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
    if load_accounts():
        st.markdown("---")
        st.markdown("### 👥 Existing Accounts")
        accounts = load_accounts()
        for username, data in accounts.items():
            last_login = data.get('last_login', 'Never')
            if last_login != 'Never':
                last_login = datetime.fromisoformat(last_login).strftime("%Y-%m-%d %H:%M")
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
        created = datetime.fromisoformat(account_data.get('created', datetime.now().isoformat()))
        st.text(f"Member since: {created.strftime('%Y-%m-%d')}")
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    st.text(f"👤 Playing as: {st.session_state.username}")
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

# Multiplayer button
st.markdown("###, mp_col3 = st.columns(3)")

with mp_col1:
    start_server_button = st.button(
        "🖥️ Start Server",
        use_container_width=True
    )

with mp_col2:
    join_server_button = st.button(
        "🌍 Direct Connect",
        use_container_width=True
    )

with mp_col3:
  Realms System
if realm_button or st.session_state.show_realm_selector:
    st.session_state.show_realm_selector = True
    st.markdown("---")
    st.markdown("### 🏰 PyCraft Realms")
    
    realm_tab1, realm_tab2, realm_tab3 = st.tabs(["🌍 My Realms", "➕ Join Realm", "📖 Realm List"])
    
    saved_realms = load_realms()
    
    with realm_tab1:
        st.markdown("#### Your Saved Realms")
        if saved_realms:
            realm_to_delete = None
            for realm_name, realm_data in saved_realms.items():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**🏰 {realm_name}**")
                    st.text(f"📍 {realm_data['ip']}:{realm_data['port']}")
                with col2:
                    if st.button(f"🎮 Connect", key=f"connect_{realm_name}"):
                        # Connect to this realm
                        if selected_version in version_ including username
                    if os.name == 'nt':  # Windows
                        subprocess.Popen(
                            f'start cmd /k "cd /d {game_dir} && python "{game_file}" --multiplayer {server_ip} {server_port} --username {st.session_state.username}"',
                            shell=True
                        )
                    else:  # Linux/Mac
                        subprocess.Popen(
                            ["python", game_path, "--multiplayer", server_ip, str(server_port), "--username", st.session_state.username],
                            cwd=game_dir
                        )
                    
                    # Update play count
                    accounts = load_accounts()
                    if st.session_state.username in accounts:
                        accounts[st.session_state.username]["play_count"] = accounts[st.session_state.username].get("play_count", 0) + 1
                        save_accounts(accounts)
                    
                    st.success(f"✅ Connecting to server as {st.session_state.username}
                                        subprocess.Popen(
                                            ["python", game_path, "--multiplayer", realm_data["ip"], str(realm_data["port"]), "--username", st.session_state.username],
                                            cwd=game_dir
                                        )
                                    
                                    # Update play count
                                    accounts = load_accounts()
                                    if st.session_state.username in accounts:
                                        accounts[st.session_state.username]["play_count"] = accounts[st.session_state.username].get("play_count", 0) + 1
                                        save_accounts(accounts)
                                    
                                    st.success(f"✅ Connecting to {realm_name}...")
                                    st.balloons()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                with col3:
                    if st.button("🗑️", key=f"del_{realm_name}"):
                        realm_to_delete = realm_name
                
                st.markdown("---")
            
            if realm_to_delete:
                del saved_realms[realm_to_delete]
                save_realms(saved_realms)
                st.rerun()
        else:
            st.info("No saved realms. Add one in the 'Join Realm' tab!")
    
    with realm_tab2:
        st.markdown("#### Add New Realm")
        realm_name_input = st.text_input("Realm Name:", placeholder="e.g., My Awesome Server")
        realm_ip_input = st.text_input("Server IP Address:", value="localhost", placeholder="e.g., 192.168.1.100")
        realm_port_input = st.number_input("Port:", min_value=1024, max_value=65535, value=5555)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save & Connect", type="primary", use_container_width=True):
                if realm_name_input:
                    # Save realm
                    saved_realms[realm_name_input] = {
                        "ip": realm_ip_input,
                        "port": realm_port_input,
                        "added_by": st.session_state.username,
                        "added_date": datetime.now().isoformat()
                    }
                    save_realms(saved_realms)
                    
                    # Connect
                    if selected_version in version_map:
                        game_path = version_map[selected_version]
                        game_dir = str(Path(game_path).parent)
                        game_file = Path(game_path).name
                        
                        try:
                            if os.name == 'nt':
                                subprocess.Popen(
                                    f'start cmd /k "cd /d {game_dir} && python "{game_file}" --multiplayer {realm_ip_input} {realm_port_input} --username {st.session_state.username}"',
                                    shell=True
                                )
                            else:
                                subprocess.Popen(
                                    ["python", game_path, "--multiplayer", realm_ip_input, str(realm_port_input), "--username", st.session_state.username],
                                    cwd=game_dir
                                )
                            
                            # Update play count
                            accounts = load_accounts()
                            if st.session_state.username in accounts:
                                accounts[st.session_state.username]["play_count"] = accounts[st.session_state.username].get("play_count", 0) + 1
                                save_accounts(accounts)
                            
                            st.success(f"✅ Realm saved and connecting!")
                            st.balloons()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("Please enter a realm name!")
        
        with col2:
            if st.button("🌐 Connect Only", use_container_width=True):
                if selected_version in version_map:
                    game_path = version_map[selected_version]
                    game_dir = str(Path(game_path).parent)
                    game_file = Path(game_path).name
                    
                    try:
                        if os.name == 'nt':
                            subprocess.Popen(
                                f'start cmd /k "cd /d {game_dir} && python "{game_file}" --multiplayer {realm_ip_input} {realm_port_input} --username {st.session_state.username}"',
                                shell=True
                            )
                        else:
                            subprocess.Popen(
                                ["python", game_path, "--multiplayer", realm_ip_input, str(realm_port_input), "--username", st.session_state.username],
                                cwd=game_dir
                            )
                        
                        # Update play count
                        accounts = load_accounts()
                        if st.session_state.username in accounts:
                            accounts[st.session_state.username]["play_count"] = accounts[st.session_state.username].get("play_count", 0) + 1
                            save_accounts(accounts)
                        
                        st.success(f"✅ Connecting...")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with realm_tab3:
        st.markdown("#### 📋 All Available Realms")
        if saved_realms:
            for realm_name, realm_data in saved_realms.items():
                with st.expander(f"🏰 {realm_name}"):
                    st.text(f"IP: {realm_data['ip']}")
                    st.text(f"Port: {realm_data['port']}")
                    st.text(f"Added by: {realm_data.get('added_by', 'Unknown')}")
                    added_date = realm_data.get('added_date', '')
                    if added_date:
                        date_str = datetime.fromisoformat(added_date).strftime("%Y-%m-%d %H:%M")
                        st.text(f"Added: {date_str}")
        else:
            st.info("No realms available yet!")
    
    if st.button("⬅️ Back to Main Menu"):
        st.session_state.show_realm_selector = False
        st.rerun()
    
    st.stop()

# ===== VOTING SYSTEM =====
st.markdown("---")
st.markdown("### 🗳️ Vote for Next Feature!")

poll_data = load_poll()

# Check if user has voted
has_voted = st.session_state.username in poll_data.get("voters", [])

if not has_voted:
    st.markdown("**What should we add next?**")
    vote_option = st.radio(
        "Select your choice:",
        ["🐉 More Mobs & Animals", "🏗️ New Building Blocks", "⚔️ Better Combat & Weapons", "🌍 New Biomes & Dimensions"],
        label_visibility="collapsed"
    )
    
    if st.button("✅ Submit Vote", type="primary"):
        # Map display text to option keys
        vote_map = {
            "🐉 More Mobs & Animals": "option1",
            "🏗️ New Building Blocks": "option2",
            "⚔️ Better Combat & Weapons": "option3",
            "🌍 New Biomes & Dimensions": "option4"
        }
        
        option_key = vote_map[vote_option]
        poll_data[option_key] = poll_data.get(option_key, 0) + 1
        
        if "voters" not in poll_data:
            poll_data["voters"] = []
        poll_data["voters"].append(st.session_state.username)
        
        save_poll(poll_data)
        st.success("✅ Thanks for voting!")
        st.balloons()
        st.rerun()
else:
    st.success("✅ You've already voted! Thank you!")

# Show results
st.markdown("#### 📊 Current Results")
total_votes = poll_data.get("option1", 0) + poll_data.get("option2", 0) + poll_data.get("option3", 0) + poll_data.get("option4", 0)

if total_votes > 0:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🐉 More Mobs", poll_data.get("option1", 0))
        st.metric("⚔️ Better Combat", poll_data.get("option3", 0))
    with col2:
        st.metric("🏗️ New Blocks", poll_data.get("option2", 0))
        st.metric("🌍 New Biomes", poll_data.get("option4", 0))
    
    st.caption(f"Total votes: {total_votes}")
else:
    st.info("No votes yet. Be the first to vote!")

# ===== MEME OF THE MONTH =====
st.markdown("---")
st.markdown("### 😂 Meme of the Month")

meme_path = base_dir / "Assets" / "meme_of_month.png"
if meme_path.exists():
    try:
        st.image(str(meme_path), use_column_width=True, caption="Community Meme of the Month! 🎉")
    except:
        st.info("📸 Meme image found but couldn't be displayed.")
else:
    st.info("📸 No meme this month! Check back later.")
    st.caption("💡 Admins can add memes to Assets/meme_of_month.png")

# ===== BUG REPORTS =====
st.markdown("---")
st.markdown("### 🐛 Report a Bug")

with st.expander("📝 Submit Bug Report"):
    bug_title = st.text_input("Bug Title:", placeholder="e.g., Game crashes when opening chest")
    bug_description = st.text_area("Description:", placeholder="Describe the bug in detail...")
    
    if st.button("📤 Submit Bug Report", type="primary"):
        if bug_title and bug_description:
            bugs = load_bugs()
            bug_report = {
                "id": len(bugs) + 1,
                "title": bug_title,
                "description": bug_description,
                "version": selected_version,
                "reported_by": st.session_state.username,
                "date": datetime.now().isoformat(),
                "status": "Open"
            }
            bugs.append(bug_report)
            save_bugs(bugs)
            st.success("✅ Bug report submitted! Thank you!")
            st.balloons()
        else:
            st.error("Please fill in all fields!")

# Show recent bugs
bugs = load_bugs()
if bugs:
    st.markdown("#### 📋 Recent Bug Reports")
    recent_bugs = sorted(bugs, key=lambda x: x.get('date', ''), reverse=True)[:3]
    
    for bug in recent_bugs:
        status_emoji = "🟢" if bug.get('status') == 'Fixed' else "🔴"
        with st.expander(f"{status_emoji} {bug.get('title', 'Untitled')} - by {bug.get('reported_by', 'Unknown')}"):
            st.text(f"Version: {bug.get('version', 'Unknown')}")
            st.text(f"Status: {bug.get('status', 'Open')}")
            try:
                date_str = datetime.fromisoformat(bug.get('date', '')).strftime("%Y-%m-%d %H:%M")
                st.text(f"Reported: {date_str}")
            except:
                pass
            st.markdown(f"**Description:** {bug.get('description', 'No description')}")

# ===== MULTIPLAYER SECTION =====
st.markdown("---")
st.markdown("### 🌐 Multiplayer")

mp_col1, mp_col2 = st.columns(2)

with mp_col1:
    start_server_button = st.button(
        "🖥️ Start Server",
        use_container_width=True
    )

with mp_col2:
    join_server_button = st.button(
        "🌍 Join Server",
        use_container_width=True
    )

# Server IP input (shown if joining)
if join_server_button:
    st.markdown("#### 🔗 Enter Server Details")
    server_ip = st.text_input("Server IP Address", value="localhost", placeholder="e.g., 192.168.1.100 or localhost")
    server_port = st.number_input("Port", min_value=1024, max_value=65535, value=5555)
    
    join_confirm = st.button("✅ Connect to Server", type="primary")
    
    if join_confirm:
        # Store server info and launch with multiplayer enabled
        st.session_state['multiplayer_mode'] = True
        st.session_state['server_ip'] = server_ip
        st.session_state['server_port'] = server_port
        
        if selected_version in version_map:
            game_path = version_map[selected_version]
            
            with st.spinner(f"🌐 Connecting to {server_ip}:{server_port}..."):
                try:
                    game_dir = str(Path(game_path).parent)
                    game_file = Path(game_path).name
                    
                    # Launch with multiplayer arguments
                    if os.name == 'nt':  # Windows
                        subprocess.Popen(
                            f'start cmd /k "cd /d {game_dir} && python "{game_file}" --multiplayer {server_ip} {server_port}"',
                            shell=True
                        )
                    else:  # Linux/Mac
                        subprocess.Popen(
                            ["python", game_path, "--multiplayer", server_ip, str(server_port)],
                            cwd=game_dir
                        )
                    
                    st.success(f"✅ Connecting to server...")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Handle server start
if start_server_button:
    server_path = base_dir / "Alpha" / "multiplayer_server.py"
    
    if server_path.exists():
        with st.spinner("🖥️ Starting multiplayer server..."):
            try:
                server_dir = str(server_path.parent)
                
                if os.name == 'nt':  # Windows
                    subprocess.Popen(
                        f'start cmd /k "cd /d {server_dir} && python multiplayer_server.py"',
                        shell=True
                    )
                else:
                    subprocess.Popen(
                        ["python", str(server_path)],
                        cwd=server_dir
                    )
                
                st.success("✅ Server started! Players can now connect to your IP address on port 5555")
                st.info("💡 Share your IP address with friends so they can join.")
                st.code("Your local IP: Check your network settings")
            except Exception as e:
                st.error(f"❌ Error starting server: {str(e)}")
    else:
        st.error("❌ Multiplayer server file not found!")

# Handle launch
if launch_button:
    if selected_version in version_map:
        game_path = version_map[selected_version]
        
        # Show loading message
        with st.spinner(f"🎮 Launching {selected_versiousername
                if os.name == 'nt':  # Windows
                    # Use start command to keep window open
                    subprocess.Popen(
                        f'start cmd /k "cd /d {game_dir} && python "{game_file}" --username {st.session_state.username}"',
                        shell=True
                    )
                else:  # Linux/Mac
                    subprocess.Popen(
                        ["python", game_path, "--username", st.session_state.username],
                        cwd=game_dir
                    )
                
                # Update play count
                accounts = load_accounts()
                if st.session_state.username in accounts:
                    accounts[st.session_state.username]["play_count"] = accounts[st.session_state.username].get("play_count", 0) + 1
                    save_accounts(accounts)
                
                st.success(f"✅ {selected_version} launched successfully as {st.session_state.username}
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
