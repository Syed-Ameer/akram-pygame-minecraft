# PyCraft Desktop - Universal Game Launcher
# Launches actual game files with auto-dependency installation

import asyncio
import pygame
import sys
import os
import subprocess
from pathlib import Path

# Auto-install dependencies on first run
def auto_install_dependencies():
    """Install required packages if missing"""
    required = ["pygame", "pillow", "numpy"]
    
    print("🔧 Checking dependencies...")
    missing = []
    
    for package in required:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"📦 Installing {len(missing)} packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing, 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ All dependencies installed!")
        except Exception as e:
            print(f"⚠️ Install warning: {e}")
    else:
        print("✅ All dependencies ready!")

# Run installer at startup
try:
    auto_install_dependencies()
except:
    pass

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = None
clock = None

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
DARKER_GRAY = (20, 20, 20)
GREEN = (46, 139, 87)
BRIGHT_GREEN = (0, 255, 127)
BLUE = (100, 149, 237)
GOLD = (255, 215, 0)

# Game versions available (ALL VERSIONS!)
GAME_VERSIONS = [
    {"name": "🏰 Pre-Classic", "file": "pre_classic", "status": "playable"},
    {"name": "🟫 Classic 1 - Beginning", "file": "classic1", "status": "playable"},
    {"name": "🟫 Classic 2 - Survival", "file": "classic2", "status": "playable"},
    {"name": "🟫 Classic 3 - Multiplayer", "file": "classic3", "status": "playable"},
    {"name": "🟫 Classic 4 - Creative", "file": "classic4", "status": "playable"},
    {"name": "🟫 Classic 5 - Mobs", "file": "classic5", "status": "playable"},
    {"name": "🟫 Classic 6 - World", "file": "classic6", "status": "playable"},
    {"name": "🟫 Classic 7 - Complete", "file": "classic7", "status": "playable"},
    {"name": "🏠 Indev 1 - Basics", "file": "indev1", "status": "playable"},
    {"name": "🏠 Indev 2 - Building", "file": "indev2", "status": "playable"},
    {"name": "🏠 Indev 3 - Caves", "file": "indev3", "status": "playable"},
    {"name": "🏠 Indev 4 - Redstone", "file": "indev4", "status": "playable"},
    {"name": "🏠 Indev 5 - Farming", "file": "indev5", "status": "playable"},
    {"name": "🏠 Indev 6 - Combat", "file": "indev6", "status": "playable"},
    {"name": "🏠 Indev 7 - Dimensions", "file": "indev7", "status": "playable"},
    {"name": "⚡ Alpha 1", "file": "alpha1", "status": "playable"},
    {"name": "⚡ Alpha 2", "file": "alpha2", "status": "playable"},
    {"name": "🌍 Alpha 3 - Overworld", "file": "alpha3", "status": "playable"},
    {"name": "🌍 Alpha 4 - Overworld", "file": "alpha4_overworld", "status": "playable"},
    {"name": "🌍 Alpha v1.0 - Overworld", "file": "alpha_v1_overworld", "status": "playable"},
    {"name": "🔮 Alpha 4 - End", "file": "alpha4_end", "status": "playable"},
    {"name": "🔮 Alpha v1.0 - End", "file": "alpha_v1_end", "status": "playable"},
    {"name": "🔥 Alpha 4 - Nether", "file": "alpha4_nether", "status": "playable"},
    {"name": "🔥 Alpha v1.0 - Nether", "file": "alpha_v1_nether", "status": "playable"},
    {"name": "📱 Bedrock Mobile", "file": "bedrock", "status": "playable"},
    {"name": "🧪 Experimental", "file": "experimental", "status": "playable"},
]

