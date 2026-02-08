# Universal Game Loader - Runs any Pygame game in browser with async support
# Dynamically wraps existing games for Pygbag compatibility

import asyncio
import pygame
import importlib.util
import sys
from pathlib import Path
import types

class AsyncGameLoader:
    """Loads and runs any Pygame game with async support"""
    
    def __init__(self, game_file_path):
        self.game_path = Path(game_file_path)
        self.module = None
        self.game_name = self.game_path.stem
        
    async def load_and_run(self):
        """Load the game module and run its main loop with async support"""
        
        # Show loading screen
        screen = pygame.display.get_surface()
        if not screen:
            screen = pygame.display.set_mode((1280, 720))
        
        font = pygame.font.Font(None, 64)
        small_font = pygame.font.Font(None, 32)
        
        # Loading animation
        for frame in range(60):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return True
            
            screen.fill((30, 50, 80))
            
            title = font.render(f"🎮 {self.game_name}", True, (255, 255, 255))
            title_shadow = font.render(f"🎮 {self.game_name}", True, (0, 0, 0))
            title_rect = title.get_rect(center=(640, 300))
            screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
            screen.blit(title, title_rect)
            
            dots = "." * ((frame // 15) % 4)
            status = small_font.render(f"Loading{dots}", True, (100, 200, 255))
            status_rect = status.get_rect(center=(640, 400))
            screen.blit(status, status_rect)
            
            pygame.display.flip()
            await asyncio.sleep(1/60)
        
        # Try to load and run the actual game
        try:
            await self._run_game_module()
        except Exception as e:
            print(f"❌ Error running {self.game_name}: {e}")
            await self._show_error(str(e))
        
        return True
    
    async def _run_game_module(self):
        """Load and execute the game module"""
        # Load the module
        spec = importlib.util.spec_from_file_location(self.game_name, self.game_path)
        if spec and spec.loader:
            self.module = importlib.util.module_from_spec(spec)
            sys.modules[self.game_name] = self.module
            
            # Inject asyncio support into the module
            self._inject_async_support()
            
            # Execute the module
            spec.loader.exec_module(self.module)
            
            # Try to find and run the main game loop
            await self._find_and_run_main_loop()
    
    def _inject_async_support(self):
        """Inject async-friendly versions of blocking calls"""
        if self.module:
            # Store original asyncio for use in game
            self.module.asyncio = asyncio
            
            # Create async-friendly clock
            original_clock = pygame.time.Clock
            
            class AsyncClock:
                def __init__(self):
                    self._clock = original_clock()
                    self._last_tick = pygame.time.get_ticks()
                
                def tick(self, fps=60):
                    """Non-blocking tick that returns immediately"""
                    current = pygame.time.get_ticks()
                    delta = current - self._last_tick
                    self._last_tick = current
                    return delta
                
                async def tick_async(self, fps=60):
                    """Async version that yields control"""
                    await asyncio.sleep(0)
                    return self.tick(fps)
            
            self.module.AsyncClock = AsyncClock
    
    async def _find_and_run_main_loop(self):
        """Try to find and run the game's main loop"""
        if not self.module:
            return
        
        # Strategy 1: Look for a main() function
        if hasattr(self.module, 'main'):
            main_func = getattr(self.module, 'main')
            if asyncio.iscoroutinefunction(main_func):
                await main_func()
            else:
                # Run in executor to avoid blocking
                await asyncio.get_event_loop().run_in_executor(None, main_func)
        
        # Strategy 2: Look for a 'running' game loop
        elif hasattr(self.module, 'running'):
            await self._run_traditional_loop()
        
        # Strategy 3: Module executed its own main loop during import
        else:
            print(f"✅ {self.game_name} ran its own main loop")
    
    async def _run_traditional_loop(self):
        """Run a traditional Pygame loop with async yields"""
        frame_count = 0
        clock = pygame.time.Clock()
        
        while getattr(self.module, 'running', True):
            # Process one frame
            if hasattr(self.module, 'handle_events'):
                self.module.handle_events()
            if hasattr(self.module, 'update'):
                self.module.update()
            if hasattr(self.module, 'draw'):
                self.module.draw()
            
            pygame.display.flip()
            clock.tick(60)
            
            # Yield control every frame
            await asyncio.sleep(0)
            
            frame_count += 1
            if frame_count > 108000:  # 30 minutes max
                break
    
    async def _show_error(self, error_msg):
        """Show error screen"""
        screen = pygame.display.get_surface()
        if not screen:
            return
        
        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 24)
        
        for _ in range(180):  # Show for 3 seconds
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    return
            
            screen.fill((80, 20, 20))
            
            title = font.render("⚠️ Error Loading Game", True, (255, 255, 255))
            title_rect = title.get_rect(center=(640, 300))
            screen.blit(title, title_rect)
            
            # Split error message into lines
            error_lines = error_msg.split('\n')[:5]
            for i, line in enumerate(error_lines):
                error_text = small_font.render(line[:70], True, (255, 200, 200))
                error_rect = error_text.get_rect(center=(640, 360 + i * 30))
                screen.blit(error_text, error_rect)
            
            info = small_font.render("Press any key to return", True, (200, 200, 200))
            info_rect = info.get_rect(center=(640, 550))
            screen.blit(info, info_rect)
            
            pygame.display.flip()
            await asyncio.sleep(1/60)


# Factory functions for each game version
def create_game_loader(game_file):
    """Create an async game loader for any game file"""
    async def game_runner():
        loader = AsyncGameLoader(game_file)
        return await loader.load_and_run()
    return game_runner


# Export loader functions for all games
GAME_LOADERS = {
    # Pre-Classic
    "pre_classic": create_game_loader("Pre-Classic.py"),
    
    # Classic Series
    "classic1": create_game_loader("Classic/Classic 1.py"),
    "classic2": create_game_loader("Classic/Classic 2.py"),
    "classic3": create_game_loader("Classic/Classic 3.py"),
    "classic4": create_game_loader("Classic/Classic 4.py"),
    "classic5": create_game_loader("Classic/Classic 5.py"),
    "classic6": create_game_loader("Classic/Classic 6.py"),
    "classic7": create_game_loader("Classic/Classic 7.py"),
    
    # Indev Series
    "indev1": create_game_loader("Indev/Indev 1.py"),
    "indev2": create_game_loader("Indev/Indev 2.py"),
    "indev3": create_game_loader("Indev/Indev 3.py"),
    "indev4": create_game_loader("Indev/Indev 4.py"),
    "indev5": create_game_loader("Indev/Indev 5.py"),
    "indev6": create_game_loader("Indev/Indev 6.py"),
    "indev7": create_game_loader("Indev/Indev 7.py"),
    
    # Alpha Series
    "alpha1": create_game_loader("Alpha/Alpha 1.py"),
    "alpha2": create_game_loader("Alpha/Alpha 2.py"),
    "alpha3": create_game_loader("Alpha/Alpha 3 Overworld.py"),
    "alpha4_overworld": create_game_loader("Alpha/Alpha 4 Overworld.py"),
    "alpha_v1_overworld": create_game_loader("Alpha/Alpha v1.0 Overworld.py"),
    "alpha4_end": create_game_loader("Alpha/Alpha 4 End.py"),
    "alpha_v1_end": create_game_loader("Alpha/Alpha v1.0 End.py"),
    "alpha4_nether": create_game_loader("Alpha/Alpha 4-snapshot 1.py"),
    "alpha_v1_nether": create_game_loader("Alpha/Alpha v1.0 Nether.py"),
    
    # Experimental
    "experimental": create_game_loader("Experimental.py"),
}
