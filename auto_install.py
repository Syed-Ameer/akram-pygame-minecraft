#!/usr/bin/env python3
"""
PyCraft Universal One-Click Installer
Detects environment and installs everything automatically
Works on Windows, Linux, Mac, and Cloud
"""
import subprocess
import sys
import os
from pathlib import Path

def print_header():
    """Print fancy header"""
    print("\n" + "="*60)
    print("🎮 PYCRAFT UNIVERSAL AUTO-INSTALLER")
    print("="*60 + "\n")

def detect_environment():
    """Detect where we're running"""
    is_cloud = (
        os.path.exists('/mount/src') or 
        os.environ.get('STREAMLIT_SHARING_MODE') or
        'streamlit.app' in os.environ.get('HOSTNAME', '')
    )
    
    platform = sys.platform
    
    print(f"📍 Environment: {'☁️  Streamlit Cloud' if is_cloud else '💻 Local'}")
    print(f"💻 Platform: {platform}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print()
    
    return is_cloud

def install_package(package, quiet=True):
    """Install a Python package"""
    try:
        cmd = [sys.executable, "-m", "pip", "install", package]
        if quiet:
            cmd.append("--quiet")
        
        subprocess.check_call(cmd, 
            stdout=subprocess.DEVNULL if quiet else None,
            stderr=subprocess.DEVNULL if quiet else None
        )
        return True
    except:
        return False

def install_python_packages():
    """Install all Python packages"""
    print("[1/3] 📦 Installing Python packages...")
    
    packages = [
        ('pygame', 'pygame>=2.5.0'),
        ('streamlit', 'streamlit>=1.28.0'),
        ('pyvirtualdisplay', 'pyvirtualdisplay>=3.0'),
        ('PIL', 'pillow>=10.0.0')
    ]
    
    installed = 0
    failed = 0
    
    for module, package in packages:
        try:
            __import__(module)
            print(f"   ✅ {package.split('>=')[0]} - already installed")
        except ImportError:
            print(f"   📥 {package} - installing...")
            if install_package(package):
                print(f"   ✅ {package.split('>=')[0]} - installed!")
                installed += 1
            else:
                print(f"   ⚠️  {package} - failed (trying without quiet mode)")
                if install_package(package, quiet=False):
                    installed += 1
                else:
                    failed += 1
    
    print(f"\n   Summary: {installed} installed, {failed} failed")
    print()

def install_system_packages(is_cloud):
    """Install system packages (cloud only)"""
    if not is_cloud:
        print("[2/3] ⏭️  Skipping system packages (not on cloud)")
        print()
        return
    
    print("[2/3] 🖥️  System packages (handled by Streamlit Cloud)")
    print("   These are installed via packages.txt:")
    print("   ✅ xvfb - Virtual display")
    print("   ✅ x11vnc - VNC server")
    print("   ✅ fluxbox - Window manager")
    print("   ✅ websockify - WebSocket proxy")
    print("   ✅ novnc - HTML5 VNC client")
    print()

def verify_installation():
    """Verify everything is installed correctly"""
    print("[3/3] ✔️  Verifying installation...")
    
    required = {
        'pygame': 'Game engine',
        'streamlit': 'Launcher UI'
    }
    
    all_good = True
    for module, description in required.items():
        try:
            __import__(module)
            print(f"   ✅ {module} - {description}")
        except ImportError:
            print(f"   ❌ {module} - {description} (MISSING!)")
            all_good = False
    
    print()
    return all_good

def launch_launcher():
    """Launch the Streamlit launcher"""
    print("="*60)
    print("🚀 LAUNCHING PYCRAFT LAUNCHER...")
    print("="*60)
    print()
    print("🌐 Opening in your browser...")
    print("💡 Press Ctrl+C to stop")
    print()
    
    launcher = Path(__file__).parent / "launcher.py"
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(launcher),
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Launcher stopped!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n💡 Try manually: streamlit run {launcher}")

def main():
    """Main installer"""
    print_header()
    
    # Detect environment
    is_cloud = detect_environment()
    
    # Install packages
    install_python_packages()
    install_system_packages(is_cloud)
    
    # Verify
    if not verify_installation():
        print("⚠️  Some packages failed to install!")
        print("The launcher may not work correctly.")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return 1
    else:
        print("✅ Installation complete!\n")
    
    # Launch
    try:
        launch_launcher()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        input("\nPress Enter to exit...")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user. Goodbye!")
        sys.exit(0)
