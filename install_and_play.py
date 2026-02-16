"""
PyCraft Auto-Installer and Launcher
Automatically installs all dependencies and launches the game
"""
import subprocess
import sys
import os

print("="*60)
print("🎮 PyCraft v1.0 - Auto-Installer")
print("="*60)

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        print(f"✅ {package} installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def check_and_install():
    """Check for required packages and install if missing"""
    required_packages = {
        'pygame': 'pygame',
    }
    
    missing_packages = []
    
    # Check which packages are missing
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            print(f"✅ {module_name} is already installed")
        except ImportError:
            print(f"❌ {module_name} not found")
            missing_packages.append(package_name)
    
    # Install missing packages
    if missing_packages:
        print(f"\n📥 Installing {len(missing_packages)} missing package(s)...")
        for package in missing_packages:
            install_package(package)
        print("\n✅ All dependencies installed!")
    else:
        print("\n✅ All dependencies are already installed!")
    
    return True

def launch_launcher():
    """Launch the Desktop launcher"""
    print("\n" + "="*60)
    print("🚀 Launching PyCraft Desktop Launcher...")
    print("="*60)
    print("\n💡 Select your game and press PLAY!")
    print("\n⚠️  Press ESC to close the launcher\n")
    
    try:
        subprocess.run([sys.executable, "desktop_launcher.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for playing PyCraft!")
    except Exception as e:
        print(f"\n❌ Error launching: {e}")
        print("\n💡 Try running manually: python desktop_launcher.py")

if __name__ == "__main__":
    try:
        # Check and install dependencies
        if check_and_install():
            input("\n✅ Press ENTER to launch PyCraft Launcher...")
            launch_launcher()
    except KeyboardInterrupt:
        print("\n\n👋 Installation cancelled. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress ENTER to exit...")
