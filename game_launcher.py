# PyCraft Web - Universal Game Launcher
# Launches any game version based on user selection

import asyncio
import pygame
import sys
import os

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
    {"name": "🏰 Pre-Classic", "file": "pre_classic", "status": "beta"},
    {"name": "🟫 Classic 1 - Beginning", "file": "classic1", "status": "beta"},
    {"name": "🟫 Classic 2 - Survival", "file": "classic2", "status": "beta"},
    {"name": "🟫 Classic 3 - Multiplayer", "file": "classic3", "status": "beta"},
    {"name": "🟫 Classic 4 - Creative", "file": "classic4", "status": "beta"},
    {"name": "🟫 Classic 5 - Mobs", "file": "classic5", "status": "playable"},
    {"name": "🟫 Classic 6 - World", "file": "classic6", "status": "beta"},
    {"name": "🟫 Classic 7 - Complete", "file": "classic7", "status": "beta"},
    {"name": "🏠 Indev 1 - Basics", "file": "indev1", "status": "beta"},
    {"name": "🏠 Indev 2 - Building", "file": "indev2", "status": "beta"},
    {"name": "🏠 Indev 3 - Caves", "file": "indev3", "status": "beta"},
    {"name": "🏠 Indev 4 - Redstone", "file": "indev4", "status": "beta"},
    {"name": "🏠 Indev 5 - Farming", "file": "indev5", "status": "beta"},
    {"name": "🏠 Indev 6 - Combat", "file": "indev6", "status": "beta"},
    {"name": "🏠 Indev 7 - Dimensions", "file": "indev7", "status": "beta"},
    {"name": "⚡ Alpha 1", "file": "alpha1", "status": "beta"},
    {"name": "⚡ Alpha 2", "file": "alpha2", "status": "beta"},
    {"name": "🌍 Alpha 3 - Overworld", "file": "alpha3", "status": "beta"},
    {"name": "🌍 Alpha 4 - Overworld", "file": "alpha4_overworld", "status": "beta"},
    {"name": "🌍 Alpha v1.0 - Overworld", "file": "alpha_v1_overworld", "status": "beta"},
    {"name": "🔮 Alpha 4 - End", "file": "alpha4_end", "status": "beta"},
    {"name": "🔮 Alpha v1.0 - End", "file": "alpha_v1_end", "status": "beta"},
    {"name": "🔥 Alpha 4 - Nether", "file": "alpha4_nether", "status": "beta"},
    {"name": "🔥 Alpha v1.0 - Nether", "file": "alpha_v1_nether", "status": "beta"},
    {"name": "📱 Bedrock Mobile", "file": "bedrock", "status": "beta"},
    {"name": "🧪 Experimental", "file": "experimental", "status": "beta"},
]

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
    subtitle = subtitle_font.render("Browser Edition - Select Your Version", True, WHITE)
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

async def run_classic5():
    """Launch Classic 5 game"""
    from classic5_web import run_game
    return await run_game()

async def launch_game(game_file):
    """Universal game launcher - loads any version"""
    # Import game registry
    try:
        from game_registry import get_game
        
        # Get the game function
        game_func = get_game(game_file)
        
        if game_func:
            return await game_func()
        else:
            # Fallback to placeholder
            return await show_placeholder(game_file)
            
    except ImportError as e:
        print(f"Import error: {e}")
        return await show_placeholder(game_file)

async def show_placeholder(game_file):
    """Show placeholder for games not yet converted to async"""
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
    running = True
    
    # Get game name from GAME_VERSIONS
    game_name = next((v["name"] for v in GAME_VERSIONS if v["file"] == game_file), game_file)
    
    while running:
        screen.fill((60, 80, 120))
        
        # Title
        msg = font.render(f"{game_name}", True, WHITE)
        shadow = font.render(f"{game_name}", True, BLACK)
        rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        screen.blit(shadow, (rect.x + 2, rect.y + 2))
        screen.blit(msg, rect)
        
        # Status
        status = small_font.render("🎮 Coming Soon to Web!", True, GOLD)
        status_rect = status.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(status, status_rect)
        
        # Instructions
        info = small_font.render("Download full version to play this", True, LIGHT_GRAY)
        info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        screen.blit(info, info_rect)
        
        info2 = small_font.render("Press ESC to return", True, LIGHT_GRAY)
        info2_rect = info2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        screen.blit(info2, info2_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

async def run_alpha3():
    """Launch Alpha 3 game"""
    font = pygame.font.Font(None, 64)
    running = True
    
    while running:
        screen.fill((34, 139, 34))
        
        msg = font.render("🌍 Alpha 3 Loading...", True, WHITE)
        shadow = font.render("🌍 Alpha 3 Loading...", True, BLACK)
        rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(shadow, (rect.x + 2, rect.y + 2))
        screen.blit(msg, rect)
        
        small_font = pygame.font.Font(None, 32)
        info = small_font.render("Press ESC to return to launcher", True, LIGHT_GRAY)
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