# Map game IDs to actual Python file paths
GAME_FILE_PATHS = {
    "pre_classic": "Pre-Classic.py",
    "classic1": "Classic/Classic 1.py",
    "classic2": "Classic/Classic 2.py",
    "classic3": "Classic/Classic 3.py",
    "classic4": "Classic/Classic 4.py",
    "classic5": "Classic/Classic 5.py",
    "classic6": "Classic/Classic 6.py",
    "classic7": "Classic/Classic 7.py",
    "indev1": "Indev/Indev 1.py",
    "indev2": "Indev/Indev 2.py",
    "indev3": "Indev/Indev 3.py",
    "indev4": "Indev/Indev 4.py",
    "indev5": "Indev/Indev 5.py",
    "indev6": "Indev/Indev 6.py",
    "indev7": "Indev/Indev 7.py",
    "alpha1": "Alpha/Alpha 1.py",
    "alpha2": "Alpha/Alpha 2.py",
    "alpha3": "Alpha/Alpha 3 Overworld.py",
    "alpha4_overworld": "Alpha/Alpha 4 Overworld.py",
    "alpha_v1_overworld": "Alpha/Alpha v1.0 Overworld.py",
    "alpha4_end": "Alpha/Alpha 4 End.py",
    "alpha_v1_end": "Alpha/Alpha v1.0 End.py",
    "alpha4_nether": "Alpha/Alpha 4-snapshot 1.py",
    "alpha_v1_nether": "Alpha/Alpha v1.0 Nether.py",
    "bedrock": "Alpha/pycraft_bedrock_mobile.py",
    "experimental": "Experimental.py",
}

selected_version = 0
game_launched = False

class Button:
    def __init__(self, x, y, width, height, text, color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
    
    def draw(self, surface):
        color = BRIGHT_GREEN if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=10)
        
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def draw_launcher(surface):
    """Draw the game launcher screen"""
    surface.fill(DARKER_GRAY)
    
    # Title
    title_font = pygame.font.Font(None, 72)
    title = title_font.render("⛏️ PyCraft", True, GOLD)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
    # Shadow
    shadow = title_font.render("⛏️ PyCraft", True, BLACK)
    surface.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
    surface.blit(title, title_rect)
    
    # Subtitle
    subtitle_font = pygame.font.Font(None, 32)
    subtitle = subtitle_font.render("Desktop Edition - All Games Playable!", True, WHITE)
    subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 160))
    surface.blit(subtitle, subtitle_rect)
    
    # Version display
    version_font = pygame.font.Font(None, 48)
    version_text = GAME_VERSIONS[selected_version]["name"]
    
    # Add status indicator
    status = GAME_VERSIONS[selected_version].get("status", "soon")
    if status == "playable":
        status_text = " ✅"
        status_color = BRIGHT_GREEN
    elif status == "beta":
        status_text = " 🧪"
        status_color = BLUE
    else:
        status_text = " 🔜"
        status_color = GOLD
    
    version = version_font.render(version_text + status_text, True, WHITE)
    version_rect = version.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    # Version box
    box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 500, SCREEN_HEIGHT // 2 - 60, 1000, 120)
    pygame.draw.rect(surface, DARK_GRAY, box_rect, border_radius=15)
    pygame.draw.rect(surface, status_color, box_rect, 4, border_radius=15)
    surface.blit(version, version_rect)
    
    # Status legend
    legend_font = pygame.font.Font(None, 24)
    legend = legend_font.render("✅ Fully Tested | 🧪 Web Beta | 🔜 Coming Soon", True, LIGHT_GRAY)
    legend_rect = legend.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    surface.blit(legend, legend_rect)
    
    # Instructions
    inst_font = pygame.font.Font(None, 28)
    inst = inst_font.render("← → Arrow Keys to Select | ENTER to Play", True, LIGHT_GRAY)
    inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
    surface.blit(inst, inst_rect)
    
    # Footer
    playable_count = sum(1 for v in GAME_VERSIONS if v.get("status") == "playable")
    beta_count = sum(1 for v in GAME_VERSIONS if v.get("status") == "beta")
    footer = inst_font.render(f"{playable_count} Stable | {beta_count} Beta | {len(GAME_VERSIONS)} Total | Version {selected_version + 1}/{len(GAME_VERSIONS)}", True, GRAY)
    footer_rect = footer.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
    surface.blit(footer, footer_rect)

