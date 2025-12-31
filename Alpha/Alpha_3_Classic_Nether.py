import pygame
import random
import math
import pickle
import os
import sys

# Cannot import from overworld as it has no main guard and will execute the entire game
# Instead, we'll define a NetherPlayer based on the overworld's Player class
USING_OVERWORLD_CLASSES = False
print("🔥 Using Nether-optimized Player class")



# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 40
FPS = 60
SHOW_GRID = True  # Show coordinate grid

# --- Nether World Dimensions ---
WORLD_WIDTH_BLOCKS = 1280  # Same as overworld
GRID_WIDTH = WORLD_WIDTH_BLOCKS
GRID_HEIGHT = 128  # Shorter than overworld (128 vs 150)

# --- Nether Block ID Constants ---
AIR_ID = 0
NETHERRACK_ID = 250
SOUL_SAND_ID = 251
GLOWSTONE_ID = 252
NETHER_BRICK_ID = 253
NETHER_QUARTZ_ORE_ID = 254
LAVA_ID = 199  # Same as overworld
BEDROCK_ID = 4
NETHER_WART_ID = 255
NETHER_FORTRESS_BRICK_ID = 256
MAGMA_BLOCK_ID = 257
ENDER_PEARL_ID = 222
BLAZE_ROD_ID = 223
FIRE_ID = 220
OBSIDIAN_ID = 221

# --- Nether Block Types ---
BLOCK_TYPES = {
    0: {"name": "Air", "color": (135, 206, 235), "mineable": False, "solid": False},
    4: {"name": "Bedrock", "color": (50, 50, 50), "mineable": False, "solid": True},
    199: {"name": "Lava", "color": (255, 100, 0), "mineable": False, "solid": False},
    250: {"name": "Netherrack", "color": (115, 30, 30), "mineable": True, "min_tool_level": 1, "solid": True},
    251: {"name": "Soul Sand", "color": (84, 64, 51), "mineable": True, "min_tool_level": 0, "solid": True},
    252: {"name": "Glowstone", "color": (255, 200, 100), "mineable": True, "min_tool_level": 1, "solid": True, "emits_light": True, "drops": (151, 4)},  # Drops 4 glowstone dust
    253: {"name": "Nether Brick", "color": (44, 21, 26), "mineable": True, "min_tool_level": 1, "solid": True},
    254: {"name": "Nether Quartz Ore", "color": (145, 90, 90), "mineable": True, "min_tool_level": 1, "solid": True, "drops": (160, 1)},  # Drops nether quartz
    255: {"name": "Nether Wart", "color": (139, 0, 0), "mineable": True, "min_tool_level": 0, "solid": False},
    256: {"name": "Nether Fortress Brick", "color": (35, 17, 21), "mineable": True, "min_tool_level": 1, "solid": True},
    257: {"name": "Magma Block", "color": (140, 50, 0), "mineable": True, "min_tool_level": 1, "solid": True},
    # Portal blocks
    220: {"name": "Fire", "color": (255, 150, 0), "mineable": True, "min_tool_level": 0, "solid": False},
    221: {"name": "Obsidian", "color": (20, 10, 30), "mineable": True, "min_tool_level": 5, "solid": True},
    # Items
    151: {"name": "Glowstone Dust", "color": (255, 230, 150), "mineable": False, "solid": False},
    160: {"name": "Nether Quartz", "color": (230, 220, 210), "mineable": False, "solid": False},
}

# Global variables
WORLD_MAP = []
MOBS = pygame.sprite.Group()
DROPPED_ITEMS = pygame.sprite.Group()
PROJECTILES = pygame.sprite.Group()  # For blaze fireballs
LIGHT_SOURCES = set()

# Nether has no day/night cycle - always dark red ambiance
NETHER_AMBIANCE_COLOR = (80, 20, 20)  # Dark red tint

# Merge nether block types with overworld block types
# Update BLOCK_TYPES to include nether blocks while keeping original blocks
BLOCK_TYPES.update({
    199: {"name": "Lava", "color": (255, 100, 0), "mineable": False, "solid": False},
    250: {"name": "Netherrack", "color": (115, 30, 30), "mineable": True, "min_tool_level": 1, "solid": True},
    251: {"name": "Soul Sand", "color": (84, 64, 51), "mineable": True, "min_tool_level": 0, "solid": True},
    252: {"name": "Glowstone", "color": (255, 200, 100), "mineable": True, "min_tool_level": 1, "solid": True, "emits_light": True, "drops": (151, 4)},
    253: {"name": "Nether Brick", "color": (44, 21, 26), "mineable": True, "min_tool_level": 1, "solid": True},
    254: {"name": "Nether Quartz Ore", "color": (145, 90, 90), "mineable": True, "min_tool_level": 1, "solid": True, "drops": (160, 1)},
    255: {"name": "Nether Wart", "color": (139, 0, 0), "mineable": True, "min_tool_level": 0, "solid": False},
    256: {"name": "Nether Fortress Brick", "color": (35, 17, 21), "mineable": True, "min_tool_level": 1, "solid": True},
    257: {"name": "Magma Block", "color": (140, 50, 0), "mineable": True, "min_tool_level": 1, "solid": True},
    220: {"name": "Fire", "color": (255, 150, 0), "mineable": True, "min_tool_level": 0, "solid": False},
    221: {"name": "Obsidian", "color": (20, 10, 30), "mineable": True, "min_tool_level": 5, "solid": True},
    151: {"name": "Glowstone Dust", "color": (255, 230, 150), "mineable": False, "solid": False},
    160: {"name": "Nether Quartz", "color": (230, 220, 210), "mineable": False, "solid": False},
    222: {"name": "Ender Pearl", "color": (0, 200, 150), "mineable": False, "solid": False},
    223: {"name": "Blaze Rod", "color": (255, 200, 50), "mineable": False, "solid": False},
})

