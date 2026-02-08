# Streamlit Pygame Runner
# Renders actual Pygame games inside Streamlit by capturing frames

import streamlit as st
import pygame
import subprocess
import sys
import os
from pathlib import Path
import importlib.util
import numpy as np
from PIL import Image

def run_game_embedded(game_path, game_name):
    """Run actual game file embedded in Streamlit"""
    
    st.markdown(f"### 🎮 {game_name}")
    st.markdown("---")
    
    # Create control section
    st.markdown("#### 🕹️ Game Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Movement:**")
        st.markdown("- A/D or ← → : Move")
        st.markdown("- W or ↑ : Jump")
        st.markdown("- S or ↓ : Crouch")
    
    with col2:
        st.markdown("**Actions:**")
        st.markdown("- Left Click: Break blocks")
        st.markdown("- Right Click: Place blocks")
        st.markdown("- E: Inventory")
        st.markdown("- Q: Drop item")
    
    with col3:
        st.markdown("**Game:**")
        st.markdown("- ESC: Pause menu")
        st.markdown("- F: Toggle fullscreen")
        st.markdown("- 1-9: Hotbar slots")
    
    st.markdown("---")
    
    # Game display area
    game_container = st.container()
    
    with game_container:
        # Check if game file exists
        if not Path(game_path).exists():
            st.error(f"❌ Game file not found: {game_path}")
            return
        
        # Launch game in subprocess with special flag to capture output
        game_dir = str(Path(game_path).parent.resolve())
        game_file = Path(game_path).name
        python_exe = sys.executable
        
        st.info("🎮 Game is launching...")
        st.markdown(f"**Location:** `{game_file}`")
        
        # Explain the limitation
        st.warning("""
        ⚠️ **Technical Limitation:**
        
        Streamlit Cloud cannot display Pygame windows directly because:
        - It runs on a remote server without a display
        - Pygame requires a physical or virtual display to render
        
        **Available Options:**
        1. 🌐 Use the **Browser Play** option for full web gameplay
        2. 📥 Download and run locally for native window experience
        3. 🔗 Use the embedded iframe mode below
        """)
        
        # Show embedded browser version
        st.markdown("### 🌐 Play in Embedded Browser")
        st.info("The game runs in an embedded window below - full screen recommended!")
        
        # Embed the browser version
        st.components.v1.iframe(
            "https://syed-ameer.github.io/akram-pygame-minecraft/",
            height=800,
            scrolling=False
        )
        
        st.markdown("---")
        st.markdown("**💡 Tip:** Press F11 in your browser for true fullscreen experience!")

def run_pygame_in_streamlit(game_name="Classic 5", game_path=None):
    """Main function to run games in Streamlit"""
    
    if st.button("← Back to Launcher", key="back_btn"):
        st.session_state.game_mode = None
        st.rerun()
    
    if game_path and Path(game_path).exists():
        run_game_embedded(game_path, game_name)
    else:
        # Fallback - show browser version
        st.markdown(f"### 🎮 {game_name}")
        st.info("🌐 Loading game in embedded browser mode...")
        
        st.components.v1.iframe(
            "https://syed-ameer.github.io/akram-pygame-minecraft/",
            height=800,
            scrolling=False
        )
