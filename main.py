# PyCraft Web - Pygbag Compatible Version
# This is a simplified launcher that works in the browser

import asyncio
import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PyCraft - Web Edition")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (46, 139, 87)
BLUE = (100, 149, 237)
BROWN = (139, 69, 19)

# Font
try:
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
except:
    font = pygame.font.SysFont('Arial', 48)
    small_font = pygame.font.SysFont('Arial', 32)

clock = pygame.time.Clock()

# Game state
menu_state = "main"
selected_option = 0

menu_options = [
    "Classic 1",
    "Classic 2", 
    "Indev 1",
    "Alpha 1",
    "Quit"
]

async def main():
    global menu_state, selected_option
    
    running = True
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if menu_state == "main":
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        option = menu_options[selected_option]
                        if option == "Quit":
                            running = False
                        else:
                            print(f"Selected: {option}")
                            # You would launch the selected game here
        
        # Clear screen
        screen.fill(BLUE)
        
        # Draw title
        title_text = font.render("PyCraft - Web Edition", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle = small_font.render("Use Arrow Keys + Enter to Select", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(subtitle, subtitle_rect)
        
        # Draw menu options
        for i, option in enumerate(menu_options):
            color = GREEN if i == selected_option else WHITE
            text = small_font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 50))
            screen.blit(text, text_rect)
            
            # Draw selection indicator
            if i == selected_option:
                pygame.draw.rect(screen, GREEN, 
                               (text_rect.left - 10, text_rect.top, 
                                text_rect.width + 20, text_rect.height), 2)
        
        # Draw info
        info = small_font.render("Browser version - Full game available for download", True, WHITE)
        info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(info, info_rect)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
        
        # Yield control to browser (REQUIRED for Pygbag)
        await asyncio.sleep(0)
    
    pygame.quit()
    sys.exit()

# Start the game
asyncio.run(main())
