# Classic 5 - Browser Web Version
# Simplified async-compatible version for Pygbag

import pygame
import random
import math
import asyncio

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BLOCK_SIZE = 40
FPS = 60

# World
WORLD_WIDTH = 200
WORLD_HEIGHT = 100

# Block IDs
AIR = 0
GRASS = 1
DIRT = 2
STONE = 3
BEDROCK = 4
WOOD = 18
LEAVES = 6
COAL = 11

# Colors
COLORS = {
    AIR: (135, 206, 235),
    GRASS: (0, 150, 0),
    DIRT: (139, 69, 19),
    STONE: (100, 100, 100),
    BEDROCK: (50, 50, 50),
    WOOD: (101, 67, 33),
    LEAVES: (34, 139, 34),
    COAL: (70, 70, 70),
}

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.inventory = {WOOD: 0, STONE: 0, DIRT: 0, GRASS: 0, COAL: 0}
        self.selected_block = DIRT
        self.mining_progress = 0
        self.mining_pos = None
    
    def update(self, world):
        # Apply gravity
        if not self.on_ground:
            self.vy += 0.5
        
        # Move
        self.x += self.vx
        self.y += self.vy
        
        # Collision
        self.on_ground = False
        
        # Check collisions
        px = int(self.x // BLOCK_SIZE)
        py = int(self.y // BLOCK_SIZE)
        
       # Bottom collision
        if py + 1 < WORLD_HEIGHT:
            if world[py + 1][px] != AIR:
                self.y = py * BLOCK_SIZE
                self.vy = 0
                self.on_ground = True
        
        # Horizontal collision
        if self.vx > 0:  # Moving right
            if px + 1 < WORLD_WIDTH and world[py][px + 1] != AIR:
                self.vx = 0
        elif self.vx < 0:  # Moving left
            if px > 0 and world[py][px] != AIR:
                self.vx = 0
    
    def jump(self):
        if self.on_ground:
            self.vy = -10
            self.on_ground = False

def generate_world():
    """Generate a simple world"""
    world = [[AIR for _ in range(WORLD_WIDTH)] for _ in range(WORLD_HEIGHT)]
    
    # Generate terrain
    for x in range(WORLD_WIDTH):
        height = int(50 + math.sin(x * 0.1) * 5)
        
        # Bedrock
        world[WORLD_HEIGHT - 1][x] = BEDROCK
        
        # Stone layer
        for y in range(height + 5, WORLD_HEIGHT - 1):
            world[y][x] = STONE
            
            # Add coal
            if random.random() < 0.05:
                world[y][x] = COAL
        
        # Dirt layer
        for y in range(height, height + 5):
            world[y][x] = DIRT
        
        # Grass top
        if height < WORLD_HEIGHT:
            world[height][x] = GRASS
        
        # Trees
        if random.random() < 0.05 and height > 10:
            trunk_height = 4
            for ty in range(height - trunk_height, height):
                if ty >= 0:
                    world[ty][x] = WOOD
            
            # Leaves
            for ly in range(height - trunk_height - 2, height - trunk_height + 1):
                for lx in range(x - 2, x + 3):
                    if 0 <= ly < WORLD_HEIGHT and 0 <= lx < WORLD_WIDTH:
                        if world[ly][lx] == AIR:
                            world[ly][lx] = LEAVES
    
    return world

def draw_world(screen, world, camera_x, camera_y):
    """Draw the visible world"""
    start_x = max(0, int(camera_x // BLOCK_SIZE))
    end_x = min(WORLD_WIDTH, int((camera_x + SCREEN_WIDTH) // BLOCK_SIZE) + 1)
    start_y = max(0, int(camera_y // BLOCK_SIZE))
    end_y = min(WORLD_HEIGHT, int((camera_y + SCREEN_HEIGHT) // BLOCK_SIZE) + 1)
    
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            block = world[y][x]
            if block != AIR:
                color = COLORS.get(block, (255, 0, 255))
                rect = pygame.Rect(
                    x * BLOCK_SIZE - camera_x,
                    y * BLOCK_SIZE - camera_y,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)

def draw_ui(screen, player, font):
    """Draw UI elements"""
    # Inventory
    y_pos = 10
    pygame.draw.rect(screen, (50, 50, 50), (10, y_pos, 250, 150), border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), (10, y_pos, 250, 150), 3, border_radius=10)
    
    text = font.render("Inventory:", True, (255, 255, 255))
    screen.blit(text, (20, y_pos + 10))
    
    y_pos += 40
    for block_id, count in player.inventory.items():
        if count > 0:
            block_name = {WOOD: "Wood", STONE: "Stone", DIRT: "Dirt", GRASS: "Grass", COAL: "Coal"}.get(block_id, "Item")
            text = font.render(f"{block_name}: {count}", True, (255, 255, 255))
            screen.blit(text, (20, y_pos))
            y_pos += 25
    
    # Controls
    controls = [
        "Controls:",
        "← → Move",
        "SPACE Jump",
        "LEFT CLICK Mine",
        "RIGHT CLICK Place",
        "ESC Return to Menu"
    ]
    
    y_pos = 10
    for line in controls:
        text = font.render(line, True, (255, 255, 255))
        shadow = font.render(line, True, (0, 0, 0))
        screen.blit(shadow, (SCREEN_WIDTH - 202, y_pos + 2))
        screen.blit(text, (SCREEN_WIDTH - 200, y_pos))
        y_pos += 25

async def run_game():
    """Main game loop"""
    # Setup
    screen = pygame.display.get_surface()
    if not screen:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    pygame.display.set_caption("🟫 Classic 5 - Mining & Crafting")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)
    
    # Generate world
    world = generate_world()
    
    # Create player
    spawn_x = WORLD_WIDTH // 2 * BLOCK_SIZE
    spawn_y = 20 * BLOCK_SIZE
    player = Player(spawn_x, spawn_y)
    
    camera_x = player.x - SCREEN_WIDTH // 2
    camera_y = player.y - SCREEN_HEIGHT // 2
    
    running = True
    keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False}
    
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True  # Return to launcher
                elif event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key in keys:
                    keys[event.key] = True
            
            elif event.type == pygame.KEYUP:
                if event.key in keys:
                    keys[event.key] = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Get mouse world position
                mx, my = event.pos
                world_x = int((mx + camera_x) // BLOCK_SIZE)
                world_y = int((my + camera_y) // BLOCK_SIZE)
                
                if 0 <= world_x < WORLD_WIDTH and 0 <= world_y < WORLD_HEIGHT:
                    if event.button == 1:  # Left click - mine
                        block = world[world_y][world_x]
                        if block not in [AIR, BEDROCK]:
                            if block in player.inventory:
                                player.inventory[block] += 1
                            else:
                                player.inventory[block] = 1
                            world[world_y][world_x] = AIR
                    
                    elif event.button == 3:  # Right click - place
                        if world[world_y][world_x] == AIR:
                            # Place selected block
                            if player.selected_block in player.inventory:
                                if player.inventory[player.selected_block] > 0:
                                    world[world_y][world_x] = player.selected_block
                                    player.inventory[player.selected_block] -= 1
        
        # Update player movement
        player.vx = 0
        if keys[pygame.K_LEFT]:
            player.vx = -5
        if keys[pygame.K_RIGHT]:
            player.vx = 5
        
        player.update(world)
        
        # Update camera
        camera_x = player.x - SCREEN_WIDTH // 2
        camera_y = player.y - SCREEN_HEIGHT // 2
        camera_x = max(0, min(camera_x, WORLD_WIDTH * BLOCK_SIZE - SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, WORLD_HEIGHT * BLOCK_SIZE - SCREEN_HEIGHT))
        
        #Draw
        screen.fill((135, 206, 235))  # Sky
        draw_world(screen, world, camera_x, camera_y)
        
        # Draw player
        player_screen_x = player.x - camera_x
        player_screen_y = player.y - camera_y
        pygame.draw.rect(screen, (255, 100, 100), 
                        (player_screen_x, player_screen_y, BLOCK_SIZE - 5, BLOCK_SIZE * 2))
        
        draw_ui(screen, player, font)
        
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)  # Required for Pygbag
    
    return True