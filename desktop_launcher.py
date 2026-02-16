# PyCraft Desktop Launcher
# Opens the Pygbag web version in default browser

import webbrowser
import sys

def main():
    """Launch PyCraft in browser"""
    print("🎮 PyCraft Desktop Launcher")
    print("=" * 50)
    print("")
    print("Opening PyCraft in your browser...")
    print("")
    
    # Web launcher URL
    url = "https://syed-ameer.github.io/akram-pygame-minecraft/"
    
    try:
        # Open in default browser
        webbrowser.open(url)
        print("✅ Browser launched successfully!")
        print("")
        print("🎮 Game Controls:")
        print("   ← → arrows - Browse game versions")
        print("   ENTER - Launch selected game")
        print("")
        print(f"🌐 URL: {url}")
        print("")
        print("💡 Bookmark this page to play anytime!")
        
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"")
        print(f"📋 Please open this URL manually:")
        print(f"   {url}")
    
    print("")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()