# --- SAVE/LOAD SYSTEM ---
def save_nether_state(player, mobs, world_map, filename="nether_save.pkl"):
    """Saves the complete nether state to a file."""
    # Convert player position to overworld coordinates for spawning back
    overworld_x, overworld_y = convert_nether_to_overworld_coords(player.rect.x, player.rect.y)
    
    # Handle both inventory types (inventory or inventory_slots)
    inventory_data = player.inventory if hasattr(player, 'inventory') else getattr(player, 'inventory_slots', [(0, 0)] * 27)
    
    save_data = {
        'player_pos': (player.rect.x, player.rect.y),
        'overworld_return': (overworld_x, overworld_y),  # Where to spawn in overworld
        'player_health': player.health,
        'player_hunger': player.hunger,
        'player_hotbar': player.hotbar_slots,
        'player_inventory': inventory_data,
        'player_armor': player.armor_slots,
        'player_tool_durability': player.tool_durability,
        'world_map': world_map,
        'mobs': [(type(mob).__name__, mob.rect.x, mob.rect.y, mob.health) for mob in mobs]
    }
    
    with open(filename, 'wb') as f:
        pickle.dump(save_data, f)
    print(f"💾 Nether saved to {filename}")


def load_nether_state(filename="nether_save.pkl"):
    """Loads the nether state from a file."""
    if not os.path.exists(filename):
        print(f"⚠️ No save file found: {filename}")
        return None
    
    with open(filename, 'rb') as f:
        save_data = pickle.load(f)
    print(f"📂 Nether loaded from {filename}")
    return save_data

def load_overworld_state(filename="overworld_save.pkl"):
    """Loads the overworld state from a file."""
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'rb') as f:
        save_data = pickle.load(f)
    return save_data


def convert_nether_to_overworld_coords(nether_x, nether_y):
    """Convert nether coordinates to overworld (multiply by 8)."""
    return nether_x * 8, nether_y * 8


def convert_overworld_to_nether_coords(overworld_x, overworld_y):
    """Convert overworld coordinates to nether (divide by 8)."""
    return overworld_x // 8, overworld_y // 8


def is_inside_portal(world_map, col, row):
    """Check if player is inside a lit nether portal (obsidian frame with fire)."""
    OBSIDIAN_ID = 221
    FIRE_ID = 220
    
    # Look for obsidian frame pattern with fire inside
    for dc in range(-3, 4):
        check_col = col + dc
        if 0 <= check_col < GRID_WIDTH:
            obsidian_count = 0
            for dr in range(-3, 4):
                check_row = row + dr
                if 0 <= check_row < GRID_HEIGHT:
                    if world_map[check_row][check_col] == OBSIDIAN_ID:
                        obsidian_count += 1
            
            if obsidian_count >= 3:
                for dr in [-3, -2, 2, 3]:
                    check_row = row + dr
                    if 0 <= check_row < GRID_HEIGHT:
                        horizontal_count = 0
                        fire_found = False
                        
                        for dc2 in range(-3, 4):
                            check_col2 = col + dc2
                            if 0 <= check_col2 < GRID_WIDTH:
                                if world_map[check_row][check_col2] == OBSIDIAN_ID:
                                    horizontal_count += 1
                                if world_map[check_row][check_col2] == FIRE_ID:
                                    fire_found = True
                        
                        if horizontal_count >= 3 and fire_found:
                            return True
    return False


SHOULD_RETURN_TO_OVERWORLD = False

def return_to_overworld():
    """Signal nether main loop to return control to caller (Overworld).

    This avoids quitting the Python process or launching a new process, allowing
    an in-process seamless transition when the overworld imports and calls
    `pycraft_nether.main(overworld_save=...)`.
    """
    global SHOULD_RETURN_TO_OVERWORLD
    print("🌍 Returning to Overworld (in-process)...")
    SHOULD_RETURN_TO_OVERWORLD = True


