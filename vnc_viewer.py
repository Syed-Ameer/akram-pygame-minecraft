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
    
    # noVNC HTML - FASTEST & MOST ROBUST approach
    vnc_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PyCraft - Game Display</title>
        <meta charset="UTF-8">
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
                font-size: 14px;
            }}
            .loading {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #fff;
                font-family: Arial;
                font-size: 16px;
                text-align: center;
            }}
            .spinner {{
                border: 3px solid rgba(255,255,255,0.3);
                border-top: 3px solid #4CAF50;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 0.8s linear infinite;
                margin: 0 auto 15px;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div>Connecting...</div>
        </div>
        <div class="status" id="status" style="display: none;"></div>
        <div id="screen"></div>
        
        <script>
            // FASTEST & MOST ROBUST: Load all CDNs in parallel, use first success
            const cdnSources = [
                'https://unpkg.com/@novnc/novnc@1.4.0/core/rfb.js',
                'https://cdn.jsdelivr.net/npm/@novnc/novnc@1.4.0/core/rfb.js',
                'https://cdnjs.cloudflare.com/ajax/libs/noVNC/1.3.0/core/rfb.min.js'
            ];
            
            let libraryLoaded = false;
            let connected = false;
            let failedCount = 0;
            
            // Try all CDNs simultaneously (FASTEST approach)
            cdnSources.forEach((url, index) => {{
                const script = document.createElement('script');
                script.src = url;
                script.async = true;
                
                script.onload = function() {{
                    if (!libraryLoaded) {{
                        libraryLoaded = true;
                        setTimeout(connectVNC, 50); // Immediate connection attempt
                    }}
                }};
                
                script.onerror = function() {{
                    failedCount++;
                    if (failedCount >= cdnSources.length) {{
                        document.getElementById('loading').innerHTML = 
                            '<div style="color: #ff6b6b;">\u274c All CDNs failed</div>' +
                            '<div style="font-size: 12px; margin-top: 10px;">Check internet connection</div>';
                    }}
                }};
                
                document.head.appendChild(script);
            }});
            
            function connectVNC() {{
                if (typeof RFB === 'undefined') {{
                    setTimeout(connectVNC, 100);
                    return;
                }}
                
                // Quick timeout for slow servers
                const timeout = setTimeout(() => {{
                    if (!connected) {{
                        document.getElementById('loading').innerHTML = 
                            '<div style="color: #ff9800;">\u231b Still connecting...</div>';
                    }}
                }}, 15000);
                
                try {{
                    const rfb = new RFB(document.getElementById('screen'), 
                        'ws://{host}:{port}/websockify',
                        {{ credentials: {{}} }}
                    );
                    
                    rfb.addEventListener("connect", () => {{
                        connected = true;
                        clearTimeout(timeout);
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('status').style.display = 'block';
                        document.getElementById('status').textContent = '\u2705 Connected!';
                        setTimeout(() => {{
                            document.getElementById('status').style.display = 'none';
                        }}, 2000);
                    }});
                    
                    rfb.addEventListener("disconnect", () => {{
                        document.getElementById('status').textContent = '\u274c Disconnected';
                        document.getElementById('status').style.display = 'block';
                    }});
                    
                    rfb.scaleViewport = true;
                    rfb.resizeSession = true;
                }} catch (e) {{
                    clearTimeout(timeout);
                    document.getElementById('loading').innerHTML = 
                        '<div style="color: #ff6b6b;">\u274c Connection error</div>';
                }}
            }}
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
