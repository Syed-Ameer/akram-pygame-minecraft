"""
Virtual Display Manager for Streamlit Cloud
Allows Pygame games to run on headless servers
"""
import os
import subprocess
import time
from pathlib import Path

class VirtualDisplay:
    def __init__(self, width=800, height=600, display_num=99):
        self.width = width
        self.height = height
        self.display_num = display_num
        self.display = f":{display_num}"
        self.xvfb_process = None
        self.vnc_process = None
        self.websockify_process = None
        
    def start(self):
        """Start virtual display and VNC server"""
        try:
            # Start Xvfb (virtual framebuffer)
            print(f"Starting virtual display {self.display}")
            self.xvfb_process = subprocess.Popen([
                'Xvfb',
                self.display,
                '-screen', '0', f'{self.width}x{self.height}x24',
                '-ac',  # disable access control
                '+extension', 'GLX',
                '+render',
                '-noreset'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for Xvfb to start
            time.sleep(2)
            
            # Set DISPLAY environment variable
            os.environ['DISPLAY'] = self.display
            
            # Start x11vnc server
            print(f"Starting VNC server on display {self.display}")
            self.vnc_process = subprocess.Popen([
                'x11vnc',
                '-display', self.display,
                '-forever',
                '-shared',
                '-bg',
                '-rfbport', '5900'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(1)
            
            # Start websockify to make VNC accessible via WebSocket for noVNC
            try:
                print("Starting websockify for browser VNC client...")
                self.websockify_process = subprocess.Popen([
                    'websockify',
                    '--web=/usr/share/novnc',
                    '6080',
                    'localhost:5900'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(1)
                print("✅ Websockify started on port 6080")
            except Exception as e:
                print(f"⚠️ Websockify failed (optional): {e}")
                self.websockify_process = None
            
            print(f"✅ Virtual display running on {self.display}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start virtual display: {e}")
            return False
    
    def stop(self):
        """Stop virtual display and VNC server"""
        if self.websockify_process:
            self.websockify_process.terminate()
        if self.vnc_process:
            self.vnc_process.terminate()
        if self.xvfb_process:
            self.xvfb_process.terminate()
        print("Virtual display stopped")
    
    def is_running(self):
        """Check if virtual display is running"""
        return self.xvfb_process and self.xvfb_process.poll() is None

# Global display instance
_display = None

def get_display():
    """Get or create virtual display"""
    global _display
    if _display is None or not _display.is_running():
        _display = VirtualDisplay()
        _display.start()
    return _display

def ensure_display():
    """Ensure virtual display is running (for cloud environments)"""
    is_cloud = os.path.exists('/mount/src') or os.environ.get('STREAMLIT_SHARING_MODE')
    
    if is_cloud and 'DISPLAY' not in os.environ:
        print("🖥️ Cloud environment detected - starting virtual display...")
        display = get_display()
        return display.is_running()
    
    return True