# --- Nether World Generation ---
def generate_nether():
    """Generates the Nether dimension with netherrack, lava lakes, glowstone, and fortresses."""
    global WORLD_MAP, LIGHT_SOURCES
    
    world = []
    
    # Fill with air
    for _ in range(GRID_HEIGHT):
        world.append([AIR_ID] * GRID_WIDTH)
    
    # Bedrock ceiling and floor (multiple layers for safety)
    for col in range(GRID_WIDTH):
        world[0][col] = BEDROCK_ID  # Ceiling bedrock
        world[1][col] = BEDROCK_ID  # Extra ceiling layer
        world[GRID_HEIGHT - 1][col] = BEDROCK_ID  # Floor bedrock
        world[GRID_HEIGHT - 2][col] = BEDROCK_ID
        world[GRID_HEIGHT - 3][col] = BEDROCK_ID  # Extra floor layer
    
    # Create solid base layers (prevents falling through)
    for row in range(GRID_HEIGHT - 15, GRID_HEIGHT - 3):
        for col in range(GRID_WIDTH):
            world[row][col] = NETHERRACK_ID
    
    # Fill middle section with netherrack (higher density)
    for row in range(10, GRID_HEIGHT - 15):
        for col in range(GRID_WIDTH):
            if random.random() < 0.95:  # 95% netherrack, 5% air for small caves
                world[row][col] = NETHERRACK_ID
    
    # Add some horizontal platforms for safety every 15 blocks
    for platform_row in range(20, GRID_HEIGHT - 20, 15):
        for col in range(GRID_WIDTH):
            if random.random() < 0.7:  # 70% chance for platform blocks
                world[platform_row][col] = NETHERRACK_ID
    
    # Fill in any dangerous single-block gaps
    for row in range(5, GRID_HEIGHT - 5):
        for col in range(2, GRID_WIDTH - 2):
            if world[row][col] == AIR_ID:
                # Check if surrounded by solid blocks
                solid_neighbors = 0
                for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                    nr, nc = row + dr, col + dc
                    if BLOCK_TYPES.get(world[nr][nc], {}).get("solid", False):
                        solid_neighbors += 1
                # Fill in if mostly surrounded (prevents small holes)
                if solid_neighbors >= 3:
                    world[row][col] = NETHERRACK_ID
    
    # Create safe spawn platform in the center
    spawn_col = GRID_WIDTH // 2
    spawn_row = 50
    for r in range(spawn_row - 3, spawn_row + 10):
        for c in range(spawn_col - 20, spawn_col + 20):
            if 0 <= c < GRID_WIDTH and 0 <= r < GRID_HEIGHT:
                if r < spawn_row + 1:  # Solid platform below spawn
                    world[r][c] = NETHERRACK_ID
                elif r <= spawn_row + 3:  # Clear air above spawn
                    world[r][c] = AIR_ID
    
    # Add lava lakes throughout the nether (fewer and smaller)
    for _ in range(30):  # Reduced from 50 to 30 lava lakes
        lake_col = random.randint(50, GRID_WIDTH - 50)  # Keep away from edges
        lake_row = random.randint(30, GRID_HEIGHT - 25)  # Keep away from floor
        lake_width = random.randint(3, 8)  # Smaller lakes (was 5-12)
        lake_depth = random.randint(1, 3)  # Shallower (was 2-5)
        
        # Ensure solid ground around lava
        for r in range(lake_row - 1, min(lake_row + lake_depth + 2, GRID_HEIGHT - 2)):
            for c in range(lake_col - 1, min(lake_col + lake_width + 1, GRID_WIDTH)):
                if r == lake_row - 1 or r == lake_row + lake_depth + 1 or c == lake_col - 1 or c == lake_col + lake_width:
                    # Build walls around lava
                    if world[r][c] != BEDROCK_ID:
                        world[r][c] = NETHERRACK_ID
        
        # Place lava
        for r in range(lake_row, min(lake_row + lake_depth, GRID_HEIGHT - 3)):
            for c in range(lake_col, min(lake_col + lake_width, GRID_WIDTH)):
                if world[r][c] == NETHERRACK_ID or world[r][c] == AIR_ID:
                    world[r][c] = LAVA_ID
    
    # Add glowstone clusters on ceiling
    for _ in range(100):  # 100 glowstone patches
        glow_col = random.randint(5, GRID_WIDTH - 5)
        glow_row = random.randint(1, 8)  # Near ceiling
        cluster_size = random.randint(3, 7)
        
        for r in range(glow_row, min(glow_row + 3, GRID_HEIGHT)):
            for c in range(glow_col, min(glow_col + cluster_size, GRID_WIDTH)):
                if world[r][c] == AIR_ID or world[r][c] == NETHERRACK_ID:
                    world[r][c] = GLOWSTONE_ID
                    LIGHT_SOURCES.add((c, r))
    
    # Add soul sand patches
    for _ in range(80):
        sand_col = random.randint(10, GRID_WIDTH - 10)
        sand_row = random.randint(20, GRID_HEIGHT - 15)
        patch_size = random.randint(4, 8)
        
        for c in range(sand_col, min(sand_col + patch_size, GRID_WIDTH)):
            if world[sand_row][c] == NETHERRACK_ID:
                world[sand_row][c] = SOUL_SAND_ID
                # Add nether wart on top
                if sand_row - 1 > 0 and world[sand_row - 1][c] == AIR_ID and random.random() < 0.3:
                    world[sand_row - 1][c] = NETHER_WART_ID
    
    # Add nether quartz ore veins
    for _ in range(150):  # 150 quartz ore veins
        ore_col = random.randint(5, GRID_WIDTH - 5)
        ore_row = random.randint(10, GRID_HEIGHT - 10)
        vein_size = random.randint(3, 6)
        
        for _ in range(vein_size):
            r = ore_row + random.randint(-2, 2)
            c = ore_col + random.randint(-2, 2)
            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                if world[r][c] == NETHERRACK_ID:
                    world[r][c] = NETHER_QUARTZ_ORE_ID
    
    # Generate nether fortresses (3-5 fortresses)
    num_fortresses = random.randint(3, 5)
    for _ in range(num_fortresses):
        fortress_col = random.randint(50, GRID_WIDTH - 150)
        fortress_row = random.randint(30, GRID_HEIGHT - 40)
        generate_nether_fortress(world, fortress_col, fortress_row)
    
    # Add magma blocks near lava
    for row in range(GRID_HEIGHT - 3):
        for col in range(GRID_WIDTH):
            if world[row][col] == LAVA_ID:
                # Place magma blocks around lava
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    r, c = row + dr, col + dc
                    if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                        if world[r][c] == NETHERRACK_ID and random.random() < 0.3:
                            world[r][c] = MAGMA_BLOCK_ID
    
    WORLD_MAP = world
    print("🔥 Nether dimension generated!")
    return world


def generate_nether_fortress(world, start_col, start_row):
    """Generates a nether fortress structure."""
    fortress_width = random.randint(30, 50)
    fortress_height = random.randint(15, 25)
    
    # Clear area for fortress
    for r in range(max(0, start_row - 5), min(GRID_HEIGHT, start_row + fortress_height + 5)):
        for c in range(max(0, start_col - 5), min(GRID_WIDTH, start_col + fortress_width + 5)):
            if world[r][c] != BEDROCK_ID:
                world[r][c] = AIR_ID
    
    # Build walls with nether brick
    for r in range(start_row, min(GRID_HEIGHT - 2, start_row + fortress_height)):
        # Left wall
        if start_col >= 0:
            world[r][start_col] = NETHER_FORTRESS_BRICK_ID
        # Right wall
        if start_col + fortress_width < GRID_WIDTH:
            world[r][start_col + fortress_width] = NETHER_FORTRESS_BRICK_ID
    
    # Floor and ceiling
    for c in range(start_col, min(GRID_WIDTH, start_col + fortress_width)):
        # Floor
        if start_row < GRID_HEIGHT - 2:
            world[start_row][c] = NETHER_FORTRESS_BRICK_ID
        # Ceiling
        if start_row + fortress_height < GRID_HEIGHT - 2:
            world[start_row + fortress_height][c] = NETHER_FORTRESS_BRICK_ID
    
    # Add internal rooms
    for _ in range(3):
        room_col = start_col + random.randint(5, max(6, fortress_width - 15))
        room_width = random.randint(8, 12)
        room_height = random.randint(6, 10)
        room_row = start_row + random.randint(5, max(6, fortress_height - room_height - 5))
        
        # Room walls
        for r in range(room_row, min(GRID_HEIGHT - 2, room_row + room_height)):
            world[r][room_col] = NETHER_BRICK_ID
            if room_col + room_width < GRID_WIDTH:
                world[r][room_col + room_width] = NETHER_BRICK_ID
    
    print(f"🏰 Nether Fortress generated at column {start_col}")