async def run_demo():
    """Quick demo game"""
    screen.fill((135, 206, 235))  # Sky blue
    
    # Draw grass
    pygame.draw.rect(screen, (34, 139, 34), (0, SCREEN_HEIGHT - 300, SCREEN_WIDTH, 300))
    
    # Message
    font = pygame.font.Font(None, 48)
    msg = font.render("🎮 Demo Mode - Press ESC to return", True, WHITE)
    shadow = font.render("🎮 Demo Mode - Press ESC to return", True, BLACK)
    rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(shadow, (rect.x + 2, rect.y + 2))
    screen.blit(msg, rect)
    
    pygame.display.flip()
    await asyncio.sleep(0)

async def launch_game(game_file):
    """Launch actual Python game file"""
    global screen
    
    # Get actual file path
    file_path = GAME_FILE_PATHS.get(game_file)
    if not file_path:
        return await show_error(f"Game file not found: {game_file}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        return await show_error(f"File missing: {file_path}")
    
    # Show loading screen
    show_loading_screen(game_file)
    
    # Hide launcher window (minimize pygame)
    pygame.display.iconify()
    
    try:
        # Launch game in new process
        print(f"🎮 Launching {file_path}...")
        process = subprocess.Popen([sys.executable, file_path], 
                                  cwd=os.getcwd(),
                                  creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
        
        # Wait for game to finish
        while process.poll() is None:
            await asyncio.sleep(0.1)
        
        print(f"✅ Game closed (exit code: {process.returncode})")
        
    except Exception as e:
        print(f"❌ Launch error: {e}")
        return await show_error(f"Failed to launch: {e}")
    
    # Restore launcher window
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("⛏️ PyCraft - Game Launcher")
    
    return True  # Return to launcher

def show_loading_screen(game_file):
    """Display loading screen"""
    screen.fill(DARKER_GRAY)
    
    game_name = next((v["name"] for v in GAME_VERSIONS if v["file"] == game_file), game_file)
    
    font = pygame.font.Font(None, 64)
    title = font.render(f"🎮 {game_name}", True, GOLD)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
    screen.blit(title, title_rect)
    
    small_font = pygame.font.Font(None, 36)
    status = small_font.render("Loading...", True, WHITE)
    status_rect = status.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    screen.blit(status, status_rect)
    
    pygame.display.flip()

async def show_error(message):
    """Show error message"""
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
    
    waiting = True
    while waiting:
        screen.fill((80, 20, 20))
        
        title = font.render("❌ Error", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        screen.blit(title, title_rect)
        
        msg = small_font.render(str(message)[:60], True, LIGHT_GRAY)
        msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(msg, msg_rect)
        
        info = small_font.render("Press ESC to return", True, WHITE)
        info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        screen.blit(info, info_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    
    return True

async def main():
    """Main launcher loop"""
    global screen, clock, selected_version, game_launched
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("⛏️ PyCraft - Game Launcher")
    clock = pygame.time.Clock()
    
    running = True
    in_launcher = True
    
    while running:
        if in_launcher:
            # Launcher screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        selected_version = (selected_version - 1) % len(GAME_VERSIONS)
                    elif event.key == pygame.K_RIGHT:
                        selected_version = (selected_version + 1) % len(GAME_VERSIONS)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Launch selected game
                        game_file = GAME_VERSIONS[selected_version]["file"]
                        in_launcher = False
            
            draw_launcher(screen)
            pygame.display.flip()
            clock.tick(60)
            await asyncio.sleep(0)
        
        else:
            # Game is running
            game_file = GAME_VERSIONS[selected_version]["file"]
            
            # Use universal launcher
            continue_launcher = await launch_game(game_file)
            if continue_launcher:
                in_launcher = True
            else:
                running = False
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
