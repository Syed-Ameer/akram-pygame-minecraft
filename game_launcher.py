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

# Game versions available
GAME_VERSIONS = [
    {"name": "🟫 Classic 5 - Mobs & Crafting", "file": "classic5"},
    {"name": "🌍 Alpha 3 - Overworld Adventure", "file": "alpha3"},
    {"name": "🎮 Quick Demo", "file": "demo"},
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
    version = version_font.render(version_text, True, WHITE)
    version_rect = version.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    # Version box
    box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 400, SCREEN_HEIGHT // 2 - 60, 800, 120)
    pygame.draw.rect(surface, DARK_GRAY, box_rect, border_radius=15)
    pygame.draw.rect(surface, GREEN, box_rect, 4, border_radius=15)
    surface.blit(version, version_rect)
    
    # Instructions
    inst_font = pygame.font.Font(None, 28)
    inst = inst_font.render("← → Arrow Keys to Select | ENTER to Play", True, LIGHT_GRAY)
    inst_rect = inst.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
    surface.blit(inst, inst_rect)
    
    # Footer
    footer = inst_font.render(f"Version {selected_version + 1} of {len(GAME_VERSIONS)}", True, GRAY)
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
            
            if game_file == "demo":
                # Run demo then return
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        in_launcher = True
                
                await run_demo()
                
            elif game_file == "classic5":
                continue_launcher = await run_classic5()
                if continue_launcher:
                    in_launcher = True
                else:
                    running = False
                    
            elif game_file == "alpha3":
                continue_launcher = await run_alpha3()
                if continue_launcher:
                    in_launcher = True
                else:
                    running = False
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
