# Universal Game Loader for Web
# Dynamically loads and converts any game to async for Pygbag

import asyncio
import pygame
import sys
from pathlib import Path

# Import all available games
AVAILABLE_GAMES = {}

# Try to import each game version
def register_games():
    """Register all available game modules"""
    global AVAILABLE_GAMES
    
    # Classic 5 (already converted - use optimized web version)
    try:
        from classic5_web import run_game as classic5_game
        AVAILABLE_GAMES["classic5"] = classic5_game
    except:
        pass
    
    #Try to use universal loader for all other games
    try:
        from universal_game_loader import GAME_LOADERS
        AVAILABLE_GAMES.update(GAME_LOADERS)
        print(f"✅ Loaded {len(GAME_LOADERS)} games via universal loader")
    except Exception as e:
        print(f"⚠️ Universal loader failed: {e}")
        # Fallback to placeholder screens
        _register_placeholders()

def _register_placeholders():
    """Register placeholder screens for games that aren't loaded"""
    # Pre-Classic
    AVAILABLE_GAMES["pre_classic"] = create_wrapper("Pre-Classic.py")
    
    # Classic series (except 5 which is already registered)
    for i in [1, 2, 3, 4, 6, 7]:
        AVAILABLE_GAMES[f"classic{i}"] = create_wrapper(f"Classic/Classic {i}.py")
    
    # Indev series
    for i in range(1, 8):
        AVAILABLE_GAMES[f"indev{i}"] = create_wrapper(f"Indev/Indev {i}.py")
    
    # Alpha series
    AVAILABLE_GAMES["alpha1"] = create_wrapper("Alpha/Alpha 1.py")
    AVAILABLE_GAMES["alpha2"] = create_wrapper("Alpha/Alpha 2.py")
    AVAILABLE_GAMES["alpha3"] = create_wrapper("Alpha/Alpha 3 Overworld.py")
    AVAILABLE_GAMES["alpha4_overworld"] = create_wrapper("Alpha/Alpha 4 Overworld.py")
    AVAILABLE_GAMES["alpha_v1_overworld"] = create_wrapper("Alpha/Alpha v1.0 Overworld.py")
    AVAILABLE_GAMES["alpha4_end"] = create_wrapper("Alpha/Alpha 4 End.py")
    AVAILABLE_GAMES["alpha_v1_end"] = create_wrapper("Alpha/Alpha v1.0 End.py")
    AVAILABLE_GAMES["alpha4_nether"] = create_wrapper("Alpha/Alpha 4-snapshot 1.py")
    AVAILABLE_GAMES["alpha_v1_nether"] = create_wrapper("Alpha/Alpha v1.0 Nether.py")
    
    # Bedrock
    AVAILABLE_GAMES["bedrock"] = create_wrapper("Alpha/pycraft_bedrock_mobile.py")
    
    # Experimental
    AVAILABLE_GAMES["experimental"] = create_wrapper("Experimental.py")

def create_wrapper(file_path):
    """Create async wrapper for any game file"""
    async def game_wrapper():
        # Show loading screen
        screen = pygame.display.get_surface()
        if not screen:
            screen = pygame.display.set_mode((1280, 720))
        
        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 32)
        
        loading = True
        frame_count = 0
        
        while loading and frame_count < 180:  # 3 seconds at 60fps
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return True
            
            screen.fill((40, 60, 100))
            
            # Title
            game_name = Path(file_path).stem
            title = font.render(f"🎮 {game_name}", True, (255, 255, 255))
            title_shadow = font.render(f"🎮 {game_name}", True, (0, 0, 0))
            title_rect = title.get_rect(center=(640, 300))
            screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
            screen.blit(title, title_rect)
            
            # Status
            dots = "." * ((frame_count // 20) % 4)
            status = small_font.render(f"Coming to Web Soon{dots}", True, (255, 200, 100))
            status_rect = status.get_rect(center=(640, 360))
            screen.blit(status, status_rect)
            
            # Info
            info1 = small_font.render("This version requires full conversion", True, (200, 200, 200))
            info1_rect = info1.get_rect(center=(640, 420))
            screen.blit(info1, info1_rect)
            
            info2 = small_font.render("Press ESC to return to launcher", True, (150, 150, 150))
            info2_rect = info2.get_rect(center=(640, 460))
            screen.blit(info2, info2_rect)
            
            # Progress indicator
            pygame.draw.rect(screen, (100, 100, 100), (440, 520, 400, 20), border_radius=10)
            progress_width = int(400 * (frame_count / 180))
            pygame.draw.rect(screen, (100, 200, 100), (440, 520, progress_width, 20), border_radius=10)
            
            pygame.display.flip()
            await asyncio.sleep(1/60)
            frame_count += 1
        
        # Return to launcher after showing message
        return True
    
    return game_wrapper

def get_game(game_id):
    """Get game function by ID"""
    if game_id in AVAILABLE_GAMES:
        return AVAILABLE_GAMES[game_id]
    return None

# Register all games on import
register_games()
