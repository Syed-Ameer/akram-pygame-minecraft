"""
VNC Viewer Component for Streamlit
Embeds noVNC web client to display virtual display in browser
"""
import streamlit.components.v1 as components
import streamlit as st
import time

def vnc_viewer(host='localhost', port=6080, width=800, height=600, autoconnect=True):
    """
    Embed noVNC viewer in Streamlit
    
    Args:
        host: VNC server host (default: localhost)
        port: noVNC websocket port (default: 6080)
        width: Viewer width in pixels
        height: Viewer height in pixels
        autoconnect: Auto-connect on load (default: True)
    """
    
    # Enhanced noVNC HTML with better error handling
    vnc_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PyCraft - Game Display</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                background: linear-gradient(135deg, #1e1e1e 0%, #2d3748 100%);
                overflow: hidden;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            #screen {{
                width: 100%;
                height: 100%;
                display: none;
            }}
            #screen.active {{
                display: block;
            }}
            .overlay {{
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background: rgba(0, 0, 0, 0.9);
                z-index: 1000;
                transition: opacity 0.3s;
            }}
            .overlay.hidden {{
                opacity: 0;
                pointer-events: none;
            }}
            .status-card {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                padding: 30px 40px;
                text-align: center;
                max-width: 400px;
                backdrop-filter: blur(10px);
            }}
            .spinner {{
                border: 4px solid rgba(255,255,255,0.1);
                border-top: 4px solid #4CAF50;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .progress-bar {{
                width: 100%;
                height: 6px;
                background: rgba(255,255,255,0.1);
                border-radius: 3px;
                margin: 20px 0;
                overflow: hidden;
            }}
            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #4CAF50, #81C784);
                border-radius: 3px;
                transition: width 0.3s ease;
                box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
            }}
            .status-text {{
                color: #fff;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 10px;
            }}
            .status-detail {{
                color: rgba(255,255,255,0.7);
                font-size: 14px;
                margin-top: 10px;
            }}
            .error {{
                color: #ff6b6b;
            }}
            .success {{
                color: #4CAF50;
            }}
            .retry-btn {{
                background: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                cursor: pointer;
                margin-top: 20px;
                transition: background 0.2s;
            }}
            .retry-btn:hover {{
                background: #45a049;
            }}
            .connection-info {{
                position: absolute;
                top: 10px;
                right: 10px;
                background: rgba(0,0,0,0.8);
                color: #4CAF50;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                z-index: 100;
                display: none;
            }}
            .connection-info.show {{
                display: block;
            }}
        </style>
    </head>
    <body>
        <div class="overlay" id="overlay">
            <div class="status-card">
                <div class="spinner" id="spinner"></div>
                <div class="status-text" id="statusText">Initializing...</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                </div>
                <div class="status-detail" id="statusDetail">Loading VNC libraries</div>
                <button class="retry-btn" id="retryBtn" style="display: none;">Retry Connection</button>
            </div>
        </div>
        <div class="connection-info" id="connInfo">
            <span id="connStatus">●</span> Connected to {host}:{port}
        </div>
        <div id="screen"></div>
        
        <script>
            // State management
            const state = {{
                progress: 0,
                stage: 'init',
                libraryLoaded: false,
                connected: false,
                rfb: null,
                retryCount: 0,
                maxRetries: 3
            }};
            
            // DOM elements
            const elements = {{
                overlay: document.getElementById('overlay'),
                screen: document.getElementById('screen'),
                spinner: document.getElementById('spinner'),
                statusText: document.getElementById('statusText'),
                statusDetail: document.getElementById('statusDetail'),
                progressFill: document.getElementById('progressFill'),
                retryBtn: document.getElementById('retryBtn'),
                connInfo: document.getElementById('connInfo'),
                connStatus: document.getElementById('connStatus')
            }};
            
            // CDN sources for noVNC library (try multiple for reliability)
            const cdnSources = [
                'https://unpkg.com/@novnc/novnc@1.4.0/core/rfb.js',
                'https://cdn.jsdelivr.net/npm/@novnc/novnc@1.4.0/core/rfb.js',
                'https://cdnjs.cloudflare.com/ajax/libs/noVNC/1.4.0/core/rfb.min.js'
            ];
            
            // Update UI with progress
            function updateStatus(progress, text, detail = '', showSpinner = true) {{
                state.progress = progress;
                elements.progressFill.style.width = progress + '%';
                elements.statusText.textContent = text;
                elements.statusDetail.textContent = detail;
                elements.spinner.style.display = showSpinner ? 'block' : 'none';
                console.log(`[${{progress}}%] ${{text}} - ${{detail}}`);
            }}
            
            // Show error with retry option
            function showError(message, detail = '', allowRetry = true) {{
                elements.spinner.style.display = 'none';
                elements.statusText.className = 'status-text error';
                elements.statusText.textContent = '❌ ' + message;
                elements.statusDetail.textContent = detail;
                elements.progressFill.style.background = '#ff6b6b';
                
                if (allowRetry && state.retryCount < state.maxRetries) {{
                    elements.retryBtn.style.display = 'block';
                    elements.retryBtn.textContent = `Retry (${{state.maxRetries - state.retryCount}} attempts left)`;
                }} else if (!allowRetry) {{
                    elements.statusDetail.textContent += '\\n\\nℹ️ Make sure the virtual display is running';
                }}
            }}
            
            // Hide overlay and show game
            function showGame() {{
                elements.overlay.classList.add('hidden');
                elements.screen.classList.add('active');
                elements.connInfo.classList.add('show');
                setTimeout(() => {{
                    elements.overlay.style.display = 'none';
                }}, 300);
            }}
            
            // Load noVNC library from CDN
            function loadLibrary() {{
                updateStatus(10, 'Loading VNC library', 'Connecting to CDN...');
                
                let loadedFromCDN = false;
                let failedCount = 0;
                
                cdnSources.forEach((url, index) => {{
                    const script = document.createElement('script');
                    script.src = url;
                    script.async = true;
                    
                    script.onload = function() {{
                        if (!loadedFromCDN) {{
                            loadedFromCDN = true;
                            state.libraryLoaded = true;
                            console.log('✅ Loaded noVNC from:', url);
                            updateStatus(30, 'Library loaded', 'Initializing VNC client...');
                            setTimeout(initializeVNC, 500);
                        }}
                    }};
                    
                    script.onerror = function() {{
                        failedCount++;
                        console.warn('❌ Failed to load from:', url);
                        if (failedCount >= cdnSources.length && !loadedFromCDN) {{
                            showError(
                                'Failed to load VNC library',
                                'Unable to load from any CDN. Check your internet connection.',
                                true
                            );
                        }}
                    }};
                    
                    document.head.appendChild(script);
                }});
                
                // Timeout if library doesn't load
                setTimeout(() => {{
                    if (!state.libraryLoaded) {{
                        showError(
                            'Library loading timeout',
                            'The VNC library took too long to load',
                            true
                        );
                    }}
                }}, 15000);
            }}
            
            // Initialize VNC connection
            function initializeVNC() {{
                if (typeof RFB === 'undefined') {{
                    setTimeout(initializeVNC, 100);
                    return;
                }}
                
                updateStatus(50, 'Connecting to VNC server', 'ws://{host}:{port}');
                
                try {{
                    const url = 'ws://{host}:{port}/websockify';
                    
                    state.rfb = new RFB(elements.screen, url, {{
                        credentials: {{}},
                        shared: true,
                        wsProtocols: ['binary']
                    }});
                    
                    // Event: Connection successful
                    state.rfb.addEventListener('connect', () => {{
                        state.connected = true;
                        state.retryCount = 0;
                        updateStatus(100, '✅ Connected', 'Game display is ready', false);
                        elements.statusText.className = 'status-text success';
                        elements.progressFill.style.background = 'linear-gradient(90deg, #4CAF50, #81C784)';
                        
                        setTimeout(showGame, 1000);
                    }});
                    
                    // Event: Disconnected
                    state.rfb.addEventListener('disconnect', (e) => {{
                        state.connected = false;
                        elements.screen.classList.remove('active');
                        elements.connInfo.classList.remove('show');
                        elements.overlay.style.display = 'flex';
                        elements.overlay.classList.remove('hidden');
                        
                        const reason = e.detail.clean ? 'Server closed connection' : 'Connection lost';
                        showError(
                            'Disconnected',
                            reason + '. The game may have closed.',
                            true
                        );
                    }});
                    
                    // Event: Security failure
                    state.rfb.addEventListener('securityfailure', (e) => {{
                        showError(
                            'Security Error',
                            'Authentication failed: ' + e.detail.reason,
                            false
                        );
                    }});
                    
                    // Configure display settings
                    state.rfb.scaleViewport = true;
                    state.rfb.resizeSession = true;
                    state.rfb.clipViewport = false;
                    state.rfb.dragViewport = false;
                    state.rfb.focusOnClick = true;
                    state.rfb.background = '#1e1e1e';
                    
                    updateStatus(70, 'Requesting connection', 'Waiting for server...');
                    
                    // Timeout if connection doesn't complete
                    setTimeout(() => {{
                        if (!state.connected) {{
                            showError(
                                'Connection timeout',
                                'VNC server did not respond. Is the virtual display running?',
                                true
                            );
                        }}
                    }}, 20000);
                    
                }} catch (error) {{
                    showError(
                        'Connection Error',
                        'Failed to initialize VNC: ' + error.message,
                        true
                    );
                    console.error('VNC Error:', error);
                }}
            }}
            
            // Retry connection
            elements.retryBtn.onclick = function() {{
                state.retryCount++;
                elements.retryBtn.style.display = 'none';
                elements.spinner.style.display = 'block';
                elements.statusText.className = 'status-text';
                elements.progressFill.style.background = 'linear-gradient(90deg, #4CAF50, #81C784)';
                
                if (state.libraryLoaded) {{
                    updateStatus(40, 'Retrying connection', 'Attempt ' + (state.retryCount + 1));
                    setTimeout(initializeVNC, 1000);
                }} else {{
                    updateStatus(0, 'Retrying', 'Reloading library...');
                    setTimeout(loadLibrary, 1000);
                }}
            }};
            
            // Start the connection process
            setTimeout(loadLibrary, 500);
        </script>
    </body>
    </html>
    """
    
    components.html(vnc_html, height=height, width=width)

def show_game_display(host='localhost', port=6080):
    """Show game display in Streamlit with VNC viewer"""
    st.markdown("### 🎮 Game Display")
    st.caption(f"🔌 Connecting to VNC server at {host}:{port}")
    
    with st.expander("ℹ️ Display Info", expanded=False):
        st.info("""
        **VNC Game Display**
        - Server: `{}`
        - Port: `{}`
        - Protocol: WebSocket (noVNC)
        
        **Controls:**
        - Click inside to focus
        - Use mouse and keyboard normally
        - Display auto-scales to fit
        """.format(host, port))
    
    vnc_viewer(host=host, port=port, width=800, height=600)
    
    st.caption("💡 Having issues? Make sure the virtual display service is running.")

# Backwards compatibility
def vnc_viewer_legacy(host='localhost', port=6080, width=800, height=600):
    """Legacy function name for compatibility"""
    return vnc_viewer(host, port, width, height)
