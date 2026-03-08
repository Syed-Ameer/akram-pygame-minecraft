"""
Universal Game Display for Streamlit
Works GLOBALLY on ALL platforms and environments

Environment detection:
  - LOCAL (Windows/Mac): Popen -> opens game in native window
  - DEPLOYED (Replit/Streamlit Cloud): VNC viewer or browser embed
  - ANY BROWSER USER: Pygbag WebAssembly game embed (always available)

Usage:
    from game_display import GameDisplay
    display = GameDisplay()
    display.launch_and_show(game_path, game_name)
"""
import streamlit as st
import streamlit.components.v1 as components
import subprocess
import sys
import os
import platform
import time
import json
import base64
from pathlib import Path

IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'
IS_MAC = platform.system() == 'Darwin'

# Pygbag browser URLs for each game version
BROWSER_GAME_URLS = {
    "default": "https://syed-ameer.github.io/akram-pygame-minecraft/",
    # Add more version-specific URLs here as they get deployed:
    # "Alpha v1.0": "https://syed-ameer.github.io/pycraft-alpha1/",
    # "Classic 5": "https://syed-ameer.github.io/pycraft-classic5/",
}


def is_deployed():
    """Detect if running in a cloud/deployed environment (not local)"""
    indicators = [
        os.environ.get('REPL_ID'),           # Replit
        os.environ.get('REPL_SLUG'),         # Replit
        os.environ.get('REPLIT'),            # Replit
        os.environ.get('STREAMLIT_SHARING_MODE'),  # Streamlit Cloud
        os.environ.get('RENDER'),            # Render.com
        os.environ.get('DYNO'),             # Heroku
        os.environ.get('RAILWAY_ENVIRONMENT'),  # Railway
        os.environ.get('CODESPACE_NAME'),    # GitHub Codespaces
    ]
    return any(indicators)


def is_local():
    """Detect if running on a local machine (developer's PC)"""
    return not is_deployed()


