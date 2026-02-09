# PyCraft Desktop Launcher - Pure Pygame, No Web Required
# Works offline on any computer

import pygame
import sys
import os
from pathlib import Path

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("⛏️ PyCraft - Desktop Edition")
clock = pygame.time.Clock()

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
RED = (220, 50, 50)

# Fonts
try:
    TITLE_FONT = pygame.font.Font(None, 96)
    SUBTITLE_FONT = pygame.font.Font(None, 48)
    BUTTON_FONT = pygame.font.Font(None, 36)
    SMALL_FONT = pygame.font.Font(None, 24)
except:
    TITLE_FONT = pygame.font.SysFont('arial', 96)
    SUBTITLE_FONT = pygame.font.SysFont('arial', 48)
    BUTTON_FONT = pygame.font.SysFont('arial', 36)
    SMALL_FONT = pygame.font.SysFont('arial', 24)

# Game versions - LOCAL DESKTOP VERSIONS
GAME_VERSIONS = [
    {"name": "🏰 Pre-Classic", "file": "Pre-Classic.py", "folder": ""},
    {"name": "🟫 Classic 1", "file": "Classic 1.py", "folder": "Classic"},
    {"name": "🟫 Classic 2", "file": "Classic 2.py", "folder": "Classic"},
    {"name": "🟫 Classic 3", "file": "Classic 3.py", "folder": "Classic"},
    {"name": "🟫 Classic 4", "file": "Classic 4.py", "folder": "Classic"},
    {"name": "🟫 Classic 5", "file": "Classic 5.py", "folder": "Classic"},
    {"name": "🟫 Classic 6", "file": "Classic 6.py", "folder": "Classic"},
    {"name": "🟫 Classic 7", "file": "Classic 7.py", "folder": "Classic"},
    {"name": "🏠 Indev 1", "file": "Indev 1.py", "folder": "Indev"},
    {"name": "🏠 Indev 2", "file": "Indev 2.py", "folder": "Indev"},
    {"name": "🏠 Indev 3", "file": "Indev 3.py", "folder": "Indev"},
    {"name": "🏠 Indev 4", "file": "Indev 4.py", "folder": "Indev"},
    {"name": "🏠 Indev 5", "file": "Indev 5.py", "folder": "Indev"},
    {"name": "🏠 Indev 6", "file": "Indev 6.py", "folder": "Indev"},
    {"name": "🏠 Indev 7", "file": "Indev 7.py", "folder": "Indev"},
    {"name": "⚡ Alpha 1", "file": "Alpha 1.py", "folder": "Alpha"},
    {"name": "⚡ Alpha 2", "file": "Alpha 2.py", "folder": "Alpha"},
    {"name": "🌍 Alpha 3 - Overworld", "file": "Alpha 3 Overworld.py", "folder": "Alpha"},
    {"name": "🌍 Alpha 4 - Overworld", "file": "Alpha 4 Overworld.py", "folder": "Alpha"},
    {"name": "🌍 Alpha v1.0 - Overworld", "file": "Alpha v1.0 Overworld.py", "folder": "Alpha"},
    {"name": "🔮 Alpha 4 - End", "file": "Alpha 4 End.py", "folder": "Alpha"},
    {"name": "🔮 Alpha v1.0 - End", "file": "Alpha v1.0 End.py", "folder": "Alpha"},
    {"name": "🔥 Alpha 4 - Nether", "file": "Alpha 4-snapshot 1.py", "folder": "Alpha"},
    {"name": "🔥 Alpha v1.0 - Nether", "file": "Alpha v1.0 Nether.py", "folder": "Alpha"},
    {"name": "🧪 Experimental", "file": "Experimental.py", "folder": ""},
]

selected_version = 0
scroll_offset = 0

class Button:
    def __init__(self, x, y, width, height, text, color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
        self.enabled = True
    
    def draw(self, surface):
        if not self.enabled:
            color = GRAY
        elif self.hover:
            color = BRIGHT_GREEN
        else:
            color = self.color
        
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=10)
        
        text = BUTTON_FONT.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
    
    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def draw_gradient_background(surface):
    """Draw a nice gradient background"""
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        color = (
            int(20 + ratio * 20),
            int(30 + ratio * 30),
            int(50 + ratio * 50)
        )
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

def draw_title(surface):
    """Draw the main title"""
    # Shadow
    title_shadow = TITLE_FONT.render("⛏️ PyCraft", True, BLACK)
    title_shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, 84))
    surface.blit(title_shadow, title_shadow_rect)
    
    # Title
    title = TITLE_FONT.render("⛏️ PyCraft", True, GOLD)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
    surface.blit(title, title_rect)
    
    # Subtitle
    subtitle = SMALL_FONT.render("Desktop Edition - Select Your Game", True, LIGHT_GRAY)
    subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 150))
    surface.blit(subtitle, subtitle_rect)

