"""
VNC Viewer Component for Streamlit
Embeds noVNC web client to display virtual display in browser
"""
import streamlit.components.v1 as components
import streamlit as st

def vnc_viewer(host='localhost', port=6080, width=800, height=600):
    """
    Embed noVNC viewer in Streamlit
    
    Args:
        host: VNC server host
        port: noVNC websocket port (default 6080)
        width: Viewer width
        height: Viewer height
    """
    
    # noVNC HTML with fast connection and timeout
    vnc_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PyCraft - Game Display</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: #1e1e1e;
                overflow: hidden;
            }}
            #screen {{
                width: 100%;
                height: 100%;
            }}
            .status {{
                position: absolute;
                top: 10px;
                left: 10px;
                color: #0f0;
                font-family: monospace;
                background: rgba(0,0,0,0.7);
                padding: 10px;
                border-radius: 5px;
                z-index: 1000;
            }}
            .loading {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #fff;
                font-family: Arial;
                font-size: 18px;
                text-align: center;
            }}
            .spinner {{
                border: 4px solid rgba(255,255,255,0.3);
                border-top: 4px solid #fff;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
        <script src="https://unpkg.com/@novnc/novnc@1.4.0/core/rfb.js"></script>
    </head>
    <body>
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div>Loading VNC client...</div>
            <div style="font-size: 12px; margin-top: 10px; color: #888;">Initializing display connection</div>
        </div>
        <div class="status" id="status" style="display: none;"></div>
        <div id="screen"></div>
        
        <script>
            // Wait for RFB to be available before trying to connect
            function initVNC() {{
                // Check if RFB is defined
                if (typeof RFB === 'undefined') {{
                    document.getElementById('loading').innerHTML = 
                        '<div style="color: #ff6b6b;">❌ VNC client failed to load</div>' +
                        '<div style="font-size: 14px; margin-top: 10px;">noVNC library could not be loaded</div>' +
                        '<div style="font-size: 12px; margin-top: 10px;">Check your internet connection or use browser version</div>';
                    return;
                }}
                
                document.getElementById('loading').innerHTML = 
                    '<div class="spinner"></div>' +
                    '<div>Connecting to game display...</div>' +
                    '<div style="font-size: 12px; margin-top: 10px; color: #888;">This may take 5-10 seconds</div>';
                
                let connectionTimeout;
                let connected = false;
                
                // Connection timeout (10 seconds)
                connectionTimeout = setTimeout(() => {{
                    if (!connected) {{
                        document.getElementById('loading').innerHTML = 
                            '<div style="color: #ff6b6b;">⚠️ Connection timeout</div>' +
                            '<div style="font-size: 14px; margin-top: 10px;">VNC server may not be ready yet</div>' +
                            '<div style="font-size: 12px; margin-top: 10px;">Game may still be starting up...</div>';
                    }}
                }}, 10000);
                
                try {{
                    const rfb = new RFB(document.getElementById('screen'), 
                        'ws://{host}:{port}/websockify',
                        {{
                            credentials: {{}}
                        }}
                    );
                    
                    rfb.addEventListener("connect", () => {{
                        connected = true;
                        clearTimeout(connectionTimeout);
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('status').style.display = 'block';
                        document.getElementById('status').textContent = '✅ Connected - Game Running!';
                        setTimeout(() => {{
                            document.getElementById('status').style.display = 'none';
                        }}, 3000);
                    }});
                    
                    rfb.addEventListener("disconnect", () => {{
                        document.getElementById('status').textContent = '❌ Disconnected';
                        document.getElementById('status').style.display = 'block';
                        document.getElementById('loading').style.display = 'none';
                    }});
                    
                    rfb.scaleViewport = true;
                    rfb.resizeSession = true;
                }} catch (e) {{
                    clearTimeout(connectionTimeout);
                    document.getElementById('loading').innerHTML = 
                        '<div style="color: #ff6b6b;">❌ Connection failed</div>' +
                        '<div style="font-size: 14px; margin-top: 10px;">' + e.message + '</div>' +
                        '<div style="font-size: 12px; margin-top: 10px;">VNC server may not be running</div>';
                }}
            }}
            
            // Wait for page to load, then wait a bit more for RFB to be available
            window.onload = function() {{
                setTimeout(initVNC, 100);
            }};
        </script>
    </body>
    </html>
    """
    
    components.html(vnc_html, height=height, width=width)

def show_game_display():
    """Show game display in Streamlit"""
    st.markdown("### 🎮 Game Display")
    st.info("🖥️ Game is rendering below. Use mouse and keyboard to play!")
    vnc_viewer(width=800, height=600)
