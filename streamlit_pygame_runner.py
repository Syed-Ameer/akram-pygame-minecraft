# Streamlit Pygame Runner  
# Hybrid approach: Try to run pygame, fallback to browser version

import streamlit as st
import pygame
import sys
import os
from pathlib import Path

def display_pygame_game(game_file, username="Player", fps=30):
    """
    Display Pygame game - tries native pygame in browser, falls back to pygbag version
    
    Args:
        game_file: Path to game .py file
        username: Player username
        fps: Target frames per second (not used in fallback)
    """
    st.markdown("### 🎮 Game Display")
    st.caption(f"Selected: {Path(game_file).name} | User: {username}")
    
    # Reality check: We can't actually run .py pygame files in browser
    st.warning("""
    ⚠️ **Technical Limitation**
    
    Native .py Pygame files cannot run directly in web browsers.
    
    **Your options:**
    1. 🌐 **Play the browser version below** (pygbag-converted, works anywhere)
    2. 💻 **Download the launcher** and run locally (full .py file support)
    """)
    
    st.markdown("---")
    
    # Offer browser version
    st.markdown("### 🌐 Play in Browser (Recommended)")
    st.info("Full game running in HTML5 canvas - works on any device!")
    
    st.components.v1.iframe(
        "https://syed-ameer.github.io/akram-pygame-minecraft/",
        height=800,
        scrolling=False
    )
    
    st.markdown("---")
    
    # Offer download option
    st.markdown("### 💻 Download for Local Play")
    st.info("For the full Python experience with all 27 versions:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Download Launcher:**")
        st.markdown("[📥 Get from GitHub](https://github.com/Syed-Ameer/akram-pygame-minecraft/archive/refs/heads/feature-streamlit-pygame.zip)")
        st.caption("Includes all game versions and launcher")
    
    with col2:
        st.markdown("**How to run:**")
        st.code("""
# Extract the files
# Install dependencies:
pip install -r requirements.txt

# Run launcher:
streamlit run launcher.py
        """, language="bash")