def draw_version_list(surface):
    """Draw the list of game versions"""
    list_x = 50
    list_y = 200
    list_width = SCREEN_WIDTH - 100
    list_height = SCREEN_HEIGHT - 300
    
    # Background
    pygame.draw.rect(surface, DARK_GRAY, (list_x, list_y, list_width, list_height), border_radius=15)
    pygame.draw.rect(surface, GOLD, (list_x, list_y, list_width, list_height), 3, border_radius=15)
    
    # Versions
    visible_count = 8
    item_height = 50
    start_idx = scroll_offset
    end_idx = min(start_idx + visible_count, len(GAME_VERSIONS))
    
    for i in range(start_idx, end_idx):
        version = GAME_VERSIONS[i]
        y_pos = list_y + 20 + (i - start_idx) * (item_height + 10)
        
        # Check if file exists
        if version["folder"]:
            file_path = Path(version["folder"]) / version["file"]
        else:
            file_path = Path(version["file"])
        
        exists = file_path.exists()
        
        # Highlight selected
        if i == selected_version:
            pygame.draw.rect(surface, BLUE, (list_x + 10, y_pos, list_width - 20, item_height), border_radius=8)
        
        # Version name
        color = WHITE if exists else RED
        text = BUTTON_FONT.render(version["name"], True, color)
        surface.blit(text, (list_x + 30, y_pos + 10))
        
        # Status indicator
        if exists:
            status = SMALL_FONT.render("✅ Available", True, BRIGHT_GREEN)
        else:
            status = SMALL_FONT.render("❌ Not Found", True, RED)
        surface.blit(status, (list_x + list_width - 200, y_pos + 15))
    
    # Scroll indicators
    if scroll_offset > 0:
        arrow_up = BUTTON_FONT.render("▲ Scroll Up", True, LIGHT_GRAY)
        surface.blit(arrow_up, (list_x + 20, list_y - 30))
    
    if end_idx < len(GAME_VERSIONS):
        arrow_down = BUTTON_FONT.render("▼ Scroll Down", True, LIGHT_GRAY)
        surface.blit(arrow_down, (list_x + 20, list_y + list_height + 10))

def draw_controls(surface):
    """Draw control instructions"""
    y_pos = SCREEN_HEIGHT - 80
    
    controls = [
        "↑↓ Arrow Keys: Select Game",
        "ENTER or Click: Play Selected",
        "ESC: Exit Launcher"
    ]
    
    x_start = 100
    x_spacing = 350
    
    for i, control in enumerate(controls):
        text = SMALL_FONT.render(control, True, LIGHT_GRAY)
        surface.blit(text, (x_start + i * x_spacing, y_pos))

def launch_game(version_idx):
    """Launch the selected game"""
    version = GAME_VERSIONS[version_idx]
    
    if version["folder"]:
        file_path = Path(version["folder"]) / version["file"]
    else:
        file_path = Path(version["file"])
    
    if not file_path.exists():
        print(f"❌ Game file not found: {file_path}")
        return False
    
    print(f"🎮 Launching {version['name']}...")
    print(f"📂 Path: {file_path}")
    
    # Close launcher
    pygame.quit()
    
    # Launch the game
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(file_path)])
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error launching game: {e}")
        return False
    finally:
        # Restart launcher after game closes
        pygame.init()
        global screen, clock
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("⛏️ PyCraft - Desktop Edition")
        clock = pygame.time.Clock()

def main():
    """Main launcher loop"""
    global selected_version, scroll_offset
    
    running = True
    play_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 150, 300, 60, "🎮 PLAY", GREEN)
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    selected_version = max(0, selected_version - 1)
                    # Auto scroll
                    if selected_version < scroll_offset:
                        scroll_offset = selected_version
                elif event.key == pygame.K_DOWN:
                    selected_version = min(len(GAME_VERSIONS) - 1, selected_version + 1)
                    # Auto scroll
                    if selected_version >= scroll_offset + 8:
                        scroll_offset = selected_version - 7
                elif event.key == pygame.K_RETURN:
                    launch_game(selected_version)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel up
                    scroll_offset = max(0, scroll_offset - 1)
                elif event.button == 5:  # Mouse wheel down
                    scroll_offset = min(len(GAME_VERSIONS) - 8, scroll_offset + 1)
            
            # Button handling
            if play_button.handle_event(event):
                launch_game(selected_version)
        
        # Drawing
        draw_gradient_background(screen)
        draw_title(screen)
        draw_version_list(screen)
        draw_controls(screen)
        play_button.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
