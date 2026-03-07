"""
Windows VNC Alternative  —  Screen-Capture Streaming
=====================================================
Captures the Pygame game window and streams it as MJPEG
to an embedded browser viewer inside Streamlit.

Works on Windows (and Mac) without xvfb / websockify / noVNC.

Dependencies
------------
* **mss**   – fast cross-platform screen capture  (auto-installed if missing)
* **Pillow** – image processing  (already in requirements.txt)
"""

import io
import os
import sys
import time
import socket
import platform
import threading
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

IS_WINDOWS = platform.system() == "Windows"

# ---------------------------------------------------------------------------
#  Lazy dependency loading
# ---------------------------------------------------------------------------
_mss = None
_Image = None


def _ensure_pkg(name):
    """Import *name*; pip-install it first if necessary."""
    try:
        return __import__(name)
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return __import__(name)


def _load_deps():
    global _mss, _Image
    if _mss is None:
        _mss = _ensure_pkg("mss")
    if _Image is None:
        try:
            from PIL import Image
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet", "Pillow"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            from PIL import Image
        _Image = Image


# ---------------------------------------------------------------------------
#  Find the Pygame window on Windows  (uses only ctypes — no extra deps)
# ---------------------------------------------------------------------------

def find_pygame_window(*title_hints):
    """
    Return an mss-compatible monitor dict for the first visible window
    whose title contains any of *title_hints* (case-insensitive).

    Falls back to ``None`` (= primary monitor) when nothing matches.
    """
    if not title_hints:
        return None

    # --- Windows: ctypes EnumWindows ---
    if IS_WINDOWS:
        return _find_window_windows(title_hints)

    # --- macOS: osascript AppleScript ---
    if platform.system() == "Darwin":
        return _find_window_mac(title_hints)

    return None