def find_safe_spawn(world, start_col, start_row):
    """Find a safe spawn position with solid ground below and air above."""
    # Try the starting position first
    for attempt_row in range(start_row, GRID_HEIGHT - 10):
        # Check if there's solid ground
        if BLOCK_TYPES.get(world[attempt_row][start_col], {}).get("solid", False):
            # Check if there's air above (3 blocks)
            air_above = True
            for check_row in range(attempt_row - 3, attempt_row):
                if check_row >= 0:
                    if BLOCK_TYPES.get(world[check_row][start_col], {}).get("solid", False):
                        air_above = False
                        break
            
            if air_above:
                # Found a good spot! Return position above the solid block
                return start_col * BLOCK_SIZE, (attempt_row - 1) * BLOCK_SIZE
    
    # If not found, try nearby columns
    for offset in range(-10, 10):
        check_col = start_col + offset
        if 0 <= check_col < GRID_WIDTH:
            for attempt_row in range(start_row, GRID_HEIGHT - 10):
                if BLOCK_TYPES.get(world[attempt_row][check_col], {}).get("solid", False):
                    air_above = True
                    for check_row in range(attempt_row - 3, attempt_row):
                        if check_row >= 0:
                            if BLOCK_TYPES.get(world[check_row][check_col], {}).get("solid", False):
                                air_above = False
                                break
                    
                    if air_above:
                        return check_col * BLOCK_SIZE, (attempt_row - 1) * BLOCK_SIZE
    
    # Fallback: just return the original position
    return start_col * BLOCK_SIZE, start_row * BLOCK_SIZE


# Note: We use the imported Player class from overworld instead of a custom NetherPlayer
# This gives us all the advanced features like proper inventory, mining, crafting, etc.


