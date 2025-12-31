import pygame
import random
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 40
FPS = 60

# --- World Map Dimensions (Larger for scrolling) ---
WORLD_WIDTH_BLOCKS = 400
WORLD_HEIGHT_BLOCKS = 150

GRID_WIDTH = WORLD_WIDTH_BLOCKS
GRID_HEIGHT = WORLD_HEIGHT_BLOCKS

# --- Block Definitions (ID and Color) ---
AIR_ID = 0
GRASS_ID = 1
DIRT_ID = 2
STONE_ID = 3
BEDROCK_ID = 4
WATER_ID = 5
LEAVES_ID = 6
WOOL_ID = 7
PLANK_ID = 8
SAND_ID = 19
SANDSTONE_ID = 20
CACTUS_ID = 21
DEAD_BUSH_ID = 22
WOOD_ID = 18

BLOCK_TYPES = {
    0: {"name": "Air", "color": (135, 206, 235), "mineable": False, "solid": False},
    1: {"name": "Grass", "color": (0, 150, 0), "mineable": True, "min_tool_level": 0, "solid": True},
    2: {"name": "Dirt", "color": (139, 69, 19), "mineable": True, "min_tool_level": 0, "solid": True},
    3: {"name": "Stone", "color": (100, 100, 100), "mineable": True, "min_tool_level": 1, "solid": True},
    4: {"name": "Bedrock", "color": (50, 50, 50), "mineable": False, "solid": True},
    5: {"name": "Water", "color": (65, 105, 225), "mineable": False, "solid": False}, 
    6: {"name": "Leaves", "color": (34, 139, 34), "mineable": True, "min_tool_level": 0, "solid": True},
    7: {"name": "Wool", "color": (200, 200, 200), "mineable": True, "min_tool_level": 0, "solid": True},
    8: {"name": "Wood Plank", "color": (205, 133, 63), "mineable": True, "min_tool_level": 0, "solid": True},
    10: {"name": "Stick", "color": (160, 82, 45), "mineable": False, "solid": False}, 
    9: {"name": "Wood Pickaxe", "color": (139, 69, 19), "mineable": False, "tool_level": 1, "solid": False},
    11: {"name": "Coal Ore", "color": (70, 70, 70), "mineable": True, "min_tool_level": 1, "solid": True}, 
    12: {"name": "Iron Ore", "color": (180, 140, 100), "mineable": True, "min_tool_level": 2, "solid": True}, 
    13: {"name": "Rotten Flesh", "color": (100, 50, 50), "mineable": False, "solid": False},
    14: {"name": "Leather", "color": (130, 80, 50), "mineable": False, "solid": False},
    15: {"name": "Torch", "color": (255, 200, 0), "mineable": True, "min_tool_level": 0, "solid": False},
    16: {"name": "Furnace", "color": (90, 90, 90), "mineable": True, "min_tool_level": 1, "solid": True},
    17: {"name": "Stone Pickaxe", "color": (120, 120, 120), "mineable": False, "tool_level": 2, "solid": False},
    18: {"name": "Wood", "color": (101, 67, 33), "mineable": True, "min_tool_level": 0, "solid": True},
    19: {"name": "Sand", "color": (194, 178, 128), "mineable": True, "min_tool_level": 0, "solid": True},
    20: {"name": "Sandstone", "color": (160, 140, 100), "mineable": True, "min_tool_level": 1, "solid": True},
    21: {"name": "Cactus", "color": (30, 130, 50), "mineable": True, "min_tool_level": 0, "solid": True},
    22: {"name": "Dead Bush", "color": (150, 120, 80), "mineable": True, "min_tool_level": 0, "solid": False},
    23: {"name": "Porkchop", "color": (255, 150, 150), "mineable": False, "solid": False},
    24: {"name": "Feather", "color": (240, 240, 240), "mineable": False, "solid": False},
    25: {"name": "Raw Chicken", "color": (255, 200, 180), "mineable": False, "solid": False}
}

CRAFTING_RECIPES = {
    frozenset([(18, 1)]): (8, 4), 
    frozenset([(8, 2)]): (10, 4), 
    frozenset([(8, 3), (10, 2)]): (9, 1),
    frozenset([(3, 3), (10, 2)]): (17, 1),
    frozenset([(3, 8)]): (16, 1),
    frozenset([(10, 1), (11, 1)]): (15, 4)
}

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pycraft Enhanced - Minecraft Edition")
clock = pygame.time.Clock()

pygame.font.init()
FONT_SMALL = pygame.font.Font(None, 16)
FONT_BIG = pygame.font.Font(None, 24)

WORLD_MAP = [] 
CRAFTING_GRID = [0, 0, 0, 0] 
CRAFTING_AMOUNTS = [0, 0, 0, 0] 
CRAFTING_SLOT_RECTS = [] 


# --- World Decoration Functions ---
def add_trees(world, height_map):
    """Randomly adds simple trees to the world on top of grass blocks."""
    for col in range(GRID_WIDTH):
        if random.random() < 0.1:
            ground_row = height_map[col]
            if ground_row < GRID_HEIGHT and world[ground_row][col] == GRASS_ID:
                trunk_height = random.randint(3, 5)
                if ground_row - trunk_height >= 1: 
                    for r in range(ground_row - 1, ground_row - 1 - trunk_height, -1):
                        world[r][col] = WOOD_ID 
                    
                    crown_top = ground_row - 1 - trunk_height - 1
                    for r in range(crown_top, crown_top + 3):
                        for c in range(col - 1, col + 2):
                            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                                if abs(r - (crown_top + 1)) + abs(c - col) <= 2:
                                    if world[r][c] == AIR_ID: 
                                        world[r][c] = LEAVES_ID 

def add_cacti(world, height_map, start_col, end_col):
    """Randomly adds cacti to desert biome."""
    for col in range(start_col, end_col):
        if random.random() < 0.08:
            ground_row = height_map[col]
            if ground_row < GRID_HEIGHT and world[ground_row][col] == SAND_ID:
                cactus_height = random.randint(2, 4)
                if ground_row - cactus_height >= 1:
                    for r in range(ground_row - 1, ground_row - 1 - cactus_height, -1):
                        if 0 <= r < GRID_HEIGHT and world[r][col] == AIR_ID: 
                            world[r][col] = CACTUS_ID

def add_dead_bushes(world, height_map, start_col, end_col):
    """Randomly adds dead bushes to desert biome."""
    for col in range(start_col, end_col):
        if random.random() < 0.05:
            ground_row = height_map[col]
            if ground_row < GRID_HEIGHT and ground_row > 0 and world[ground_row][col] == SAND_ID:
                if world[ground_row - 1][col] == AIR_ID:
                    world[ground_row - 1][col] = DEAD_BUSH_ID


