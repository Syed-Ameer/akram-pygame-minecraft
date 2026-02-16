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
            // VISUAL PROGRESS: Show percentage and stage
            const cdnSources = [
                'https://unpkg.com/@novnc/novnc@1.4.0/core/rfb.js',
                'https://cdn.jsdelivr.net/npm/@novnc/novnc@1.4.0/core/rfb.js',
                'https://cdnjs.cloudflare.com/ajax/libs/noVNC/1.3.0/core/rfb.min.js'
            ];
            
            let progress = 0;
            let libraryLoaded = false;
            let connected = false;
            let failedCount = 0;
            let stage = 'Loading library';
            
            // Animated progress display
            function showProgress(percent, message) {{
                document.getElementById('loading').innerHTML = 
                    '<div class="spinner"></div>' +
                    `<div style="font-size: 24px; font-weight: bold; color: #4CAF50;">${{percent}}%</div>` +
                    `<div style="margin-top: 10px;">${{message}}</div>` +
                    `<div style="width: 200px; height: 4px; background: rgba(255,255,255,0.2); border-radius: 2px; margin: 15px auto 0;">` +
                    `<div style="width: ${{percent}}%; height: 100%; background: #4CAF50; border-radius: 2px; transition: width 0.3s;"></div></div>`;
            }}
            
            // Smooth progress animation
            function animateProgress() {{
                if (connected) return;
                
                if (progress < 20 && !libraryLoaded) {{
                    progress += 5;
                    showProgress(progress, '📦 Loading VNC library...');
                    setTimeout(animateProgress, 200);
                }} else if (progress < 40 && libraryLoaded && stage === 'Loading library') {{
                    stage = 'Initializing';
                    progress = 40;
                    showProgress(progress, '⚙️ Initializing connection...');
                    setTimeout(animateProgress, 300);
                }} else if (progress < 85 && stage === 'Initializing') {{
                    progress += 5;
                    showProgress(progress, '🔌 Connecting to server...');
                    setTimeout(animateProgress, 500);
                }} else if (progress >= 85 && !connected) {{
                    showProgress(95, '⏳ Waiting for server response...');
                    // Check if stuck
                    setTimeout(() => {{
                        if (!connected) {{
                            showProgress(95, '⚠️ Server is slow to respond...');
                            setTimeout(() => {{
                                if (!connected) {{
                                    document.getElementById('loading').innerHTML = 
                                        '<div style="color: #ff6b6b;">❌ Connection timeout</div>' +
                                        '<div style="font-size: 12px; margin-top: 10px;">Server may not be running</div>' +
                                        '<div style="font-size: 12px;">Check if game launched successfully</div>';
                                }}
                            }}, 10000);
                        }}
                    }}, 8000);
                }}
            }}
            
            // Start progress animation immediately
            animateProgress();
            
            // Try all CDNs simultaneously
            cdnSources.forEach((url, index) => {{
                const script = document.createElement('script');
                script.src = url;
                script.async = true;
                
                script.onload = function() {{
                    if (!libraryLoaded) {{
                        libraryLoaded = true;
                        progress = 30;
                        showProgress(progress, '✅ Library loaded!');
                        setTimeout(connectVNC, 100);
                    }}
                }};
                
                script.onerror = function() {{
                    failedCount++;
                    if (failedCount >= cdnSources.length) {{
                        document.getElementById('loading').innerHTML = 
                            '<div style="color: #ff6b6b;">❌ Library failed to load</div>' +
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
                
                stage = 'Initializing';
                animateProgress();
                
                try {{
                    const rfb = new RFB(document.getElementById('screen'), 
                        'ws://{host}:{port}/websockify',
                        {{ 
                            credentials: {{}},
                            wsProtocols: ['binary']
                        }}
                    );
                    
                    rfb.addEventListener("connect", () => {{
                        connected = true;
                        progress = 100;
                        showProgress(100, '✅ Connected successfully!');
                        setTimeout(() => {{
                            document.getElementById('loading').style.display = 'none';
                            document.getElementById('status').style.display = 'block';
                            document.getElementById('status').style.color = '#0f0';
                            document.getElementById('status').textContent = '✅ Game Display Active';
                            setTimeout(() => {{
                                document.getElementById('status').style.display = 'none';
                            }}, 3000);
                        }}, 1000);
                    }});
                    
                    rfb.addEventListener("disconnect", () => {{
                        document.getElementById('status').style.color = '#f00';
                        document.getElementById('status').textContent = '❌ Disconnected';
                        document.getElementById('status').style.display = 'block';
                    }});
                    
                    rfb.scaleViewport = true;
                    rfb.resizeSession = true;
                }} catch (e) {{
                    document.getElementById('loading').innerHTML = 
                        '<div style="color: #ff6b6b;">❌ Error: ' + e.message + '</div>';
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