# --- Enhanced Player Class (Based on Overworld but Nether-Optimized) ---
class Player(pygame.sprite.Sprite):
    """Enhanced player class based on overworld implementation."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([BLOCK_SIZE, BLOCK_SIZE * 2])
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        # Enhanced player with body parts
        # Legs (blue pants)
        pygame.draw.rect(self.image, (0, 0, 150), (8, BLOCK_SIZE * 1.2, 10, BLOCK_SIZE * 0.8))  # Left leg
        pygame.draw.rect(self.image, (0, 0, 150), (22, BLOCK_SIZE * 1.2, 10, BLOCK_SIZE * 0.8))  # Right leg
        
        # Body (cyan/teal shirt)
        pygame.draw.rect(self.image, (0, 150, 150), (5, BLOCK_SIZE * 0.5, 30, BLOCK_SIZE * 0.7))
        
        # Arms (skin color)
        arm_color = (180, 120, 80)
        pygame.draw.rect(self.image, arm_color, (0, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.5))  # Left arm
        pygame.draw.rect(self.image, arm_color, (34, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.5))  # Right arm
        
        # Head (skin tone)
        pygame.draw.rect(self.image, (100, 60, 20), (10, 2, 20, 20))
        
        # Hair (brown)
        pygame.draw.rect(self.image, (60, 40, 20), (10, 2, 20, 6))
        
        # Eyes (white with black pupils)
        pygame.draw.rect(self.image, (255, 255, 255), (14, 10, 4, 3))  # Left eye white
        pygame.draw.rect(self.image, (0, 0, 0), (15, 11, 2, 2))  # Left pupil
        pygame.draw.rect(self.image, (255, 255, 255), (22, 10, 4, 3))  # Right eye white
        pygame.draw.rect(self.image, (0, 0, 0), (23, 11, 2, 2))  # Right pupil
        
        # Mouth (small line)
        pygame.draw.rect(self.image, (50, 30, 10), (16, 17, 8, 2))

        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.base_speed = 5
        self.gravity = 0.5
        self.jump_strength = -12
        self.is_on_ground = False
        
        # --- Stats ---
        self.health = 20
        self.max_health = 20
        self.hunger = 20
        self.max_hunger = 20
        self.hunger_timer = 0
        self.damage_flash_timer = 0
        
        # --- Inventory and Hotbar ---
        self.hotbar_slots = [(250, 64), (253, 32), (252, 16), (254, 10), (221, 14), (0, 0), (0, 0), (0, 0), (0, 0)]
        self.inventory = [(0, 0)] * 27  # Empty inventory
        self.active_slot = 0
        self.held_block = self.hotbar_slots[self.active_slot][0]
        
        # --- Armor Slots ---
        self.armor_slots = {
            'helmet': 0,
            'chestplate': 0,
            'leggings': 0,
            'boots': 0
        }
        
        # --- Tool Durability ---
        self.tool_durability = {}
        
        # --- Mining Progress ---
        self.mining_progress = 0
        self.mining_target = None
        
        # --- Effects ---
        self.slowness_timer = 0
    
    def switch_active_slot(self, slot_index):
        """Switches the active hotbar slot."""
        if 0 <= slot_index <= 8:
            self.active_slot = slot_index
            self.held_block = self.hotbar_slots[self.active_slot][0]
    
    def add_to_inventory(self, block_id, amount=1):
        """Adds a block to inventory - tries hotbar first, then main inventory."""
        remaining = amount
        
        # Try to add to existing stacks in hotbar first
        for i in range(9):
            item_id, count = self.hotbar_slots[i]
            if item_id == block_id and count < 64:
                add_amount = min(remaining, 64 - count)
                self.hotbar_slots[i] = (item_id, count + add_amount)
                remaining -= add_amount
                if remaining <= 0:
                    self.held_block = self.hotbar_slots[self.active_slot][0]
                    return
        
        # Try to add to existing stacks in inventory
        for i in range(27):
            item_id, count = self.inventory[i]
            if item_id == block_id and count < 64:
                add_amount = min(remaining, 64 - count)
                self.inventory[i] = (item_id, count + add_amount)
                remaining -= add_amount
                if remaining <= 0:
                    return
        
        # Create new stacks in hotbar empty slots
        for i in range(9):
            item_id, count = self.hotbar_slots[i]
            if item_id == 0 and remaining > 0:
                add_amount = min(remaining, 64)
                self.hotbar_slots[i] = (block_id, add_amount)
                remaining -= add_amount
                self.held_block = self.hotbar_slots[self.active_slot][0]
                if remaining <= 0:
                    return
        
        # Create new stacks in inventory empty slots
        for i in range(27):
            item_id, count = self.inventory[i]
            if item_id == 0 and remaining > 0:
                add_amount = min(remaining, 64)
                self.inventory[i] = (block_id, add_amount)
                remaining -= add_amount
                if remaining <= 0:
                    return
    
    def consume_item(self, block_id, amount=1):
        """Consumes a block from hotbar and inventory."""
        remaining = amount
        
        # First consume from hotbar
        for i in range(9):
            item_id, count = self.hotbar_slots[i]
            if item_id == block_id:
                consume_amount = min(remaining, count)
                new_count = count - consume_amount
                if new_count <= 0:
                    self.hotbar_slots[i] = (0, 0)
                else:
                    self.hotbar_slots[i] = (item_id, new_count)
                remaining -= consume_amount
                if remaining <= 0:
                    self.held_block = self.hotbar_slots[self.active_slot][0]
                    return True
        
        # Then consume from inventory
        for i in range(27):
            item_id, count = self.inventory[i]
            if item_id == block_id:
                consume_amount = min(remaining, count)
                new_count = count - consume_amount
                if new_count <= 0:
                    self.inventory[i] = (0, 0)
                else:
                    self.inventory[i] = (item_id, new_count)
                remaining -= consume_amount
                if remaining <= 0:
                    return True
        
        self.held_block = self.hotbar_slots[self.active_slot][0]
        return remaining < amount
    
    def take_damage(self, amount, all_mobs=None, attacker=None):
        """Applies damage with cooldown and starts the flash timer."""
        if self.damage_flash_timer <= 0:
            self.health -= amount
            self.damage_flash_timer = FPS // 2
            
            if self.health <= 0:
                self.health = 0
                print("💀 Player died in the Nether!")
    
    def get_image(self):
        """Returns the player image with damage flash effect if needed."""
        original_image = self.image.copy()
        
        if self.damage_flash_timer > 0 and self.damage_flash_timer % 3 < 2:
            overlay = pygame.Surface(original_image.get_size()).convert_alpha()
            overlay.fill((255, 0, 0, 150))
            original_image.blit(overlay, (0, 0))
        
        return original_image
    
    def update(self):
        """Applies gravity, movement, and updates health/hunger stats."""
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
        
        # Decrement slowness timer
        if self.slowness_timer > 0:
            self.slowness_timer -= 1
        
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 15:
            self.vel_y = 15
        
        self.rect.x += self.vel_x
        self.collide_x()
        
        self.rect.y += self.vel_y
        self.collide_y()
        
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(GRID_WIDTH * BLOCK_SIZE, self.rect.right)
        
        # Hunger logic
        self.hunger_timer += 1
        if self.vel_x != 0 or self.vel_y < 0:
            self.hunger_timer += 0.5
        
        if self.hunger_timer >= FPS * 20:
            if self.hunger > 0:
                self.hunger -= 1
            self.hunger_timer = 0
    
    def collide_x(self):
        """Check horizontal collision."""
        global WORLD_MAP
        left_col = self.rect.left // BLOCK_SIZE
        right_col = self.rect.right // BLOCK_SIZE
        top_row = self.rect.top // BLOCK_SIZE
        bottom_row = self.rect.bottom // BLOCK_SIZE
        
        for row in range(top_row, bottom_row + 1):
            if 0 <= row < GRID_HEIGHT:
                if 0 <= left_col < GRID_WIDTH:
                    if BLOCK_TYPES.get(WORLD_MAP[row][left_col], {}).get("solid", False):
                        self.rect.left = (left_col + 1) * BLOCK_SIZE
                        self.vel_x = 0
                
                if 0 <= right_col < GRID_WIDTH:
                    if BLOCK_TYPES.get(WORLD_MAP[row][right_col], {}).get("solid", False):
                        self.rect.right = right_col * BLOCK_SIZE
                        self.vel_x = 0
    
    def collide_y(self):
        """Check vertical collision."""
        global WORLD_MAP
        self.is_on_ground = False
        left_col = self.rect.left // BLOCK_SIZE
        right_col = self.rect.right // BLOCK_SIZE
        top_row = self.rect.top // BLOCK_SIZE
        bottom_row = self.rect.bottom // BLOCK_SIZE
        
        for col in range(left_col, right_col + 1):
            if 0 <= col < GRID_WIDTH:
                if 0 <= bottom_row < GRID_HEIGHT:
                    if BLOCK_TYPES.get(WORLD_MAP[bottom_row][col], {}).get("solid", False):
                        self.rect.bottom = bottom_row * BLOCK_SIZE
                        self.vel_y = 0
                        self.is_on_ground = True
                
                if 0 <= top_row < GRID_HEIGHT:
                    if BLOCK_TYPES.get(WORLD_MAP[top_row][col], {}).get("solid", False):
                        self.rect.top = (top_row + 1) * BLOCK_SIZE
                        self.vel_y = 0


# --- Simple DroppedItem class ---
class DroppedItem(pygame.sprite.Sprite):
    """Simple dropped item sprite."""
    def __init__(self, x, y, item_id, count):
        super().__init__()
        self.rect = pygame.Rect(x, y, 20, 20)
        self.item_id = item_id
        self.count = count
        self.vel_y = 0
        self.gravity = 0.3
        
    def update(self):
        self.vel_y += self.gravity
        if self.vel_y > 5:
            self.vel_y = 5
        self.rect.y += self.vel_y


# --- NETHER MOBS ---
class Enderman(pygame.sprite.Sprite):
    """Tall black mob that teleports, drops ender pearls, attacks when looked at."""
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE * 3)  # 3 blocks tall
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 0.5
        self.health = 40
        self.max_health = 40
        self.speed = 3
        self.damage = 7
        self.agro = False
        self.teleport_cooldown = 0
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE * 3))
        self.image.fill((20, 0, 20))  # Dark purple/black
        # Purple eyes
        pygame.draw.rect(self.image, (200, 0, 200), (10, 10, 8, 8))
        pygame.draw.rect(self.image, (200, 0, 200), (22, 10, 8, 8))
    
    def update(self, world_map, player):
        """Update enderman AI."""
        # Apply gravity
        self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, 15)
        
        # Teleport cooldown
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1
        
        # Check if player is looking at enderman (within 10 blocks and facing)
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 10 * BLOCK_SIZE and not self.agro:
            self.agro = True
            print("👁️ Enderman provoked!")
        
        # Move toward player if agro
        if self.agro:
            if abs(dx) > 20:
                self.vel_x = -self.speed if dx > 0 else self.speed
            else:
                self.vel_x = 0
            
            # Teleport if damaged or random chance
            if self.teleport_cooldown == 0 and random.random() < 0.02:
                self.teleport(world_map)
                self.teleport_cooldown = 60
        
        # Apply velocity
        self.rect.x += self.vel_x
        self.collide_x(world_map)
        self.rect.y += self.vel_y
        self.collide_y(world_map)
        
        # Attack player if close
        if distance < BLOCK_SIZE * 1.5:
            player.take_damage(self.damage)
    
    def teleport(self, world_map):
        """Teleport to random nearby location."""
        for _ in range(10):  # Try 10 times to find valid spot
            new_x = self.rect.x + random.randint(-200, 200)
            new_y = self.rect.y + random.randint(-100, 100)
            col = new_x // BLOCK_SIZE
            row = new_y // BLOCK_SIZE
            
            if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT - 3:
                # Check if destination is clear
                if world_map[row][col] == 0 and world_map[row+1][col] == 0 and world_map[row+2][col] == 0:
                    self.rect.x = new_x
                    self.rect.y = new_y
                    print("✨ Enderman teleported!")
                    break
    
    def collide_x(self, world_map):
        """Check horizontal collision."""
        left_col = self.rect.left // BLOCK_SIZE
        right_col = self.rect.right // BLOCK_SIZE
        
        for row_offset in range(3):  # Check all 3 blocks of height
            check_row = self.rect.top // BLOCK_SIZE + row_offset
            if 0 <= check_row < GRID_HEIGHT:
                if 0 <= left_col < GRID_WIDTH and BLOCK_TYPES.get(world_map[check_row][left_col], {}).get("solid", False):
                    self.rect.left = (left_col + 1) * BLOCK_SIZE
                    self.vel_x = 0
                
                if 0 <= right_col < GRID_WIDTH and BLOCK_TYPES.get(world_map[check_row][right_col], {}).get("solid", False):
                    self.rect.right = right_col * BLOCK_SIZE
                    self.vel_x = 0
    
    def collide_y(self, world_map):
        """Check vertical collision."""
        left_col = self.rect.left // BLOCK_SIZE
        right_col = self.rect.right // BLOCK_SIZE
        top_row = self.rect.top // BLOCK_SIZE
        bottom_row = self.rect.bottom // BLOCK_SIZE
        
        for col in range(left_col, right_col + 1):
            if 0 <= col < GRID_WIDTH:
                if 0 <= bottom_row < GRID_HEIGHT and BLOCK_TYPES.get(world_map[bottom_row][col], {}).get("solid", False):
                    self.rect.bottom = bottom_row * BLOCK_SIZE
                    self.vel_y = 0
                
                if 0 <= top_row < GRID_HEIGHT and BLOCK_TYPES.get(world_map[top_row][col], {}).get("solid", False):
                    self.rect.top = (top_row + 1) * BLOCK_SIZE
                    self.vel_y = 0
    
    def take_damage(self, amount):
        """Take damage and teleport away."""
        self.health -= amount
        self.agro = True
        if self.teleport_cooldown == 0:
            self.teleport(WORLD_MAP)
            self.teleport_cooldown = 30


class Blaze(pygame.sprite.Sprite):
    """Flying fire mob that shoots fireballs, spawns in fortresses, drops blaze rods."""
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE * 2)
        self.vel_x = 0
        self.vel_y = 0
        self.health = 20
        self.max_health = 20
        self.speed = 2
        self.damage = 6
        self.float_offset = 0
        self.shoot_cooldown = 0
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE * 2))
        self.image.fill((255, 150, 0))  # Orange/yellow
        # Fire particles
        for _ in range(8):
            px = random.randint(5, 35)
            py = random.randint(5, 75)
            pygame.draw.circle(self.image, (255, 200, 0), (px, py), 3)
    
    def update(self, world_map, player, projectiles):
        """Update blaze AI."""
        # Float up and down
        self.float_offset += 0.1
        self.vel_y = math.sin(self.float_offset) * 2
        
        # Move toward player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 15 * BLOCK_SIZE:
            # Keep distance from player (stay 5-10 blocks away)
            if distance > 10 * BLOCK_SIZE:
                self.vel_x = self.speed if dx > 0 else -self.speed
            elif distance < 5 * BLOCK_SIZE:
                self.vel_x = -self.speed if dx > 0 else self.speed
            else:
                self.vel_x = 0
            
            # Shoot fireballs
            if self.shoot_cooldown == 0:
                self.shoot_fireball(player, projectiles)
                self.shoot_cooldown = 60  # Shoot every second
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Apply velocity
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Stay above ground
        feet_row = self.rect.bottom // BLOCK_SIZE
        feet_col = self.rect.centerx // BLOCK_SIZE
        if 0 <= feet_row < GRID_HEIGHT and 0 <= feet_col < GRID_WIDTH:
            if BLOCK_TYPES.get(world_map[feet_row][feet_col], {}).get("solid", False):
                self.rect.y -= 5  # Float up
    
    def shoot_fireball(self, player, projectiles):
        """Shoot a fireball toward the player."""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize and create velocity
            vx = (dx / distance) * 8
            vy = (dy / distance) * 8
            
            # Create fireball projectile
            fireball = BlazeFireball(self.rect.centerx, self.rect.centery, vx, vy, self.damage)
            projectiles.add(fireball)
            print("🔥 Blaze shot fireball!")
    
    def take_damage(self, amount):
        """Take damage."""
        self.health -= amount


class BlazeFireball(pygame.sprite.Sprite):
    """Fireball projectile shot by blazes."""
    def __init__(self, x, y, vx, vy, damage):
        super().__init__()
        self.rect = pygame.Rect(x, y, 10, 10)
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.lifetime = 120  # 2 seconds
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 100, 0))
    
    def update(self, world_map, player):
        """Update fireball movement."""
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.lifetime -= 1
        
        # Check collision with player
        if self.rect.colliderect(player.rect):
            player.take_damage(self.damage)
            self.kill()
            return
        
        # Check collision with blocks
        col = self.rect.centerx // BLOCK_SIZE
        row = self.rect.centery // BLOCK_SIZE
        if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT:
            if BLOCK_TYPES.get(world_map[row][col], {}).get("solid", False):
                self.kill()
                return
        
        # Remove if lifetime expired or out of bounds
        if self.lifetime <= 0 or self.rect.x < 0 or self.rect.x > GRID_WIDTH * BLOCK_SIZE:
            self.kill()



# --- Main Nether Game Loop ---
def main(overworld_save=None):
    """Main function for nether dimension.

    If `overworld_save` dict is provided, use it instead of loading from disk.
    This allows seamless in-process transitions when called from the overworld.
    """
    global WORLD_MAP

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PyCraft - The Nether")
    clock = pygame.time.Clock()
    
    # Check if coming from overworld (passed in) or loading nether save from disk
    loaded_from_disk = False
    if overworld_save is None:
        if "--load" in sys.argv or os.path.exists("overworld_save.pkl"):
            overworld_save = load_overworld_state()
            loaded_from_disk = True
        else:
            overworld_save = None

    if overworld_save and 'nether_spawn' in overworld_save:
        # Player is entering from overworld - use converted coordinates
        nether_x, nether_y = overworld_save['nether_spawn']
        WORLD_MAP = generate_nether()
        # Find safe ground near the spawn point
        safe_x, safe_y = find_safe_spawn(WORLD_MAP, nether_x // BLOCK_SIZE, nether_y // BLOCK_SIZE)
        
        # Use enhanced Player class
        player = Player(safe_x, safe_y)
            
        player.health = overworld_save['player_health']
        player.hunger = overworld_save['player_hunger']
        player.hotbar_slots = overworld_save['player_hotbar']
        if hasattr(player, 'inventory'):
            player.inventory = overworld_save['player_inventory']
        else:
            player.inventory_slots = overworld_save['player_inventory']
        player.armor_slots = overworld_save['player_armor']
        player.tool_durability = overworld_save['player_tool_durability']
        print(f"🌀 Entered Nether at ({safe_x}, {safe_y}) - Safe spawn found!")
        # Delete the OVERWORLD save file (we left the overworld) only if we loaded it from disk
        if loaded_from_disk and os.path.exists("overworld_save.pkl"):
            os.remove("overworld_save.pkl")
            print("🗑️ Cleared overworld save file")
    elif "--load" in sys.argv:
        save_data = load_nether_state()
        if save_data:
            WORLD_MAP = save_data['world_map']
            player = Player(save_data['player_pos'][0], save_data['player_pos'][1])
            player.health = save_data['player_health']
            player.hunger = save_data['player_hunger']
            player.hotbar_slots = save_data['player_hotbar']
            player.inventory = save_data['player_inventory']
            player.armor_slots = save_data['player_armor']
            player.tool_durability = save_data['player_tool_durability']
        else:
            WORLD_MAP = generate_nether()
            safe_x, safe_y = find_safe_spawn(WORLD_MAP, GRID_WIDTH // 2, 50)
            player = Player(safe_x, safe_y)
            print(f"🔥 New Nether spawn at ({safe_x}, {safe_y})")
    else:
        WORLD_MAP = generate_nether()
        safe_x, safe_y = find_safe_spawn(WORLD_MAP, GRID_WIDTH // 2, 50)
        player = Player(safe_x, safe_y)
        print(f"🔥 New Nether spawn at ({safe_x}, {safe_y})")
    
    # Spawn nether mobs
    PROJECTILES = pygame.sprite.Group()
    
    # Spawn Endermen (rare, spread throughout nether)
    for _ in range(5):
        spawn_x = random.randint(50, GRID_WIDTH - 50) * BLOCK_SIZE
        spawn_y = random.randint(20, GRID_HEIGHT - 30) * BLOCK_SIZE
        MOBS.add(Enderman(spawn_x, spawn_y))
    
    # Spawn Blazes in fortresses (need to find fortress locations)
    for _ in range(3):
        spawn_x = random.randint(50, GRID_WIDTH - 50) * BLOCK_SIZE
        spawn_y = random.randint(30, GRID_HEIGHT - 40) * BLOCK_SIZE
        MOBS.add(Blaze(spawn_x, spawn_y))
    
    print(f"🔥 Spawned {len(MOBS)} nether mobs!")
    
    running = True
    
    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_nether_state(player, MOBS, WORLD_MAP)
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to overworld
                    save_nether_state(player, MOBS, WORLD_MAP)
                    return_to_overworld()
                
                if event.key == pygame.K_SPACE and player.is_on_ground:
                    player.vel_y = player.jump_strength
        
        # Input
        keys = pygame.key.get_pressed()
        player.vel_x = 0
        
        if keys[pygame.K_a]:
            player.vel_x = -player.speed
        if keys[pygame.K_d]:
            player.vel_x = player.speed
        
        # Update
        player.update()
        
        # Nether-specific environmental effects
        player_col = player.rect.centerx // BLOCK_SIZE
        player_row = player.rect.centery // BLOCK_SIZE
        feet_row = player.rect.bottom // BLOCK_SIZE
        feet_col = player.rect.centerx // BLOCK_SIZE
        
        # Soul sand slowness effect
        if 0 <= feet_row < GRID_HEIGHT and 0 <= feet_col < GRID_WIDTH:
            if WORLD_MAP[feet_row][feet_col] == SOUL_SAND_ID:
                player.vel_x *= 0.4  # 60% slower on soul sand
                player.speed = player.base_speed * 0.4
                if hasattr(player, 'slowness_timer'):
                    player.slowness_timer = 20
            else:
                # Reset speed when not on soul sand
                if hasattr(player, 'base_speed'):
                    player.speed = player.base_speed
        
        # Lava damage
        if 0 <= player_row < GRID_HEIGHT and 0 <= player_col < GRID_WIDTH:
            if WORLD_MAP[player_row][player_col] == LAVA_ID:
                player.take_damage(2)  # Lava deals 2 damage per tick
                print("🔥 Burning in lava!")
        
        # Magma block damage (when standing on it)
        if 0 <= feet_row < GRID_HEIGHT and 0 <= feet_col < GRID_WIDTH:
            if WORLD_MAP[feet_row][feet_col] == MAGMA_BLOCK_ID:
                if hasattr(player, 'is_on_ground') and player.rect.bottom % BLOCK_SIZE < 5:
                    if random.random() < 0.05:  # 5% chance per frame
                        player.take_damage(1)
                        print("🔥 Magma block burn!")
        
        # Update mobs
        for mob in list(MOBS):
            if isinstance(mob, Enderman):
                mob.update(WORLD_MAP, player)
            elif isinstance(mob, Blaze):
                mob.update(WORLD_MAP, player, PROJECTILES)
            
            # Check if mob died and drop items
            if mob.health <= 0:
                if isinstance(mob, Enderman):
                    # Drop ender pearl
                    DROPPED_ITEMS.add(DroppedItem(mob.rect.x, mob.rect.y, ENDER_PEARL_ID, 1))
                    print("💎 Enderman dropped ender pearl!")
                elif isinstance(mob, Blaze):
                    # Drop blaze rod
                    DROPPED_ITEMS.add(DroppedItem(mob.rect.x, mob.rect.y, BLAZE_ROD_ID, 1))
                    print("🔥 Blaze dropped blaze rod!")
                mob.kill()
        
        # Update projectiles
        for projectile in list(PROJECTILES):
            projectile.update(WORLD_MAP, player)
        
        # --- NETHER PORTAL DETECTION (Return to Overworld) ---
        player_col = player.rect.centerx // BLOCK_SIZE
        player_row = player.rect.centery // BLOCK_SIZE
        
        if 0 <= player_row < GRID_HEIGHT and 0 <= player_col < GRID_WIDTH:
            if is_inside_portal(WORLD_MAP, player_col, player_row):
                print("🌀 Exiting Nether Portal - Returning to Overworld...")
                save_nether_state(player, MOBS, WORLD_MAP)
                return_to_overworld()

        # If running in-process, check if return was requested
        if 'SHOULD_RETURN_TO_OVERWORLD' in globals() and globals().get('SHOULD_RETURN_TO_OVERWORLD'):
            running = False
        
        # Camera
        camera_x = player.rect.centerx - SCREEN_WIDTH // 2
        camera_y = player.rect.centery - SCREEN_HEIGHT // 2
        camera_x = max(0, min(camera_x, GRID_WIDTH * BLOCK_SIZE - SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, GRID_HEIGHT * BLOCK_SIZE - SCREEN_HEIGHT))
        
        # Render
        screen.fill(NETHER_AMBIANCE_COLOR)
        
        # Draw world
        start_col = max(0, camera_x // BLOCK_SIZE)
        end_col = min(GRID_WIDTH, (camera_x + SCREEN_WIDTH) // BLOCK_SIZE + 1)
        start_row = max(0, camera_y // BLOCK_SIZE)
        end_row = min(GRID_HEIGHT, (camera_y + SCREEN_HEIGHT) // BLOCK_SIZE + 1)
        
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                block_id = WORLD_MAP[row][col]
                if block_id != 0:
                    block_color = BLOCK_TYPES[block_id]["color"]
                    screen_x = col * BLOCK_SIZE - camera_x
                    screen_y = row * BLOCK_SIZE - camera_y
                    pygame.draw.rect(screen, block_color, (screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw coordinate grid
        if SHOW_GRID:
            grid_font = pygame.font.Font(None, 16)
            for col in range(start_col, end_col, 5):
                x = col * BLOCK_SIZE - camera_x
                if 0 <= x <= SCREEN_WIDTH:
                    pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, SCREEN_HEIGHT), 1)
                    label = grid_font.render(str(col), True, (150, 150, 150))
                    screen.blit(label, (x + 2, 2))
            for row in range(start_row, end_row, 5):
                y = row * BLOCK_SIZE - camera_y
                if 0 <= y <= SCREEN_HEIGHT:
                    pygame.draw.line(screen, (100, 100, 100), (0, y), (SCREEN_WIDTH, y), 1)
                    label = grid_font.render(str(row), True, (150, 150, 150))
                    screen.blit(label, (2, y + 2))
        
        # Draw mobs
        for mob in MOBS:
            mob_screen_x = mob.rect.x - camera_x
            mob_screen_y = mob.rect.y - camera_y
            screen.blit(mob.image, (mob_screen_x, mob_screen_y))
            
            # Draw health bar
            health_percent = mob.health / mob.max_health
            bar_width = 30
            bar_height = 4
            pygame.draw.rect(screen, (255, 0, 0), (mob_screen_x + 5, mob_screen_y - 10, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (mob_screen_x + 5, mob_screen_y - 10, bar_width * health_percent, bar_height))
        
        # Draw projectiles
        for projectile in PROJECTILES:
            proj_screen_x = projectile.rect.x - camera_x
            proj_screen_y = projectile.rect.y - camera_y
            screen.blit(projectile.image, (proj_screen_x, proj_screen_y))
        
        # Draw dropped items
        for item in DROPPED_ITEMS:
            item_screen_x = item.rect.x - camera_x
            item_screen_y = item.rect.y - camera_y
            # Simple square for items
            pygame.draw.rect(screen, (200, 200, 0), (item_screen_x, item_screen_y, 20, 20))
        
        # Draw player
        player_screen_x = player.rect.x - camera_x
        player_screen_y = player.rect.y - camera_y
        screen.blit(player.get_image(), (player_screen_x, player_screen_y))
        
        # Draw HUD
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"❤️ {player.health}/{player.max_health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))
        
        dimension_text = font.render("THE NETHER - Press ESC to return", True, (255, 100, 100))
        screen.blit(dimension_text, (SCREEN_WIDTH // 2 - 150, 10))
        
        pygame.display.flip()
    
    # Do not call pygame.quit() when used in-process; let caller manage pygame lifecycle.
    if __name__ == "__main__":
        pygame.quit()


if __name__ == "__main__":
    main()
