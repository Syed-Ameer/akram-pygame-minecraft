# PyCraft Web - Instant Game Launch
# Launches games directly without launcher screens

import asyncio
import pygame
import sys
import os

# Detect which version to launch (can be set via URL parameter or default)
LAUNCH_VERSION = os.environ.get("PYCRAFT_VERSION", "alpha3")  # Default to Alpha 3

async def launch_alpha3():
    """Launch Alpha 3 Overworld - Async version"""
    # Import the game module
    sys.path.append('Alpha')
    
    # Simple version - will make a converted async game
    from alpha3_web import run_game
    await run_game()

async def launch_classic5():
    """Launch Classic 5 - Async version"""
    sys.path.append('Classic')
    
    from classic5_web import run_game
    await run_game()

async def main():
    """Main entry point - launches selected game"""
    if LAUNCH_VERSION == "alpha3":
        await launch_alpha3()
    elif LAUNCH_VERSION == "classic5":
        await launch_classic5()
    else:
        # Default quick demo
        await quick_demo()

async def quick_demo():
    """Quick demo game that runs instantly"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("🎮 PyCraft - Loading...")
    clock = pygame.time.Clock()
    
    running = True
    message = "🎮 PyCraft Web Edition\n\n✨ Full games coming soon!\n\nPress SPACE to see a demo"
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    message = "🌟 Demo Mode Active!\n\n← → Move\nESC Quit"
        
        screen.fill((135, 206, 235))  # Sky blue
        
        # Draw grass
        pygame.draw.rect(screen, (34, 139, 34), (0, 400, 800, 200))
        
        # Draw message
        y = 150
        for line in message.split('\n'):
            text = small_font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(400, y))
            # Shadow
            shadow = small_font.render(line, True, (0, 0, 0))
            screen.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
            screen.blit(text, text_rect)
            y += 40
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # Required for Pygbag
    
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