# --- IMPROVED STRUCTURE GENERATION ---
def generate_plains_village(world, height_map, col_start, village_mobs):
    """Generates a bigger village with 3-5 houses and villagers."""
    house_count = random.randint(3, 5)
    current_col = col_start
    houses_built = 0
    
    for _ in range(house_count):
        if current_col >= GRID_WIDTH - 10:
            break
            
        house_width = random.randint(5, 8)
        house_height = random.randint(4, 6)
        
        # Check for space and flatness
        valid_spot = True
        for col in range(current_col, current_col + house_width):
            if col >= GRID_WIDTH or world[height_map[col]][col] != GRASS_ID:
                valid_spot = False
                break
            if abs(height_map[col] - height_map[current_col]) > 1:
                valid_spot = False
                break
        
        if not valid_spot:
            current_col += 5
            continue
        
        ground_row = height_map[current_col]
        
        # Build house
        for r in range(ground_row - house_height, ground_row):
            for c in range(current_col, current_col + house_width):
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    if current_col < c < current_col + house_width - 1 and ground_row - house_height < r < ground_row - 1:
                        world[r][c] = AIR_ID
                    elif r == ground_row - house_height or r == ground_row - 1 or c == current_col or c == current_col + house_width - 1:
                        world[r][c] = PLANK_ID
                        
        # Roof
        roof_row = ground_row - house_height - 1
        for c in range(current_col - 1, current_col + house_width + 1):
            if 0 <= roof_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                world[roof_row][c] = WOOL_ID
                    
        # Door
        door_col = current_col + house_width // 2
        world[ground_row - 1][door_col] = AIR_ID
        world[ground_row - 2][door_col] = AIR_ID
        
        # Spawn villager near this house
        villager_x = (current_col + house_width // 2) * BLOCK_SIZE
        villager_y = (ground_row - 2) * BLOCK_SIZE
        villager = Villager(villager_x, villager_y)
        village_mobs.append(villager)
        
        houses_built += 1
        current_col += house_width + random.randint(3, 6)  # Space between houses
    
    return current_col - col_start if houses_built > 0 else 0

def generate_desert_temple(world, height_map, col_start):
    """Generates a SYMMETRICAL Sandstone pyramid structure."""
    temple_size = random.choice([9, 11, 13])  # Odd numbers for symmetry
    temple_height = temple_size // 2 + 2
    
    max_height_diff = 2
    
    # Check for space
    for col in range(col_start, col_start + temple_size):
        if col >= GRID_WIDTH or world[height_map[col]][col] != SAND_ID:
            return 0
        if abs(height_map[col] - height_map[col_start]) > max_height_diff:
            return 0
    
    print(f"✅ DESERT TEMPLE GENERATED (Symmetrical) at column {col_start}")
    
    ground_row = height_map[col_start]
    center_col = col_start + temple_size // 2
    
    # Build symmetrical pyramid
    for level in range(temple_height):
        level_row = ground_row - level - 1
        level_width = temple_size - (level * 2)
        
        if level_width <= 0:
            break
            
        level_start = center_col - level_width // 2
        level_end = center_col + level_width // 2 + 1
        
        for c in range(level_start, level_end):
            if 0 <= level_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                # Hollow interior on middle levels
                if level < temple_height - 1 and level > 0:
                    if c == level_start or c == level_end - 1:
                        world[level_row][c] = SANDSTONE_ID
                    elif level_row == ground_row - level - 1:
                        world[level_row][c] = AIR_ID if level_start < c < level_end - 1 else SANDSTONE_ID
                    else:
                        world[level_row][c] = AIR_ID if level_start < c < level_end - 1 else SANDSTONE_ID
                else:
                    world[level_row][c] = SANDSTONE_ID
    
    # Add entrance (centered)
    entrance_row = ground_row - 1
    world[entrance_row][center_col] = AIR_ID
    world[entrance_row - 1][center_col] = AIR_ID
    
    return temple_size + 5

# --- Mob Texture Creation (Minecraft-accurate) ---
def create_minecraft_spider_texture():
    """Creates a Minecraft-accurate spider (black body, red eyes)."""
    size = BLOCK_SIZE
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Black body (8x8 pixels main body)
    body_color = (25, 25, 25)
    
    # Main body (center rectangle)
    pygame.draw.rect(surf, body_color, (size//4, size//3, size//2, size//3))
    
    # Head section (smaller, in front)
    pygame.draw.rect(surf, body_color, (size//4 + 2, size//4, size//3, size//4))
    
    # Red eyes (Minecraft spider signature)
    eye_color = (255, 0, 0)
    eye_size = 4
    pygame.draw.rect(surf, eye_color, (size//3, size//4 + 2, eye_size, eye_size))
    pygame.draw.rect(surf, eye_color, (size//2, size//4 + 2, eye_size, eye_size))
    
    # Legs (4 on each side)
    leg_color = (40, 40, 40)
    leg_thickness = 2
    
    # Left legs
    for i in range(4):
        y_offset = size//3 + i * 6
        pygame.draw.line(surf, leg_color, (size//4, y_offset), (2, y_offset - 8), leg_thickness)
    
    # Right legs
    for i in range(4):
        y_offset = size//3 + i * 6
        pygame.draw.line(surf, leg_color, (3*size//4, y_offset), (size - 2, y_offset - 8), leg_thickness)
    
    return surf

def create_minecraft_cow_texture():
    """Creates the original detailed cow texture."""
    size = BLOCK_SIZE
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Legs (4 brown legs)
    leg_color = (80, 50, 30)
    pygame.draw.rect(surf, leg_color, (5, size - 12, 6, 12))  # Front left
    pygame.draw.rect(surf, leg_color, (size - 11, size - 12, 6, 12))  # Front right
    pygame.draw.rect(surf, leg_color, (15, size - 12, 6, 12))  # Back left
    pygame.draw.rect(surf, leg_color, (size - 21, size - 12, 6, 12))  # Back right
    
    # Body (brown with spots)
    pygame.draw.rect(surf, (139, 69, 19), (3, 8, size - 6, size - 20))
    
    # Spots (white/cream patches)
    pygame.draw.rect(surf, (240, 230, 210), (6, 10, 10, 8))  # Left spot
    pygame.draw.rect(surf, (240, 230, 210), (22, 12, 12, 10))  # Right spot
    pygame.draw.rect(surf, (240, 230, 210), (14, 18, 8, 6))  # Middle spot
    
    # Head (brown)
    pygame.draw.rect(surf, (139, 69, 19), (size - 10, 4, 9, 12))
    
    # Ears (small brown rectangles)
    pygame.draw.rect(surf, (120, 60, 18), (size - 12, 4, 3, 4))  # Left ear
    pygame.draw.rect(surf, (120, 60, 18), (size - 2, 4, 3, 4))  # Right ear
    
    # Snout (lighter brown)
    pygame.draw.rect(surf, (160, 90, 30), (size - 10, 11, 9, 5))
    
    # Eyes (black dots)
    pygame.draw.rect(surf, (0, 0, 0), (size - 8, 7, 2, 2))  # Left eye
    pygame.draw.rect(surf, (0, 0, 0), (size - 4, 7, 2, 2))  # Right eye
    
    return surf

def create_minecraft_sheep_texture():
    """Creates the original detailed sheep texture."""
    size = BLOCK_SIZE
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Legs (4 brown legs)
    leg_color = (101, 67, 33)
    pygame.draw.rect(surf, leg_color, (5, size - 10, 6, 10))  # Front left
    pygame.draw.rect(surf, leg_color, (size - 11, size - 10, 6, 10))  # Front right
    pygame.draw.rect(surf, leg_color, (15, size - 10, 6, 10))  # Back left
    pygame.draw.rect(surf, leg_color, (size - 21, size - 10, 6, 10))  # Back right
    
    # Body (fluffy white wool with rounded edges)
    pygame.draw.rect(surf, (255, 255, 255), (3, 8, size - 6, size - 18), 0, 5)
    
    # Wool texture details (small squares for fluffy effect)
    pygame.draw.rect(surf, (245, 245, 245), (8, 12, 8, 8))
    pygame.draw.rect(surf, (245, 245, 245), (20, 12, 8, 8))
    pygame.draw.rect(surf, (245, 245, 245), (14, 18, 8, 8))
    
    # Head (white with brown face)
    pygame.draw.rect(surf, (255, 255, 255), (size - 10, 5, 8, 10))  # Head
    pygame.draw.rect(surf, (101, 67, 33), (size - 9, 7, 6, 6))  # Face
    
    # Eyes (black dots)
    pygame.draw.rect(surf, (0, 0, 0), (size - 8, 8, 2, 2))  # Eye
    
    return surf

def create_minecraft_pig_texture():
    """Creates a Minecraft-accurate pig (pink body, snout)."""
    size = BLOCK_SIZE
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Pink body
    pig_color = (255, 180, 200)
    
    # Body
    pygame.draw.rect(surf, pig_color, (size//4, size//3, size//2, size//2))
    
    # Head
    pygame.draw.rect(surf, pig_color, (size//5, size//4, size//3, size//3))
    
    # Snout (darker pink)
    snout_color = (240, 150, 170)
    pygame.draw.rect(surf, snout_color, (size//6, size//3, size//5, size//6))
    
    # Nostrils
    pygame.draw.circle(surf, (180, 100, 120), (size//5, size//3 + 3), 2)
    pygame.draw.circle(surf, (180, 100, 120), (size//4, size//3 + 3), 2)
    
    # Legs
    leg_width = size//10
    pygame.draw.rect(surf, pig_color, (size//4, 2*size//3, leg_width, size//5))
    pygame.draw.rect(surf, pig_color, (size//2, 2*size//3, leg_width, size//5))
    
    # Eyes
    pygame.draw.circle(surf, (0, 0, 0), (size//4, size//3 - 3), 2)
    
    # Curly tail
    tail_color = (255, 180, 200)
    pygame.draw.circle(surf, tail_color, (3*size//4, size//2), 3)
    
    return surf

def create_minecraft_chicken_texture():
    """Creates a Minecraft-accurate chicken (white body, red comb, yellow beak)."""
    size = BLOCK_SIZE
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # White body
    body_color = (255, 255, 255)
    
    # Body (round-ish)
    pygame.draw.rect(surf, body_color, (size//3, size//2, size//3, size//3))
    
    # Head
    pygame.draw.circle(surf, body_color, (size//3, size//3), size//6)
    
    # Red comb on top (Minecraft chicken signature)
    comb_color = (220, 0, 0)
    pygame.draw.polygon(surf, comb_color, [
        (size//3 - 3, size//4),
        (size//3, size//5),
        (size//3 + 3, size//4)
    ])
    
    # Yellow beak
    beak_color = (255, 200, 0)
    pygame.draw.polygon(surf, beak_color, [
        (size//4, size//3),
        (size//5, size//3 + 3),
        (size//4, size//3 + 5)
    ])
    
    # Red wattle (under beak)
    wattle_color = (200, 0, 0)
    pygame.draw.circle(surf, wattle_color, (size//4 + 2, size//3 + 8), 3)
    
    # Eye
    pygame.draw.circle(surf, (0, 0, 0), (size//3 + 2, size//3 - 2), 2)
    
    # Wing
    wing_color = (240, 240, 240)
    pygame.draw.ellipse(surf, wing_color, (size//3 + 5, size//2 + 5, size//5, size//6))
    
    # Legs (yellow/orange)
    leg_color = (255, 180, 0)
    leg_width = 2
    pygame.draw.line(surf, leg_color, (size//3, 5*size//6), (size//3 - 3, size - 2), leg_width)
    pygame.draw.line(surf, leg_color, (size//2, 5*size//6), (size//2 + 3, size - 2), leg_width)
    
    return surf

def create_minecraft_zombie_texture():
    """Creates the original detailed zombie texture."""
    size = BLOCK_SIZE
    surf = pygame.Surface((size, BLOCK_SIZE * 2), pygame.SRCALPHA)
    
    # Legs (green)
    leg_color = (50, 100, 50)
    pygame.draw.rect(surf, leg_color, (8, BLOCK_SIZE * 1.2, 10, BLOCK_SIZE * 0.8))  # Left leg
    pygame.draw.rect(surf, leg_color, (22, BLOCK_SIZE * 1.2, 10, BLOCK_SIZE * 0.8))  # Right leg
    
    # Body (darker green shirt)
    pygame.draw.rect(surf, (40, 80, 70), (5, BLOCK_SIZE * 0.5, 30, BLOCK_SIZE * 0.7))
    
    # Arms (green)
    pygame.draw.rect(surf, (60, 110, 60), (0, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.5))  # Left arm
    pygame.draw.rect(surf, (60, 110, 60), (34, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.5))  # Right arm
    
    # Head (green)
    pygame.draw.rect(surf, (70, 120, 70), (10, 2, 20, 20))
    
    # Hair (dark)
    pygame.draw.rect(surf, (30, 30, 30), (10, 2, 20, 4))
    
    # Eyes (glowing red - zombie eyes)
    pygame.draw.rect(surf, (255, 0, 0), (14, 10, 4, 4))  # Left eye
    pygame.draw.rect(surf, (255, 0, 0), (22, 10, 4, 4))  # Right eye
    
    # Mouth (dark line)
    pygame.draw.rect(surf, (30, 30, 30), (14, 17, 12, 2))
    
    return surf

def create_minecraft_camel_texture():
    """Creates the original detailed camel texture."""
    w = int(BLOCK_SIZE * 1.5)
    h = int(BLOCK_SIZE * 1.5)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    
    # Legs (4 blocky legs)
    leg_color = (180, 140, 90)
    leg_width = 8
    leg_height = 20
    pygame.draw.rect(surf, leg_color, (8, h - leg_height, leg_width, leg_height))  # Front left leg
    pygame.draw.rect(surf, leg_color, (w - 16, h - leg_height, leg_width, leg_height))  # Front right leg
    pygame.draw.rect(surf, leg_color, (20, h - leg_height, leg_width, leg_height))  # Back left leg
    pygame.draw.rect(surf, leg_color, (w - 28, h - leg_height, leg_width, leg_height))  # Back right leg
    
    # Body (main rectangular body)
    body_color = (193, 154, 107)
    pygame.draw.rect(surf, body_color, (8, h - 40, w - 16, 24))
    
    # Hump (blocky rectangles stacked)
    hump_color = (180, 140, 90)
    pygame.draw.rect(surf, hump_color, (w // 2 - 10, h - 50, 20, 12))
    pygame.draw.rect(surf, hump_color, (w // 2 - 6, h - 56, 12, 6))
    
    # Neck (vertical rectangle)
    pygame.draw.rect(surf, body_color, (w - 20, h - 55, 12, 20))
    
    # Head (small rectangle)
    pygame.draw.rect(surf, body_color, (w - 20, h - 62, 12, 10))
    
    return surf

def create_minecraft_narwhal_texture():
    """Creates the original detailed narwhal texture."""
    w = int(BLOCK_SIZE * 1.2)
    h = int(BLOCK_SIZE * 0.5)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    
    # Body (rounded white/gray whale body)
    body_color = (230, 230, 255)
    pygame.draw.rect(surf, body_color, (8, 0, w - 16, h))
    
    # Darker back (top shading)
    pygame.draw.rect(surf, (200, 200, 230), (12, 0, w - 24, h // 3))
    
    # Spots (gray spots on body)
    spot_color = (180, 180, 200)
    pygame.draw.rect(surf, spot_color, (16, h // 3, 5, 3))
    pygame.draw.rect(surf, spot_color, (24, h // 4, 4, 2))
    pygame.draw.rect(surf, spot_color, (w - 20, h // 2, 3, 2))
    
    # Head (slightly lighter)
    pygame.draw.rect(surf, (240, 240, 255), (w - 12, 2, 10, h - 4))
    
    # Eye (small black dot)
    pygame.draw.rect(surf, (0, 0, 0), (w - 8, h // 3, 2, 2))
    
    # Tusk (long spiral horn - iconic narwhal feature!)
    tusk_color = (200, 200, 180)
    pygame.draw.rect(surf, tusk_color, (w - 4, h // 2 - 1, 12, 2))  # Main tusk
    
    # Tusk spiral detail (darker lines)
    for i in range(3):
        pygame.draw.rect(surf, (160, 160, 140), (w + i * 3, h // 2 - 1, 1, 2))
    
    # Flippers (two side fins)
    flipper_color = (210, 210, 235)
    pygame.draw.rect(surf, flipper_color, (18, h - 2, 8, 2))  # Left flipper
    pygame.draw.rect(surf, flipper_color, (w - 24, h - 2, 8, 2))  # Right flipper
    
    # Tail fluke (horizontal tail fin)
    pygame.draw.rect(surf, body_color, (4, h // 2 - 2, 6, 5))  # Left tail
    pygame.draw.rect(surf, body_color, (2, h // 2 - 1, 3, 3))  # Tail tip
    
    return surf

def create_villager_texture():
    """Creates a Minecraft-accurate villager (brown robe, large nose)."""
    size = BLOCK_SIZE
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Skin color (peachy)
    skin_color = (250, 200, 180)
    
    # Brown robe
    robe_color = (120, 80, 50)
    
    # Head (blocky)
    pygame.draw.rect(surf, skin_color, (size//3, size//6, size//3, size//3))
    
    # Large nose (Minecraft villager signature)
    nose_color = (230, 180, 160)
    pygame.draw.polygon(surf, nose_color, [
        (size//2 - 2, size//3),
        (size//2 - 5, size//3 + 8),
        (size//2 + 2, size//3 + 8)
    ])
    
    # Eyes (simple dots)
    pygame.draw.circle(surf, (100, 70, 50), (size//3 + 5, size//4), 2)
    pygame.draw.circle(surf, (100, 70, 50), (size//2 + 2, size//4), 2)
    
    # Unibrow
    pygame.draw.line(surf, (80, 50, 30), (size//3 + 3, size//5), (size//2 + 4, size//5), 2)
    
    # Robe body
    pygame.draw.rect(surf, robe_color, (size//4, size//2, size//2, size//2))
    
    # Arms
    pygame.draw.rect(surf, robe_color, (size//6, size//2 + 5, size//8, size//4))
    pygame.draw.rect(surf, robe_color, (2*size//3, size//2 + 5, size//8, size//4))
    
    # Hands (crossed in front)
    pygame.draw.rect(surf, skin_color, (size//3, 3*size//5, size//3, size//8))
    
    return surf


# --- Mob Classes ---
class Mob(pygame.sprite.Sprite):
    def __init__(self, x, y, max_health, speed, color, width, height, drops=None):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = speed
        self.max_health = max_health
        self.health = max_health
        self.on_ground = False
        self.drops = drops if drops else []
        self.direction = random.choice([-1, 1])
        self.move_timer = 0
        
    def update(self, player):
        self.apply_gravity()
        self.move()
        self.check_collisions()
        
    def apply_gravity(self):
        if not self.on_ground:
            self.velocity_y += 0.8
            if self.velocity_y > 15:
                self.velocity_y = 15
                
    def move(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
    def check_collisions(self):
        global WORLD_MAP
        self.on_ground = False
        
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                block_id = WORLD_MAP[row][col]
                if BLOCK_TYPES[block_id]["solid"]:
                    block_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    
                    if self.rect.colliderect(block_rect):
                        if self.velocity_y > 0:
                            self.rect.bottom = block_rect.top
                            self.velocity_y = 0
                            self.on_ground = True
                        elif self.velocity_y < 0:
                            self.rect.top = block_rect.bottom
                            self.velocity_y = 0
                            
                        if self.velocity_x > 0:
                            self.rect.right = block_rect.left
                            self.velocity_x = 0
                            self.direction *= -1
                        elif self.velocity_x < 0:
                            self.rect.left = block_rect.right
                            self.velocity_x = 0
                            self.direction *= -1
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()
            
    def die(self):
        self.kill()


class Zombie(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 2.0, (0, 100, 0), BLOCK_SIZE, int(BLOCK_SIZE * 2), drops=[(13, 1)])
        self.image = create_minecraft_zombie_texture()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.attack_damage = 3
        self.attack_cooldown = 0
        self.aggro_range = 200
        
    def update(self, player):
        super().update(player)
        
        distance_to_player = math.sqrt((self.rect.centerx - player.rect.centerx)**2 + 
                                      (self.rect.centery - player.rect.centery)**2)
        
        if distance_to_player < self.aggro_range:
            if player.rect.centerx < self.rect.centerx:
                self.velocity_x = -self.speed
                self.direction = -1
            else:
                self.velocity_x = self.speed
                self.direction = 1
        else:
            self.move_timer += 1
            if self.move_timer > 60:
                self.direction = random.choice([-1, 1])
                self.move_timer = 0
            self.velocity_x = self.direction * self.speed * 0.5
            
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
    def attack(self, player):
        if self.attack_cooldown <= 0:
            player.take_damage(self.attack_damage)
            self.attack_cooldown = 60


class Spider(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, 16, 1.5, (50, 0, 0), int(BLOCK_SIZE * 0.8), int(BLOCK_SIZE * 0.6), drops=[(10, 2)])
        self.image = create_minecraft_spider_texture()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.attack_damage = 2
        self.attack_cooldown = 0
        self.aggro_range = 250
        self.jump_cooldown = 0
        
    def update(self, player):
        super().update(player)
        
        distance_to_player = math.sqrt((self.rect.centerx - player.rect.centerx)**2 + 
                                      (self.rect.centery - player.rect.centery)**2)
        
        if distance_to_player < self.aggro_range:
            if player.rect.centerx < self.rect.centerx:
                self.velocity_x = -self.speed
                self.direction = -1
            else:
                self.velocity_x = self.speed
                self.direction = 1
                
            if self.on_ground and self.jump_cooldown <= 0 and distance_to_player < 100:
                self.velocity_y = -12
                self.jump_cooldown = 40
        else:
            self.move_timer += 1
            if self.move_timer > 80:
                self.direction = random.choice([-1, 1])
                self.move_timer = 0
            self.velocity_x = self.direction * self.speed * 0.3
            
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
            
    def attack(self, player):
        if self.attack_cooldown <= 0:
            player.take_damage(self.attack_damage)
            self.attack_cooldown = 40


class Cow(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, 10, 0.5, (139, 69, 19), int(BLOCK_SIZE * 0.9), int(BLOCK_SIZE * 0.8), drops=[(14, 2)])
        self.image = create_minecraft_cow_texture()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def update(self, player):
        super().update(player)
        
        self.move_timer += 1
        if self.move_timer > 120:
            self.direction = random.choice([-1, 0, 1])
            self.move_timer = 0
            
        self.velocity_x = self.direction * self.speed


class Sheep(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, 8, 0.5, (240, 240, 240), int(BLOCK_SIZE * 0.8), int(BLOCK_SIZE * 0.7), drops=[(7, 1)])
        self.image = create_minecraft_sheep_texture()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def update(self, player):
        super().update(player)
        
        self.move_timer += 1
        if self.move_timer > 120:
            self.direction = random.choice([-1, 0, 1])
            self.move_timer = 0
            
        self.velocity_x = self.direction * self.speed


class Pig(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, 10, 0.6, (255, 180, 200), int(BLOCK_SIZE * 0.8), int(BLOCK_SIZE * 0.7), drops=[(23, 2)])
        self.image = create_minecraft_pig_texture()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def update(self, player):
        super().update(player)
        
        self.move_timer += 1
        if self.move_timer > 100:
            self.direction = random.choice([-1, 0, 1])
            self.move_timer = 0
            
        self.velocity_x = self.direction * self.speed


class Chicken(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, 4, 0.8, (255, 255, 255), int(BLOCK_SIZE * 0.5), int(BLOCK_SIZE * 0.6), drops=[(24, 1), (25, 1)])
        self.image = create_minecraft_chicken_texture()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.flap_timer = 0
        
    def update(self, player):
        super().update(player)
        
        self.move_timer += 1
        if self.move_timer > 80:
            self.direction = random.choice([-1, 0, 1])
            self.move_timer = 0
            
        self.velocity_x = self.direction * self.speed
        
        # Chickens flap and fall slowly
        self.flap_timer += 1
        if self.flap_timer > 30 and not self.on_ground:
            self.velocity_y = min(self.velocity_y, 2)
            self.flap_timer = 0


class Camel(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 0.4, (194, 150, 100), int(BLOCK_SIZE * 1.5), int(BLOCK_SIZE * 1.2), drops=[(14, 3)])
        self.image = create_minecraft_camel_texture()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_rideable = True
        self.rider = None
        
    def update(self, player):
        if self.rider is None:
            super().update(player)
            
            self.move_timer += 1
            if self.move_timer > 150:
                self.direction = random.choice([-1, 0, 1])
                self.move_timer = 0
                
            self.velocity_x = self.direction * self.speed
        else:
            self.apply_gravity()
            self.move()
            self.check_collisions()


class Narwhal(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, 15, 1.2, (120, 140, 160), int(BLOCK_SIZE * 1.2), int(BLOCK_SIZE * 0.8), drops=[(14, 1)])
        self.image = create_minecraft_narwhal_texture()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.swim_timer = 0
        
    def update(self, player):
        # Check if in water
        col = self.rect.centerx // BLOCK_SIZE
        row = self.rect.centery // BLOCK_SIZE
        
        in_water = False
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            if WORLD_MAP[row][col] == WATER_ID:
                in_water = True
        
        if in_water:
            # Narwhal swims in water
            self.velocity_y = 0
            
            self.swim_timer += 1
            if self.swim_timer > 80:
                self.direction = random.choice([-1, 1])
                self.swim_timer = 0
                
            self.velocity_x = self.direction * self.speed
            
            # Check if approaching air (water surface or edge)
            check_col = col + (2 if self.direction > 0 else -2)
            if 0 <= check_col < GRID_WIDTH:
                # Check blocks ahead
                air_ahead = False
                for check_row in range(max(0, row - 2), min(GRID_HEIGHT, row + 2)):
                    if WORLD_MAP[check_row][check_col] == AIR_ID:
                        air_ahead = True
                        break
                
                # Turn back if approaching air
                if air_ahead:
                    self.direction *= -1
                    self.velocity_x = self.direction * self.speed
        else:
            # Out of water, apply gravity
            self.apply_gravity()
            self.velocity_x = self.direction * self.speed * 0.3
        
        self.move()
        self.check_collisions()


class Villager(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 0.3, (120, 80, 50), int(BLOCK_SIZE * 0.6), int(BLOCK_SIZE * 1.4), drops=[])
        self.image = create_villager_texture()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.wander_range = 150
        self.home_x = x
        
    def update(self, player):
        super().update(player)
        
        # Wander near spawn point
        distance_from_home = abs(self.rect.x - self.home_x)
        
        self.move_timer += 1
        if self.move_timer > 120:
            if distance_from_home > self.wander_range:
                # Return home
                self.direction = 1 if self.home_x > self.rect.x else -1
            else:
                self.direction = random.choice([-1, 0, 1])
            self.move_timer = 0
            
        self.velocity_x = self.direction * self.speed


# --- Player Class (with extended inventory) ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BLOCK_SIZE // 2, BLOCK_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 100, 200), (0, 0, BLOCK_SIZE // 2, BLOCK_SIZE // 2))
        pygame.draw.rect(self.image, (50, 50, 200), (0, BLOCK_SIZE // 2, BLOCK_SIZE // 2, BLOCK_SIZE // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 4
        self.jump_strength = 15
        self.on_ground = False
        
        # Extended inventory with armor and shield slots
        self.inventory = {}
        self.hotbar_size = 9
        self.held_block = 0
        
        # Armor slots: helmet, chestplate, leggings, boots
        self.helmet = None
        self.chestplate = None
        self.leggings = None
        self.boots = None
        
        # Shield slot
        self.shield = None
        
        # Off-hand slot
        self.offhand = None
        
        self.max_health = 20
        self.health = self.max_health
        
        self.is_crafting = False
        self.damage_flash_timer = 0
        
        self.mounted_camel = None
        self.mount_offset_y = 10
        
    def handle_input(self, keys):
        if self.is_crafting:
            return
            
        self.velocity_x = 0
        
        if self.mounted_camel is None:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.velocity_x = -self.speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.velocity_x = self.speed
            if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.on_ground:
                self.velocity_y = -self.jump_strength
        else:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.mounted_camel.velocity_x = -self.mounted_camel.speed * 3
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.mounted_camel.velocity_x = self.mounted_camel.speed * 3
            else:
                self.mounted_camel.velocity_x = 0
                
            if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.mounted_camel.on_ground:
                self.mounted_camel.velocity_y = -12
                
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.mounted_camel.rider = None
                self.mounted_camel = None
                
        if keys[pygame.K_e]:
            if not self.is_crafting:
                self.is_crafting = True
                
        for i in range(1, min(10, self.hotbar_size + 1)):
            if keys[pygame.K_0 + i]:
                self.held_block = i - 1
                
    def update(self):
        if self.mounted_camel is None:
            self.apply_gravity()
            self.move()
            self.check_collisions()
            
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
            
    def apply_gravity(self):
        if not self.on_ground:
            self.velocity_y += 0.8
            if self.velocity_y > 15:
                self.velocity_y = 15
                
    def move(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
    def check_collisions(self):
        global WORLD_MAP
        self.on_ground = False
        
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                block_id = WORLD_MAP[row][col]
                
                if BLOCK_TYPES[block_id]["solid"]:
                    block_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    
                    if self.rect.colliderect(block_rect):
                        if self.velocity_y > 0:
                            self.rect.bottom = block_rect.top
                            self.velocity_y = 0
                            self.on_ground = True
                        elif self.velocity_y < 0:
                            self.rect.top = block_rect.bottom
                            self.velocity_y = 0
                            
                        if self.velocity_x > 0:
                            self.rect.right = block_rect.left
                        elif self.velocity_x < 0:
                            self.rect.left = block_rect.right
                            
    def add_to_inventory(self, block_id, amount=1):
        if block_id in self.inventory:
            self.inventory[block_id] += amount
        else:
            self.inventory[block_id] = amount
            
    def consume_item(self, block_id, amount=1):
        if block_id in self.inventory:
            self.inventory[block_id] -= amount
            if self.inventory[block_id] <= 0:
                del self.inventory[block_id]
                
    def take_damage(self, damage):
        self.health -= damage
        self.damage_flash_timer = 30
        if self.health <= 0:
            self.health = 0
            
    def get_image(self):
        if self.damage_flash_timer > 0 and self.damage_flash_timer % 10 < 5:
            flash_img = self.image.copy()
            flash_img.fill((255, 100, 100), special_flags=pygame.BLEND_ADD)
            return flash_img
        return self.image


# --- World Generation ---
def generate_world():
    """Generates the world with biomes, lakes, structures, and mobs."""
    global WORLD_MAP
    world = [[AIR_ID for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    base_level = GRID_HEIGHT // 2
    
    # Generate height map
    height_map = [0] * GRID_WIDTH
    amplitude = 4
    frequency = 0.05
    random_offset = random.uniform(0, 10)
    
    for col in range(GRID_WIDTH):
        wave_height = math.sin(col * frequency + random_offset) * amplitude
        noise = random.uniform(-1, 1) * 0.5
        final_height = base_level + int(wave_height + noise)
        final_height = max(1, min(GRID_HEIGHT - 3, final_height))
        height_map[col] = final_height
    
    # Determine biome regions
    biome_map = []
    biome_size = 50
    
    for col in range(GRID_WIDTH):
        biome_phase = (col // biome_size) % 3
        if biome_phase == 0:
            biome_map.append(0)  # Plains
        elif biome_phase == 1:
            biome_map.append(1)  # Desert
        else:
            biome_map.append(0)  # Plains
    
    # Populate world with blocks
    for col in range(GRID_WIDTH):
        ground_level = height_map[col]
        is_desert = biome_map[col] == 1
        
        for row in range(ground_level, GRID_HEIGHT):
            if row == GRID_HEIGHT - 1:
                world[row][col] = BEDROCK_ID
            elif row == ground_level:
                if is_desert:
                    world[row][col] = SAND_ID
                else:
                    world[row][col] = GRASS_ID
            elif row < ground_level + 3:
                if is_desert:
                    world[row][col] = SAND_ID
                else:
                    world[row][col] = DIRT_ID
            else:
                block_id = STONE_ID
                
                depth = row - ground_level
                r = random.random()
                
                if depth > 10:
                    if r < 0.04:
                        block_id = 11  # Coal
                elif depth > 20:
                    if r < 0.02:
                        block_id = 11  # Coal
                    elif r < 0.11:
                        block_id = 12  # Iron
                
                world[row][col] = block_id
    
    # Lake generation and mob spawning
    mobs = pygame.sprite.Group()
    village_mobs = []
    zombies_spawned = 0
    narwhals_spawned = 0
    
    LAKE_PROBABILITY = 0.02
    MAX_LAKE_DEPTH = 5
    MAX_LAKE_WIDTH = 15
    current_lake_width = 0
    lake_bottom_row = 0
    narwhal_spawn_col = -1
    
    WORLD_MAP = world
    
    # Lake carving
    for col in range(GRID_WIDTH):
        ground_row = height_map[col]
        
        if current_lake_width == 0:
            if random.random() < LAKE_PROBABILITY:
                current_lake_width = random.randint(5, MAX_LAKE_WIDTH)
                lake_bottom_row = ground_row + random.randint(3, MAX_LAKE_DEPTH)
                lake_bottom_row = min(lake_bottom_row, GRID_HEIGHT - 5)
                narwhal_spawn_col = col
        
        if current_lake_width > 0:
            water_surface_row = ground_row
            
            for r in range(water_surface_row, lake_bottom_row):
                if 0 <= r < GRID_HEIGHT:
                    if r == lake_bottom_row - 1:
                        if biome_map[col] == 1:
                            WORLD_MAP[r][col] = SAND_ID
                        else:
                            WORLD_MAP[r][col] = DIRT_ID
                    else:
                        WORLD_MAP[r][col] = WATER_ID
            
            if col == narwhal_spawn_col:
                spawn_depth = water_surface_row + 1
                spawn_narwhal_x = col * BLOCK_SIZE
                spawn_narwhal_y = spawn_depth * BLOCK_SIZE
                
                if WORLD_MAP[spawn_depth][col] == WATER_ID:
                    mobs.add(Narwhal(spawn_narwhal_x, spawn_narwhal_y))
                    narwhals_spawned += 1
            
            current_lake_width -= 1
            
            if current_lake_width == 0:
                narwhal_spawn_col = -1
    
    # Add decorations (trees, cacti, etc.)
    add_trees(world, height_map)
    
    for col in range(GRID_WIDTH):
        if biome_map[col] == 1:
            add_cacti(world, height_map, col, col + 1)
            add_dead_bushes(world, height_map, col, col + 1)
    
    # Generate structures
    col = 50
    while col < GRID_WIDTH - 50:
        if biome_map[col] == 0:  # Plains
            width = generate_plains_village(world, height_map, col, village_mobs)
            if width > 0:
                col += width + 20
            else:
                col += 10
        elif biome_map[col] == 1:  # Desert
            width = generate_desert_temple(world, height_map, col)
            if width > 0:
                col += width + 30
            else:
                col += 15
        else:
            col += 10
    
    # Spawn mobs
    for col in range(GRID_WIDTH):
        if random.random() < 0.005:  # Reduced spawn rate
            ground_row = height_map[col]
            
            if biome_map[col] == 0:  # Plains
                spawn_y = (ground_row - 2) * BLOCK_SIZE
                spawn_x = col * BLOCK_SIZE
                
                mob_type = random.random()
                if mob_type < 0.25:
                    mobs.add(Cow(spawn_x, spawn_y))
                elif mob_type < 0.5:
                    mobs.add(Sheep(spawn_x, spawn_y))
                elif mob_type < 0.75:
                    mobs.add(Pig(spawn_x, spawn_y))
                else:
                    mobs.add(Chicken(spawn_x, spawn_y))
                    
            elif biome_map[col] == 1:  # Desert
                if random.random() < 0.5:
                    spawn_y = (ground_row - 2) * BLOCK_SIZE
                    spawn_x = col * BLOCK_SIZE
                    mobs.add(Camel(spawn_x, spawn_y))
        
        # Spawn hostile mobs at night or in caves
        if random.random() < 0.003:
            ground_row = height_map[col]
            spawn_y = (ground_row - 2) * BLOCK_SIZE
            spawn_x = col * BLOCK_SIZE
            
            if random.random() < 0.5:
                mobs.add(Zombie(spawn_x, spawn_y))
            else:
                mobs.add(Spider(spawn_x, spawn_y))
    
    # Add villagers
    for villager in village_mobs:
        mobs.add(villager)
    
    return world, mobs


# --- Drawing Functions ---
def calculate_camera_offset(player_rect):
    """Calculates camera offset to keep player centered."""
    camera_x = player_rect.centerx - SCREEN_WIDTH // 2
    camera_y = player_rect.centery - SCREEN_HEIGHT // 2
    
    camera_x = max(0, min(camera_x, GRID_WIDTH * BLOCK_SIZE - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, GRID_HEIGHT * BLOCK_SIZE - SCREEN_HEIGHT))
    
    return camera_x, camera_y

def draw_world(camera_x, camera_y):
    """Draws visible portion of the world."""
    start_col = max(0, camera_x // BLOCK_SIZE)
    end_col = min(GRID_WIDTH, (camera_x + SCREEN_WIDTH) // BLOCK_SIZE + 1)
    start_row = max(0, camera_y // BLOCK_SIZE)
    end_row = min(GRID_HEIGHT, (camera_y + SCREEN_HEIGHT) // BLOCK_SIZE + 1)
    
    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            block_id = WORLD_MAP[row][col]
            if block_id != AIR_ID:
                block_color = BLOCK_TYPES[block_id]["color"]
                screen_x = col * BLOCK_SIZE - camera_x
                screen_y = row * BLOCK_SIZE - camera_y
                pygame.draw.rect(screen, block_color, (screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE))

def draw_hud(player):
    """Draws HUD with extended inventory, armor, and shield slots."""
    # Health bar
    health_bar_width = 200
    health_bar_height = 20
    health_ratio = player.health / player.max_health
    
    pygame.draw.rect(screen, (50, 50, 50), (10, 10, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, health_bar_width * health_ratio, health_bar_height))
    
    health_text = FONT_SMALL.render(f"Health: {player.health}/{player.max_health}", True, (255, 255, 255))
    screen.blit(health_text, (15, 12))
    
    # Hotbar (bottom center)
    hotbar_start_x = SCREEN_WIDTH // 2 - (player.hotbar_size * 42) // 2
    hotbar_y = SCREEN_HEIGHT - 60
    
    inventory_items = sorted(player.inventory.items())
    
    for i in range(player.hotbar_size):
        slot_x = hotbar_start_x + i * 42
        slot_rect = pygame.Rect(slot_x, hotbar_y, 40, 40)
        
        if i == player.held_block:
            pygame.draw.rect(screen, (255, 255, 100), slot_rect, 3)
        else:
            pygame.draw.rect(screen, (100, 100, 100), slot_rect, 2)
        
        if i < len(inventory_items):
            item_id, amount = inventory_items[i]
            item_color = BLOCK_TYPES[item_id]["color"]
            pygame.draw.rect(screen, item_color, (slot_x + 5, hotbar_y + 5, 30, 30))
            
            amount_text = FONT_SMALL.render(str(amount), True, (255, 255, 255))
            screen.blit(amount_text, (slot_x + 25, hotbar_y + 25))
    
    # Armor and shield display (top right)
    armor_x = SCREEN_WIDTH - 60
    armor_y = 10
    
    armor_slots = [
        ("Helmet", player.helmet),
        ("Chest", player.chestplate),
        ("Legs", player.leggings),
        ("Boots", player.boots),
        ("Shield", player.shield)
    ]
    
    for i, (label, item) in enumerate(armor_slots):
        slot_y = armor_y + i * 45
        slot_rect = pygame.Rect(armor_x, slot_y, 40, 40)
        pygame.draw.rect(screen, (80, 80, 80), slot_rect, 2)
        
        label_text = FONT_SMALL.render(label[:3], True, (200, 200, 200))
        screen.blit(label_text, (armor_x - 30, slot_y + 12))
        
        if item:
            item_color = BLOCK_TYPES.get(item, {}).get("color", (150, 150, 150))
            pygame.draw.rect(screen, item_color, (armor_x + 5, slot_y + 5, 30, 30))
    
    # Controls help (bottom left)
    help_y = SCREEN_HEIGHT - 100
    controls = [
        "WASD/Arrows: Move",
        "Mouse: Mine/Place",
        "E: Craft",
        "1-9: Hotbar"
    ]
    
    for i, text in enumerate(controls):
        help_text = FONT_SMALL.render(text, True, (200, 200, 200))
        screen.blit(help_text, (10, help_y + i * 18))

def draw_crafting_menu(player):
    """Draws crafting menu overlay."""
    global CRAFTING_SLOT_RECTS
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    menu_width = 400
    menu_height = 400
    menu_x = (SCREEN_WIDTH - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    
    pygame.draw.rect(screen, (100, 100, 100), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, (200, 200, 200), (menu_x, menu_y, menu_width, menu_height), 3)
    
    title = FONT_BIG.render("Crafting Menu (Press E to close)", True, (255, 255, 255))
    screen.blit(title, (menu_x + 50, menu_y + 10))
    
    # 2x2 crafting grid
    grid_start_x = menu_x + 50
    grid_start_y = menu_y + 60
    slot_size = 60
    slot_spacing = 10
    
    CRAFTING_SLOT_RECTS = []
    
    for i in range(4):
        row = i // 2
        col = i % 2
        slot_x = grid_start_x + col * (slot_size + slot_spacing)
        slot_y = grid_start_y + row * (slot_size + slot_spacing)
        
        slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
        CRAFTING_SLOT_RECTS.append(slot_rect)
        
        pygame.draw.rect(screen, (60, 60, 60), slot_rect)
        pygame.draw.rect(screen, (150, 150, 150), slot_rect, 2)
        
        if CRAFTING_GRID[i] != 0:
            item_color = BLOCK_TYPES[CRAFTING_GRID[i]]["color"]
            pygame.draw.rect(screen, item_color, (slot_x + 5, slot_y + 5, slot_size - 10, slot_size - 10))
            
            amount_text = FONT_BIG.render(str(CRAFTING_AMOUNTS[i]), True, (255, 255, 255))
            screen.blit(amount_text, (slot_x + 40, slot_y + 40))
    
    # Arrow
    arrow_x = grid_start_x + 2 * (slot_size + slot_spacing) + 20
    arrow_y = grid_start_y + slot_size // 2
    pygame.draw.polygon(screen, (255, 255, 255), [
        (arrow_x, arrow_y),
        (arrow_x + 30, arrow_y - 10),
        (arrow_x + 30, arrow_y + 10)
    ])
    
    # Output slot
    output_x = arrow_x + 50
    output_y = grid_start_y + slot_size // 2 - slot_size // 2
    output_rect = pygame.Rect(output_x, output_y, slot_size, slot_size)
    CRAFTING_SLOT_RECTS.append(output_rect)
    
    pygame.draw.rect(screen, (60, 60, 60), output_rect)
    pygame.draw.rect(screen, (200, 200, 100), output_rect, 3)
    
    craftable = get_craftable_item()
    if craftable:
        output_id, output_count = craftable
        output_color = BLOCK_TYPES[output_id]["color"]
        pygame.draw.rect(screen, output_color, (output_x + 5, output_y + 5, slot_size - 10, slot_size - 10))
        
        count_text = FONT_BIG.render(str(output_count), True, (255, 255, 255))
        screen.blit(count_text, (output_x + 40, output_y + 40))
    
    # Recipe list
    inst_x = menu_x + 50
    inst_y = menu_y + 220
    
    instructions = [
        "Recipes:",
        "1 Wood → 4 Planks",
        "2 Planks → 4 Sticks",
        "3 Planks + 2 Sticks → Wood Pickaxe",
        "3 Stone + 2 Sticks → Stone Pickaxe",
        "8 Stone → Furnace",
        "1 Stick + 1 Coal → 4 Torches"
    ]
    
    for i, text in enumerate(instructions):
        inst_text = FONT_SMALL.render(text, True, (255, 255, 255))
        screen.blit(inst_text, (inst_x, inst_y + i * 20))

def get_craftable_item():
    """Returns (item_id, count) if current grid matches a recipe."""
    current_recipe = frozenset((CRAFTING_GRID[i], CRAFTING_AMOUNTS[i]) 
                               for i in range(4) if CRAFTING_GRID[i] != 0)
    
    return CRAFTING_RECIPES.get(current_recipe, None)

def handle_interaction(player, mobs, event, camera_x, camera_y):
    """Handles mining, placing, and attacking."""
    mouse_x, mouse_y = event.pos
    target_world_x = mouse_x + camera_x
    target_world_y = mouse_y + camera_y
    target_col = target_world_x // BLOCK_SIZE
    target_row = target_world_y // BLOCK_SIZE
    
    player_col = player.rect.centerx // BLOCK_SIZE
    player_row = player.rect.centery // BLOCK_SIZE
    
    distance = max(abs(target_col - player_col), abs(target_row - player_row))
    
    if distance > 4:
        return
        
    # Attack mobs
    if event.button == 1:
        mouse_rect = pygame.Rect(target_world_x - 10, target_world_y - 10, 20, 20)
        
        for mob in mobs:
            if mouse_rect.colliderect(mob.rect):
                tool_level = 0
                if player.held_block < len(list(player.inventory.keys())):
                    held_item = list(player.inventory.keys())[player.held_block]
                    tool_level = BLOCK_TYPES.get(held_item, {}).get("tool_level", 0)
                
                damage = 1 + tool_level * 2
                mob.take_damage(damage)
                
                if not mob.alive():
                    for drop_id, drop_amount in mob.drops:
                        player.add_to_inventory(drop_id, drop_amount)
                        
                # Try to mount camel
                if isinstance(mob, Camel) and mob.rider is None and player.mounted_camel is None:
                    player.mounted_camel = mob
                    mob.rider = player
                    
                return
    
    # Mine or place blocks
    if 0 <= target_row < GRID_HEIGHT and 0 <= target_col < GRID_WIDTH:
        target_block = WORLD_MAP[target_row][target_col]
        
        if event.button == 1:
            if BLOCK_TYPES[target_block]["mineable"]:
                tool_level = 0
                if player.held_block < len(list(player.inventory.keys())):
                    held_item = list(player.inventory.keys())[player.held_block]
                    tool_level = BLOCK_TYPES.get(held_item, {}).get("tool_level", 0)
                
                required_level = BLOCK_TYPES[target_block].get("min_tool_level", 0)
                
                if tool_level >= required_level:
                    WORLD_MAP[target_row][target_col] = AIR_ID
                    player.add_to_inventory(target_block, 1)
                    
        elif event.button == 3:
            if target_block == AIR_ID or not BLOCK_TYPES[target_block]["solid"]:
                if player.held_block < len(list(player.inventory.keys())):
                    block_to_place = list(player.inventory.keys())[player.held_block]
                    
                    if BLOCK_TYPES[block_to_place]["mineable"] and player.inventory[block_to_place] > 0:
                        WORLD_MAP[target_row][target_col] = block_to_place
                        player.consume_item(block_to_place, 1)

def handle_crafting_interaction(player, event):
    """Handles clicks inside the crafting menu."""
    global CRAFTING_GRID, CRAFTING_AMOUNTS
    
    for i in range(4):
        if CRAFTING_SLOT_RECTS[i].collidepoint(event.pos):
            if event.button == 1:
                held_id = player.held_block
                
                if held_id < len(list(player.inventory.keys())):
                    item_id = list(player.inventory.keys())[held_id]
                    
                    if BLOCK_TYPES.get(item_id, {}).get("mineable", True):
                        if player.inventory.get(item_id, 0) > 0:
                            if CRAFTING_GRID[i] == 0 or CRAFTING_GRID[i] == item_id:
                                CRAFTING_GRID[i] = item_id
                                CRAFTING_AMOUNTS[i] += 1
                                player.consume_item(item_id, 1)
                                
            elif event.button == 3:
                if CRAFTING_GRID[i] != 0 and CRAFTING_AMOUNTS[i] > 0:
                    player.add_to_inventory(CRAFTING_GRID[i], 1)
                    CRAFTING_AMOUNTS[i] -= 1
                    if CRAFTING_AMOUNTS[i] <= 0:
                        CRAFTING_GRID[i] = 0
                        CRAFTING_AMOUNTS[i] = 0
            return
    
    if len(CRAFTING_SLOT_RECTS) > 4 and CRAFTING_SLOT_RECTS[4].collidepoint(event.pos) and event.button == 1:
        craftable = get_craftable_item()
        if craftable:
            output_id, output_count = craftable
            
            for i in range(4):
                if CRAFTING_GRID[i] != 0:
                    CRAFTING_GRID[i] = 0
                    CRAFTING_AMOUNTS[i] = 0
            
            player.add_to_inventory(output_id, output_count)
            return

def reset_crafting_grid(player):
    """Returns items from grid to player inventory when menu closes."""
    global CRAFTING_GRID, CRAFTING_AMOUNTS
    
    for i in range(4):
        item_id = CRAFTING_GRID[i]
        amount = CRAFTING_AMOUNTS[i]
        
        if item_id != 0 and amount > 0:
            player.add_to_inventory(item_id, amount)
            
    CRAFTING_GRID = [0, 0, 0, 0]
    CRAFTING_AMOUNTS = [0, 0, 0, 0]


# --- Game Setup ---
WORLD_MAP, MOBS = generate_world()

spawn_col = GRID_WIDTH // 2
spawn_row = GRID_HEIGHT // 2
for r in range(GRID_HEIGHT):
    if WORLD_MAP[r][spawn_col] != 0:
        spawn_row = r - 2
        break

player_x = spawn_col * BLOCK_SIZE
player_y = spawn_row * BLOCK_SIZE

player = Player(player_x, player_y)
all_sprites = pygame.sprite.Group(player)
all_sprites.add(MOBS)

running = True

# --- Main Game Loop ---
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if player.is_crafting:
                reset_crafting_grid(player)
                player.is_crafting = False
            else:
                running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if player.is_crafting:
                handle_crafting_interaction(player, event)
            else:
                camera_x, camera_y = calculate_camera_offset(player.rect)
                handle_interaction(player, MOBS, event, camera_x, camera_y)
    
    # Input processing
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    
    # Game logic update
    if not player.is_crafting:
        player.update()
        MOBS.update(player)
        
        if player.mounted_camel is not None and player.mounted_camel.alive():
            player.rect.centerx = player.mounted_camel.rect.centerx
            player.rect.bottom = player.mounted_camel.rect.top + player.mount_offset_y
    
    # Mob damage
    for mob in MOBS:
        if player.rect.colliderect(mob.rect):
            if hasattr(mob, 'attack') and player.damage_flash_timer <= 0:
                mob.attack(player)
    
    camera_x, camera_y = calculate_camera_offset(player.rect)
    
    # Drawing
    screen.fill(BLOCK_TYPES[0]["color"])
    draw_world(camera_x, camera_y)
    
    if not player.is_crafting:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        target_world_x = mouse_x + camera_x
        target_world_y = mouse_y + camera_y
        target_col = target_world_x // BLOCK_SIZE
        target_row = target_world_y // BLOCK_SIZE
        
        if 0 <= target_row < GRID_HEIGHT and 0 <= target_col < GRID_WIDTH:
            player_col = player.rect.centerx // BLOCK_SIZE
            player_row = player.rect.centery // BLOCK_SIZE
            
            if max(abs(target_col - player_col), abs(target_row - player_row)) <= 4:
                highlight_x = target_col * BLOCK_SIZE - camera_x
                highlight_y = target_row * BLOCK_SIZE - camera_y
                highlight_rect = pygame.Rect(highlight_x, highlight_y, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, (0, 0, 0), highlight_rect, 3)
    
    # Draw mobs
    for mob in MOBS:
        mob_screen_pos = (mob.rect.x - camera_x, mob.rect.y - camera_y)
        screen.blit(mob.image, mob_screen_pos)
        
        if mob.health < mob.max_health:
            bar_width = mob.rect.width
            bar_height = 5
            health_ratio = mob.health / mob.max_health
            pygame.draw.rect(screen, (50, 50, 50), (mob_screen_pos[0], mob_screen_pos[1] - 10, bar_width, bar_height))
            pygame.draw.rect(screen, (255, 0, 0), (mob_screen_pos[0], mob_screen_pos[1] - 10, bar_width * health_ratio, bar_height))
    
    player_screen_pos = (player.rect.x - camera_x, player.rect.y - camera_y)
    screen.blit(player.get_image(), player_screen_pos)
    
    draw_hud(player)
    
    if player.is_crafting:
        draw_crafting_menu(player)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
