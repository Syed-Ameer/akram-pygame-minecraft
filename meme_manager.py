# Meme of the Month - Download and Display System

import os
import urllib.request
from pathlib import Path

# Default meme URL (can be updated monthly)
MEME_URL = "https://i.imgur.com/YourMemeIDHere.png"  # Update this monthly!
MEME_PATH = Path("Assets/meme_of_month.png")

def download_meme():
    """Download the current meme of the month"""
    try:
        # Create Assets folder if it doesn't exist
        MEME_PATH.parent.mkdir(exist_ok=True)
        
        # Download the meme
        print("📥 Downloading meme of the month...")
        urllib.request.urlretrieve(MEME_URL, MEME_PATH)
        print("✅ Meme downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to download meme: {e}")
        return False

def get_meme_path():
    """Get path to meme, download if needed"""
    if not MEME_PATH.exists():
        download_meme()
    
    if MEME_PATH.exists():
        return str(MEME_PATH)
    return None

# Update this URL monthly with new meme!
# Example URLs:
# "https://i.imgur.com/diamond_meme.png"
# "https://i.imgur.com/creeper_meme.png"
# "https://raw.githubusercontent.com/user/repo/main/meme.png"
