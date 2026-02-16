# Streamlit Pygame Runner  
# Embeds Pygame games directly in Streamlit using frame capture

import streamlit as st
import pygame
import threading
import sys
import os
from pathlib import Path
from PIL import Image
import time
import io

class PygameStreamlitRunner:
    """Runs Pygame games embedded in Streamlit by capturing frames"""
    
    def __init__(self, game_file, username="Player", width=800, height=600):
        self.game_file = game_file
        self.username = username
        self.width = width
        self.height = height
        self.running = False
        self.game_thread = None
        self.current_frame = None
        self.fps = 30
        
    def run_game(self):
        """Run the game in a separate thread"""
        try:
            # Set up environment
            os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Headless mode
            
            #Initialize pygame
            pygame.init()
            
            # Create surface
            screen = pygame.display.set_mode((self.width, self.height))
            clock = pygame.time.Clock()
            
            # Import and run game module
            game_dir = str(Path(self.game_file).parent.resolve())
            game_file = Path(self.game_file).name
            
            # Add game directory to path
            if game_dir not in sys.path:
                sys.path.insert(0, game_dir)
            
            # Set username argument
            sys.argv = [game_file, "--username", self.username]
            
            # Import game module
            game_module_name = game_file.replace('.py', '')
            
            # Execute game file
            with open(self.game_file, 'r') as f:
                game_code = f.read()
            
            # Create namespace for game
            game_namespace = {
                '__name__': '__main__',
                '__file__': self.game_file,
            }
            
            self.running = True
            
            # Execute game in namespace
            exec(game_code, game_namespace)
            
        except Exception as e:
            print(f"Game error: {e}")
        finally:
            self.running = False
            pygame.quit()
    
    def get_frame(self):
        """Capture current pygame frame as PIL Image"""
        try:
            surface = pygame.display.get_surface()
            if surface:
                # Convert pygame surface to PIL Image
                size = surface.get_size()
                buffer = pygame.image.tostring(surface, 'RGB')
                image = Image.frombytes('RGB', size, buffer)
                return image
        except:
            return None
        return None

def display_pygame_game(game_file, username="Player", fps=30):
    """
    Display Pygame game embedded in Streamlit
    
    Args:
        game_file: Path to game .py file
        username: Player username
        fps: Target frames per second
    """
    st.markdown("### 🎮 Game Display")
    st.caption(f"Playing: {Path(game_file).name} | User: {username}")
    
    # Create placeholders
    game_placeholder = st.empty()
    control_col1, control_col2 = st.columns(2)
    
    with control_col1:
        st.info("🎮 Game is running in embedded mode")
    
    with control_col2:
        if st.button("⏹️ Stop Game"):
            st.session_state.game_running = False
            st.rerun()
    
    st.markdown("---")
    
    # Initialize runner
    runner = PygameStreamlitRunner(game_file, username)
    
    # Start game thread
    runner.game_thread = threading.Thread(target=runner.run_game, daemon=True)
    runner.game_thread.start()
    
    st.session_state.game_running = True
    
    # Frame display loop
    frame_delay = 1.0 / fps
    frame_count = 0
    
    try:
        while st.session_state.get('game_running', False) and runner.running:
            # Capture frame
            frame = runner.get_frame()
            
            if frame:
                # Display frame
                game_placeholder.image(frame, use_column_width=True)
                frame_count += 1
            
            # Control frame rate
            time.sleep(frame_delay)
            
            # Stop if thread ended
            if not runner.game_thread.is_alive():
                break
                
    except Exception as e:
        st.error(f"Display error: {e}")
    finally:
        runner.running = False
        st.success(f"Game ended ({frame_count} frames displayed)")
