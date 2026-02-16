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
    
    # noVNC HTML
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
            }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/noVNC/1.3.0/core/rfb.min.js"></script>
    </head>
    <body>
        <div class="status" id="status">Connecting to game display...</div>
        <div id="screen"></div>
        
        <script>
            const rfb = new RFB(document.getElementById('screen'), 
                'ws://{host}:{port}/websockify',
                {{
                    credentials: {{}}
                }}
            );
            
            rfb.addEventListener("connect", () => {{
                document.getElementById('status').textContent = '✅ Connected - Game Running!';
                setTimeout(() => {{
                    document.getElementById('status').style.display = 'none';
                }}, 3000);
            }});
            
            rfb.addEventListener("disconnect", () => {{
                document.getElementById('status').textContent = '❌ Disconnected';
                document.getElementById('status').style.display = 'block';
            }});
            
            rfb.scaleViewport = true;
            rfb.resizeSession = true;
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
