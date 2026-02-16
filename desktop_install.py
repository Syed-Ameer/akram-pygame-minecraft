"""
PyCraft Desktop Auto-Installer and Launcher
Simple offline launcher - only requires pygame
"""
import subprocess
import sys
import os

print("="*60)
print("🎮 PyCraft Desktop Edition - Auto-Installer")
print("="*60)

def install_pygame():
    """Install pygame if missing"""
    try:
        import pygame
        print("✅ Pygame is already installed")
        return True
    except ImportError:
        print("❌ Pygame not found")
        print("📦 Installing pygame...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame", "--quiet"])
            print("✅ Pygame installed successfully!")
            return True
        except:
            print("❌ Failed to install pygame")
            print("\n💡 Try installing manually:")
            print("   pip install pygame")
            return False

def launch_desktop_launcher():
    """Launch the desktop launcher"""
    print("\n" + "="*60)
    print("🚀 Launching PyCraft Desktop Launcher...")
    print("="*60)
    print("\n💡 Select your game from the list and click PLAY!")
    print("💡 Use arrow keys to navigate")
    print("💡 Press ESC to exit\n")
    
    try:
        subprocess.run([sys.executable, "desktop_launcher.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for playing PyCraft!")
    except Exception as e:
        print(f"\n❌ Error launching: {e}")
        print("\n💡 Try running manually: python desktop_launcher.py")

if __name__ == "__main__":
    try:
        if install_pygame():
            input("\n✅ Press ENTER to launch PyCraft...")
            launch_desktop_launcher()
    except KeyboardInterrupt:
        print("\n\n👋 Installation cancelled. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress ENTER to exit...")