def _find_window_windows(title_hints):
    """Windows implementation using ctypes."""
    try:
        import ctypes
        import ctypes.wintypes

        user32 = ctypes.windll.user32
        results = []

        def _cb(hwnd, _lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title_lower = buf.value.lower()
                    for hint in title_hints:
                        if hint.lower() in title_lower:
                            r = ctypes.wintypes.RECT()
                            user32.GetWindowRect(hwnd, ctypes.byref(r))
                            w, h = r.right - r.left, r.bottom - r.top
                            if w > 100 and h > 100:
                                results.append({
                                    "left": r.left, "top": r.top,
                                    "width": w, "height": h,
                                })
                            break
            return True

        proto = ctypes.WINFUNCTYPE(
            ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM,
        )
        user32.EnumWindows(proto(_cb), 0)
        return results[0] if results else None
    except Exception:
        return None


def _find_window_mac(title_hints):
    """macOS implementation using osascript / AppleScript."""
    try:
        # Ask macOS for all visible window names + bounds
        script = '''
        set output to ""
        tell application "System Events"
            set procs to every process whose visible is true
            repeat with p in procs
                set wins to every window of p
                repeat with w in wins
                    try
                        set t to name of w
                        set pos to position of w
                        set sz to size of w
                        set output to output & t & "|" & (item 1 of pos) & "|" & (item 2 of pos) & "|" & (item 1 of sz) & "|" & (item 2 of sz) & linefeed
                    end try
                end repeat
            end repeat
        end tell
        return output
        '''
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.strip().splitlines():
            parts = line.split("|")
            if len(parts) >= 5:
                title = parts[0].lower()
                for hint in title_hints:
                    if hint.lower() in title:
                        x, y, w, h = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                        if w > 100 and h > 100:
                            return {"left": x, "top": y, "width": w, "height": h}
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
#  Shared streaming state  (read by the HTTP handler threads)
# ---------------------------------------------------------------------------

class _StreamCfg:
    capture_region = None
    fps: int = 12
    quality: int = 55
    running: bool = True


# ---------------------------------------------------------------------------
#  MJPEG HTTP request handler
# ---------------------------------------------------------------------------

class _Handler(BaseHTTPRequestHandler):
    """Serves ``/stream`` (MJPEG), ``/snapshot`` (single JPEG), ``/status``."""

    # ---- routing -----------------------------------------------------------
    def do_GET(self):
        routes = {
            "/stream":   self._stream,
            "/snapshot": self._snapshot,
            "/status":   self._status,
        }
        handler = routes.get(self.path, self._index)
        handler()

    # ---- /stream  (MJPEG multipart) ---------------------------------------
    def _stream(self):
        self.send_response(200)
        self.send_header("Content-Type",
                         "multipart/x-mixed-replace; boundary=--frame")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        sct = _mss.mss()
        mon = _StreamCfg.capture_region or sct.monitors[1]

        try:
            while _StreamCfg.running:
                jpg = self._grab(sct, mon)
                self.wfile.write(b"--frame\r\n")
                self.wfile.write(b"Content-Type: image/jpeg\r\n")
                self.wfile.write(f"Content-Length: {len(jpg)}\r\n".encode())
                self.wfile.write(b"\r\n")
                self.wfile.write(jpg)
                self.wfile.write(b"\r\n")
                self.wfile.flush()
                time.sleep(1.0 / _StreamCfg.fps)
        except (BrokenPipeError, ConnectionResetError,
                ConnectionAbortedError, OSError):
            pass

    # ---- /snapshot  (single JPEG) -----------------------------------------
    def _snapshot(self):
        sct = _mss.mss()
        mon = _StreamCfg.capture_region or sct.monitors[1]
        jpg = self._grab(sct, mon, quality=75)
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(jpg)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(jpg)

    # ---- /status -----------------------------------------------------------
    def _status(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    # ---- fallback ----------------------------------------------------------
    def _index(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"PyCraft screen-stream server running.")

    # ---- helpers -----------------------------------------------------------
    @staticmethod
    def _grab(sct, mon, quality=None):
        quality = quality or _StreamCfg.quality
        raw = sct.grab(mon)
        img = _Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
        # Cap width at 960 px for performance
        if img.width > 960:
            ratio = 960 / img.width
            img = img.resize((960, int(img.height * ratio)), _Image.BILINEAR)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        return buf.getvalue()

    def log_message(self, *_a):
        pass  # suppress noisy HTTP logs


# ---------------------------------------------------------------------------
#  Public API
# ---------------------------------------------------------------------------

def _free_port(lo=6090, hi=6200):
    for p in range(lo, hi):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return None


class WindowsScreenStream:
    """
    MJPEG screen-capture server — drop-in VNC alternative for Windows.

    Usage inside Streamlit::

        stream = WindowsScreenStream()
        port = stream.start()               # starts HTTP server
        url  = stream.stream_url            # http://localhost:<port>/stream
        stream.stop()                       # clean shutdown
    """

    def __init__(self, fps=12, quality=55):
        self.fps = fps
        self.quality = quality
        self.port = None
        self._server = None
        self._thread = None

    # ---- availability check -----------------------------------------------
    @staticmethod
    def is_available():
        try:
            _load_deps()
            return _mss is not None and _Image is not None
        except Exception:
            return False

    # ---- start / stop -----------------------------------------------------
    def start(self, capture_region=None):
        """
        Begin capturing and streaming.

        Parameters
        ----------
        capture_region : dict | None
            ``{"left": x, "top": y, "width": w, "height": h}``
            Pass ``None`` to capture the primary monitor.

        Returns
        -------
        int | None
            The port the server is listening on, or ``None`` on failure.
        """
        _load_deps()
        self.port = _free_port()
        if self.port is None:
            return None

        _StreamCfg.capture_region = capture_region
        _StreamCfg.fps = self.fps
        _StreamCfg.quality = self.quality
        _StreamCfg.running = True

        self._server = HTTPServer(("127.0.0.1", self.port), _Handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever, daemon=True,
        )
        self._thread.start()
        return self.port

    def stop(self):
        _StreamCfg.running = False
        if self._server:
            self._server.shutdown()
            self._server = None

    # ---- convenience URLs -------------------------------------------------
    @property
    def stream_url(self):
        return f"http://localhost:{self.port}/stream" if self.port else None

    @property
    def snapshot_url(self):
        return f"http://localhost:{self.port}/snapshot" if self.port else None