class GameDisplay:
    """Universal game display that works on any platform, locally or deployed"""
    
    def __init__(self, platform_override=None):
        self.process = None
        self.display = None
        self.deployed = is_deployed()
        self.local = is_local()

        # Allow the UI to override auto-detected platform
        # platform_override: 'windows', 'mac', 'linux', or None (auto)
        _plat = (platform_override or '').lower()
        if _plat == 'windows':
            self._win, self._linux, self._mac = True, False, False
        elif _plat in ('mac', 'darwin'):
            self._win, self._linux, self._mac = False, False, True
        elif _plat == 'linux':
            self._win, self._linux, self._mac = False, True, False
        else:
            self._win  = IS_WINDOWS
            self._linux = IS_LINUX
            self._mac  = IS_MAC
    
    def launch_and_show(self, game_path, game_name="Game", version_key=None, force_vnc=False):
        """
        Launch game and display it - works globally.
        
        force_vnc=False (default): Opens native window on local, VNC/browser on deployed
        force_vnc=True: Always uses VNC/browser streaming mode
        
        Local: Opens native window via Popen
        Deployed/VNC: VNC viewer OR browser embed (playable by anyone worldwide)
        """
        game_path = str(game_path)
        
        if force_vnc:
            if self._linux or self.deployed:
                # VNC is possible on Linux / cloud-deployed environments
                st.info("📡 **VNC Mode**: Streaming game to your browser...")
                return self._launch_deployed(game_path, game_name, version_key)
            else:
                # Windows / Mac — use screen-capture streaming
                st.info("📡 **Stream Mode**: Capturing game window to your browser...")
                return self._try_screen_stream(game_path, game_name)
        
        if self.local:
            # LOCAL (any OS): Native window
            return self._launch_local_popen(game_path, game_name)
        elif self._linux or self.deployed:
            # DEPLOYED or LINUX: Try VNC, then browser embed
            return self._launch_deployed(game_path, game_name, version_key)
        else:
            return self._launch_browser(game_name, version_key)
    
    def _launch_local_popen(self, game_path, game_name):
        """LOCAL: Launch game in native window with Popen"""
        st.info(f"🪟 **Local Mode**: Launching {game_name} in new window...")
        
        try:
            game_dir = str(Path(game_path).parent.resolve())
            game_file = Path(game_path).name
            python_exe = sys.executable
            
            if self._win:
                # Windows: os.startfile() on a .bat fully detaches from Streamlit's process.
                # Popen (even with CREATE_NEW_CONSOLE) stays attached and may be blocked.
                import tempfile, textwrap
                bat_content = textwrap.dedent(f"""\
                    @echo off
                    cd /d "{game_dir}"
                    "{python_exe}" "{game_file}"
                    pause
                """)
                bat = tempfile.NamedTemporaryFile(
                    mode='w', suffix='.bat', delete=False, dir=game_dir
                )
                bat.write(bat_content)
                bat.close()
                os.startfile(bat.name)
            elif self._mac:
                # Mac: detach from Streamlit via open command (opens in Terminal.app)
                script = f'tell application "Terminal" to do script "cd {repr(game_dir)} && {repr(python_exe)} {repr(game_file)}"'
                try:
                    subprocess.Popen(
                        ['osascript', '-e', script],
                        start_new_session=True,
                    )
                except Exception:
                    # Fallback: plain Popen detached
                    self.process = subprocess.Popen(
                        [python_exe, game_file],
                        cwd=game_dir,
                        start_new_session=True,
                    )
            else:
                # Linux local
                self.process = subprocess.Popen(
                    [python_exe, game_file],
                    cwd=game_dir,
                    start_new_session=True,
                )
            
            st.success(f"✅ {game_name} launched successfully!")
            st.balloons()
            
            # Show game info card
            self._show_game_card(game_name, "local")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Failed to launch locally: {e}")
            st.info("🌐 Falling back to browser version...")
            return self._launch_browser(game_name)
    
    def _launch_deployed(self, game_path, game_name, version_key=None):
        """DEPLOYED: Try VNC first, fall back to browser embed"""
        
        # 1) Try VNC virtual display (Replit with xvfb)
        vnc_success = self._try_vnc(game_path, game_name)
        if vnc_success:
            return True
        
        # 2) VNC failed — try launching headless + show status
        st.warning("⚠️ VNC display not available — the game needs a graphical display.")
        
        # Attempt to run the game headless anyway (it may still work via SDL_VIDEODRIVER=dummy)
        try:
            game_dir = str(Path(game_path).parent.resolve())
            game_file = Path(game_path).name
            env = {**os.environ, 'SDL_VIDEODRIVER': 'dummy', 'SDL_AUDIODRIVER': 'dummy'}
            self.process = subprocess.Popen(
                [sys.executable, game_file],
                cwd=game_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            time.sleep(1)
            if self.process.poll() is None:
                st.info("🖥️ Game process started (headless). VNC viewer would connect here on a full Linux server.")
        except Exception:
            pass
        
        # 3) Show browser embed as last resort
        st.info("🌐 **Cloud Mode**: Loading browser-playable version...")
        return self._launch_browser(game_name, version_key)
    
    def _try_screen_stream(self, game_path, game_name):
        """Windows/Mac: Launch game natively + capture window via MJPEG stream."""
        try:
            from windows_vnc import WindowsScreenStream, find_pygame_window
        except ImportError as e:
            st.warning(f"Screen streaming not available: {e}")
            st.info("Falling back to native window...")
            return self._launch_local_popen(game_path, game_name)

        if not WindowsScreenStream.is_available():
            st.warning("Screen capture dependencies (mss, Pillow) not available.")
            st.info("Falling back to native window...")
            return self._launch_local_popen(game_path, game_name)

        # 1) Launch game natively (detached from Streamlit)
        game_dir = str(Path(game_path).parent.resolve())
        game_file = Path(game_path).name
        python_exe = sys.executable
        launched_ok = False
        try:
            if self._win:
                # Windows: bat + os.startfile() to fully detach from Streamlit
                import tempfile, textwrap
                bat_content = textwrap.dedent(f"""\
                    @echo off
                    cd /d "{game_dir}"
                    "{python_exe}" "{game_file}"
                    pause
                """)
                bat = tempfile.NamedTemporaryFile(
                    mode='w', suffix='.bat', delete=False, dir=game_dir
                )
                bat.write(bat_content)
                bat.close()
                os.startfile(bat.name)
                launched_ok = True
                self.process = None  # no handle when using startfile
            elif self._mac:
                # Mac: detach via start_new_session
                self.process = subprocess.Popen(
                    [python_exe, game_file],
                    cwd=game_dir,
                    start_new_session=True,
                )
                launched_ok = True
            else:
                self.process = subprocess.Popen(
                    [python_exe, game_file],
                    cwd=game_dir,
                    start_new_session=True,
                )
                launched_ok = True
        except Exception as e:
            st.error(f"Failed to launch game: {e}")
            return False

        # 2) Wait for the game window to appear
        with st.spinner("Waiting for game window to appear..."):
            region = None
            for _ in range(25):  # up to ~5 seconds
                time.sleep(0.2)
                # Only poll if we have a process handle
                if self.process is not None and self.process.poll() is not None:
                    st.error("Game exited before window appeared.")
                    return False
                region = find_pygame_window("pycraft", "pygame", "minecraft")
                if region:
                    break

        # 3) Start MJPEG capture server
        stream = WindowsScreenStream(fps=15, quality=60)
        port = stream.start(capture_region=region)
        if port is None:
            st.warning("Could not start capture server.")
            st.info("Game is running in a native window — check your taskbar.")
            self._show_game_card(game_name, "local")
            return True

        # Store so we can stop later
        if 'screen_stream' not in st.session_state:
            st.session_state['screen_stream'] = stream

        st.success(f"✅ {game_name} is streaming to your browser!")
        st.balloons()

        # 4) Show the MJPEG viewer
        self._show_stream_viewer(game_name, port)
        self._show_game_card(game_name, "vnc")
        return True

    def _try_vnc(self, game_path, game_name):
        """Try to launch with VNC virtual display (Linux only)"""
        if not self._linux:
            return False
        
        try:
            from virtual_display import VirtualDisplay
        except ImportError:
            return False
        
        try:
            display = VirtualDisplay(width=800, height=600)
            if display.start():
                self.display = display
                self.process = subprocess.Popen(
                    [sys.executable, str(game_path)],
                    env={**os.environ, 'DISPLAY': display.display}
                )
                
                st.success(f"✅ {game_name} is running via VNC!")
                st.balloons()
                
                # Show VNC viewer (streams game to browser)
                self._show_vnc_viewer(game_name)
                return True
        except Exception as e:
            st.warning(f"VNC not available: {e}")
        
        return False
    
    def _launch_browser(self, game_name, version_key=None):
        """UNIVERSAL: Browser-playable version (works for anyone, anywhere)"""
        url = BROWSER_GAME_URLS.get(version_key, BROWSER_GAME_URLS["default"])
        
        # Styled browser game embed
        st.markdown("### 🌐 Play in Browser")
        st.caption(f"Playing: **{game_name}** — works on any device, any browser, anywhere!")
        
        # Environment badge
        env_name = "Cloud" if self.deployed else "Local"
        env_icon = "☁️" if self.deployed else "🏠"
        
        components.html(f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #e9456033;
            border-radius: 12px 12px 0 0;
            padding: 14px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 22px;">🎮</span>
                <div>
                    <h3 style="margin: 0; color: #fff; font-size: 15px;">{game_name}</h3>
                    <p style="margin: 2px 0 0 0; color: #888; font-size: 12px;">Pygame WebAssembly • Runs in browser</p>
                </div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <span style="
                    background: #28a74522;
                    color: #28a745;
                    padding: 3px 10px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: 600;
                ">● LIVE</span>
                <span style="
                    background: #0078d422;
                    color: #60a5fa;
                    padding: 3px 10px;
                    border-radius: 12px;
                    font-size: 11px;
                ">{env_icon} {env_name}</span>
            </div>
        </div>
        """, height=65)
        
        # Embed the actual game
        st.components.v1.iframe(url, height=700, scrolling=False)
        
        # Controls reminder
        components.html("""
        <div style="
            background: #16213e;
            border: 1px solid #e9456033;
            border-top: none;
            border-radius: 0 0 12px 12px;
            padding: 10px 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <p style="margin: 0; color: #888; font-size: 12px;">
                <strong style="color: #aaa;">Controls:</strong> 
                WASD/Arrows = Move &nbsp;|&nbsp; Left Click = Break &nbsp;|&nbsp; Right Click = Place &nbsp;|&nbsp; ESC = Pause &nbsp;|&nbsp; 1-9 = Hotbar
            </p>
        </div>
        """, height=45)
        
        return True
    
    def _show_game_card(self, game_name, mode):
        """Show an interactive game info card"""
        mode_info = {
            "local": {
                "icon": "🪟",
                "status": "Running in native window",
                "tip": "Check your taskbar for the game window!",
                "color": "#0078d4"
            },
            "vnc": {
                "icon": "🌐",
                "status": "Streaming via VNC",
                "tip": "Game is displayed below via VNC viewer",
                "color": "#28a745"
            },
            "browser": {
                "icon": "🌍",
                "status": "Running in browser (WebAssembly)",
                "tip": "Playing directly in your browser — works anywhere!",
                "color": "#e94560"
            }
        }
        
        info = mode_info.get(mode, mode_info["local"])
        
        env_label = "Cloud ☁️" if self.deployed else "Local 🏠"
        
        components.html(f"""
        <div style="
            background: linear-gradient(135deg, {info['color']}22 0%, {info['color']}11 100%);
            border: 1px solid {info['color']}44;
            border-radius: 12px;
            padding: 24px;
            margin: 16px 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
                <span style="font-size: 32px;">{info['icon']}</span>
                <div>
                    <h3 style="margin: 0; color: #fff; font-size: 18px;">🎮 {game_name}</h3>
                    <p style="margin: 4px 0 0 0; color: #aaa; font-size: 14px;">{info['status']}</p>
                </div>
                <span style="
                    margin-left: auto;
                    background: #28a74533;
                    color: #28a745;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                ">● RUNNING</span>
            </div>
            
            <div style="
                background: rgba(0,0,0,0.2);
                border-radius: 8px;
                padding: 12px 16px;
                margin-top: 12px;
            ">
                <p style="margin: 0; color: #ccc; font-size: 14px;">
                    💡 {info['tip']}
                </p>
            </div>
            
            <div style="margin-top: 16px; display: flex; gap: 16px; flex-wrap: wrap;">
                <div style="color: #888; font-size: 12px;">
                    📋 Platform: <strong style="color: #fff;">{platform.system()}</strong>
                </div>
                <div style="color: #888; font-size: 12px;">
                    🔧 Mode: <strong style="color: #fff;">{mode.title()}</strong>
                </div>
                <div style="color: #888; font-size: 12px;">
                    🌐 Env: <strong style="color: #fff;">{env_label}</strong>
                </div>
                <div style="color: #888; font-size: 12px;">
                    🐍 Python: <strong style="color: #fff;">{platform.python_version()}</strong>
                </div>
            </div>
            
            <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.1);">
                <p style="margin: 0; color: #999; font-size: 13px;">
                    <strong>Controls:</strong> WASD/Arrows = Move  |  Left Click = Break  |  Right Click = Place  |  ESC = Pause  |  1-9 = Hotbar
                </p>
            </div>
        </div>
        """, height=260)
    
    def _show_vnc_viewer(self, game_name, host='localhost', port=6080, height=600):
        """Show embedded VNC viewer"""
        vnc_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ background: #1a1a2e; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                
                .header {{
                    background: linear-gradient(90deg, #0f3460, #16213e);
                    padding: 12px 20px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    border-bottom: 2px solid #e94560;
                }}
                .header h3 {{
                    color: #fff;
                    font-size: 16px;
                }}
                .status {{
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    color: #aaa;
                    font-size: 13px;
                }}
                .status-dot {{
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #ffa500;
                    animation: pulse 1.5s infinite;
                }}
                .status-dot.connected {{
                    background: #28a745;
                    animation: none;
                }}
                .status-dot.error {{
                    background: #dc3545;
                    animation: none;
                }}
                
                @keyframes pulse {{
                    0%, 100% {{ opacity: 1; }}
                    50% {{ opacity: 0.3; }}
                }}
                
                #vnc-container {{
                    width: 100%;
                    height: calc(100vh - 50px);
                    background: #0a0a0a;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                .connecting-msg {{
                    text-align: center;
                    color: #aaa;
                }}
                .connecting-msg h4 {{
                    font-size: 18px;
                    margin-bottom: 8px;
                    color: #fff;
                }}
                .connecting-msg p {{
                    font-size: 14px;
                }}
                
                .progress-bar {{
                    width: 300px;
                    height: 4px;
                    background: #333;
                    border-radius: 2px;
                    margin: 16px auto;
                    overflow: hidden;
                }}
                .progress-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #e94560, #0f3460);
                    border-radius: 2px;
                    width: 0%;
                    transition: width 0.5s ease;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h3>🎮 {game_name}</h3>
                <div class="status">
                    <div class="status-dot" id="statusDot"></div>
                    <span id="statusText">Connecting...</span>
                </div>
            </div>
            
            <div id="vnc-container">
                <div class="connecting-msg" id="connectMsg">
                    <h4>🔌 Connecting to Game Display</h4>
                    <p>Setting up VNC connection to {host}:{port}</p>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <p id="progressText" style="font-size: 12px; margin-top: 8px;">Loading VNC library...</p>
                </div>
            </div>
            
            <script type="module">
                const container = document.getElementById('vnc-container');
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');
                const connectMsg = document.getElementById('connectMsg');
                
                function setProgress(pct, text) {{
                    progressFill.style.width = pct + '%';
                    if (text) progressText.textContent = text;
                }}
                
                // Try loading noVNC from CDN
                const cdnUrls = [
                    'https://unpkg.com/@nicedoc/novnc@1.3.0/lib/rfb.js',
                    'https://cdn.jsdelivr.net/npm/@nicedoc/novnc@1.3.0/lib/rfb.js'
                ];
                
                setProgress(20, 'Loading noVNC library...');
                
                let RFB = null;
                for (const url of cdnUrls) {{
                    try {{
                        const module = await import(url);
                        RFB = module.default;
                        break;
                    }} catch (e) {{
                        console.warn('Failed to load from:', url);
                    }}
                }}
                
                if (!RFB) {{
                    setProgress(100, 'Could not load VNC library - using fallback display');
                    statusDot.classList.add('error');
                    statusText.textContent = 'VNC library unavailable';
                    connectMsg.innerHTML = `
                        <h4>⚠️ VNC Library Not Available</h4>
                        <p style="color: #aaa;">The game is running but VNC display could not connect.</p>
                        <p style="color: #888; font-size: 12px; margin-top: 12px;">
                            The game window is open on the server.<br>
                            If deployed on Replit, check the Output tab.
                        </p>
                    `;
                }} else {{
                    setProgress(50, 'Connecting to game display...');
                    
                    try {{
                        connectMsg.style.display = 'none';
                        
                        const rfb = new RFB(container, `ws://{host}:{port}/websockify`);
                        rfb.scaleViewport = true;
                        rfb.resizeSession = false;
                        rfb.focusOnClick = true;
                        
                        rfb.addEventListener('connect', () => {{
                            setProgress(100, 'Connected!');
                            statusDot.classList.add('connected');
                            statusText.textContent = 'Connected';
                        }});
                        
                        rfb.addEventListener('disconnect', (e) => {{
                            statusDot.classList.remove('connected');
                            statusDot.classList.add('error');
                            statusText.textContent = e.detail.clean ? 'Disconnected' : 'Connection lost';
                        }});
                        
                        rfb.addEventListener('securityfailure', () => {{
                            statusDot.classList.add('error');
                            statusText.textContent = 'Auth failed';
                        }});
                        
                    }} catch (e) {{
                        statusDot.classList.add('error');
                        statusText.textContent = 'Connection failed';
                        connectMsg.style.display = 'block';
                        connectMsg.innerHTML = `
                            <h4>❌ Connection Failed</h4>
                            <p style="color: #aaa;">${{e.message}}</p>
                        `;
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
        components.html(vnc_html, height=height + 50)

    def _show_stream_viewer(self, game_name, port, height=620):
        """Embed MJPEG stream from WindowsScreenStream in Streamlit."""
        stream_url = f"http://localhost:{port}/stream"
        snapshot_url = f"http://localhost:{port}/snapshot"

        viewer_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ background: #0a0a0a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                .header {{
                    background: linear-gradient(90deg, #0f3460, #16213e);
                    padding: 10px 20px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    border-bottom: 2px solid #e94560;
                }}
                .header h3 {{ color: #fff; font-size: 15px; }}
                .badge {{
                    background: #28a74522; color: #28a745;
                    padding: 3px 10px; border-radius: 12px;
                    font-size: 11px; font-weight: 600;
                }}
                .badge.error {{ background: #dc354522; color: #dc3545; }}
                #game-frame {{
                    width: 100%; height: calc(100vh - 90px);
                    display: block; object-fit: contain;
                    background: #111;
                }}
                .controls {{
                    background: #16213e; padding: 8px 20px;
                    border-top: 1px solid #e9456033;
                }}
                .controls p {{ margin: 0; color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h3>🎮 {game_name} — Live Stream</h3>
                <span class="badge" id="statusBadge">● CONNECTING</span>
            </div>
            <img id="game-frame" />
            <div class="controls">
                <p><strong style="color:#aaa">Controls:</strong>
                   WASD = Move | Mouse = Look | LMB = Break | RMB = Place | 1-9 = Hotbar | ESC = Pause</p>
            </div>
            <script>
                const img = document.getElementById('game-frame');
                const badge = document.getElementById('statusBadge');
                let connected = false;

                // Use the MJPEG stream — most browsers render this natively
                img.src = "{stream_url}";

                img.onload = function() {{
                    if (!connected) {{
                        connected = true;
                        badge.textContent = '● LIVE';
                        badge.className = 'badge';
                    }}
                }};

                img.onerror = function() {{
                    if (!connected) {{
                        badge.textContent = '● OFFLINE';
                        badge.className = 'badge error';
                        // Retry after 2s
                        setTimeout(() => {{ img.src = "{stream_url}?t=" + Date.now(); }}, 2000);
                    }}
                }};

                // Heartbeat — if stream breaks, try reconnecting
                setInterval(() => {{
                    fetch("{snapshot_url}").then(r => {{
                        if (!r.ok && connected) {{
                            connected = false;
                            badge.textContent = '● RECONNECTING';
                            badge.className = 'badge error';
                            img.src = "{stream_url}?t=" + Date.now();
                        }}
                    }}).catch(() => {{
                        if (connected) {{
                            connected = false;
                            badge.textContent = '● RECONNECTING';
                            badge.className = 'badge error';
                            img.src = "{stream_url}?t=" + Date.now();
                        }}
                    }});
                }}, 5000);
            </script>
        </body>
        </html>
        """
        components.html(viewer_html, height=height)


def show_game_display(game_path, game_name="Game"):
    """Quick function to launch and display a game"""
    display = GameDisplay()
    return display.launch_and_show(game_path, game_name)
