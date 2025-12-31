import pygame
import random
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 40
FPS = 60

# --- Chunk System Constants ---
CHUNK_SIZE = 256  # Blocks per chunk width
WORLD_HEIGHT_BLOCKS = 150

# --- World Map Dimensions (Larger for scrolling) ---
WORLD_WIDTH_BLOCKS = CHUNK_SIZE * 5  # Start with 5 chunks loaded
GRID_WIDTH = WORLD_WIDTH_BLOCKS
GRID_HEIGHT = WORLD_HEIGHT_BLOCKS

# Chunk tracking
LOADED_CHUNKS = {}  # Dictionary: chunk_x -> chunk_data
CURRENT_CHUNK_RANGE = [-2, 2]  # Initially load chunks -2 to 2 (5 chunks)

# --- Block ID Constants ---
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
SNOW_ID = 24 
ICE_ID = 25

# --- New Biome Block IDs ---
MUD_ID = 30
SWAMP_WATER_ID = 31
DARK_OAK_LOG_ID = 32
COARSE_DIRT_ID = 33
SPRUCE_LOG_ID = 34
EMERALD_ID = 23 # Already exists, but useful to keep here
FENCE_ID = 40
LADDER_ID = 41
COBBLESTONE_ID = 42
VINES_ID = 135

FLUID_BLOCKS = {WATER_ID, SWAMP_WATER_ID}

# --- Biome Type Constants ---
OAK_FOREST_BIOME = 0
DESERT_BIOME = 1
SNOW_BIOME = 2
SWAMP_BIOME = 3
TAIGA_BIOME = 4
PLAINS_BIOME = 5
BIRCH_FOREST_BIOME = 6
LAKE_BIOME = 7  # New biome for lakes
JUNGLE_BIOME = 8  # New jungle biome
BAMBOO_JUNGLE_BIOME = 9  # Bamboo variant of jungle
SAVANNAH_BIOME = 10  # Savannah with acacia trees
OCEAN_BIOME = 11  # Large ocean biome (500-1000 blocks)

# --- Day/Night Cycle Constants ---
# Total cycle: 12 minutes = 720 seconds = 43,200 frames at 60 FPS
DAY_LENGTH = FPS * 60 * 5      # 5 minutes = 18,000 frames
EVENING_LENGTH = FPS * 60 * 1    # 1 minute = 3,600 frames
NIGHT_LENGTH = FPS * 60 * 5     # 5 minutes = 18,000 frames
DAWN_LENGTH = FPS * 60 * 1       # 1 minute = 3,600 frames
TOTAL_CYCLE_LENGTH = DAY_LENGTH + EVENING_LENGTH + NIGHT_LENGTH + DAWN_LENGTH

# Time phases
DAY_PHASE = 0
EVENING_PHASE = 1
NIGHT_PHASE = 2
DAWN_PHASE = 3

# Global time tracking
TIME_OF_DAY = 0  # Frame counter
TIME_PHASE = DAY_PHASE  # Current phase

# --- Block Definitions (ID and Color) ---
BLOCK_TYPES = {
    # --- Existing Blocks (Check IDs 0-25 are correct) ---
    0: {"name": "Air", "color": (135, 206, 235), "mineable": False, "solid": False},
    1: {"name": "Grass", "color": (0, 150, 0), "mineable": True, "min_tool_level": 0, "solid": True},
    2: {"name": "Dirt", "color": (139, 69, 19), "mineable": True, "min_tool_level": 0, "solid": True, "mine_time": 60},
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
    15: {"name": "Torch", "color": (255, 200, 0), "mineable": True, "min_tool_level": 0, "solid": False, "emits_light": True, "breaks_in_water": True},
    16: {"name": "Furnace", "color": (90, 90, 90), "mineable": True, "min_tool_level": 1, "solid": True},
    17: {"name": "Stone Pickaxe", "color": (120, 120, 120), "mineable": False, "tool_level": 2, "solid": False},
    18: {"name": "Wood", "color": (101, 67, 33), "mineable": True, "min_tool_level": 0, "solid": True},
    19: {"name": "Sand", "color": (194, 178, 128), "mineable": True, "min_tool_level": 0, "solid": True},
    20: {"name": "Sandstone", "color": (160, 140, 100), "mineable": True, "min_tool_level": 1, "solid": True},
    21: {"name": "Cactus", "color": (30, 130, 50), "mineable": True, "min_tool_level": 0, "solid": True},
    22: {"name": "Dead Bush", "color": (150, 120, 80), "mineable": True, "min_tool_level": 0, "solid": False},
    23: {"name": "Emerald", "color": (0, 200, 80), "mineable": False, "solid": False},
    24: {"name": "Snow", "color": (255, 255, 255), "mineable": True, "min_tool_level": 0, "solid": True},
    25: {"name": "Ice", "color": (174, 221, 240), "mineable": True, "min_tool_level": 0, "solid": True},
    26: {"name": "Gravel", "color": (136, 136, 136), "mineable": True, "min_tool_level": 0, "solid": True},

    # --- New Biome Blocks ---
    30: {"name": "Mud", "color": (70, 50, 30), "mineable": True, "min_tool_level": 0, "solid": True},
    31: {"name": "Swamp Water", "color": (40, 70, 80), "mineable": False, "solid": False},
    32: {"name": "Dark Oak Log", "color": (60, 40, 20), "mineable": True, "min_tool_level": 1, "solid": True},
    33: {"name": "Coarse Dirt", "color": (80, 60, 40), "mineable": True, "min_tool_level": 0, "solid": True},
    34: {"name": "Spruce Log", "color": (40, 30, 20), "mineable": True, "min_tool_level": 0, "solid": True},
    40: {"name": "Fence", "color": (150, 100, 50), "mineable": True, "min_tool_level": 0, "solid": False}, 
    41: {"name": "Ladder", "color": (150, 100, 50), "mineable": True, "min_tool_level": 0, "solid": False}, 
    42: {"name": "Cobblestone", "color": (80, 80, 80), "mineable": True, "min_tool_level": 1, "solid": True},
    
    # --- New Items (Mob Drops & Colored Wools) ---
    50: {"name": "Mutton", "color": (160, 100, 100), "mineable": False, "solid": False},
    51: {"name": "Beef", "color": (150, 50, 50), "mineable": False, "solid": False},
    52: {"name": "String", "color": (230, 230, 230), "mineable": False, "solid": False},
    53: {"name": "Arrow", "color": (120, 80, 40), "mineable": False, "solid": False},
    54: {"name": "Bone", "color": (220, 220, 200), "mineable": False, "solid": False},
    55: {"name": "Bow", "color": (100, 70, 40), "mineable": False, "solid": False},
    56: {"name": "Gunpowder", "color": (60, 60, 60), "mineable": False, "solid": False},
    57: {"name": "Deer Horn", "color": (200, 180, 150), "mineable": False, "solid": False},
    58: {"name": "Narwhal Horn", "color": (240, 240, 220), "mineable": False, "solid": False},
    59: {"name": "Flipper", "color": (40, 40, 50), "mineable": False, "solid": False, "armor_type": "boots"},
    60: {"name": "Redstone Dust", "color": (180, 0, 0), "mineable": False, "solid": False},
    61: {"name": "Glass Bottle", "color": (200, 230, 240), "mineable": False, "solid": False},
    62: {"name": "Glowstone Dust", "color": (255, 220, 100), "mineable": False, "solid": False},
    63: {"name": "Spider Eye", "color": (120, 40, 40), "mineable": False, "solid": False},
    64: {"name": "Sugar", "color": (255, 255, 255), "mineable": False, "solid": False},
    131: {"name": "Healing Potion", "color": (255, 50, 50), "mineable": False, "solid": False, "potion_type": "drinkable", "heal_amount": 6},
    132: {"name": "Splash Healing Potion", "color": (255, 100, 100), "mineable": False, "solid": False, "potion_type": "splash", "heal_amount": 4},
    133: {"name": "Splash Poison Potion", "color": (100, 255, 100), "mineable": False, "solid": False, "potion_type": "splash", "damage_amount": 6},
    134: {"name": "Trident", "color": (100, 150, 200), "mineable": False, "solid": False, "attack_damage": 9},
    135: {"name": "Vines", "color": (34, 139, 34), "mineable": True, "min_tool_level": 0, "solid": False},
    136: {"name": "Apple", "color": (220, 50, 50), "mineable": False, "solid": False},
    137: {"name": "Orange", "color": (255, 165, 0), "mineable": False, "solid": False},
    138: {"name": "Banana", "color": (255, 255, 0), "mineable": False, "solid": False},
    139: {"name": "Oak Sapling", "color": (100, 180, 100), "mineable": True, "min_tool_level": 0, "solid": False, "tree_type": "oak"},
    140: {"name": "Birch Sapling", "color": (180, 220, 180), "mineable": True, "min_tool_level": 0, "solid": False, "tree_type": "birch"},
    141: {"name": "Spruce Sapling", "color": (60, 120, 60), "mineable": True, "min_tool_level": 0, "solid": False, "tree_type": "spruce"},
    142: {"name": "Jungle Sapling", "color": (120, 200, 120), "mineable": True, "min_tool_level": 0, "solid": False, "tree_type": "jungle"},
    143: {"name": "Berry Bush", "color": (139, 69, 19), "mineable": True, "min_tool_level": 0, "solid": False},
    144: {"name": "Berry", "color": (180, 50, 100), "mineable": False, "solid": False},
    81: {"name": "Chicken", "color": (240, 230, 200), "mineable": False, "solid": False},
    82: {"name": "Pork", "color": (230, 120, 120), "mineable": False, "solid": False},
    # Colored Wools (16 Minecraft colors)
    65: {"name": "White Wool", "color": (255, 255, 255), "mineable": True, "min_tool_level": 0, "solid": True},
    66: {"name": "Light Gray Wool", "color": (157, 157, 151), "mineable": True, "min_tool_level": 0, "solid": True},
    67: {"name": "Gray Wool", "color": (71, 79, 82), "mineable": True, "min_tool_level": 0, "solid": True},
    68: {"name": "Black Wool", "color": (29, 29, 33), "mineable": True, "min_tool_level": 0, "solid": True},
    69: {"name": "Brown Wool", "color": (131, 84, 50), "mineable": True, "min_tool_level": 0, "solid": True},
    70: {"name": "Red Wool", "color": (176, 46, 38), "mineable": True, "min_tool_level": 0, "solid": True},
    71: {"name": "Orange Wool", "color": (249, 128, 29), "mineable": True, "min_tool_level": 0, "solid": True},
    72: {"name": "Yellow Wool", "color": (254, 216, 61), "mineable": True, "min_tool_level": 0, "solid": True},
    73: {"name": "Lime Wool", "color": (128, 199, 31), "mineable": True, "min_tool_level": 0, "solid": True},
    74: {"name": "Green Wool", "color": (94, 124, 22), "mineable": True, "min_tool_level": 0, "solid": True},
    75: {"name": "Cyan Wool", "color": (22, 156, 156), "mineable": True, "min_tool_level": 0, "solid": True},
    76: {"name": "Light Blue Wool", "color": (58, 175, 217), "mineable": True, "min_tool_level": 0, "solid": True},
    77: {"name": "Blue Wool", "color": (53, 57, 157), "mineable": True, "min_tool_level": 0, "solid": True},
    78: {"name": "Purple Wool", "color": (137, 50, 184), "mineable": True, "min_tool_level": 0, "solid": True},
    79: {"name": "Magenta Wool", "color": (199, 78, 189), "mineable": True, "min_tool_level": 0, "solid": True},
    80: {"name": "Pink Wool", "color": (243, 139, 170), "mineable": True, "min_tool_level": 0, "solid": True},
    83: {"name": "Birch Wood", "color": (216, 216, 216), "mineable": True, "min_tool_level": 0, "solid": True},
    84: {"name": "Birch Leaves", "color": (50, 120, 50), "mineable": True, "min_tool_level": 0, "solid": True},
    85: {"name": "Coal", "color": (40, 40, 40), "mineable": False, "solid": False},
    86: {"name": "Glass", "color": (200, 230, 255), "mineable": True, "min_tool_level": 0, "solid": True},
    87: {"name": "Steak", "color": (100, 60, 40), "mineable": False, "solid": False},
    88: {"name": "Cooked Mutton", "color": (120, 80, 60), "mineable": False, "solid": False},
    89: {"name": "Cooked Chicken", "color": (200, 180, 140), "mineable": False, "solid": False},
    90: {"name": "Porckchop", "color": (180, 130, 100), "mineable": False, "solid": False},
    91: {"name": "Door", "color": (139, 90, 43), "mineable": True, "min_tool_level": 0, "solid": True},
    92: {"name": "Crafting Table", "color": (140, 90, 50), "mineable": True, "min_tool_level": 0, "solid": True},
    93: {"name": "Wheat Item", "color": (240, 220, 130), "mineable": False, "solid": False},
    94: {"name": "Carrot Item", "color": (255, 140, 0), "mineable": False, "solid": False},
    95: {"name": "Wheat Block", "color": (220, 200, 100), "mineable": True, "min_tool_level": 0, "solid": False, "drops": (93, 1)},
    96: {"name": "Carrot Block", "color": (255, 160, 50), "mineable": True, "min_tool_level": 0, "solid": False, "drops": (94, 1)},
    97: {"name": "Book", "color": (139, 69, 19), "mineable": False, "solid": False},
    98: {"name": "Bookshelf", "color": (101, 67, 33), "mineable": True, "min_tool_level": 0, "solid": True},
    99: {"name": "Wooden Sword", "color": (160, 100, 60), "mineable": False, "solid": False, "tool_level": 1, "durability": 60, "damage_bonus": 3, "attack_cooldown": 10},
    100: {"name": "Wooden Shovel", "color": (150, 95, 55), "mineable": False, "solid": False, "tool_level": 1, "durability": 60},
    101: {"name": "Wooden Spear", "color": (140, 90, 50), "mineable": False, "solid": False, "tool_level": 1, "durability": 60, "attack_range": 3, "attack_cooldown": 180, "can_charge": True},
    102: {"name": "Wooden Axe", "color": (130, 85, 45), "mineable": False, "solid": False, "tool_level": 1, "durability": 60, "damage_bonus": 5, "attack_cooldown": 180},
    103: {"name": "Bread", "color": (210, 180, 140), "mineable": False, "solid": False},
    104: {"name": "Hay Bale", "color": (230, 220, 130), "mineable": True, "min_tool_level": 0, "solid": True},
    105: {"name": "Birch Planks", "color": (220, 220, 200), "mineable": True, "min_tool_level": 0, "solid": True},
    106: {"name": "Spruce Planks", "color": (90, 70, 50), "mineable": True, "min_tool_level": 0, "solid": True},
    107: {"name": "Trident", "color": (0, 180, 200), "mineable": False, "solid": False, "tool_level": 2, "durability": 250, "damage_bonus": 12, "attack_cooldown": 20, "attack_range": 3, "can_throw": True},
    108: {"name": "Iron Ingot", "color": (220, 220, 220), "mineable": False, "solid": False},
    109: {"name": "Stone Pickaxe", "color": (128, 128, 128), "mineable": False, "solid": False, "tool_level": 2, "durability": 132, "damage_bonus": 0, "attack_cooldown": 10},
    110: {"name": "Stone Sword", "color": (120, 120, 120), "mineable": False, "solid": False, "tool_level": 2, "durability": 132, "damage_bonus": 6, "attack_cooldown": 10},
    111: {"name": "Stone Shovel", "color": (115, 115, 115), "mineable": False, "solid": False, "tool_level": 2, "durability": 132},
    112: {"name": "Stone Spear", "color": (110, 110, 110), "mineable": False, "solid": False, "tool_level": 2, "durability": 132, "attack_range": 3, "attack_cooldown": 180, "can_charge": True},
    113: {"name": "Stone Axe", "color": (125, 125, 125), "mineable": False, "solid": False, "tool_level": 2, "durability": 132, "damage_bonus": 8, "attack_cooldown": 180},
    114: {"name": "Iron Pickaxe", "color": (200, 200, 200), "mineable": False, "solid": False, "tool_level": 3, "durability": 250, "damage_bonus": 0, "attack_cooldown": 10},
    115: {"name": "Iron Sword", "color": (210, 210, 210), "mineable": False, "solid": False, "tool_level": 3, "durability": 250, "damage_bonus": 9, "attack_cooldown": 10},
    116: {"name": "Iron Shovel", "color": (205, 205, 205), "mineable": False, "solid": False, "tool_level": 3, "durability": 250},
    117: {"name": "Iron Spear", "color": (195, 195, 195), "mineable": False, "solid": False, "tool_level": 3, "durability": 250, "attack_range": 3, "attack_cooldown": 180, "can_charge": True},
    118: {"name": "Iron Axe", "color": (215, 215, 215), "mineable": False, "solid": False, "tool_level": 3, "durability": 250, "damage_bonus": 11, "attack_cooldown": 180},
    119: {"name": "Iron Helmet", "color": (220, 220, 220), "mineable": False, "solid": False, "armor_type": "helmet", "armor_points": 2},
    120: {"name": "Iron Chestplate", "color": (215, 215, 215), "mineable": False, "solid": False, "armor_type": "chestplate", "armor_points": 6},
    121: {"name": "Iron Leggings", "color": (210, 210, 210), "mineable": False, "solid": False, "armor_type": "leggings", "armor_points": 5},
    122: {"name": "Iron Boots", "color": (205, 205, 205), "mineable": False, "solid": False, "armor_type": "boots", "armor_points": 2},
    
    # Jungle Biome Blocks (123-128)
    123: {"name": "Podzol", "color": (98, 70, 45), "mineable": True, "solid": True, "tool_level": 1, "drop_id": 2},  # Dirt when mined
    124: {"name": "Jungle Wood", "color": (145, 120, 75), "mineable": True, "solid": True, "tool_level": 1, "drop_id": 124},  # Slightly yellow wood
    125: {"name": "Jungle Planks", "color": (160, 130, 80), "mineable": True, "solid": True, "tool_level": 1, "drop_id": 125},
    126: {"name": "Jungle Leaves", "color": (60, 140, 50), "mineable": True, "solid": True, "tool_level": 0, "drop_id": 0},  # Rich green leaves
    127: {"name": "Bamboo", "color": (130, 180, 70), "mineable": True, "solid": False, "tool_level": 0, "drop_id": 127, "half_block": True},  # Thin bamboo stalk
    128: {"name": "Vine", "color": (50, 120, 40), "mineable": True, "solid": False, "tool_level": 0, "drop_id": 128},
    129: {"name": "Bamboo Planks", "color": (235, 220, 100), "mineable": True, "min_tool_level": 0, "solid": True},  # Yellow bamboo planks
    130: {"name": "Slimeball", "color": (100, 200, 100), "mineable": False, "solid": False},  # Green slimeball
    145: {"name": "Rabbit Meat", "color": (200, 140, 120), "mineable": False, "solid": False},  # Raw rabbit meat
    146: {"name": "Cooked Rabbit", "color": (160, 110, 80), "mineable": False, "solid": False},  # Cooked rabbit
    147: {"name": "Acacia Wood", "color": (150, 150, 150), "mineable": True, "solid": True, "tool_level": 1, "drop_id": 147},  # Gray acacia wood
    148: {"name": "Acacia Planks", "color": (255, 140, 60), "mineable": True, "solid": True, "tool_level": 1, "drop_id": 148},  # Orange planks
    149: {"name": "Acacia Leaves", "color": (180, 200, 100), "mineable": True, "solid": True, "tool_level": 0, "drop_id": 0},  # Yellowish green leaves
    150: {"name": "Acacia Sapling", "color": (150, 180, 80), "mineable": True, "min_tool_level": 0, "solid": False, "tree_type": "acacia"},
    151: {"name": "Glowstone Dust", "color": (255, 255, 150), "mineable": False, "solid": False},  # Yellow glowing dust
    152: {"name": "Glowstone", "color": (255, 255, 100), "mineable": True, "solid": True, "tool_level": 1, "drop_id": 151, "emits_light": True},  # Glowing block
    153: {"name": "Hay Bale", "color": (230, 200, 70), "mineable": True, "solid": True, "tool_level": 0, "drop_id": 153},  # Yellow hay block
    154: {"name": "Bird Meat", "color": (210, 160, 140), "mineable": False, "solid": False},  # Raw bird meat
    155: {"name": "Cooked Bird Meat", "color": (180, 130, 100), "mineable": False, "solid": False},  # Cooked bird meat
    156: {"name": "Cod", "color": (160, 130, 100), "mineable": False, "solid": False},  # Raw cod
    157: {"name": "Cooked Cod", "color": (220, 200, 180), "mineable": False, "solid": False},  # Cooked cod
    158: {"name": "Salmon", "color": (220, 100, 80), "mineable": False, "solid": False},  # Raw salmon
    159: {"name": "Cooked Salmon", "color": (240, 150, 130), "mineable": False, "solid": False},  # Cooked salmon
    160: {"name": "Kelp", "color": (40, 120, 60), "mineable": True, "solid": False},  # Ocean grass
    161: {"name": "Yellow Coral", "color": (255, 220, 80), "mineable": True, "solid": True, "tool_level": 0, "drop_id": 161},
    162: {"name": "Red Coral", "color": (255, 80, 80), "mineable": True, "solid": True, "tool_level": 0, "drop_id": 162},
    163: {"name": "Blue Coral", "color": (80, 150, 255), "mineable": True, "solid": True, "tool_level": 0, "drop_id": 163},
    164: {"name": "Nautilus Shell", "color": (200, 180, 255), "mineable": False, "solid": False},
    165: {"name": "Tropical Fish Meat", "color": (255, 180, 100), "mineable": False, "solid": False},
}


# --- Crafting Recipes (No change) ---
CRAFTING_RECIPES = {
    frozenset([(18, 1)]): (8, 4),  # Oak wood -> Oak planks (1 wood = 4 planks)
    frozenset([(83, 1)]): (105, 4),  # Birch wood -> Birch planks (1 wood = 4 planks)
    frozenset([(34, 1)]): (106, 4),  # Spruce log -> Spruce planks (1 wood = 4 planks)
    frozenset([(124, 1)]): (125, 4),  # Jungle wood -> Jungle planks (1 wood = 4 planks)
    # Acacia wood (147) cannot be crafted into planks - decorative only
    frozenset([(127, 4)]): (129, 1),  # 4 Bamboo -> 1 Bamboo plank
    frozenset([(129, 2)]): (10, 4),  # Bamboo planks -> Sticks
    frozenset([(8, 2)]): (10, 4),  # Oak planks -> Sticks
    frozenset([(105, 2)]): (10, 4),  # Birch planks -> Sticks
    frozenset([(106, 2)]): (10, 4),  # Spruce planks -> Sticks
    frozenset([(125, 2)]): (10, 4),  # Jungle planks -> Sticks
    frozenset([(8, 3), (10, 2)]): (9, 1),
    frozenset([(3, 3), (10, 2)]): (17, 1),
    frozenset([(3, 8)]): (16, 1),
    frozenset([(10, 1), (85, 1)]): (15, 4),  # 1 stick + 1 coal -> 4 torches
    frozenset([(151, 4)]): (152, 1),  # 4 glowstone dust -> 1 glowstone block
    frozenset([(93, 9)]): (153, 1),  # 9 wheat -> 1 hay bale
    frozenset([(8, 4)]): (92, 1),  # 4 planks -> crafting table
    frozenset([(105, 4)]): (92, 1),  # 4 birch planks -> crafting table
    frozenset([(106, 4)]): (92, 1),  # 4 spruce planks -> crafting table
    frozenset([(125, 4)]): (92, 1),  # 4 jungle planks -> crafting table
    frozenset([(129, 4)]): (92, 1),  # 4 bamboo planks -> crafting table
}

# --- Crafting Table Recipes (3x3 grid) ---
CRAFTING_TABLE_RECIPES = {
    # Sticks from planks: [P .] [P .] - 2 planks vertically = 4 sticks
    # Pattern: [P . .]
    #          [P . .]
    #          [. . .]
    # (This allows making sticks in the 3x3 grid like in 2x2 grid)
    
    # Wooden Pickaxe: 3 wood on top row, 2 sticks in column below center
    # Pattern: [W W W]
    #          [. S .]
    #          [. S .]
    frozenset([(18, 3), (10, 2)]): (9, 1),
    
    # Wooden Sword: 2 planks stacked, 1 stick at bottom
    # Pattern: [. P .]
    #          [. P .]
    #          [. S .]
    frozenset([(8, 2), (10, 1)]): (99, 1),
    frozenset([(105, 2), (10, 1)]): (99, 1),  # Birch planks
    frozenset([(106, 2), (10, 1)]): (99, 1),  # Spruce planks
    frozenset([(125, 2), (10, 1)]): (99, 1),  # Jungle planks
    frozenset([(129, 2), (10, 1)]): (99, 1),  # Bamboo planks
    
    # Wooden Shovel: 1 wood on top, 2 sticks stacked below
    # Pattern: [. W .]
    #          [. S .]
    #          [. S .]
    frozenset([(18, 1), (10, 2)]): (100, 1),
    
    # Wooden Spear: Shovel placed horizontally (1 wood, 2 sticks)
    # Pattern: [W S S]
    #          [. . .]
    #          [. . .]
    frozenset([(18, 1), (10, 2)]): (101, 1),  # Same ingredients as shovel, different pattern
    
    # Wooden Axe: 1 plank on top center, 2 on left side, 2 sticks stacked
    # Pattern: [P P .]
    #          [P S .]
    #          [. S .]
    frozenset([(8, 3), (10, 2)]): (102, 1),
    frozenset([(105, 3), (10, 2)]): (102, 1),  # Birch planks
    frozenset([(106, 3), (10, 2)]): (102, 1),  # Spruce planks
    frozenset([(125, 3), (10, 2)]): (102, 1),  # Jungle planks
    frozenset([(129, 3), (10, 2)]): (102, 1),  # Bamboo planks
    frozenset([(105, 3), (10, 2)]): (102, 1),  # Birch planks
    frozenset([(106, 3), (10, 2)]): (102, 1),  # Spruce planks
    
    # Bread: 3 wheat in a row
    # Pattern: [W W W]
    #          [. . .]
    #          [. . .]
    frozenset([(93, 3)]): (103, 1),
    
    # Hay Bale -> 9 Wheat
    frozenset([(104, 1)]): (93, 9),
}

# --- Smelting Recipes ---
SMELTING_RECIPES = {
    51: 87,  # Beef → Cooked Beef
    50: 88,  # Mutton → Cooked Mutton
    81: 89,  # Chicken → Cooked Chicken
    82: 90,  # Pork → Cooked Pork
    154: 155,  # Bird Meat → Cooked Bird Meat
    156: 157,  # Cod → Cooked Cod
    158: 159,  # Salmon → Cooked Salmon
    19: 86,  # Sand → Glass
}

# --- Fuel Items (item_id: burn_time_in_frames) ---
FUEL_ITEMS = {
    85: 480,  # Coal: 8 seconds (480 frames)
    18: 180,  # Wood: 3 seconds
    8: 180,   # Planks: 3 seconds
}

# --- Pygame Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Simple Pycraft Clone (Scrolling World with Enemies and Crafting)")
clock = pygame.time.Clock()

pygame.font.init()
FONT_SMALL = pygame.font.Font(None, 16)
FONT_BIG = pygame.font.Font(None, 24)

WORLD_MAP = [] 
CRAFTING_GRID = [0, 0, 0, 0] 
CRAFTING_AMOUNTS = [0, 0, 0, 0] 
CRAFTING_SLOT_RECTS = []
INVENTORY_SLOT_RECTS = []  # For inventory menu click detection
HELD_ITEM = (0, 0)  # For dragging items in inventory: (item_id, count) 

# Furnace GUI State
FURNACE_OPEN = False
FURNACE_POS = (0, 0)  # World position of furnace being used
FURNACE_INPUT = (0, 0)  # (item_id, count) in input slot
FURNACE_FUEL = (0, 0)  # (item_id, count) in fuel slot
FURNACE_OUTPUT = (0, 0)  # (item_id, count) in output slot
FURNACE_PROGRESS = 0  # Smelting progress (0-100)
FURNACE_FUEL_TIME = 0  # Remaining fuel burn time

# Crafting Table GUI State
CRAFTING_TABLE_OPEN = False
CRAFTING_TABLE_POS = (0, 0)  # World position of crafting table
CRAFTING_TABLE_GRID = [(0, 0) for _ in range(9)]  # 9 slots for 3x3 grid
CRAFTING_TABLE_OUTPUT = (0, 0)  # Output slot 


# --- World Decoration Functions (remain the same) ---
def add_trees(world, height_map, biome_map):
    """Randomly adds simple trees to the world on top of grass blocks. Skips plains and savannah biomes."""
    for col in range(GRID_WIDTH):
        biome_type = biome_map[col]
        # Skip tree spawning in plains and savannah (they have their own tree generation)
        if biome_type in [PLAINS_BIOME, SAVANNAH_BIOME]:
            continue
        
        # Determine tree type and spawn chance based on biome
        if biome_type == BIRCH_FOREST_BIOME:
            tree_chance = 0.1
            wood_id = 83  # Birch wood (white with black spots)
            leaves_id = 84  # Darker leaves
        elif biome_type == OAK_FOREST_BIOME:
            tree_chance = 0.1
            wood_id = WOOD_ID  # Oak wood
            leaves_id = LEAVES_ID  # Oak leaves
        elif biome_type in [JUNGLE_BIOME, BAMBOO_JUNGLE_BIOME]:
            tree_chance = 0.35  # MUCH denser jungles
            wood_id = WOOD_ID
            leaves_id = LEAVES_ID
        else:
            tree_chance = 0.1
            wood_id = WOOD_ID
            leaves_id = LEAVES_ID
            
        if random.random() < tree_chance:
            ground_row = height_map[col]
            if ground_row < GRID_HEIGHT and world[ground_row][col] == GRASS_ID:
                trunk_height = random.randint(3, 5)
                if ground_row - trunk_height >= 1: 
                    for r in range(ground_row - 1, ground_row - 1 - trunk_height, -1):
                        world[r][col] = wood_id 
                    
                    crown_top = ground_row - 1 - trunk_height - 1
                    for r in range(crown_top, crown_top + 3):
                        for c in range(col - 1, col + 2):
                            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                                if abs(r - (crown_top + 1)) + abs(c - col) <= 2:
                                    if world[r][c] == AIR_ID: 
                                        world[r][c] = leaves_id 

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


def generate_tree(world, col, row, biome_type):
    """Wrapper function to generate a tree based on biome type for sapling growth."""
    # Find ground level at this position
    ground_row = row + 1
    while ground_row < GRID_HEIGHT - 1 and world[ground_row][col] == 0:
        ground_row += 1
    
    # Generate tree based on biome type
    if biome_type == OAK_FOREST_BIOME:
        # Oak tree - simple trunk and leaves
        trunk_height = random.randint(4, 6)
        for r in range(ground_row - 1, ground_row - 1 - trunk_height, -1):
            if 0 <= r < GRID_HEIGHT:
                world[r][col] = WOOD_ID
        crown_top = ground_row - 1 - trunk_height - 1
        for r in range(crown_top, crown_top + 3):
            for c in range(col - 1, col + 2):
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    if abs(r - (crown_top + 1)) + abs(c - col) <= 2:
                        if world[r][c] == AIR_ID:
                            world[r][c] = LEAVES_ID
    elif biome_type == BIRCH_FOREST_BIOME:
        trunk_height = random.randint(5, 7)
        add_birch_tree(world, col, ground_row, trunk_height)
    elif biome_type == TAIGA_BIOME:
        trunk_height = random.randint(6, 9)
        add_spruce_tree(world, col, ground_row, trunk_height)
    elif biome_type in [JUNGLE_BIOME, BAMBOO_JUNGLE_BIOME]:
        trunk_height = random.randint(8, 12)
        add_jungle_tree(world, col, ground_row, trunk_height)

# --- STRUCTURE GENERATION FUNCTIONS ---

def generate_plains_village(world, height_map, col_start):
    """Generates a larger village with 3+ houses, farms with wheat/carrots, iron golems, farmers and librarians."""
    
    village_width = random.randint(30, 45)  # Much bigger
    house_count = random.randint(3, 5)  # 3-5 houses
    house_width_min = 5
    
    # Check for space and flatness across the entire potential village area
    for col in range(col_start, min(col_start + village_width, GRID_WIDTH)):
        if col >= GRID_WIDTH or world[height_map[col]][col] != GRASS_ID:
            return 0, []
        if abs(height_map[col] - height_map[col_start]) > 2:
            return 0, []
            
    ground_row = height_map[col_start]
    current_col = col_start
    villagers_to_spawn = []
    iron_golems_to_spawn = []
    
    print(f"🏠 LARGE PLAINS VILLAGE GENERATED at column {col_start} with {house_count} houses.")

    # 2. Generate Multiple Houses
    for i in range(house_count):
        house_width = random.randint(house_width_min, 7)
        house_height = random.randint(4, 6)
        
        if current_col + house_width >= col_start + village_width - 10:
            break
            
        house_ground_row = height_map[current_col]
        
        # Determine house type
        is_librarian_house = (i == 1)  # Second house is librarian
        is_smoker_house = (i == 2 and house_count >= 4)  # Third house is smoker if 4+ houses
        is_nitwit_house = (i == house_count - 1)  # Last house is nitwit
        
        # Determine door position (front wall center)
        door_col = current_col + house_width // 2
        
        # --- Draw Individual House ---
        for r in range(house_ground_row - house_height, house_ground_row + 1):
            for c in range(current_col, current_col + house_width):
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    # Stone floor
                    if r == house_ground_row:
                        world[r][c] = 3  # Stone
                    # Clear inside to Air
                    elif current_col < c < current_col + house_width - 1 and house_ground_row - house_height < r < house_ground_row:
                        world[r][c] = AIR_ID
                        # Add bookshelves in librarian house (on walls)
                        if is_librarian_house and (c == current_col + 1 or c == current_col + house_width - 2) and r == house_ground_row - 2:
                            world[r][c] = 98  # Bookshelf
                        # Add furnace in smoker house
                        if is_smoker_house and c == current_col + house_width // 2 and r == house_ground_row - 1:
                            world[r][c] = 16  # Furnace
                        # Add bed in nitwit house (wool blocks)
                        if is_nitwit_house and c == current_col + 2 and r == house_ground_row - 1:
                            world[r][c] = 7  # Wool bed
                        if is_nitwit_house and c == current_col + 3 and r == house_ground_row - 1:
                            world[r][c] = 7  # Wool bed
                    # Walls (Plank ID 8) - skip door position on front wall
                    elif r == house_ground_row - house_height or c == current_col + house_width - 1:
                        world[r][c] = PLANK_ID
                    elif c == current_col and not (c == door_col and r in [house_ground_row - 1, house_ground_row - 2]):
                        # Front wall, but leave gap for door
                        world[r][c] = PLANK_ID
                        
        # Roof (Wool ID 7)
        roof_row = house_ground_row - house_height - 1
        for c in range(current_col - 1, current_col + house_width + 1):
              if 0 <= roof_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                  world[roof_row][c] = WOOL_ID
                  
        # Door (Door block ID 91) - placed in the front wall
        world[house_ground_row - 1][door_col] = 91  # Door bottom
        world[house_ground_row - 2][door_col] = 91  # Door top

        # 3. Villager Spawning (type based on house)
        spawn_col = current_col + house_width // 2
        spawn_x = spawn_col * BLOCK_SIZE
        spawn_y = (house_ground_row - 2) * BLOCK_SIZE
        
        if spawn_y > 0 and 0 <= spawn_col < GRID_WIDTH:
            if is_librarian_house:
                villagers_to_spawn.append(Villager(spawn_x, spawn_y, "librarian"))
            elif is_smoker_house:
                villagers_to_spawn.append(Villager(spawn_x, spawn_y, "smoker"))
            elif is_nitwit_house:
                villagers_to_spawn.append(Villager(spawn_x, spawn_y, "nitwit"))
            else:
                villagers_to_spawn.append(Villager(spawn_x, spawn_y, "farmer"))
            
        current_col += house_width + random.randint(2, 4)

    # 4. Generate Large Farm with Wheat and Carrots
    farm_start_col = current_col + 2
    farm_width = 9  # 4 blocks + 1 water + 4 blocks
    farm_end_col = farm_start_col + farm_width
    
    # Make sure farm fits within world bounds
    if farm_end_col < GRID_WIDTH and farm_start_col < GRID_WIDTH:
        farm_row = height_map[farm_start_col]
        farm_center = farm_start_col + 4  # Center is 4 blocks from start
        
        for c in range(farm_start_col, min(farm_end_col, GRID_WIDTH)):
            if c == farm_center:
                # Water in the middle
                world[farm_row][c] = WATER_ID
            else:
                # Farmland with crops (4 blocks on each side of water)
                world[farm_row][c] = DIRT_ID
                # Place wheat or carrots on top
                if farm_row - 1 > 0:
                    if random.random() < 0.5:
                        world[farm_row - 1][c] = 95  # Wheat block
                    else:
                        world[farm_row - 1][c] = 96  # Carrot block
        
        current_col = farm_end_col
    
    # 6. Add Hay Bales near farms
    haybale_count = random.randint(2, 4)
    for _ in range(haybale_count):
        haybale_col = random.randint(farm_start_col - 2, min(farm_end_col + 2, GRID_WIDTH - 1))
        if 0 <= haybale_col < GRID_WIDTH:
            haybale_row = height_map[haybale_col]
            # Stack 2-3 hay bales
            stack_height = random.randint(2, 3)
            for h in range(stack_height):
                if haybale_row - h - 1 > 0:
                    world[haybale_row - h - 1][haybale_col] = 104  # Hay Bale
    
    # 7. Spawn Iron Golems (1-2 per village)
    golem_count = random.randint(1, 2)
    for _ in range(golem_count):
        golem_col = random.randint(col_start + 5, min(col_start + village_width - 5, GRID_WIDTH - 1))
        golem_x = golem_col * BLOCK_SIZE
        golem_y = (height_map[golem_col] - 3) * BLOCK_SIZE
        iron_golems_to_spawn.append(IronGolem(golem_x, golem_y))
        print(f"🤖 Iron Golem spawned at column {golem_col}")
    
    return current_col - col_start + 3, villagers_to_spawn + iron_golems_to_spawn


def generate_desert_temple(world, height_map, col_start):
    """Generates a symmetrical Sandstone pyramid structure."""

    temple_size = random.choice([7, 9, 11])
    temple_height = temple_size // 2 + 1 
    
    # ⚠️ REVISED: Allowed height difference increased from 3 to 4.
    max_height_diff = 4 
    
    # Check for space and flatness on Sand
    for col in range(col_start, col_start + temple_size):
        if col >= GRID_WIDTH:
            return 0  # Out of bounds
            
        # ⚠️ REVISED: Allow Sand (19) or Sandstone (20) as valid surface blocks
        surface_block_id = world[height_map[col]][col]
        if surface_block_id not in [SAND_ID, SANDSTONE_ID]:
             return 0  # Invalid surface block
        
        if abs(height_map[col] - height_map[col_start]) > max_height_diff:
            return 0  # Too bumpy
            
    print(f"✅ DESERT TEMPLE GENERATED (Symmetrical) at column {col_start}")

    ground_row = height_map[col_start]
    base_center_col = col_start + temple_size // 2
    
    # Draw the SYMMETRICAL pyramid (Sandstone ID 20)
    for h in range(temple_height):
        layer_width = temple_size - 2 * h
        layer_row = ground_row - 1 - h
        start_col_layer = base_center_col - layer_width // 2
        
        for c_offset in range(layer_width):
            c = start_col_layer + c_offset
            
            if 0 <= layer_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                if layer_row >= 0:
                    world[layer_row][c] = SANDSTONE_ID 
                        
    # Add a 'hidden' room entrance 
    entrance_row = ground_row - 1
    entrance_col = base_center_col 
    if 0 <= entrance_row < GRID_HEIGHT and 0 <= entrance_col < GRID_WIDTH:
        world[entrance_row][entrance_col] = AIR_ID 
                        
    return temple_size + 5


def generate_snow_igloo(world, height_map, col_start):
    """Generates an igloo made of snow with ice floor and spawns a penguin inside."""
    
    igloo_width = 7
    igloo_height = 4
    
    # Check for space and flatness on snow
    for col in range(col_start, col_start + igloo_width):
        if col >= GRID_WIDTH or world[height_map[col]][col] != SNOW_ID:
            return 0, []
        if abs(height_map[col] - height_map[col_start]) > 1:
            return 0, []
    
    ground_row = height_map[col_start]
    penguins_to_spawn = []
    
    print(f"🐧 SNOW IGLOO GENERATED at column {col_start}")
    
    center_col = col_start + igloo_width // 2
    
    # Floor (ice)
    for c in range(col_start, col_start + igloo_width):
        if 0 <= ground_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
            world[ground_row][c] = ICE_ID
    
    # Build dome using snow blocks
    for r in range(ground_row - igloo_height, ground_row):
        for c in range(col_start, col_start + igloo_width):
            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                dist_from_center = abs(c - center_col)
                height_from_ground = ground_row - r
                
                if height_from_ground <= igloo_height - dist_from_center:
                    if dist_from_center > 1 or height_from_ground < igloo_height - 1:
                        world[r][c] = SNOW_ID
                    else:
                        world[r][c] = AIR_ID
    
    # Door (entrance)
    door_col = col_start + igloo_width // 2
    world[ground_row - 1][door_col] = AIR_ID
    world[ground_row - 2][door_col] = AIR_ID
    
    # Spawn penguin inside
    spawn_x = center_col * BLOCK_SIZE
    spawn_y = (ground_row - 2) * BLOCK_SIZE
    
    if spawn_y > 0 and 0 <= center_col < GRID_WIDTH:
        penguins_to_spawn.append(Penguin(spawn_x, spawn_y))
    
    return igloo_width + 3, penguins_to_spawn


def generate_witch_hut(world, height_map, col_start):
    """Generates an elevated hut in the swamp biome with a witch inside."""
    
    hut_width = 7
    hut_height = 5
    
    # 1. Check for space and flatness on Swamp surface blocks (MUD_ID or SWAMP_WATER_ID)
    for col in range(col_start, col_start + hut_width):
        if col >= GRID_WIDTH:
            return 0
        surface_block = world[height_map[col]][col]
        if surface_block not in [MUD_ID, SWAMP_WATER_ID]:
            return 0
        if abs(height_map[col] - height_map[col_start]) > 2:
            return 0 # Too bumpy
            
    print(f"🛖 WITCH HUT GENERATED at column {col_start}")
    
    ground_row = min(height_map[col_start:col_start + hut_width])
    HUT_FLOOR_Y = ground_row - 5 
    
    # 1. Structure Pillars (Dark Oak Log) - Must go down to the solid ground
    for i in range(col_start, col_start + hut_width, 2): 
        for r in range(HUT_FLOOR_Y, ground_row + 1):
            if 0 <= r < GRID_HEIGHT and 0 <= i < GRID_WIDTH:
                if world[r][i] not in [BEDROCK_ID, MUD_ID, DIRT_ID]:
                    world[r][i] = DARK_OAK_LOG_ID 

    # 2. Floor, Walls, and Roof (Plank ID 8)
    for r in range(HUT_FLOOR_Y, HUT_FLOOR_Y + hut_height):
        for c in range(col_start, col_start + hut_width):
            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                is_wall = (c == col_start or c == col_start + hut_width - 1 or 
                           r == HUT_FLOOR_Y or r == HUT_FLOOR_Y + hut_height - 1)
                
                if is_wall:
                    world[r][c] = PLANK_ID
                else:
                    world[r][c] = AIR_ID

    # 3. Door (Air)
    door_col = col_start + hut_width // 2
    world[HUT_FLOOR_Y + 1][door_col] = AIR_ID
    world[HUT_FLOOR_Y + 2][door_col] = AIR_ID
    
    # 4. Chimney (Cobblestone)
    chimney_col = col_start + 1
    for r in range(HUT_FLOOR_Y + hut_height, HUT_FLOOR_Y + hut_height + 3):
        if 0 <= r < GRID_HEIGHT and 0 <= chimney_col < GRID_WIDTH:
            world[r][chimney_col] = COBBLESTONE_ID
    
    # 5. Spawn witch inside the hut
    witch_x = (col_start + hut_width // 2) * BLOCK_SIZE
    witch_y = (HUT_FLOOR_Y + 1) * BLOCK_SIZE
    witch = Witch(witch_x, witch_y)

    return hut_width + 5, witch 


def generate_shipwreck(world, height_map, col_start):
    """Generates a broken 18th century ship wreck in ocean biomes."""
    
    ship_length = 16
    ship_height = 8
    
    # Check for ocean biome (water-filled area)
    base_level = GRID_HEIGHT // 2
    for col in range(col_start, col_start + ship_length):
        if col >= GRID_WIDTH:
            return 0
        # Check if this is deep enough water
        ground_row = height_map[col]
        if ground_row < base_level + 10:  # Need at least 10 blocks of water depth
            return 0
    
    print(f"🚢 SHIPWRECK GENERATED at column {col_start}")
    
    # Place ship on ocean floor (partially buried)
    ground_row = height_map[col_start]
    ship_base_row = ground_row - 2  # Ship sits on/in the ocean floor
    
    # Define wood planks ID (use oak planks or similar)
    PLANKS_ID = 4  # Oak Planks
    DARK_PLANKS_ID = 9  # Spruce Planks (darker, for variety)
    
    # Build the ship hull (broken/damaged)
    for h in range(ship_height):
        hull_row = ship_base_row - h
        if h < 3:  # Bottom hull
            hull_width = ship_length
            for c in range(col_start, col_start + hull_width):
                if 0 <= hull_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    # Randomly break parts of the hull
                    if random.random() < 0.7:  # 70% chance for plank to be present
                        world[hull_row][c] = PLANKS_ID if random.random() < 0.6 else DARK_PLANKS_ID
        elif h < 6:  # Mid hull (narrower)
            hull_width = ship_length - 4
            offset = 2
            for c in range(col_start + offset, col_start + offset + hull_width):
                if 0 <= hull_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    # More broken in the middle
                    if random.random() < 0.5:
                        world[hull_row][c] = PLANKS_ID if random.random() < 0.6 else DARK_PLANKS_ID
        else:  # Top deck (very broken)
            deck_width = ship_length - 6
            offset = 3
            for c in range(col_start + offset, col_start + offset + deck_width):
                if 0 <= hull_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    if random.random() < 0.3:  # Only 30% remains
                        world[hull_row][c] = PLANKS_ID
    
    # Add a broken mast (vertical column)
    mast_col = col_start + ship_length // 2
    mast_height = random.randint(4, 7)  # Broken, not full height
    for h in range(mast_height):
        mast_row = ship_base_row - 3 - h
        if 0 <= mast_row < GRID_HEIGHT and 0 <= mast_col < GRID_WIDTH:
            world[mast_row][mast_col] = DARK_PLANKS_ID
    
    # Add some chests with loot (optional treasure)
    chest_row = ship_base_row - 1
    chest_col = col_start + ship_length // 3
    if 0 <= chest_row < GRID_HEIGHT and 0 <= chest_col < GRID_WIDTH:
        # TODO: Place chest block when chest system is implemented
        # For now, just clear space for potential treasure
        world[chest_row][chest_col] = AIR_ID
    
    return ship_length + 5


def generate_taiga_tower(world, height_map, col_start):
    """Generates a tall, stone Taiga Tower with a viewing platform."""
    
    tower_width = 5
    tower_height = random.randint(15, 25) 
    
    # 1. Check for space and flatness on Taiga surface blocks (COARSE_DIRT_ID or DIRT_ID)
    for col in range(col_start, col_start + tower_width):
        if col >= GRID_WIDTH:
            return 0
        surface_block = world[height_map[col]][col]
        if surface_block not in [COARSE_DIRT_ID, DIRT_ID, GRASS_ID]:
            return 0
        if abs(height_map[col] - height_map[col_start]) > 1:
            return 0 
            
    print(f"🏰 TAIGA TOWER GENERATED at column {col_start} (Height: {tower_height})")

    ground_row = height_map[col_start]
    
    # 1. Tower Base and Shaft (Cobblestone/Stone)
    for r in range(ground_row - tower_height, ground_row):
        for c in range(col_start, col_start + tower_width):
            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                is_wall = (c == col_start or c == col_start + tower_width - 1 or
                           r == ground_row - 1) 
                is_interior = (r < ground_row - 1 and col_start < c < col_start + tower_width - 1)

                if is_wall:
                    world[r][c] = COBBLESTONE_ID
                elif is_interior:
                    world[r][c] = AIR_ID 

    # 2. Add Ladder (41) for climbing
    ladder_col = col_start + tower_width - 1
    for r in range(ground_row - tower_height, ground_row - 1):
        if 0 <= r < GRID_HEIGHT and 0 <= ladder_col < GRID_WIDTH:
            world[r][ladder_col] = LADDER_ID

    # 3. Viewing Platform/Roof (Spruce Log 34)
    roof_row = ground_row - tower_height - 1
    for c in range(col_start - 2, col_start + tower_width + 2): 
        if 0 <= roof_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
            world[roof_row][c] = SPRUCE_LOG_ID
            
    return tower_width + 5

# --- NEW SPRUCE TREE GENERATION FUNCTION ---
def add_spruce_tree(world, col, ground_row, trunk_height):
    """Generates a single spruce tree with a conical leaf shape."""
    
    # 1. Generate the Trunk
    for r in range(ground_row - 1, ground_row - 1 - trunk_height, -1):
        if 0 <= r < GRID_HEIGHT:
            world[r][col] = SPRUCE_LOG_ID
            
    # 2. Generate the Leaves (Conical Shape)
    crown_top_row = ground_row - 1 - trunk_height
    
    # Layers of leaves (starts wide, gets narrower)
    for h in range(trunk_height + 1):
        r = crown_top_row + h # Start from the top and move down
        
        # Determine radius for the current layer
        # Layer 0 (Top): Radius 0 (1 block)
        # Layers 1, 2: Radius 1 (3x3 area)
        # Layers 3+: Radius 2 (5x5 area) - Capped to not be too wide
        if h == 0:
            radius = 0
        elif h < 3:
            radius = 1
        else:
            radius = 2

        # Draw the leaves for this layer
        for dc in range(-radius, radius + 1):
            for dr in range(-radius, radius + 1):
                leaf_col = col + dc
                leaf_row = r + dr

                if 0 <= leaf_row < GRID_HEIGHT and 0 <= leaf_col < GRID_WIDTH:
                    # Check for "roundness" and only place where air is
                    if world[leaf_row][leaf_col] == AIR_ID:
                        # Ensures the leaves form a solid block and don't place on logs already
                        if world[leaf_row][leaf_col] != SPRUCE_LOG_ID:
                             world[leaf_row][leaf_col] = LEAVES_ID


# --- BIRCH TREE GENERATION FUNCTION ---
def add_birch_tree(world, col, ground_row, trunk_height):
    """Generates a single birch tree with birch wood and leaves."""
    
    BIRCH_WOOD_ID = 83
    BIRCH_LEAVES_ID = 84
    
    # 1. Generate the Trunk
    for r in range(ground_row - 1, ground_row - 1 - trunk_height, -1):
        if 0 <= r < GRID_HEIGHT:
            world[r][col] = BIRCH_WOOD_ID
    
    # 2. Generate the Leaves (Round crown)
    crown_top_row = ground_row - 1 - trunk_height - 1
    
    # 2-3 layers of leaves
    for layer in range(3):
        r = crown_top_row + layer
        radius = 2 if layer == 1 else 1  # Middle layer wider
        
        for dc in range(-radius, radius + 1):
            leaf_col = col + dc
            
            if 0 <= leaf_col < GRID_WIDTH:
                # Fill vertically around this layer
                for dr in range(-1, 2):  # 3 rows per layer
                    leaf_row = r + dr
                    
                    if 0 <= leaf_row < GRID_HEIGHT:
                        if world[leaf_row][leaf_col] == AIR_ID:
                            # Random gaps for natural look (85% fill)
                            if random.random() < 0.85:
                                world[leaf_row][leaf_col] = BIRCH_LEAVES_ID


# --- JUNGLE TREE GENERATION FUNCTION ---
def add_jungle_tree(world, col, ground_row, trunk_height):
    """Generates a single tall jungle tree with vines."""
    
    JUNGLE_WOOD_ID = 124
    JUNGLE_LEAVES_ID = 126
    VINE_ID = 128
    
    # 1. Generate the Trunk (taller than normal trees)
    for r in range(ground_row - 1, ground_row - 1 - trunk_height, -1):
        if 0 <= r < GRID_HEIGHT:
            world[r][col] = JUNGLE_WOOD_ID
    
    # 2. Generate the Leaves (Large crown)
    crown_top_row = ground_row - 1 - trunk_height - 2
    
    # Multiple layers of leaves
    for layer in range(4):  # 4 layers of leaves
        r = crown_top_row + layer
        radius = 2 if layer < 3 else 3  # Larger at bottom
        
        for dc in range(-radius, radius + 1):
            leaf_col = col + dc
            
            if 0 <= leaf_col < GRID_WIDTH:
                # Fill vertically around this layer
                for dr in range(-1, 2):  # 3 rows per layer
                    leaf_row = r + dr
                    
                    if 0 <= leaf_row < GRID_HEIGHT:
                        if world[leaf_row][leaf_col] == AIR_ID:
                            # Random gaps for natural look (80% fill)
                            if random.random() < 0.8:
                                world[leaf_row][leaf_col] = JUNGLE_LEAVES_ID
    
    # 3. Add hanging vines
    for vine_attempt in range(random.randint(3, 6)):
        vine_col = col + random.randint(-3, 3)
        if 0 <= vine_col < GRID_WIDTH:
            # Find bottom of tree
            vine_start_row = ground_row - 1 - trunk_height
            vine_length = random.randint(2, 5)
            
            for v in range(vine_length):
                vine_row = vine_start_row + v
                if 0 <= vine_row < GRID_HEIGHT and world[vine_row][vine_col] == AIR_ID:
                    world[vine_row][vine_col] = VINE_ID


def add_acacia_tree(world, col, ground_row, trunk_height):
    """Generates a single acacia tree with distinctive flat-top canopy."""
    
    ACACIA_WOOD_ID = 147
    ACACIA_LEAVES_ID = 149
    
    # 1. Generate the Trunk (angled/bent trunk for acacia look)
    for r in range(ground_row - 1, ground_row - 1 - trunk_height, -1):
        if 0 <= r < GRID_HEIGHT:
            world[r][col] = ACACIA_WOOD_ID
    
    # Add bent trunk section (acacia trees have angled trunks)
    trunk_top_row = ground_row - 1 - trunk_height
    if trunk_top_row - 2 >= 0:
        # Angle the top part to the right
        world[trunk_top_row - 1][col + 1] = ACACIA_WOOD_ID if col + 1 < GRID_WIDTH else ACACIA_WOOD_ID
        world[trunk_top_row - 2][col + 2] = ACACIA_WOOD_ID if col + 2 < GRID_WIDTH else ACACIA_WOOD_ID
    
    # 2. Generate the Leaves (Flat-top canopy, characteristic of acacia)
    canopy_center_row = trunk_top_row - 3
    canopy_center_col = col + 2
    
    # Wide flat canopy (3 blocks tall, 5-7 blocks wide)
    for layer in range(3):
        r = canopy_center_row + layer
        width = 3 if layer == 0 else 2  # Top layer wider, lower layers smaller
        
        for dc in range(-width, width + 1):
            leaf_col = canopy_center_col + dc
            
            if 0 <= leaf_col < GRID_WIDTH and 0 <= r < GRID_HEIGHT:
                if world[r][leaf_col] == AIR_ID:
                    # Dense canopy (90% fill)
                    if random.random() < 0.9:
                        world[r][leaf_col] = ACACIA_LEAVES_ID


# --- TREE WRAPPER FOR SAPLING GROWTH ---
def generate_tree(world, col, row, biome_type):
    """Wrapper function to generate a tree based on biome type for sapling growth."""
    # Find ground level at this position
    ground_row = row + 1
    while ground_row < GRID_HEIGHT - 1 and world[ground_row][col] == 0:
        ground_row += 1
    
    # Generate tree based on biome type
    if biome_type == OAK_FOREST_BIOME:
        # Oak tree - simple trunk and leaves
        trunk_height = random.randint(4, 6)
        for r in range(ground_row - 1, ground_row - 1 - trunk_height, -1):
            if 0 <= r < GRID_HEIGHT:
                world[r][col] = WOOD_ID
        crown_top = ground_row - 1 - trunk_height - 1
        for r in range(crown_top, crown_top + 3):
            for c in range(col - 1, col + 2):
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    if abs(r - (crown_top + 1)) + abs(c - col) <= 2:
                        if world[r][c] == AIR_ID:
                            world[r][c] = LEAVES_ID
    elif biome_type == BIRCH_FOREST_BIOME:
        trunk_height = random.randint(5, 7)
        add_birch_tree(world, col, ground_row, trunk_height)
    elif biome_type == TAIGA_BIOME:
        trunk_height = random.randint(6, 9)
        add_spruce_tree(world, col, ground_row, trunk_height)
    elif biome_type in [JUNGLE_BIOME, BAMBOO_JUNGLE_BIOME]:
        trunk_height = random.randint(8, 12)
        add_jungle_tree(world, col, ground_row, trunk_height)
    elif biome_type == SAVANNAH_BIOME:
        trunk_height = random.randint(5, 7)
        add_acacia_tree(world, col, ground_row, trunk_height)


# --- BAMBOO GENERATION FUNCTION ---
def add_bamboo(world, col, ground_row):
    """Generates a single tall bamboo stalk."""
    
    BAMBOO_ID = 127
    bamboo_height = random.randint(8, 16)  # Tall and thin
    
    for r in range(ground_row - 1, max(0, ground_row - 1 - bamboo_height), -1):
        if 0 <= r < GRID_HEIGHT and world[r][col] == AIR_ID:
            world[r][col] = BAMBOO_ID


# --- Main World Generation Function (with Biome Logic) ---
def generate_world():
    """Generates a simple 2D world map, lakes, mobs, and structures across 5 biomes. (FIXED MOB SPAWNING)"""
    global MOBS, WORLD_MAP, STRUCTURE_NOTIFICATIONS

    world = []
    
    # 1. Fill with Sky/Air
    for _ in range(GRID_HEIGHT):
        world.append([AIR_ID] * GRID_WIDTH)

    base_level = GRID_HEIGHT // 2
    
    # --- Generate Height Map ---
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
    
    # --- Determine Biome Regions (5 biomes) ---
    biome_map = [] 
    
    all_biomes = [OAK_FOREST_BIOME, DESERT_BIOME, SNOW_BIOME, SWAMP_BIOME, TAIGA_BIOME, PLAINS_BIOME, BIRCH_FOREST_BIOME, JUNGLE_BIOME, BAMBOO_JUNGLE_BIOME, SAVANNAH_BIOME, OCEAN_BIOME]
    current_biome = random.choice(all_biomes)  
    biome_length = random.randint(100, 140)  # Half-chunk size biomes (128 +/- variation)
    col_counter = 0
    
    for col in range(GRID_WIDTH):
        if col_counter >= biome_length:
            # More balanced biome weights
            # Order: Oak, Desert, Snow, Swamp, Taiga, Plains, Birch, Jungle, Bamboo, Savannah, Ocean
            biome_weights = [1, 1, 1, 1, 1, 1.5, 1, 0.8, 0.5, 1, 1.2]  # Ocean more common, same as other biomes
            current_biome = random.choices(all_biomes, weights=biome_weights)[0]
            
            # Debug print for jungle biomes
            if current_biome == JUNGLE_BIOME:
                print(f"🌴 JUNGLE BIOME starting at column {col}, length will be {biome_length} blocks")
            elif current_biome == BAMBOO_JUNGLE_BIOME:
                print(f"🎋 BAMBOO JUNGLE BIOME starting at column {col}, length will be {biome_length} blocks")
            
            # Biomes now span approximately half a chunk (128 blocks)
            if current_biome == PLAINS_BIOME:
                biome_length = random.randint(120, 150)  # Slightly larger plains
            elif current_biome in [JUNGLE_BIOME, BAMBOO_JUNGLE_BIOME]:
                biome_length = random.randint(110, 160)  # Larger jungle biomes
            elif current_biome == OCEAN_BIOME:
                biome_length = random.randint(200, 400)  # Medium ocean biome (was 500-1000)
                print(f"🌊 OCEAN BIOME starting at column {col}, length will be {biome_length} blocks")
            else:
                biome_length = random.randint(100, 140)  # ~Half chunk for others
            col_counter = 0
        
        biome_map.append(current_biome)
        col_counter += 1
        
    # --- Populate World with Blocks ---
    for col in range(GRID_WIDTH):
        ground_level = height_map[col]
        biome_type = biome_map[col]
        
        # Define surface blocks based on biome type
        if biome_type == DESERT_BIOME:
            surface_block_id = SAND_ID
            subsurface_block_id = SAND_ID
            deep_block_id = SANDSTONE_ID
        elif biome_type == SNOW_BIOME:
            surface_block_id = SNOW_ID
            subsurface_block_id = SNOW_ID
            deep_block_id = ICE_ID
        elif biome_type == SWAMP_BIOME:
            surface_block_id = MUD_ID
            subsurface_block_id = MUD_ID
            deep_block_id = MUD_ID
        elif biome_type == OCEAN_BIOME:
            # Ocean floor should be DEEP underground (lower Y = higher row number)
            ground_level = min(base_level + 20, GRID_HEIGHT - 10)  # Floor 20 blocks deeper
            surface_block_id = SAND_ID
            subsurface_block_id = SAND_ID
            deep_block_id = STONE_ID 
        elif biome_type == TAIGA_BIOME:
            surface_block_id = COARSE_DIRT_ID
            subsurface_block_id = COARSE_DIRT_ID
            deep_block_id = STONE_ID 
        elif biome_type == PLAINS_BIOME:
            surface_block_id = GRASS_ID
            subsurface_block_id = DIRT_ID
            deep_block_id = DIRT_ID
        elif biome_type == BIRCH_FOREST_BIOME:
            surface_block_id = GRASS_ID
            subsurface_block_id = DIRT_ID
            deep_block_id = DIRT_ID
        elif biome_type in [JUNGLE_BIOME, BAMBOO_JUNGLE_BIOME]:
            surface_block_id = 123  # Podzol
            subsurface_block_id = DIRT_ID
            deep_block_id = DIRT_ID
        elif biome_type == SAVANNAH_BIOME:
            surface_block_id = SAND_ID  # Yellow sand instead of brown coarse dirt
            subsurface_block_id = DIRT_ID
            deep_block_id = DIRT_ID
        else: # OAK_FOREST_BIOME (0)
            surface_block_id = GRASS_ID
            subsurface_block_id = DIRT_ID
            deep_block_id = DIRT_ID
        
        
        for row in range(ground_level, GRID_HEIGHT):
            if row == GRID_HEIGHT - 1:
                world[row][col] = BEDROCK_ID
            elif row == ground_level:
                world[row][col] = surface_block_id
            elif row <= ground_level + 2:
                world[row][col] = subsurface_block_id
            elif row <= ground_level + 5:
                # Ensure Swamp uses MUD_ID deep down, others use their defined deep_block_id
                if biome_type == SWAMP_BIOME:
                    world[row][col] = MUD_ID 
                else:
                    world[row][col] = deep_block_id
            else:
                block_id = STONE_ID
                
                # --- Ore and Cave Generation ---
                r = random.random()
                if r < 0.04: 
                    block_id = AIR_ID
                elif r < 0.08: 
                    block_id = 11 
                elif r < 0.11: 
                    block_id = 12 
                
                world[row][col] = block_id
        
        # Fill ocean biomes with water from surface down to ocean floor
        if biome_type == OCEAN_BIOME:
            # Water fills from normal surface height down to the deep ocean floor
            surface_level = base_level  # Normal world surface
            for row in range(surface_level, ground_level):
                if world[row][col] == AIR_ID:
                    world[row][col] = WATER_ID
    
    # --- MOB/LAKE VARIABLES ---
    mobs = pygame.sprite.Group() 
    zombies_spawned = 0 
    narwhals_spawned = 0 
    turtles_to_spawn = []  # Store turtles to add after lake generation
    fish_to_spawn = []  # Store fish to add after ocean generation
    
    LAKE_PROBABILITY = 0.02
    MAX_LAKE_DEPTH = 5
    MAX_LAKE_WIDTH = 15
    current_lake_width = 0
    lake_bottom_row = 0
    lake_start_col = 0  # Track where the lake started
    lake_surface_row = 0  # Track the water surface
    
    WORLD_MAP = world 
    
    # --- FIRST PASS: LAKE CARVING ONLY ---
    for col in range(GRID_WIDTH):
        ground_row = height_map[col] 
        biome_type = biome_map[col]
        
        # Don't spawn lakes in ocean biomes
        if current_lake_width == 0 and biome_type != OCEAN_BIOME:
            if random.random() < LAKE_PROBABILITY:
                current_lake_width = random.randint(5, MAX_LAKE_WIDTH)
                lake_bottom_row = ground_row + random.randint(3, MAX_LAKE_DEPTH) 
                lake_bottom_row = min(lake_bottom_row, GRID_HEIGHT - 5)
                lake_start_col = col  # Mark the start of this lake
        
        if current_lake_width > 0:
            water_surface_row = ground_row 
            lake_surface_row = water_surface_row  # Store for narwhal spawning
            
            # Set biome to LAKE_BIOME
            biome_map[col] = LAKE_BIOME
            
            water_id = SWAMP_WATER_ID if biome_type == SWAMP_BIOME else WATER_ID
            
            for r in range(water_surface_row, lake_bottom_row):
                if 0 <= r < GRID_HEIGHT:
                    if r == lake_bottom_row - 1:
                        # Gravel at bottom of lakes (except swamp uses mud)
                        if biome_type == SWAMP_BIOME:
                            WORLD_MAP[r][col] = MUD_ID
                        else:
                            WORLD_MAP[r][col] = 26  # Gravel ID
                    else:
                        WORLD_MAP[r][col] = water_id 
            
            # Decrement lake width counter
            current_lake_width -= 1
            
            # When lake is complete, add biome-appropriate beaches and spawn mobs
            if current_lake_width == 0 and water_id == WATER_ID:
                # Add beaches with biome-specific materials
                lake_end_col = col
                
                # Determine original biome type (check columns before lake)
                original_biome = biome_type
                if lake_start_col > 0:
                    original_biome = biome_map[lake_start_col - 1]
                
                # Choose beach material based on biome
                if original_biome == SNOW_BIOME:
                    beach_material = ICE_ID  # Ice in snowy biomes
                elif original_biome in [TAIGA_BIOME, SWAMP_BIOME]:
                    beach_material = MUD_ID  # Mud in taiga/swamp
                else:
                    beach_material = SAND_ID  # Sand in other biomes
                
                # Left beach
                for beach_col in range(max(0, lake_start_col - 3), lake_start_col):
                    beach_ground = height_map[beach_col]
                    for r in range(beach_ground, min(beach_ground + 3, GRID_HEIGHT)):
                        if WORLD_MAP[r][beach_col] in [DIRT_ID, GRASS_ID, SNOW_ID, MUD_ID]:
                            WORLD_MAP[r][beach_col] = beach_material
                
                # Right beach
                for beach_col in range(lake_end_col + 1, min(GRID_WIDTH, lake_end_col + 4)):
                    beach_ground = height_map[beach_col]
                    for r in range(beach_ground, min(beach_ground + 3, GRID_HEIGHT)):
                        if WORLD_MAP[r][beach_col] in [DIRT_ID, GRASS_ID, SNOW_ID, MUD_ID]:
                            WORLD_MAP[r][beach_col] = beach_material
                
                # Spawn narwhal in taiga/snow lakes only
                if original_biome in [TAIGA_BIOME, SNOW_BIOME]:
                    if random.random() < 1.0:  # 100% chance for testing
                        lake_middle_col = (lake_start_col + lake_end_col) // 2
                        spawn_narwhal_x = lake_middle_col * BLOCK_SIZE
                        spawn_narwhal_y = water_surface_row * BLOCK_SIZE
                        mobs.add(Narwhal(spawn_narwhal_x, spawn_narwhal_y))
                        narwhals_spawned += 1
                
                # Spawn fish (cod/salmon) in all lakes
                if random.random() < 0.7:  # 70% chance for fish in lakes
                    num_fish = random.randint(2, 5)
                    for _ in range(num_fish):
                        fish_col = random.randint(lake_start_col, lake_end_col)
                        spawn_fish_x = fish_col * BLOCK_SIZE
                        # Spawn at random depth in lake (ensure valid range)
                        if lake_bottom_row > water_surface_row + 4:
                            fish_depth = random.randint(water_surface_row + 2, lake_bottom_row - 2)
                            spawn_fish_y = fish_depth * BLOCK_SIZE
                            
                            # 50% cod, 50% salmon
                            if random.random() < 0.5:
                                fish_to_spawn.append(Cod(spawn_fish_x, spawn_fish_y))
                            else:
                                fish_to_spawn.append(Salmon(spawn_fish_x, spawn_fish_y))
                    if lake_bottom_row > water_surface_row + 4:
                        print(f"🐟 {num_fish} fish spawned in lake at columns {lake_start_col}-{lake_end_col}")
                
                # Spawn turtles in other biome lakes
                if original_biome not in [TAIGA_BIOME, SNOW_BIOME]:
                    if random.random() < 0.8:  # 80% chance to spawn 1-2 turtles
                        num_turtles = random.randint(1, 2)
                        for _ in range(num_turtles):
                            turtle_col = random.randint(lake_start_col, lake_end_col)
                            spawn_turtle_x = turtle_col * BLOCK_SIZE
                            spawn_turtle_y = water_surface_row * BLOCK_SIZE
                            new_turtle = Turtle(spawn_turtle_x, spawn_turtle_y)
                            turtles_to_spawn.append(new_turtle)
                        print(f"🐢 {num_turtles} turtle(s) will spawn in lake at columns {lake_start_col}-{lake_end_col}")
                    
                    # Spawn flamingos in all lakes (not just swamp)
                    if random.random() < 0.6:  # 60% chance to spawn 1-3 flamingos
                        num_flamingos = random.randint(1, 3)
                        for _ in range(num_flamingos):
                            flamingo_col = random.randint(lake_start_col, lake_end_col)
                            spawn_flamingo_x = flamingo_col * BLOCK_SIZE
                            spawn_flamingo_y = water_surface_row * BLOCK_SIZE
                            mobs.add(Bird(spawn_flamingo_x, spawn_flamingo_y, variant="pink"))
                        print(f"🦩 {num_flamingos} flamingo(s) spawned in lake at columns {lake_start_col}-{lake_end_col}")
                    
                    # Spawn ducks in swamp lakes
                    if biome_type == SWAMP_BIOME and random.random() < 0.7:  # 70% chance in swamp
                        num_ducks = random.randint(2, 4)
                        for _ in range(num_ducks):
                            duck_col = random.randint(lake_start_col, lake_end_col)
                            spawn_duck_x = duck_col * BLOCK_SIZE
                            spawn_duck_y = water_surface_row * BLOCK_SIZE
                            mobs.add(Bird(spawn_duck_x, spawn_duck_y, variant="brown"))
                        print(f"🦆 {num_ducks} duck(s) spawned in swamp lake at columns {lake_start_col}-{lake_end_col}")
                    
                    # Rarely spawn Drowned in lakes (5% chance per lake)
                    if random.random() < 0.5:
                        drowned_col = random.randint(lake_start_col, lake_end_col)
                        spawn_drowned_x = drowned_col * BLOCK_SIZE
                        spawn_drowned_y = water_surface_row * BLOCK_SIZE
                        mobs.add(Drowned(spawn_drowned_x, spawn_drowned_y))
                        print(f"🧟 Drowned spawned at column {drowned_col} in lake")

    # --- STRUCTURE AND DECORATION PASS --- 
    
    villages_spawned = 0
    last_village_col = -100 
    
    col = 0
    while col < GRID_WIDTH:
        current_biome_type = biome_map[col]
        
        col_end = col
        while col_end < GRID_WIDTH and biome_map[col_end] == current_biome_type:
            col_end += 1
        
        biome_length = col_end - col
        blocks_used = 0
        
        structure_start_limit = col + 5
        structure_end_limit = col_end - 15 
        
        if structure_start_limit < structure_end_limit:
            structure_col_start = random.randint(structure_start_limit, structure_end_limit)
            
            # TAIGA TOWER
            if current_biome_type == TAIGA_BIOME and random.random() < 0.6:
                blocks_used = generate_taiga_tower(WORLD_MAP, height_map, structure_col_start)
                if blocks_used > 0:
                    print(f"🗼 Taiga Tower spawned at column {structure_col_start}")
                    STRUCTURE_NOTIFICATIONS.append(["Taiga Tower (Taiga)", structure_col_start, FPS * 10])
                
            # WITCH HUT
            elif current_biome_type == SWAMP_BIOME and random.random() < 0.7:
                result = generate_witch_hut(WORLD_MAP, height_map, structure_col_start)
                if isinstance(result, tuple):
                    blocks_used, witch = result
                    mobs.add(witch)
                    print(f"🏚️ Witch Hut spawned at column {structure_col_start}")
                    STRUCTURE_NOTIFICATIONS.append(["Witch Hut (Swamp)", structure_col_start, FPS * 10])
                else:
                    blocks_used = result
            
            # Desert Temple (Existing)
            elif current_biome_type == DESERT_BIOME and random.random() < 0.7:
                blocks_used = generate_desert_temple(WORLD_MAP, height_map, structure_col_start)
                if blocks_used > 0:
                    print(f"🏜️ Desert Temple spawned at column {structure_col_start}")
                    STRUCTURE_NOTIFICATIONS.append(["Desert Temple (Desert)", structure_col_start, FPS * 10])

            # Ocean Shipwreck (New)
            elif current_biome_type == OCEAN_BIOME and random.random() < 0.5:
                blocks_used = generate_shipwreck(WORLD_MAP, height_map, structure_col_start)
                if blocks_used > 0:
                    print(f"🚢 Shipwreck spawned at column {structure_col_start}")
                    STRUCTURE_NOTIFICATIONS.append(["Shipwreck (Ocean)", structure_col_start, FPS * 10])

            # Snow Igloo (Existing)
            elif current_biome_type == SNOW_BIOME and random.random() < 0.8:
                blocks_used, penguins = generate_snow_igloo(WORLD_MAP, height_map, structure_col_start)
                if blocks_used > 0:
                    mobs.add(*penguins)
                    print(f"🏔️ Snow Igloo spawned at column {structure_col_start}")
                    STRUCTURE_NOTIFICATIONS.append(["Snow Igloo (Snow)", structure_col_start, FPS * 10]) 
            
            # Plains Village - Multiple per plains biome (more common)
            elif current_biome_type == PLAINS_BIOME and col - last_village_col > 80:
                # 60% chance to spawn village in plains
                if random.random() < 0.6:
                    for attempt in range(5):  # More attempts to find a good spot
                        village_start = col + random.randint(5, max(6, biome_length - 35))
                        blocks_used, villagers = generate_plains_village(WORLD_MAP, height_map, village_start)
                        
                        if blocks_used > 0:
                            villages_spawned += 1
                            last_village_col = village_start
                            mobs.add(*villagers)
                            structure_col_start = village_start # Set start for decoration update
                            print(f"🏘️ Village #{villages_spawned} spawned at column {village_start}")
                            STRUCTURE_NOTIFICATIONS.append([f"Village #{villages_spawned} (Plains)", village_start, FPS * 10])
                            break 
            
        # Spawn fish in ocean biomes
        if current_biome_type == OCEAN_BIOME:
            print(f"🌊 Processing ocean biome at columns {col}-{col_end}")
            # Spawn fish throughout the ocean (every 10 blocks on average)
            for spawn_col in range(col, col_end, 10):
                if random.random() < 0.9:  # 90% chance per spawn point
                    # Spawn at various depths in the water
                    if spawn_col < len(height_map):
                        ground_row = height_map[spawn_col]
                        base_level = GRID_HEIGHT // 2
                        surface_row = base_level
                        
                        # Random depth between surface and floor
                        if ground_row > surface_row + 10:
                            spawn_depth = random.randint(surface_row + 5, ground_row - 5)
                            
                            spawn_x = spawn_col * BLOCK_SIZE
                            spawn_y = spawn_depth * BLOCK_SIZE
                            
                            # 50% cod, 50% salmon
                            if random.random() < 0.5:
                                fish_to_spawn.append(Cod(spawn_x, spawn_y))
                            else:
                                fish_to_spawn.append(Salmon(spawn_x, spawn_y))
            
            # Spawn kelp in groups of 5 (every 15 blocks on average)
            for spawn_col in range(col, col_end, 15):
                if random.random() < 0.6:  # 60% chance for kelp patch
                    if spawn_col < len(height_map):
                        ground_row = height_map[spawn_col]
                        base_level = GRID_HEIGHT // 2
                        
                        # Place kelp on ocean floor, growing upward 5 blocks
                        if ground_row > base_level + 5:
                            for kelp_row in range(ground_row - 5, ground_row):
                                if 0 <= kelp_row < GRID_HEIGHT:
                                    WORLD_MAP[kelp_row][spawn_col] = 160  # Kelp
            
            # Spawn coral blocks on ocean floor in clusters (every 40 blocks for a cluster start)
            for spawn_col in range(col, col_end, 40):
                if random.random() < 0.7:  # 70% chance for coral cluster
                    if spawn_col < len(height_map):
                        ground_row = height_map[spawn_col]
                        base_level = GRID_HEIGHT // 2
                        
                        # Place coral clusters (3-7 blocks wide)
                        if ground_row > base_level + 3:
                            cluster_size = random.randint(3, 7)
                            coral_id = random.choice([161, 162, 163])  # Yellow, Red, Blue coral
                            
                            for offset in range(cluster_size):
                                coral_col = spawn_col + offset
                                if coral_col < len(height_map) and coral_col < GRID_WIDTH:
                                    coral_ground = height_map[coral_col]
                                    WORLD_MAP[coral_ground][coral_col] = coral_id
                                    
                                    # Spawn 2-4 tropical fish per coral cluster at various depths
                                    if offset == cluster_size // 2:  # Spawn in middle of cluster
                                        num_fish = random.randint(2, 4)
                                        for _ in range(num_fish):
                                            fish_spawn_x = coral_col * BLOCK_SIZE
                                            # Spawn fish in water column above coral (5-15 blocks up)
                                            fish_depth = coral_ground - random.randint(5, 15)
                                            fish_spawn_y = fish_depth * BLOCK_SIZE
                                            is_large = random.random() < 0.3  # 30% chance for large fish
                                            fish_to_spawn.append(TropicalFish(fish_spawn_x, fish_spawn_y, is_large))
        
        # Update decoration/loop start
        if blocks_used > 0:
            decoration_start = structure_col_start + blocks_used
            col = decoration_start
        else:
            decoration_start = col
            
        # Add decorations for the strip
        if current_biome_type == OAK_FOREST_BIOME:
            add_trees(WORLD_MAP, height_map, biome_map)
        elif current_biome_type == PLAINS_BIOME:
            # Plains: No trees, completely flat grassland
            pass
        elif current_biome_type == DESERT_BIOME:
            add_cacti(WORLD_MAP, height_map, decoration_start, col_end)
            add_dead_bushes(WORLD_MAP, height_map, decoration_start, col_end)
        elif current_biome_type == TAIGA_BIOME:
            # Taiga trees (Spruce trees)
            for c in range(decoration_start, col_end):
                if random.random() < 0.05: 
                    ground_row = height_map[c]
                    if WORLD_MAP[ground_row][c] == COARSE_DIRT_ID:
                        trunk_height = random.randint(5, 7)
                        # 🌳 Calls the function that adds logs AND leaves
                        add_spruce_tree(WORLD_MAP, c, ground_row, trunk_height)
            # Berry bushes (taiga surface decoration)
            for c in range(decoration_start, col_end):
                if random.random() < 0.08:  # 8% chance for berry bushes
                    ground_row = height_map[c]
                    if WORLD_MAP[ground_row][c] == COARSE_DIRT_ID and ground_row > 0:
                        # Place berry bush on surface
                        WORLD_MAP[ground_row - 1][c] = 143  # Berry Bush ID
        elif current_biome_type == BIRCH_FOREST_BIOME:
            # Birch trees (White bark trees)
            for c in range(decoration_start, col_end):
                if random.random() < 0.06:  # 6% spawn rate
                    ground_row = height_map[c]
                    if WORLD_MAP[ground_row][c] == GRASS_ID:
                        trunk_height = random.randint(5, 8)  # Slightly taller than oak
                        add_birch_tree(WORLD_MAP, c, ground_row, trunk_height)
        elif current_biome_type == JUNGLE_BIOME:
            # Jungle trees (Tall trees with vines) - INCREASED TO 10+ TREES
            tree_count = 0
            target_trees = random.randint(10, 15)  # Ensure at least 10 trees per jungle biome
            attempts = 0
            max_attempts = (col_end - decoration_start) * 2  # Allow multiple passes if needed
            
            while tree_count < target_trees and attempts < max_attempts:
                c = random.randint(decoration_start, col_end - 1)
                attempts += 1
                
                if c < GRID_WIDTH:
                    ground_row = height_map[c]
                    if WORLD_MAP[ground_row][c] == 123:  # Podzol
                        # Check if there's already a tree here
                        has_tree = False
                        for check_r in range(max(0, ground_row - 25), ground_row):
                            if WORLD_MAP[check_r][c] == 126:  # Jungle wood ID
                                has_tree = True
                                break
                        
                        if not has_tree:
                            trunk_height = random.randint(15, 25)  # Very tall trees
                            add_jungle_tree(WORLD_MAP, c, ground_row, trunk_height)
                            tree_count += 1
            
            print(f"🌴 Jungle biome at cols {decoration_start}-{col_end} spawned {tree_count} trees")
        elif current_biome_type == BAMBOO_JUNGLE_BIOME:
            # Bamboo jungle (Bamboo instead of trees)
            for c in range(decoration_start, col_end):
                if random.random() < 0.15:  # Very dense bamboo
                    ground_row = height_map[c]
                    if WORLD_MAP[ground_row][c] == 123:  # Podzol
                        add_bamboo(WORLD_MAP, c, ground_row)
        elif current_biome_type == SAVANNAH_BIOME:
                # Savannah: Exactly 3 acacia trees per biome
            biome_length = col_end - decoration_start
            if biome_length >= 30:  # Only add trees if biome is large enough
                # Divide biome into thirds and place one tree in each third
                third_size = biome_length // 3
                for i in range(3):
                    tree_col = decoration_start + (i * third_size) + random.randint(5, third_size - 5)
                    if tree_col < col_end and tree_col < GRID_WIDTH:
                        ground_row = height_map[tree_col]
                        if WORLD_MAP[ground_row][tree_col] == GRASS_ID:  # Check for grass surface
                            trunk_height = random.randint(5, 7)
                            add_acacia_tree(WORLD_MAP, tree_col, ground_row, trunk_height)
                print(f"🌳 Savannah biome at cols {decoration_start}-{col_end} spawned 3 acacia trees")        # If no structure was built, move to the end of the current biome chunk
        if blocks_used == 0:
            col = col_end 

    # --- SECOND PASS: MOB SPAWNING (Independent IFs for Taiga/Swamp) ---
    for col in range(GRID_WIDTH):
        ground_row = height_map[col]
        biome_type = biome_map[col]
        
        surface_block = WORLD_MAP[ground_row][col] if ground_row < GRID_HEIGHT else AIR_ID
        
        is_valid_surface = (surface_block == GRASS_ID or surface_block == SAND_ID or 
                            surface_block == PLANK_ID or surface_block == WOOL_ID or 
                            surface_block == SNOW_ID or surface_block == ICE_ID or
                            surface_block == MUD_ID or surface_block == COARSE_DIRT_ID) 
        
        if ground_row < GRID_HEIGHT and is_valid_surface: 
            spawn_x = col * BLOCK_SIZE
            spawn_y = (ground_row - 2) * BLOCK_SIZE 
            
            if zombies_spawned == 0 and abs(col - GRID_WIDTH // 2) < 5:
                mobs.add(Zombie(spawn_x, spawn_y, biome_type))
                zombies_spawned += 1
            else:
                
                # 🐸 SWAMP BIOME MOB SPAWNING (Witch, Slime, Frog) - **INDEPENDENT IF CHECKS**
                if biome_type == SWAMP_BIOME:
                    r_mob = random.random()
                    
                    # No zombies, witches, or slimes during initial generation (only spawn at night)
                    # Frog has a slightly higher chance
                    if r_mob < 0.035 : mobs.add(Frog(spawn_x, spawn_y + BLOCK_SIZE))
                    if r_mob < 0.08: mobs.add(Bird(spawn_x, spawn_y - BLOCK_SIZE * 5, variant="pink"))  # 8% pink bird spawn 

                # 🐺 TAIGA BIOME MOB SPAWNING (Wolf, Fox, rare Stray skeletons) - **INDEPENDENT IF CHECKS**
                elif biome_type == TAIGA_BIOME:
                    r_mob = random.random()
                    
                    # No strays during initial generation (only spawn at night)
                    # Wolf
                    if r_mob < 0.01: mobs.add(Wolf(spawn_x, spawn_y)) 
                    
                    # Fox
                    if r_mob < 0.01 : mobs.add(Fox(spawn_x, spawn_y))
                    
                    # Purple bird
                    if r_mob < 0.08: mobs.add(Bird(spawn_x, spawn_y - BLOCK_SIZE * 5, variant="purple"))  # 8% purple bird spawn 

                # Existing biome mob logic (retained original elif structure for now)
                elif biome_type == DESERT_BIOME:
                    r = random.random()
                    if r < 0.03:
                        camel = Camel(spawn_x, spawn_y + BLOCK_SIZE)
                        camel.health = random.randint(5, 15)  # Spawn with damage
                        mobs.add(camel)
                    if r < 0.18: mobs.add(Rabbit(spawn_x, spawn_y + BLOCK_SIZE))  # 15% rabbit spawn
                    # No husks or spiders during initial generation (only spawn at night)
                elif biome_type == SNOW_BIOME:
                    r = random.random()
                    if r < 0.15:
                        mobs.add(Penguin(spawn_x, spawn_y + BLOCK_SIZE))  # 15% penguin spawn
                    if r < 0.17: mobs.add(Bear(spawn_x, spawn_y, is_polar=True))  # 2% polar bear spawn
                    # No hostile mobs spawn during initial generation (creepers and strays only spawn at night)
                elif biome_type == PLAINS_BIOME:
                    # Spawn farm animals in groups (every 5 blocks) - REDUCED RATES
                    if col % 5 == 0:  # Only check every 5 blocks
                        r = random.random()
                        # Reduced spawn rates for less abundance
                        if r < 0.15:
                            # Spawn sheep group (smaller)
                            for offset in range(0, 3):
                                if col + offset < GRID_WIDTH:
                                    mobs.add(Sheep(spawn_x + offset * BLOCK_SIZE, spawn_y + BLOCK_SIZE))
                        elif r < 0.30:
                            # Spawn cow group (smaller)
                            for offset in range(0, 3):
                                if col + offset < GRID_WIDTH:
                                    mobs.add(Cow(spawn_x + offset * BLOCK_SIZE, spawn_y + BLOCK_SIZE))
                        elif r < 0.45:
                            # Spawn chicken group (smaller)
                            for offset in range(0, 3):
                                if col + offset < GRID_WIDTH:
                                    mobs.add(Chicken(spawn_x + offset * BLOCK_SIZE, spawn_y + BLOCK_SIZE))
                        elif r < 0.55:
                            # Spawn pig group (smaller)
                            for offset in range(0, 3):
                                if col + offset < GRID_WIDTH:
                                    mobs.add(Pig(spawn_x + offset * BLOCK_SIZE, spawn_y + BLOCK_SIZE))
                        elif r < 0.60:
                            # Spawn horses (individual, not groups)
                            mobs.add(Horse(spawn_x, spawn_y + BLOCK_SIZE))
                    # Red bird in plains
                    r_bird = random.random()
                    if r_bird < 0.08: mobs.add(Bird(spawn_x, spawn_y - BLOCK_SIZE * 5, variant="red"))  # 8% red bird spawn
                    # Sparse hostile mob spawns (REMOVED - only spawn at night during gameplay)
                    # r2 = random.random()
                    # No hostile mobs during initial generation
                elif biome_type == BIRCH_FOREST_BIOME:
                    r = random.random()
                    if r < 0.03: mobs.add(Deer(spawn_x, spawn_y))  # Deer spawn at 3%
                    if r < 0.04: mobs.add(Bear(spawn_x, spawn_y, is_polar=False))  # 1% bear spawn
                    if r < 0.08: mobs.add(Bird(spawn_x, spawn_y - BLOCK_SIZE * 5, variant="yellow"))  # 8% yellow bird spawn
                    # No hostile mobs during initial generation (only spawn at night)
                elif biome_type in [JUNGLE_BIOME, BAMBOO_JUNGLE_BIOME]:
                    r = random.random()
                    if biome_type == BAMBOO_JUNGLE_BIOME:
                        if r < 0.20: mobs.add(Panda(spawn_x, spawn_y))  # 20% panda ONLY in bamboo jungle
                    # Removed panda spawn from regular jungle
                    if r < 0.05: mobs.add(Monkey(spawn_x, spawn_y))  # 5% monkey spawn in both jungles
                    if r < 0.10: mobs.add(Bird(spawn_x, spawn_y - BLOCK_SIZE * 5, variant="green"))  # 10% green bird spawn
                elif biome_type == SAVANNAH_BIOME:
                    r = random.random()
                    
                    # Check for elephants - only spawn if no trees within 10 blocks
                    if r < 0.005:  # 0.5% chance to attempt elephant spawn
                        can_spawn_elephant = True
                        
                        # First check if spawn point has enough air blocks above
                        has_space = True
                        for air_check in range(1, 8):  # Check 7 blocks of air above
                            check_air_row = ground_row - air_check
                            if check_air_row >= 0 and WORLD_MAP[check_air_row][col] != 0:
                                has_space = False
                                break
                        
                        if not has_space:
                            can_spawn_elephant = False
                        
                        # Check 10 blocks in each direction for trees (acacia wood = 147)
                        if can_spawn_elephant:
                            for check_col in range(max(0, col - 10), min(GRID_WIDTH, col + 10)):
                                for check_row in range(max(0, ground_row - 20), ground_row):
                                    if 0 <= check_row < GRID_HEIGHT and 0 <= check_col < len(WORLD_MAP[0]):
                                        if WORLD_MAP[check_row][check_col] == 147:  # Acacia wood
                                            can_spawn_elephant = False
                                            break
                                if not can_spawn_elephant:
                                    break
                        
                        if can_spawn_elephant:
                            # Elephants are 7 blocks tall, need to spawn higher
                            elephant_spawn_y = (ground_row - 9) * BLOCK_SIZE  # 7 blocks for elephant + 2 blocks clearance
                            mobs.add(Elephant(spawn_x, elephant_spawn_y))
                            print(f"🐘 Elephant spawned at column {col}")
                    
                    # Lion spawning (neutral, becomes aggressive when provoked)
                    if r < 0.02: mobs.add(Lion(spawn_x, spawn_y))  # 2% lion spawn
                    
                    # Rhino spawning (neutral, becomes aggressive when provoked)
                    if r < 0.015: mobs.add(Rhino(spawn_x, spawn_y))  # 1.5% rhino spawn
                    
                    # Ostrich spawning (rideable)
                    if r < 0.03: mobs.add(Ostrich(spawn_x, spawn_y))  # 3% ostrich spawn
                    
                    # Orange bird in savannah
                    if r < 0.08: mobs.add(Bird(spawn_x, spawn_y - BLOCK_SIZE * 5, variant="orange"))  # 8% orange bird spawn
                else:  # OAK_FOREST_BIOME
                    r = random.random()
                    if r < 0.03: mobs.add(Deer(spawn_x, spawn_y))  # Deer spawn at 3%
                    if r < 0.04: mobs.add(Bear(spawn_x, spawn_y, is_polar=False))  # 1% bear spawn
                    # Half red birds, half light blue birds
                    if r < 0.08:
                        bird_variant = "red" if random.random() < 0.5 else "lightblue"
                        mobs.add(Bird(spawn_x, spawn_y - BLOCK_SIZE * 5, variant=bird_variant))
                    # No hostile mobs during initial generation (only spawn at night)

    # Add all turtles that were spawned in lakes
    if turtles_to_spawn:
        mobs.add(*turtles_to_spawn)
        print(f"🐢 Added {len(turtles_to_spawn)} turtles to world from lakes!")
    
    # Add all fish that were spawned in oceans and lakes
    if fish_to_spawn:
        mobs.add(*fish_to_spawn)
        print(f"🐟 Added {len(fish_to_spawn)} fish to world from oceans and lakes!")

    MOBS = mobs
    return world, mobs, biome_map

def get_chunk_id(world_x):
    """Convert world X coordinate to chunk ID."""
    return world_x // CHUNK_SIZE

def check_and_load_chunks(player_col):
    """Check if player is near chunk boundaries and load new chunks if needed."""
    global WORLD_MAP, BIOME_MAP, GRID_WIDTH, CURRENT_CHUNK_RANGE
    
    player_chunk = get_chunk_id(player_col)
    
    # Check if we need to expand the loaded chunk range
    min_chunk = CURRENT_CHUNK_RANGE[0]
    max_chunk = CURRENT_CHUNK_RANGE[1]
    
    chunks_to_load = []
    shift_player_right = False
    
    # Player approaching left boundary - load chunk to the left
    if player_chunk <= min_chunk + 1 and min_chunk > -10:  # Limit to prevent infinite expansion
        chunks_to_load.append(min_chunk - 1)
        CURRENT_CHUNK_RANGE[0] -= 1
        shift_player_right = True  # Need to shift player when adding to left
        print(f"🔄 Loading chunk {min_chunk - 1} (left expansion)")
    elif player_chunk <= min_chunk + 1:
        print(f"⚠️ Cannot expand left - already at limit (min_chunk={min_chunk})")
    
    # Player approaching right boundary - load chunk to the right
    if player_chunk >= max_chunk - 1 and max_chunk < 10:  # Limit to prevent infinite expansion
        chunks_to_load.append(max_chunk + 1)
        CURRENT_CHUNK_RANGE[1] += 1
        print(f"🔄 Loading chunk {max_chunk + 1} (right expansion)")
    elif player_chunk >= max_chunk - 1:
        print(f"⚠️ Cannot expand right - already at limit (max_chunk={max_chunk})")
    
    # Generate and append new chunks if needed
    if chunks_to_load:
        print(f"⏸️ Pausing game to generate {len(chunks_to_load)} chunk(s)...")
        for chunk_id in chunks_to_load:
            generate_new_chunk(chunk_id)
        print(f"✅ World updated: {GRID_WIDTH} blocks wide, {len(BIOME_MAP)} biomes")
        # Force a small delay to ensure all systems sync
        pygame.time.wait(10)
        
        # Return whether player needs to be shifted
        return shift_player_right
    
    return False

def generate_new_chunk(chunk_id):
    """Generate a new chunk and append it to the world."""
    global WORLD_MAP, BIOME_MAP, GRID_WIDTH, MOBS
    
    print(f"  ⛏️ Generating chunk {chunk_id} at columns {chunk_id * CHUNK_SIZE} to {(chunk_id + 1) * CHUNK_SIZE - 1}")
    
    # Determine if we're expanding left or right
    if chunk_id < 0:
        # Expanding left - insert at beginning
        # First, prepend empty columns
        for row in range(GRID_HEIGHT):
            WORLD_MAP[row] = [AIR_ID] * CHUNK_SIZE + WORLD_MAP[row]
        
        # Update GRID_WIDTH immediately
        GRID_WIDTH = len(WORLD_MAP[0])
        
        # Generate terrain using the same logic as initial world generation
        base_level = GRID_HEIGHT // 2
        
        # If expanding left next to existing terrain, match the height
        if GRID_WIDTH > CHUNK_SIZE:
            # Find ground level at column CHUNK_SIZE (first column of old world)
            for row in range(GRID_HEIGHT):
                if WORLD_MAP[row][CHUNK_SIZE] != AIR_ID:
                    base_level = row
                    break
        
        new_biome_data = []
        
        # Create biome pattern for the new chunk
        current_biome = random.choice([OAK_FOREST_BIOME, PLAINS_BIOME, DESERT_BIOME, TAIGA_BIOME, SNOW_BIOME, SWAMP_BIOME])
        biome_length = random.randint(100, 140)
        col_counter = 0
        
        for col_offset in range(CHUNK_SIZE):
            col = col_offset
            
            # Change biome if needed
            if col_counter >= biome_length:
                biome_weights = [1, 1, 1, 1, 1, 1.5, 1, 0.8, 0.5, 1, 0.6]
                all_biomes = [OAK_FOREST_BIOME, DESERT_BIOME, SNOW_BIOME, SWAMP_BIOME, TAIGA_BIOME, PLAINS_BIOME, BIRCH_FOREST_BIOME, JUNGLE_BIOME, BAMBOO_JUNGLE_BIOME, SAVANNAH_BIOME, OCEAN_BIOME]
                current_biome = random.choices(all_biomes, weights=biome_weights)[0]
                if current_biome == OCEAN_BIOME:
                    biome_length = random.randint(500, 1000)
                else:
                    biome_length = random.randint(100, 140)
                col_counter = 0
            
            new_biome_data.append(current_biome)
            col_counter += 1
            
            # Generate height
            wave_height = math.sin((chunk_id * CHUNK_SIZE + col_offset) * 0.05) * 4
            noise = random.uniform(-1, 1) * 0.5
            final_height = base_level + int(wave_height + noise)
            final_height = max(1, min(GRID_HEIGHT - 3, final_height))
            
            # Determine surface block type based on biome
            if current_biome == DESERT_BIOME:
                surface_block = SAND_ID
                subsurface_block = SANDSTONE_ID
            elif current_biome == SNOW_BIOME:
                surface_block = SNOW_ID
                subsurface_block = DIRT_ID
            elif current_biome == SWAMP_BIOME:
                surface_block = MUD_ID
                subsurface_block = DIRT_ID
            elif current_biome == SAVANNAH_BIOME:
                surface_block = SAND_ID
                subsurface_block = DIRT_ID
            elif current_biome == OCEAN_BIOME:
                surface_block = SAND_ID
                subsurface_block = SAND_ID
                # Ocean floor goes deeper underground
                final_height = min(base_level + 20, GRID_HEIGHT - 10)
            else:
                surface_block = GRASS_ID
                subsurface_block = DIRT_ID
            
            # Fill column with terrain
            for row in range(GRID_HEIGHT):
                if row < final_height:
                    WORLD_MAP[row][col] = AIR_ID
                elif row == final_height:
                    WORLD_MAP[row][col] = surface_block
                elif row < final_height + 3:
                    WORLD_MAP[row][col] = subsurface_block
                elif row < GRID_HEIGHT - 1:
                    WORLD_MAP[row][col] = STONE_ID
                else:
                    WORLD_MAP[row][col] = BEDROCK_ID
            
            # Fill ocean biomes with water from surface to deep floor
            if current_biome == OCEAN_BIOME:
                surface_level = base_level  # Normal surface
                for row in range(surface_level, final_height):
                    if WORLD_MAP[row][col] == AIR_ID:
                        WORLD_MAP[row][col] = WATER_ID
        
        # Prepend biome data
        BIOME_MAP = new_biome_data + BIOME_MAP
        
    else:
        # Expanding right - append at end
        start_col = GRID_WIDTH
        
        # Append empty columns
        for row in range(GRID_HEIGHT):
            WORLD_MAP[row].extend([AIR_ID] * CHUNK_SIZE)
        
        # Update GRID_WIDTH immediately
        GRID_WIDTH = len(WORLD_MAP[0])
        
        # Generate terrain
        base_level = GRID_HEIGHT // 2
        
        # Get the last column's height to blend smoothly
        if len(BIOME_MAP) > 0 and start_col > 0:
            # Find the ground level of the last existing column
            last_ground_level = GRID_HEIGHT // 2
            for row in range(GRID_HEIGHT):
                if WORLD_MAP[row][start_col - 1] != AIR_ID:
                    last_ground_level = row
                    break
            base_level = last_ground_level  # Start new chunk at same height
        
        new_biome_data = []
        
        # Continue from last biome or start new pattern
        if len(BIOME_MAP) > 0:
            current_biome = BIOME_MAP[-1]  # Continue from last biome
            biome_length = random.randint(50, 100)  # Remaining length
        else:
            current_biome = PLAINS_BIOME
            biome_length = random.randint(100, 140)
        
        col_counter = 0
        
        for col_offset in range(CHUNK_SIZE):
            col = start_col + col_offset
            
            # Change biome if needed
            if col_counter >= biome_length:
                biome_weights = [1, 1, 1, 1, 1, 1.5, 1, 0.8, 0.5, 1, 0.6]
                all_biomes = [OAK_FOREST_BIOME, DESERT_BIOME, SNOW_BIOME, SWAMP_BIOME, TAIGA_BIOME, PLAINS_BIOME, BIRCH_FOREST_BIOME, JUNGLE_BIOME, BAMBOO_JUNGLE_BIOME, SAVANNAH_BIOME, OCEAN_BIOME]
                current_biome = random.choices(all_biomes, weights=biome_weights)[0]
                if current_biome == OCEAN_BIOME:
                    biome_length = random.randint(500, 1000)
                else:
                    biome_length = random.randint(100, 140)
                col_counter = 0
            
            new_biome_data.append(current_biome)
            col_counter += 1
            
            # Generate height
            wave_height = math.sin(col * 0.05) * 4
            noise = random.uniform(-1, 1) * 0.5
            final_height = base_level + int(wave_height + noise)
            final_height = max(1, min(GRID_HEIGHT - 3, final_height))
            
            # Determine surface block type based on biome
            if current_biome == DESERT_BIOME:
                surface_block = SAND_ID
                subsurface_block = SANDSTONE_ID
            elif current_biome == SNOW_BIOME:
                surface_block = SNOW_ID
                subsurface_block = DIRT_ID
            elif current_biome == SWAMP_BIOME:
                surface_block = MUD_ID
                subsurface_block = DIRT_ID
            elif current_biome == SAVANNAH_BIOME:
                surface_block = SAND_ID
                subsurface_block = DIRT_ID
            elif current_biome == OCEAN_BIOME:
                surface_block = SAND_ID
                subsurface_block = SAND_ID
                # Ocean floor goes deeper underground
                final_height = min(base_level + 20, GRID_HEIGHT - 10)
            else:
                surface_block = GRASS_ID
                subsurface_block = DIRT_ID
            
            # Fill column with terrain
            for row in range(GRID_HEIGHT):
                if row < final_height:
                    WORLD_MAP[row][col] = AIR_ID
                elif row == final_height:
                    WORLD_MAP[row][col] = surface_block
                elif row < final_height + 3:
                    WORLD_MAP[row][col] = subsurface_block
                elif row < GRID_HEIGHT - 1:
                    WORLD_MAP[row][col] = STONE_ID
                else:
                    WORLD_MAP[row][col] = BEDROCK_ID
            
            # Fill ocean biomes with water from surface to deep floor
            if current_biome == OCEAN_BIOME:
                surface_level = base_level  # Normal surface
                for row in range(surface_level, final_height):
                    if WORLD_MAP[row][col] == AIR_ID:
                        WORLD_MAP[row][col] = WATER_ID
        
        # Append biome data
        BIOME_MAP.extend(new_biome_data)
        
        # Add decorations (trees, cacti, etc.) to the new chunk
        for col_offset in range(CHUNK_SIZE):
            col = start_col + col_offset
            biome_type = new_biome_data[col_offset]
            
            # Find ground level
            ground_row = 0
            for row in range(GRID_HEIGHT - 1, -1, -1):
                if WORLD_MAP[row][col] != AIR_ID and WORLD_MAP[row][col] != WATER_ID:
                    ground_row = row
                    break
            
            # Add trees based on biome - skip for now to avoid errors
            # Trees will be added in future chunk updates
            
            # Spawn passive mobs
            if random.random() < 0.01:  # 1% chance per column
                spawn_x = col * BLOCK_SIZE
                
                # For ocean biomes, spawn in water column; for land biomes, spawn on ground
                if biome_type == OCEAN_BIOME:
                    # Find water depth for ocean spawning
                    base_level = GRID_HEIGHT // 2
                    water_surface = base_level
                    # Spawn at random depth in water column
                    if ground_row > water_surface + 10:
                        spawn_depth = random.randint(water_surface + 3, ground_row - 3)
                        spawn_y = spawn_depth * BLOCK_SIZE
                    else:
                        spawn_y = (ground_row - 2) * BLOCK_SIZE
                else:
                    # Land mobs spawn on ground
                    spawn_y = (ground_row - 2) * BLOCK_SIZE
                
                if biome_type == PLAINS_BIOME:
                    if random.random() < 0.5:
                        MOBS.add(Cow(spawn_x, spawn_y))
                    else:
                        MOBS.add(Sheep(spawn_x, spawn_y))
                elif biome_type == DESERT_BIOME:
                    if random.random() < 0.6:
                        MOBS.add(Camel(spawn_x, spawn_y))
                    else:
                        MOBS.add(Rabbit(spawn_x, spawn_y))
                elif biome_type == SNOW_BIOME:
                    MOBS.add(Sheep(spawn_x, spawn_y))  # Changed from PolarBear
                elif biome_type == TAIGA_BIOME:
                    if random.random() < 0.5:
                        MOBS.add(Deer(spawn_x, spawn_y))
                    else:
                        MOBS.add(Bear(spawn_x, spawn_y))
                elif biome_type in [OAK_FOREST_BIOME, BIRCH_FOREST_BIOME]:
                    if random.random() < 0.5:
                        MOBS.add(Pig(spawn_x, spawn_y))
                    else:
                        MOBS.add(Chicken(spawn_x, spawn_y))
                elif biome_type == OCEAN_BIOME:
                    # Ocean mob spawning with different rarities
                    rand = random.random()
                    if rand < 0.45:
                        # 45% - Dolphins (common)
                        MOBS.add(Dolphin(spawn_x, spawn_y))
                    elif rand < 0.70:
                        # 25% - Nautilus (uncommon)
                        MOBS.add(Nautilus(spawn_x, spawn_y))
                    elif rand < 0.88:
                        # 18% - Tropical Fish (common near coral)
                        is_large = random.random() < 0.3
                        MOBS.add(TropicalFish(spawn_x, spawn_y, is_large))
                    elif rand < 0.96:
                        # 8% - Sharks (rare)
                        MOBS.add(Shark(spawn_x, spawn_y))
                    else:
                        # 4% - Whales (very rare)
                        MOBS.add(Whale(spawn_x, spawn_y))
    
    print(f"  ✅ Chunk generated. New world width: {GRID_WIDTH} blocks ({GRID_WIDTH // CHUNK_SIZE} chunks)")
 
# --- DroppedItem Class ---
class DroppedItem(pygame.sprite.Sprite):
    """Represents an item dropped on the ground that can be picked up."""
    def __init__(self, x, y, item_id, amount=1):
        super().__init__()
        self.item_id = item_id
        self.amount = amount
        
        # Create small visual representation (1/2 block size)
        size = BLOCK_SIZE // 2
        self.image = pygame.Surface([size, size])
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        # Draw item with detailed rendering
        if item_id in BLOCK_TYPES:
            color = BLOCK_TYPES[item_id]["color"]
            
            # Main item body with gradient effect
            pygame.draw.rect(self.image, color, (3, 3, size - 6, size - 6))
            
            # Add highlight for 3D effect
            lighter = tuple(min(255, c + 40) for c in color)
            pygame.draw.rect(self.image, lighter, (4, 4, size - 10, 3))
            
            # Add shadow for depth
            darker = tuple(max(0, c - 40) for c in color)
            pygame.draw.rect(self.image, darker, (4, size - 7, size - 8, 3))
            
            # Border
            pygame.draw.rect(self.image, (0, 0, 0), (2, 2, size - 4, size - 4), 2)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.gravity = 0.5
        self.lifetime = FPS * 300  # 5 minutes before despawn
        
    def update(self):
        """Apply gravity and collision."""
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        
        # Apply gravity
        self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, 10)
        
        self.rect.y += self.vel_y
        
        # Check ground collision
        col = self.rect.centerx // BLOCK_SIZE
        row = (self.rect.bottom) // BLOCK_SIZE
        
        # Use actual array length for safety
        world_width = len(WORLD_MAP[0]) if WORLD_MAP else GRID_WIDTH
        
        if 0 <= row < GRID_HEIGHT and 0 <= col < world_width:
            if WORLD_MAP[row][col] != 0 and BLOCK_TYPES.get(WORLD_MAP[row][col], {}).get("solid", False):
                self.rect.bottom = row * BLOCK_SIZE
                self.vel_y = 0

# Helper function to get wool ID from color
def get_wool_id_from_color(color):
    """Returns the wool block ID (65-80) matching the color tuple."""
    wool_colors = {
        (255, 255, 255): 65,  # White
        (157, 157, 151): 66,  # Light Gray
        (71, 79, 82): 67,     # Gray
        (29, 29, 33): 68,     # Black
        (131, 84, 50): 69,    # Brown
        (176, 46, 38): 70,    # Red
        (249, 128, 29): 71,   # Orange
        (254, 216, 61): 72,   # Yellow
        (128, 199, 31): 73,   # Lime
        (94, 124, 22): 74,    # Green
        (22, 156, 156): 75,   # Cyan
        (58, 175, 217): 76,   # Light Blue
        (53, 57, 157): 77,    # Blue
        (137, 50, 184): 78,   # Purple
        (199, 78, 189): 79,   # Magenta
        (243, 139, 170): 80   # Pink
    }
    return wool_colors.get(color, 65)  # Default to white if not found

  # Call the slime's attack method on the player
class Player(pygame.sprite.Sprite):
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
        self.speed = 4
        self.gravity = 0.5
        
        # --- Stats ---
        self.health = 20 
        self.max_health = 20
        self.hunger = 20 
        self.max_hunger = 20
        self.hunger_timer = 0
        self.eating_timer = 0  # Timer for holding F to eat
        self.eating_duration = FPS * 1  # 1 second to eat
        self.drinking_timer = 0  # Timer for holding F to drink potions
        self.drinking_duration = FPS * 2  # 2 seconds to drink potions
        self.damage_flash_timer = 0 
        self.is_crafting = False
        self.inventory_open = False
        self.is_crouching = False
        self.is_sprinting = False 

        # --- Oxygen System ---
        self.oxygen = 10
        self.max_oxygen = 10
        self.oxygen_timer = 0 

        # --- Attack Cooldown ---
        self.attack_cooldown = FPS * 0.5  # 0.5 second cooldown
        self.attack_timer = 0
        
        # --- Healing System ---
        self.healing_timer = 0 

        # --- Fall Damage Tracking ---
        self.fall_velocity_threshold = 10.0  # Requires 5 blocks of falling before damage
        self.max_fall_vel = 0 

        # --- Slowness Effect ---
        self.slowness_timer = 0
        self.slowness_strength = 1.0  # 1.0 = normal speed, 0.5 = 50% speed

        # --- Riding Mechanic ---
        self.mounted_camel = None  # Reference to the camel being ridden
        self.mount_offset_y = -BLOCK_SIZE * 1.2  # Player sits on top of camel (adjusted for bigger camel)
        self.is_riding = False  # Whether player is riding a horse
        self.mount = None  # Reference to the horse being ridden

        # --- Inventory and Hotbar ---
        # Hotbar and inventory are now SEPARATE storage systems
        # Hotbar: 9 slots, each can hold an item ID and count (stored as tuples: (item_id, count))
        self.hotbar_slots = [(1, 64), (2, 64), (3, 64), (5, 32), (6, 32), (7, 16), (11, 5), (10, 20), (0, 0)]
        # Inventory: 27 slots (3 rows x 9 columns), separate from hotbar
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
        
        # --- Trading ---
        self.trading_open = False
        self.trading_villager = None
        
        # --- Tool Durability ---
        # Dictionary to track durability for each inventory slot: {(slot_type, slot_index): durability}
        # slot_type: 'hotbar' or 'inventory'
        self.tool_durability = {}
        
        # --- Mining Progress ---
        self.mining_progress = 0  # Progress towards breaking a block (0-100)
        self.mining_target = None  # (row, col) of block being mined
        
        # --- Charging/Attack State ---
        self.is_charging = False
        self.charge_velocity = 0
        self.charge_direction = 1  # 1 for right, -1 for left
        self.charge_timer = 0  # Time remaining in charge
        self.max_charge_time = FPS * 2  # 2 seconds max charge
        self.charge_hit_mobs = set()  # Track which mobs were hit during this charge
        # -----------------------------------------------------------

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
        """Applies damage with cooldown and starts the flash timer. Adds knockback."""
        if self.damage_flash_timer <= 0:
            self.health -= amount
            self.damage_flash_timer = FPS // 2
            
            # Apply knockback if attacker is specified
            if attacker and hasattr(attacker, 'rect'):
                # Knockback direction away from attacker
                if self.rect.centerx < attacker.rect.centerx:
                    self.vel_x = -6  # 1 block knockback (BLOCK_SIZE * 0.15)
                else:
                    self.vel_x = 6
            
            if self.health <= 0:
                print("Player has died!") 

    def mount_camel(self, camel):
        """Mount a camel for riding."""
        if self.mounted_camel is None and camel is not None:
            self.mounted_camel = camel
            camel.is_mounted = True
            print("Mounted camel!")
    
    def dismount_camel(self):
        """Dismount from the camel."""
        if self.mounted_camel is not None:
            self.mounted_camel.is_mounted = False
            self.mounted_camel = None
            print("Dismounted!")

    def die(self):
        # Simple player death: log and remove the player sprite
        print("Player has died!")
        self.kill()

    def get_image(self):
        """Returns the player image with damage flash effect if needed."""
        original_image = self.image.copy()
        
        # Check if player is swimming (in water)
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        in_water = False
        
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
            if WORLD_MAP[center_row][center_col] in FLUID_BLOCKS:
                in_water = True
        
        # Rotate player to horizontal when swimming
        if in_water and abs(self.vel_x) > 0.5:
            # Rotate 90 degrees to be fully horizontal when swimming
            if self.vel_x > 0:
                original_image = pygame.transform.rotate(original_image, -90)  # Horizontal right
            else:
                original_image = pygame.transform.rotate(original_image, 90)  # Horizontal left
        
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
        
        # Adjust player hitbox when crouching
        if self.is_crouching:
            # Make player shorter (crouch height is 1.5 blocks instead of 2)
            new_height = int(BLOCK_SIZE * 1.5)
            if self.rect.height != new_height:
                old_bottom = self.rect.bottom
                self.rect.height = new_height
                self.rect.bottom = old_bottom  # Keep feet at same position
        else:
            # Return to normal height
            new_height = BLOCK_SIZE * 2
            if self.rect.height != new_height:
                old_bottom = self.rect.bottom
                self.rect.height = new_height
                self.rect.bottom = old_bottom
        
        # --- Riding Logic ---
        if self.mounted_camel is not None:
            # Check if camel still exists
            if not self.mounted_camel.alive():
                self.dismount_camel()
            else:
                # Sync player position to camel
                self.rect.centerx = self.mounted_camel.rect.centerx
                self.rect.bottom = self.mounted_camel.rect.top + self.mount_offset_y
                # Skip normal movement and gravity when riding
                return
            
        if not self.is_crafting:
            # Check if player is in water
            center_col = self.rect.centerx // BLOCK_SIZE
            center_row = self.rect.centery // BLOCK_SIZE
            in_water = False
            on_ladder = False
            
            # 🟢 FIX APPLIED HERE: Check against FLUID_BLOCKS set
            if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < len(WORLD_MAP[0]):
                if WORLD_MAP[center_row][center_col] in FLUID_BLOCKS:
                    in_water = True
                if WORLD_MAP[center_row][center_col] == LADDER_ID or WORLD_MAP[center_row][center_col] == VINES_ID:
                    on_ladder = True
            
            # Apply gravity (reduced in water, disabled on ladder)
            if on_ladder:
                # On ladder - no gravity, can climb
                self.vel_y = 0  # Cancel gravity
            elif in_water:
                # Swimming: horizontal movement with natural sinking
                # Make player horizontal when swimming
                if not hasattr(self, 'is_swimming'):
                    self.is_swimming = False
                self.is_swimming = True
                
                if self.is_crouching:
                    self.vel_y += self.gravity * 0.8  # Sink faster when crouching
                    if self.vel_y > 4:  # Terminal velocity when sinking
                        self.vel_y = 4
                else:
                    # Natural sinking - slow but noticeable
                    self.vel_y += self.gravity * 0.15  # Gradual sink
                    if self.vel_y > 1.5:  # Moderate downward drift
                        self.vel_y = 1.5
            else:
                # Not in water - reset swimming state
                if hasattr(self, 'is_swimming'):
                    self.is_swimming = False
                
                self.vel_y += self.gravity
                if self.vel_y > 10:
                    self.vel_y = 10
                
            # Only track fall velocity when actually falling (positive velocity)
            if self.vel_y > 0.6 and self.vel_y > self.max_fall_vel:
                self.max_fall_vel = self.vel_y
            # Reset fall tracking when moving upward (jumping)
            elif self.vel_y < 0:
                self.max_fall_vel = 0

            self.rect.x += self.vel_x
            self.collide_x()
            
            self.rect.y += self.vel_y
            self.collide_y()
            
            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(len(WORLD_MAP[0]) * BLOCK_SIZE, self.rect.right)

        # --- Hunger Logic ---
        self.hunger_timer += 1
        if self.vel_x != 0 or self.vel_y < 0:
            self.hunger_timer += 0.5
        
        # Sprinting drains hunger much faster
        if self.is_sprinting:
            self.hunger_timer += 2.0  # 2x additional drain when sprinting

        if self.hunger_timer >= FPS * 20: 
            if self.hunger > 0:
                self.hunger -= 1
            self.hunger_timer = 0
        
        # --- Hunger-Based Healing ---
        if self.health < self.max_health:
            self.healing_timer += 1
            
            if self.hunger >= 18:  # 8-10 hunger bars (18-20 points)
                # Half a heart every second
                if self.healing_timer >= FPS * 1:
                    self.health = min(self.max_health, self.health + 1)
                    self.healing_timer = 0
            elif self.hunger >= 8:  # 4-9 hunger bars (8-17 points)
                # Half a heart every 5 seconds
                if self.healing_timer >= FPS * 5:
                    self.health = min(self.max_health, self.health + 1)
                    self.healing_timer = 0
            elif self.hunger >= 2:  # 1-3 hunger bars (2-7 points)
                # Half a heart every 2 minutes
                if self.healing_timer >= FPS * 120:
                    self.health = min(self.max_health, self.health + 1)
                    self.healing_timer = 0
            else:
                self.healing_timer = 0
        else:
            self.healing_timer = 0
        
        # Damage from starvation
        if self.hunger == 0 and self.hunger_timer % (FPS * 5) == 0:
            self.health = max(1, self.health - 1)
        
        # --- Cactus Damage ---
        # Check if player center is inside a cactus block (not while crouching)
        if not self.is_crouching:
            player_col = self.rect.centerx // BLOCK_SIZE
            player_row = self.rect.centery // BLOCK_SIZE
            
            # Only check the block at player's center position
            if 0 <= player_row < GRID_HEIGHT and 0 <= player_col < len(WORLD_MAP[0]):
                if WORLD_MAP[player_row][player_col] == 21:  # Player is inside cactus
                    # Take damage every half second
                    if not hasattr(self, 'cactus_damage_timer'):
                        self.cactus_damage_timer = 0
                    self.cactus_damage_timer += 1
                    if self.cactus_damage_timer >= FPS * 0.5:
                        self.take_damage(1)
                        self.cactus_damage_timer = 0
        
        # --- Oxygen Logic ---
        # Check if player's head is underwater
        head_col = self.rect.centerx // BLOCK_SIZE
        head_row = (self.rect.top + 5) // BLOCK_SIZE
        head_underwater = False
        
        if 0 <= head_row < GRID_HEIGHT and 0 <= head_col < len(WORLD_MAP[0]):
            if WORLD_MAP[head_row][head_col] == 5:  # Water
                head_underwater = True
        
        if head_underwater:
            # Drain oxygen while underwater
            self.oxygen_timer += 1
            if self.oxygen_timer >= FPS * 1.5:  # Lose 1 bubble every 1.5 seconds
                if self.oxygen > 0:
                    self.oxygen -= 1
                self.oxygen_timer = 0
            
            # Take damage when out of oxygen
            if self.oxygen == 0 and self.oxygen_timer % (FPS * 2) == 0:
                self.take_damage(2)
        else:
            # Restore oxygen when not underwater
            if self.oxygen < self.max_oxygen:
                self.oxygen_timer += 1
                if self.oxygen_timer >= FPS * 0.2:  # Restore quickly
                    self.oxygen = min(self.max_oxygen, self.oxygen + 1)
                    self.oxygen_timer = 0
            else:
                self.oxygen_timer = 0

    def jump(self):
        """Makes the player jump if on the ground, or swim up if in water."""
        if self.is_crafting: return
        if self.is_crouching: return  # Can't jump while crouching
        
        # Check if player is in water
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        in_water = False
        
        world_width = len(WORLD_MAP[0]) if WORLD_MAP else GRID_WIDTH
        
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < world_width:
            in_water = WORLD_MAP[center_row][center_col] in FLUID_BLOCKS  # Check all fluid types
        
        if in_water:
            # Swimming up in water - gentler, more natural flow
            self.vel_y = -4  # Swim up velocity to counter sinking
            
            # Check if head is above water (can jump out)
            head_row = (self.rect.top - 5) // BLOCK_SIZE
            if 0 <= head_row < GRID_HEIGHT and 0 <= center_col < world_width:
                block_above = WORLD_MAP[head_row][center_col]
                # If head is out of water (in air), allow powerful jump
                if block_above == 0:
                    self.vel_y = -7  # Jump power to get out of water
        else:
            # Normal jump on ground
            self.rect.y += 2 
            ground_check_coords = [
                (self.rect.left + 1, self.rect.bottom),
                (self.rect.right - 1, self.rect.bottom)
            ]
            
            on_ground = False
            for px, py in ground_check_coords:
                col = math.floor(px / BLOCK_SIZE)
                row = math.floor(py / BLOCK_SIZE)
                
                world_width = len(WORLD_MAP[0]) if WORLD_MAP else GRID_WIDTH
                
                # FIXED: Check if block is solid instead of just non-air
                if 0 <= row < GRID_HEIGHT and 0 <= col < world_width:
                    block_id = WORLD_MAP[row][col]
                    if block_id != 0 and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                        on_ground = True
                        break
                    
            self.rect.y -= 2 
            
            if on_ground:
                # Higher jump when sprinting
                if self.is_sprinting:
                    self.vel_y = -9  # Jump higher while sprinting
                else:
                    self.vel_y = -7  # Normal jump exactly 1 block high

    def collide_x(self):
        """Handles collision with blocks in the X direction."""
        if self.vel_x == 0:
            return

        if self.vel_x > 0: 
            target_col = math.floor((self.rect.right + self.vel_x) / BLOCK_SIZE)
        else:
            target_col = math.floor((self.rect.left + self.vel_x) / BLOCK_SIZE)
            
        top_row = math.floor(self.rect.top / BLOCK_SIZE)
        bottom_row = math.floor((self.rect.bottom - 1) / BLOCK_SIZE)

        for row in range(top_row, bottom_row + 1):
            if 0 <= row < GRID_HEIGHT and 0 <= target_col < len(WORLD_MAP[0]):
                block_id = WORLD_MAP[row][target_col]
                
                # Check if crouching allows passing through certain blocks
                # Oak (6,18), Birch (83,84), Cactus (21), Dark Oak (32), Spruce (34), Jungle Wood (124)
                if self.is_crouching and block_id in [6, 18, 21, 32, 34, 83, 84, 124]:
                    continue  # Pass through when crouching
                
                # FIXED: Check if block is solid instead of just non-air
                if block_id != 0 and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                    if self.vel_x > 0:
                        self.rect.right = target_col * BLOCK_SIZE
                    elif self.vel_x < 0:
                        self.rect.left = (target_col + 1) * BLOCK_SIZE
                    self.vel_x = 0
                    return
    
    def collide_y(self):
        """Handles collision with blocks in the Y direction (gravity and jumping)."""
        if self.vel_y == 0:
            return
        # Determine the target Y position based on movement direction
        is_falling = self.vel_y > 0
        if is_falling: 
            target_y = self.rect.bottom + self.vel_y
        else: 
            target_y = self.rect.top + self.vel_y
        # Check collision points (left and right edges of the player)
        for x_offset in [self.rect.left + 1, self.rect.right - 1]:
            col = math.floor(x_offset / BLOCK_SIZE)
            row = math.floor(target_y / BLOCK_SIZE)
            
            if 0 <= row < GRID_HEIGHT and 0 <= col < len(WORLD_MAP[0]):
                block_id = WORLD_MAP[row][col]
                
                # Check if crouching allows passing through certain blocks
                # Oak (6,18), Birch (83,84), Cactus (21), Dark Oak (32), Spruce (34), Jungle Wood (124)
                if self.is_crouching and block_id in [6, 18, 21, 32, 34, 83, 84, 124]:
                    continue  # Pass through when crouching
                
                # FIXED: Check if block is solid instead of just non-air
                if block_id != 0 and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                    # --- Collision with block found ---
                    
                    if is_falling:
                        # 1. Fall Damage DISABLED - no fall damage
                        # (Fall damage removed per user request)
                            
                        # 2. Resolve collision from above
                        self.max_fall_vel = 0 # Reset fall velocity tracking
                        self.rect.bottom = row * BLOCK_SIZE
                        
                    else: # Hitting a block while jumping/moving up
                        # 1. Resolve collision from below
                        self.max_fall_vel = 0 # Cannot fall while moving up
                        self.rect.top = (row + 1) * BLOCK_SIZE
                        
                    self.vel_y = 0
                    break

    def handle_input(self, keys):
        """Sets the player's horizontal velocity and handles hotbar switching/crafting/inventory toggle."""
        
        # Toggle Inventory Menu (E)
        if keys[pygame.K_e] and not getattr(self, '_e_pressed', False):
            self.inventory_open = not self.inventory_open
            if not self.inventory_open and self.is_crafting:
                reset_crafting_grid(self)
                self.is_crafting = False
            setattr(self, '_e_pressed', True)
        elif not keys[pygame.K_e]:
            setattr(self, '_e_pressed', False)
        
        # Movement is disabled while inventory is open
        if self.inventory_open:
            self.vel_x = 0
            self.is_sprinting = False
            self.is_crouching = False
            return
        
        # Check if on ladder for climbing
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        on_ladder = False
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
            if WORLD_MAP[center_row][center_col] == LADDER_ID or WORLD_MAP[center_row][center_col] == VINES_ID:
                on_ladder = True
        
        # Ladder climbing (W for up, C for down)
        if on_ladder:
            if keys[pygame.K_w]:
                self.vel_y = -4  # Climb up
            elif keys[pygame.K_c]:
                self.vel_y = 4  # Climb down
            else:
                self.vel_y = 0  # Stay in place on ladder
        
        # Crouch toggle (C) - only when not mounted
        if self.mounted_camel is None and not self.is_riding:
            if keys[pygame.K_c] and not on_ladder:
                self.is_crouching = True
                self.is_sprinting = False  # Can't sprint while crouching
            else:
                self.is_crouching = False
        else:
            # Dismount with SHIFT when mounted on camel
            if self.mounted_camel is not None:
                if keys[pygame.K_LSHIFT] and not getattr(self, '_shift_pressed', False):
                    self.dismount_camel()
                    setattr(self, '_shift_pressed', True)
                    return
                elif not keys[pygame.K_LSHIFT]:
                    setattr(self, '_shift_pressed', False)
            # Dismount with SHIFT when riding horse
            elif self.is_riding and hasattr(self, 'mount') and self.mount:
                if keys[pygame.K_LSHIFT] and not getattr(self, '_shift_pressed_horse', False):
                    self.mount.dismount()
                    setattr(self, '_shift_pressed_horse', True)
                    return
                elif not keys[pygame.K_LSHIFT]:
                    setattr(self, '_shift_pressed_horse', False)
        
        # Sprint (R) - only when moving and not crouching and hunger > 5
        if keys[pygame.K_r] and not self.is_crouching and self.mounted_camel is None and self.hunger > 5:
            self.is_sprinting = True
        else:
            self.is_sprinting = False
        
        # Control camel when mounted
        if self.mounted_camel is not None:
            self.mounted_camel.vel_x = 0
            if keys[pygame.K_a]:
                self.mounted_camel.vel_x = -self.mounted_camel.speed
                self.mounted_camel.direction = -1
            if keys[pygame.K_d]:
                self.mounted_camel.vel_x = self.mounted_camel.speed
                self.mounted_camel.direction = 1
            if keys[pygame.K_SPACE]:
                # Make camel jump
                if self.mounted_camel.is_on_ground:
                    self.mounted_camel.vel_y = -10
            return
        
        # Control mounted animals (horse, camel, ostrich) when riding
        if self.is_riding and hasattr(self, 'mount') and self.mount:
            # Determine speed multiplier based on mount type
            from_class = type(self.mount).__name__
            if from_class == 'Horse':
                mount_speed = self.speed * 3  # 3x faster on horse
            elif from_class == 'Camel':
                mount_speed = self.speed * 2.5  # 2.5x faster on camel
            elif from_class == 'Ostrich':
                mount_speed = self.speed * 4  # 4x faster on ostrich (fastest)
            else:
                mount_speed = self.speed * 2  # Default 2x for any other mount
            
            self.vel_x = 0
            if keys[pygame.K_a]:
                self.vel_x = -mount_speed
            if keys[pygame.K_d]:
                self.vel_x = mount_speed
            if keys[pygame.K_SPACE]:
                # Make mount jump
                if self.mount.is_on_ground:
                    self.vel_y = -10
            return
        
        # Calculate speed based on state
        current_speed = self.speed
        if self.is_crouching:
            current_speed = self.speed * 0.3  # Much slower when crouching
        elif self.is_sprinting:
            current_speed = self.speed * 2.0  # Twice as fast when sprinting
        
        # Check if in water and wearing flippers for speed boost
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        in_water = False
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
            if WORLD_MAP[center_row][center_col] in FLUID_BLOCKS:
                in_water = True
        
        # Flippers (ID 59) equipped as boots make you swim faster
        if in_water and self.armor_slots['boots'] == 59:
            current_speed = current_speed * 2.5  # 2.5x speed in water with flippers
        
        # Apply slowness effect
        if self.slowness_timer > 0:
            current_speed = current_speed * self.slowness_strength
            
        self.vel_x = 0
        if keys[pygame.K_a]:
            self.vel_x = -current_speed
        if keys[pygame.K_d]:
            self.vel_x = current_speed
        if keys[pygame.K_SPACE]:
            self.jump()
        
        # Hotbar switching (Keys 1-9)
        for i in range(9):
            if keys[getattr(pygame, f'K_{i+1}')]:
                self.switch_active_slot(i)

class Mob(pygame.sprite.Sprite):
    """Base class for all non-player entities (Mobs)."""
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 0.5
        
        self.health = 10
        self.max_health = 10
        self.speed = 1.5
        
        self.is_on_ground = False
        self.drowning_timer = 0  # Track time submerged underwater
        self.is_aquatic = False  # Aquatic mobs don't drown
        
    def take_damage(self, damage, all_mobs=None):
        self.health -= damage
        if self.health <= 0:
            self.die(all_mobs)

    def die(self, all_mobs=None):
        """Handle mob death: drop items (if any) and remove the mob sprite."""
        # Use the global DROPPED_ITEMS group if it exists
        if 'DROPPED_ITEMS' in globals():
            # Override this method in subclasses for custom drops
            drop_id = getattr(self, 'drop_id', 0)
            
            if drop_id != 0:
                DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, drop_id, 1))
        
        # Remove the mob sprite from all groups
        self.kill()
        
    def update(self, world_map, player=None, all_mobs=None):
        """Applies physics and checks collision."""
        # Apply gravity
        self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, 10)

        # Apply movement
        self.rect.x += self.vel_x
        self.collide_x()
        
        self.rect.y += self.vel_y
        self.collide_y()
        
        # Check for suffocation from gravel/sand blocks above head
        center_x = int(self.rect.centerx // BLOCK_SIZE)
        head_y = int((self.rect.top + 2) // BLOCK_SIZE)  # Check just above head
        
        if 0 <= head_y < len(world_map) and 0 <= center_x < len(world_map[0]):
            block_above = world_map[head_y][center_x]
            # Gravel (26) or Sand (19) causes suffocation damage
            if block_above == 26 or block_above == 19:
                # Take 1 damage every half second (30 frames at 60 FPS)
                if not hasattr(self, 'suffocation_timer'):
                    self.suffocation_timer = 0
                self.suffocation_timer += 1
                if self.suffocation_timer >= 30:
                    self.take_damage(1)
                    self.suffocation_timer = 0
            else:
                if hasattr(self, 'suffocation_timer'):
                    self.suffocation_timer = 0
        
        # Check for drowning (only if not aquatic)
        if not self.is_aquatic:
            center_x = int(self.rect.centerx // BLOCK_SIZE)
            center_y = int(self.rect.centery // BLOCK_SIZE)
            
            # Check if mob's head is underwater
            head_y = int(self.rect.top // BLOCK_SIZE)
            
            if 0 <= head_y < len(world_map) and 0 <= center_x < len(world_map[0]):
                if world_map[head_y][center_x] in FLUID_BLOCKS:
                    self.drowning_timer += 1
                    # 10 second grace period (600 frames), then take damage every second
                    if self.drowning_timer > FPS * 10 and self.drowning_timer % FPS == 0:
                        self.take_damage(1)
                else:
                    self.drowning_timer = 0
            else:
                self.drowning_timer = 0
        
    def collide_x(self):
        """Handles horizontal collision with solid blocks."""
        if self.vel_x == 0:
            return
            
        target_col = math.floor((self.rect.left + self.vel_x) / BLOCK_SIZE) if self.vel_x < 0 else math.floor((self.rect.right + self.vel_x) / BLOCK_SIZE)
        
        top_row = math.floor(self.rect.top / BLOCK_SIZE)
        bottom_row = math.floor((self.rect.bottom - 1) / BLOCK_SIZE)

        for row in range(top_row, bottom_row + 1):
            if 0 <= row < GRID_HEIGHT and 0 <= target_col < len(WORLD_MAP[0]):
                block_id = WORLD_MAP[row][target_col]
                # FIXED: Check if block is solid instead of just non-air
                if block_id != 0 and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                    if self.vel_x > 0:
                        self.rect.right = target_col * BLOCK_SIZE
                    elif self.vel_x < 0:
                        self.rect.left = (target_col + 1) * BLOCK_SIZE
                    self.vel_x = 0
                    return
    
    def collide_y(self):
        """Handles vertical collision with solid blocks (ground detection)."""
        if self.vel_y == 0:
            return

        is_falling = self.vel_y > 0
        
        if is_falling:
            target_y = self.rect.bottom + self.vel_y
        else: 
            target_y = self.rect.top + self.vel_y

        # Check collision points
        for x_offset in [self.rect.left + 1, self.rect.right - 1]:
            col = math.floor(x_offset / BLOCK_SIZE)
            row = math.floor(target_y / BLOCK_SIZE)
            
            if 0 <= row < GRID_HEIGHT and 0 <= col < len(WORLD_MAP[0]):
                block_id = WORLD_MAP[row][col]
                
                # FIXED: Check if block is solid instead of just non-air
                if block_id != 0 and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                    if is_falling:
                        self.rect.bottom = row * BLOCK_SIZE
                        self.is_on_ground = True
                    else:
                        self.rect.top = (row + 1) * BLOCK_SIZE
                    self.vel_y = 0
                    return
                elif is_falling:
                     self.is_on_ground = False
            
        if is_falling:
            self.is_on_ground = False

class Sheep(Mob):
    """A passive mob that wanders randomly and drops wool."""
    # Minecraft sheep colors (16 wool colors)
    SHEEP_COLORS = {
        'white': (255, 255, 255),
        'light_gray': (157, 157, 151),
        'gray': (71, 79, 82),
        'black': (29, 29, 33),
        'brown': (131, 84, 50),
        'red': (176, 46, 38),
        'orange': (249, 128, 29),
        'yellow': (254, 216, 61),
        'lime': (128, 199, 31),
        'green': (94, 124, 22),
        'cyan': (22, 156, 156),
        'light_blue': (58, 175, 217),
        'blue': (53, 57, 157),
        'purple': (137, 50, 184),
        'magenta': (199, 78, 189),
        'pink': (243, 139, 170)
    }
    
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255)) 
        self.health = 8
        self.max_health = 8
        self.speed = 1.5
        self.drop_id = 7 # Wool
        
        # Choose random wool color
        self.wool_color = random.choice(list(self.SHEEP_COLORS.values()))
        
        # AI state
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(1, 4) 
        self.stop_duration = FPS * random.uniform(1, 3) 
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Drawing - Enhanced blocky sheep with body parts
        self.image.fill((0, 0, 0, 0)) 
        self.image.set_colorkey((0, 0, 0))
        
        # Legs (4 brown legs)
        leg_color = (101, 67, 33)
        pygame.draw.rect(self.image, leg_color, (5, BLOCK_SIZE - 10, 6, 10))  # Front left
        pygame.draw.rect(self.image, leg_color, (BLOCK_SIZE - 11, BLOCK_SIZE - 10, 6, 10))  # Front right
        pygame.draw.rect(self.image, leg_color, (15, BLOCK_SIZE - 10, 6, 10))  # Back left
        pygame.draw.rect(self.image, leg_color, (BLOCK_SIZE - 21, BLOCK_SIZE - 10, 6, 10))  # Back right
        
        # Body (fluffy wool in chosen color)
        pygame.draw.rect(self.image, self.wool_color, (3, 8, BLOCK_SIZE - 6, BLOCK_SIZE - 18), 0, 5)
        
        # Wool texture details (slightly darker for depth)
        darker_wool = tuple(max(0, c - 10) for c in self.wool_color)
        pygame.draw.rect(self.image, darker_wool, (8, 12, 8, 8))
        pygame.draw.rect(self.image, darker_wool, (20, 12, 8, 8))
        pygame.draw.rect(self.image, darker_wool, (14, 18, 8, 8))
        
        # Head (wool color with brown face)
        pygame.draw.rect(self.image, self.wool_color, (BLOCK_SIZE - 10, 5, 8, 10))  # Head
        pygame.draw.rect(self.image, (101, 67, 33), (BLOCK_SIZE - 9, 7, 6, 6))  # Face
        
        # Eyes (black dots)
        pygame.draw.rect(self.image, (0, 0, 0), (BLOCK_SIZE - 8, 8, 2, 2))  # Eye 

    def ai_move(self):
        """Simple wandering AI, checking for cliffs."""
        self.move_timer += 1
        
        if self.is_moving:
            self.vel_x = self.direction * self.speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(1, 3)
                self.vel_x = 0
                
            if self.is_on_ground:
                check_x = self.rect.centerx + self.direction * BLOCK_SIZE
                check_y = self.rect.bottom + 1
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                if (0 <= check_row < GRID_HEIGHT and 
                    0 <= check_col < len(WORLD_MAP[0]) and 
                    WORLD_MAP[check_row][check_col] == 0):
                    
                    self.direction *= -1
                    self.move_timer = 0 
                    self.is_moving = False
                    self.vel_x = 0

        else: # Stopped
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(1, 4)
                self.direction = random.choice([-1, 1])
                
    def update(self, WORLD_MAP, player, MOBS):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
        
    def die(self, all_mobs=None):
        """Drops colored wool and mutton when killed."""
        if 'DROPPED_ITEMS' in globals():
            # Drop colored wool matching sheep's color
            wool_id = get_wool_id_from_color(self.wool_color)
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx - 5, self.rect.bottom - 10, wool_id, 1))
            # Drop mutton (ID 50)
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx + 5, self.rect.bottom - 10, 50, 1))
        
        self.kill()

class Cow(Mob):
    """A passive mob that wanders and drops leather."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 2.5, BLOCK_SIZE * 1.5, (139, 69, 19)) # Brown - BIGGER
        self.health = 10
        self.max_health = 10
        self.speed = 1.5
        self.drop_id = 14 # Leather
        
        # AI state (same as Sheep)
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(1, 4) 
        self.stop_duration = FPS * random.uniform(1, 3) 
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Enhanced drawing with body parts (BIGGER)
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 2.5)
        h = int(BLOCK_SIZE * 1.5)
        
        # Legs (4 brown legs)
        leg_color = (80, 50, 30)
        pygame.draw.rect(self.image, leg_color, (12, h - 18, 10, 18))  # Front left
        pygame.draw.rect(self.image, leg_color, (w - 22, h - 18, 10, 18))  # Front right
        pygame.draw.rect(self.image, leg_color, (32, h - 18, 10, 18))  # Back left
        pygame.draw.rect(self.image, leg_color, (w - 42, h - 18, 10, 18))  # Back right
        
        # Body (brown with spots) - wider body
        pygame.draw.rect(self.image, (139, 69, 19), (8, 12, w - 16, h - 32))
        
        # Spots (white/cream patches)
        pygame.draw.rect(self.image, (240, 230, 210), (15, 15, 18, 14))  # Left spot
        pygame.draw.rect(self.image, (240, 230, 210), (w - 38, 16, 20, 16))  # Right spot
        pygame.draw.rect(self.image, (240, 230, 210), (w // 2 - 8, 24, 16, 12))  # Middle spot
        
        # Head (brown)
        pygame.draw.rect(self.image, (139, 69, 19), (w - 20, 6, 18, 16))
        
        # Ears (small brown rectangles)
        pygame.draw.rect(self.image, (120, 60, 18), (w - 22, 6, 5, 6))  # Left ear
        pygame.draw.rect(self.image, (120, 60, 18), (w - 8, 6, 5, 6))  # Right ear
        
        # Snout (lighter brown)
        pygame.draw.rect(self.image, (160, 90, 30), (w - 20, 15, 18, 7))
        
        # Eyes (black dots)
        pygame.draw.rect(self.image, (0, 0, 0), (w - 16, 10, 3, 3))  # Left eye
        pygame.draw.rect(self.image, (0, 0, 0), (w - 9, 10, 3, 3))  # Right eye

    def ai_move(self):
        """Simple wandering AI, checking for cliffs."""
        self.move_timer += 1
        
        if self.is_moving:
            self.vel_x = self.direction * self.speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(1, 3)
                self.vel_x = 0
                
            if self.is_on_ground:
                check_x = self.rect.centerx + self.direction * BLOCK_SIZE
                check_y = self.rect.bottom + 1
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                if (0 <= check_row < GRID_HEIGHT and 
                    0 <= check_col < len(WORLD_MAP[0]) and 
                    WORLD_MAP[check_row][check_col] == 0):
                    
                    self.direction *= -1
                    self.move_timer = 0 
                    self.is_moving = False
                    self.vel_x = 0

        else: # Stopped
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(1, 4)
                self.direction = random.choice([-1, 1])
                
    def update(self, WORLD_MAP, player, MOBS):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
        
    def die(self, all_mobs=None):
        """Drops beef and leather when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 51, random.randint(1, 2)))  # Beef (ID 51)
            if random.random() < 0.5:  # 50% chance for leather
                DROPPED_ITEMS.add(DroppedItem(self.rect.centerx + 10, self.rect.bottom - 10, 14, 1))  # Leather (ID 14)
        self.kill()

class Camel(Mob):
    """A passive desert mob that wanders in sandy areas."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 2, BLOCK_SIZE * 2, (193, 154, 107)) # Tan/sandy color - made bigger
        self.health = 20
        self.max_health = 25
        self.speed = 20  # Slightly faster than cows
        self.drop_id = 14  # Leather
        
        # AI state
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(2, 5) 
        self.stop_duration = FPS * random.uniform(2, 4) 
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Riding system (like horse/ostrich)
        self.rider = None
        self.mount_cooldown = 0
        
        # Drawing - blocky camel design
        self.image.fill((0, 0, 0, 0))  # Transparent background
        self.image.set_colorkey((0, 0, 0))  # Make black transparent
        w = int(BLOCK_SIZE * 2)
        h = int(BLOCK_SIZE * 2)
        
        # Legs (4 blocky legs)
        leg_color = (180, 140, 90)
        leg_width = 10
        leg_height = 25
        pygame.draw.rect(self.image, leg_color, (10, h - leg_height, leg_width, leg_height))  # Front left leg
        pygame.draw.rect(self.image, leg_color, (w - 20, h - leg_height, leg_width, leg_height))  # Front right leg
        pygame.draw.rect(self.image, leg_color, (25, h - leg_height, leg_width, leg_height))  # Back left leg
        pygame.draw.rect(self.image, leg_color, (w - 35, h - leg_height, leg_width, leg_height))  # Back right leg
        
        # Body (main rectangular body)
        body_color = (193, 154, 107)
        pygame.draw.rect(self.image, body_color, (10, h - 50, w - 20, 30))
        
        # Hump (blocky rectangles stacked)
        hump_color = (180, 140, 90)
        pygame.draw.rect(self.image, hump_color, (w // 2 - 12, h - 60, 24, 15))
        pygame.draw.rect(self.image, hump_color, (w // 2 - 8, h - 68, 16, 8))
        
        # Neck (vertical rectangle)
        pygame.draw.rect(self.image, body_color, (w - 25, h - 70, 15, 25))
        
        # Head (small rectangle)
        pygame.draw.rect(self.image, body_color, (w - 25, h - 78, 15, 12))

    def ai_move(self):
        """Simple wandering AI, checking for cliffs."""
        self.move_timer += 1
        
        if self.is_moving:
            self.vel_x = self.direction * self.speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(2, 4)
                self.vel_x = 0
                
            if self.is_on_ground:
                check_x = self.rect.centerx + self.direction * BLOCK_SIZE
                check_y = self.rect.bottom + 1
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                if (0 <= check_row < GRID_HEIGHT and 
                    0 <= check_col < len(WORLD_MAP[0]) and 
                    WORLD_MAP[check_row][check_col] == 0):
                    
                    self.direction *= -1
                    self.move_timer = 0 
                    self.is_moving = False
                    self.vel_x = 0

        else: # Stopped
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(2, 5)
                self.direction = random.choice([-1, 1])
    
    def die(self, all_mobs=None):
        """Drops leather when killed."""
        if self.rider:
            self.dismount()
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 14, 1))  # Leather (ID 14)
        self.kill()
                
    def update(self, WORLD_MAP, player, MOBS):
        if self.mount_cooldown > 0:
            self.mount_cooldown -= 1
        
        if self.rider:
            # Don't run AI when being ridden - player controls movement
            # Sync position with rider
            self.rect.centerx = self.rider.rect.centerx
            self.rect.bottom = self.rider.rect.bottom
            # Don't copy velocity - let player control it
        else:
            # Only run AI when not being ridden
            self.ai_move()
        
        super().update(WORLD_MAP, player, MOBS)

class Chicken(Mob):
    """A small passive mob that drops feathers."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 0.6, BLOCK_SIZE * 0.6, (255, 255, 255))
        self.health = 4
        self.max_health = 4
        self.speed = 1.2
        self.drop_id = 146  # Feather
        
        # AI state
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(1, 3)
        self.stop_duration = FPS * random.uniform(1, 2)
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Drawing - blocky chicken design (SMALLER)
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 0.6)
        h = int(BLOCK_SIZE * 0.6)
        
        # Legs (2 yellow legs)
        leg_color = (255, 200, 50)
        pygame.draw.rect(self.image, leg_color, (w//4, h - 6, 3, 6))  # Left leg
        pygame.draw.rect(self.image, leg_color, (w - w//4 - 3, h - 6, 3, 6))  # Right leg
        
        # Body (white feathery body)
        body_color = (255, 255, 255)
        pygame.draw.rect(self.image, body_color, (w//6, h//3, w - w//3, h//2))
        
        # Wing outlines (light gray)
        wing_color = (220, 220, 220)
        pygame.draw.rect(self.image, wing_color, (w//6, h//2, w//4, h//4))
        pygame.draw.rect(self.image, wing_color, (w - w//3, h//2, w//4, h//4))
        
        # Head (white)
        pygame.draw.rect(self.image, body_color, (w - w//3, h//6, w//3, h//4))
        
        # Beak (orange/yellow)
        beak_color = (255, 160, 50)
        pygame.draw.rect(self.image, beak_color, (w - 3, h//4, 3, 2))
        
        # Eye (black dot)
        pygame.draw.rect(self.image, (0, 0, 0), (w - w//4, h//5, 2, 2))
        
        # Comb (red)
        comb_color = (200, 40, 40)
        pygame.draw.rect(self.image, comb_color, (w - w//3 + 2, h//8, w//4, 3))

    def ai_move(self):
        """Simple wandering AI, checking for cliffs."""
        self.move_timer += 1
        
        if self.is_moving:
            self.vel_x = self.direction * self.speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(1, 2)
                self.vel_x = 0
                
            if self.is_on_ground:
                check_x = self.rect.centerx + self.direction * BLOCK_SIZE
                check_y = self.rect.bottom + 1
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                if (0 <= check_row < GRID_HEIGHT and 
                    0 <= check_col < len(WORLD_MAP[0]) and 
                    WORLD_MAP[check_row][check_col] == 0):
                    
                    self.direction *= -1
                    self.move_timer = 0
                    self.is_moving = False
                    self.vel_x = 0

        else:  # Stopped
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(1, 3)
                self.direction = random.choice([-1, 1])
                
    def update(self, WORLD_MAP, player, MOBS):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
        
    def die(self, all_mobs=None):
        """Drops chicken when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 81, random.randint(1, 2)))  # Chicken (ID 81)
        self.kill()


class Bird(Mob):
    """A flying passive mob that flies around and perches on trees. Color varies by biome."""
    def __init__(self, x, y, variant="blue"):
        super().__init__(x, y, BLOCK_SIZE * 0.5, BLOCK_SIZE * 0.5, (100, 150, 255))
        self.health = 3
        self.max_health = 3
        self.speed = 2.0
        self.fly_speed = 2.5
        self.drop_id = 146  # Feather
        self.variant = variant
        
        # Flamingos and ducks don't fly - they walk/swim
        self.can_fly = (variant not in ["pink", "brown"])
        
        # Flying/perching AI state
        self.is_perched = False
        self.perch_timer = 0
        self.perch_duration = FPS * random.uniform(3, 8)  # Perch for 3-8 seconds
        self.fly_timer = 0
        self.fly_duration = FPS * random.uniform(5, 12)  # Fly for 5-12 seconds
        self.fly_direction_x = random.choice([-1, 1])
        self.fly_direction_y = random.choice([-1, 0, 1])
        
        # Color variants by biome
        color_schemes = {
            "blue": {"body": (100, 150, 255), "wing": (150, 200, 255), "tail": (70, 100, 200)},  # Default
            "lightblue": {"body": (150, 200, 255), "wing": (180, 220, 255), "tail": (100, 150, 220)},  # Oak Forest - Light Blue Bird
            "red": {"body": (220, 50, 50), "wing": (255, 100, 100), "tail": (160, 30, 30)},  # Oak/Plains - Cardinal
            "green": {"body": (50, 180, 50), "wing": (100, 230, 100), "tail": (30, 120, 30)},  # Jungle - Parrot
            "yellow": {"body": (255, 220, 50), "wing": (255, 240, 120), "tail": (200, 170, 30)},  # Birch - Canary
            "orange": {"body": (255, 140, 0), "wing": (255, 180, 80), "tail": (200, 100, 0)},  # Savannah - Weaver
            "purple": {"body": (150, 80, 200), "wing": (180, 120, 230), "tail": (100, 50, 150)},  # Taiga - Purple Finch
            "pink": {"body": (255, 120, 180), "wing": (255, 170, 210), "tail": (200, 80, 140)},  # Flamingo
            "brown": {"body": (120, 90, 60), "wing": (150, 120, 90), "tail": (90, 70, 50)}  # Duck
        }
        
        colors = color_schemes.get(variant, color_schemes["blue"])
        body_color = colors["body"]
        wing_color = colors["wing"]
        tail_color = colors["tail"]
        
        # Drawing - colored bird
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        # Flamingos have special tall design
        if variant == "pink":
            w = int(BLOCK_SIZE * 0.8)
            h = int(BLOCK_SIZE * 1.5)  # Taller for flamingo
            
            # Resize for flamingo
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            
            # Very long thin blocky legs
            leg_color = (50, 50, 50)
            pygame.draw.rect(self.image, leg_color, (w//2 - 5, h - 30, 3, 30))  # Left leg
            pygame.draw.rect(self.image, leg_color, (w//2 + 2, h - 30, 3, 30))  # Right leg
            
            # Small blocky body
            pygame.draw.rect(self.image, body_color, (w//4, h - 38, w//2, 8))
            
            # Long blocky neck
            pygame.draw.rect(self.image, body_color, (w//2 + 6, h - 56, 4, 20))
            
            # Blocky head
            pygame.draw.rect(self.image, body_color, (w//2 + 4, h - 62, 8, 8))
            
            # Blocky curved beak
            pygame.draw.rect(self.image, (255, 200, 0), (w//2 + 12, h - 60, 4, 2))
            pygame.draw.rect(self.image, (255, 200, 0), (w//2 + 12, h - 58, 2, 2))  # Bend down
            
            # Eye (black square)
            pygame.draw.rect(self.image, (0, 0, 0), (w//2 + 8, h - 60, 2, 2))
            
            # Wings folded on body (blocky)
            pygame.draw.rect(self.image, wing_color, (w//4 + 2, h - 36, w//4, 6))
        
        # Ducks have medium design
        elif variant == "brown":
            w = int(BLOCK_SIZE * 0.6)
            h = int(BLOCK_SIZE * 0.6)
            
            # Body (rounded)
            pygame.draw.ellipse(self.image, body_color, (w//6, h//3, w - w//3, h//2))
            
            # Head
            pygame.draw.circle(self.image, (40, 80, 40), (w - w//4, h//4), w//4)  # Green head for mallard
            
            # Orange bill
            pygame.draw.rect(self.image, (255, 160, 0), (w - 4, h//4, 4, 2))
            
            # Eye
            pygame.draw.circle(self.image, (0, 0, 0), (w - w//3, h//5), 1)
            
            # Wings
            pygame.draw.rect(self.image, wing_color, (w//6, h//2, w//3, h//4))
            
            # Tail
            pygame.draw.rect(self.image, tail_color, (w//8, h - h//4, w//6, h//4))
        
        # Regular small flying birds
        else:
            w = int(BLOCK_SIZE * 0.5)
            h = int(BLOCK_SIZE * 0.5)
            
            # Body
            pygame.draw.rect(self.image, body_color, (w//4, h//3, w//2, h//2))
            
            # Head
            pygame.draw.rect(self.image, body_color, (w - w//3, h//6, w//3, w//3))
            
            # Beak (orange for most, black for some)
            beak_color = (255, 140, 0) if variant != "purple" else (50, 50, 50)
            pygame.draw.rect(self.image, beak_color, (w - 2, h//4, 2, 1))
            
            # Eye (black)
            pygame.draw.rect(self.image, (0, 0, 0), (w - w//4, h//5, 1, 1))
            
            # Wings (lighter color, spread)
            pygame.draw.rect(self.image, wing_color, (0, h//2, w//3, h//4))  # Left wing
            pygame.draw.rect(self.image, wing_color, (w - w//3, h//2, w//3, h//4))  # Right wing
            
            # Tail
            pygame.draw.rect(self.image, tail_color, (w//6, h - h//4, w//6, h//4))
    
    def ai_move(self, WORLD_MAP):
        """Flying and perching AI, or walking for flamingos."""
        # Flamingos walk instead of fly
        if not self.can_fly:
            # Simple walking AI like deer/other ground animals
            if not hasattr(self, 'walk_timer'):
                self.walk_timer = 0
                self.walk_duration = FPS * random.uniform(1, 3)
                self.walk_direction = random.choice([-1, 1])
            
            self.walk_timer += 1
            if self.walk_timer >= self.walk_duration:
                self.walk_direction = random.choice([-1, 1, 0])  # 0 = stop
                self.walk_duration = FPS * random.uniform(1, 3)
                self.walk_timer = 0
            
            self.vel_x = self.walk_direction * self.speed
            return
        
        # Normal flying AI for other birds
        if self.is_perched:
            # Stay still while perched
            self.vel_x = 0
            self.vel_y = 0
            self.perch_timer += 1
            
            # Check if still on a valid perch (tree block)
            center_col = self.rect.centerx // BLOCK_SIZE
            center_row = self.rect.centery // BLOCK_SIZE
            on_tree = False
            
            if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < len(WORLD_MAP[0]):
                block_id = WORLD_MAP[center_row][center_col]
                # Tree blocks: oak=19, birch=80, jungle=121, bamboo=133, acacia=147
                if block_id in [19, 80, 121, 133, 147]:
                    on_tree = True
            
            # Take off if perch duration exceeded or perch destroyed
            if self.perch_timer >= self.perch_duration or not on_tree:
                self.is_perched = False
                self.perch_timer = 0
                self.fly_timer = 0
                self.fly_duration = FPS * random.uniform(5, 12)
                self.fly_direction_x = random.choice([-1, 1])
                self.fly_direction_y = random.choice([-1, 0, 1])
        
        else:
            # Flying mode
            self.vel_x = self.fly_direction_x * self.fly_speed
            self.vel_y = self.fly_direction_y * self.fly_speed * 0.5
            
            self.fly_timer += 1
            
            # Random direction changes while flying
            if random.random() < 0.02:
                self.fly_direction_x = random.choice([-1, 1])
                self.fly_direction_y = random.choice([-1, 0, 1])
            
            # Try to perch on nearby trees
            if self.fly_timer > FPS * 2:  # After flying for at least 2 seconds
                center_col = self.rect.centerx // BLOCK_SIZE
                center_row = self.rect.centery // BLOCK_SIZE
                
                # Check surrounding blocks for trees
                for check_row in range(center_row - 2, center_row + 3):
                    for check_col in range(center_col - 2, center_col + 3):
                        if 0 <= check_row < GRID_HEIGHT and 0 <= check_col < len(WORLD_MAP[0]):
                            block_id = WORLD_MAP[check_row][check_col]
                            # Found a tree block (but not water!)
                            if block_id in [19, 80, 121, 133, 147] and block_id != WATER_ID:
                                # Random chance to perch
                                if random.random() < 0.05:
                                    self.is_perched = True
                                    self.perch_timer = 0
                                    self.perch_duration = FPS * random.uniform(3, 8)
                                    # Move to tree block
                                    self.rect.centerx = check_col * BLOCK_SIZE + BLOCK_SIZE // 2
                                    self.rect.centery = check_row * BLOCK_SIZE + BLOCK_SIZE // 2
                                    return
    
    def update(self, WORLD_MAP, player, MOBS):
        self.ai_move(WORLD_MAP)
        
        # Birds are aquatic - can go underwater
        self.is_aquatic = True
        
        # Flamingos have normal gravity, flying birds don't
        if self.can_fly:
            # Birds don't have gravity when flying
            if not self.is_perched:
                # Override gravity for flying
                self.vel_y = self.fly_direction_y * self.fly_speed * 0.5
            
            # Call parent update but skip gravity
            old_vel_y = self.vel_y
            super().update(WORLD_MAP, player, MOBS)
            if not self.is_perched:
                self.vel_y = old_vel_y  # Restore flying velocity
        else:
            # Flamingos walk on ground with normal gravity
            super().update(WORLD_MAP, player, MOBS)
    
    def die(self, all_mobs=None):
        """Drops bird meat and feather when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 154, 1))  # Bird meat
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx + 5, self.rect.bottom - 10, 146, 1))  # Feather
        self.kill()


class Pig(Mob):
    """A small passive mob about the size of a sheep that drops pork."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, (255, 192, 203))
        self.health = 10
        self.max_health = 10
        self.speed = 1.3
        self.drop_id = 82  # Pork
        
        # AI state
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(1, 4)
        self.stop_duration = FPS * random.uniform(1, 3)
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Drawing - blocky pig design
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        # Legs (4 pink legs)
        leg_color = (230, 150, 170)
        pygame.draw.rect(self.image, leg_color, (6, BLOCK_SIZE - 10, 5, 10))  # Front left
        pygame.draw.rect(self.image, leg_color, (BLOCK_SIZE - 11, BLOCK_SIZE - 10, 5, 10))  # Front right
        pygame.draw.rect(self.image, leg_color, (14, BLOCK_SIZE - 10, 5, 10))  # Back left
        pygame.draw.rect(self.image, leg_color, (BLOCK_SIZE - 19, BLOCK_SIZE - 10, 5, 10))  # Back right
        
        # Body (pink rounded rectangle)
        body_color = (255, 192, 203)
        pygame.draw.rect(self.image, body_color, (4, 10, BLOCK_SIZE - 8, BLOCK_SIZE - 20), 0, 5)
        
        # Snout (lighter pink rectangle at front)
        snout_color = (255, 210, 220)
        pygame.draw.rect(self.image, snout_color, (BLOCK_SIZE - 10, 12, 8, 10))
        
        # Nostrils (dark pink dots)
        nostril_color = (200, 120, 150)
        pygame.draw.rect(self.image, nostril_color, (BLOCK_SIZE - 8, 15, 2, 3))
        pygame.draw.rect(self.image, nostril_color, (BLOCK_SIZE - 5, 15, 2, 3))
        
        # Eye (black dot)
        pygame.draw.rect(self.image, (0, 0, 0), (BLOCK_SIZE - 9, 8, 2, 2))
        
        # Ear (triangular-ish)
        pygame.draw.rect(self.image, body_color, (8, 6, 5, 6))

    def ai_move(self):
        """Simple wandering AI, checking for cliffs."""
        self.move_timer += 1
        
        if self.is_moving:
            self.vel_x = self.direction * self.speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(1, 3)
                self.vel_x = 0
                
            if self.is_on_ground:
                check_x = self.rect.centerx + self.direction * BLOCK_SIZE
                check_y = self.rect.bottom + 1
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                if (0 <= check_row < GRID_HEIGHT and 
                    0 <= check_col < len(WORLD_MAP[0]) and 
                    WORLD_MAP[check_row][check_col] == 0):
                    
                    self.direction *= -1
                    self.move_timer = 0
                    self.is_moving = False
                    self.vel_x = 0

        else:  # Stopped
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(1, 4)
                self.direction = random.choice([-1, 1])
                
    def update(self, WORLD_MAP, player, MOBS):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
        
    def die(self, all_mobs=None):
        """Drops pork when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 82, random.randint(1, 3)))  # Pork (ID 82)
        self.kill()


class Cod(Mob):
    """A brown fish that swims in oceans and drops cod."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 2, BLOCK_SIZE * 0.8, (120, 90, 60))  # 2 blocks long brown fish
        self.health = 3
        self.max_health = 3
        self.speed = 2.0
        self.drop_id = 156  # Cod
        self.is_aquatic = True  # Fish don't drown
        
        # Swimming AI
        self.swim_timer = 0
        self.swim_duration = FPS * random.uniform(2, 5)
        self.direction = random.choice([-1, 1])
        
        # Drawing - brown cod fish
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 0.8)
        h = int(BLOCK_SIZE * 0.4)
        
        # Body (long oval shape using rectangles)
        body_color = (120, 90, 60)  # Brown
        pygame.draw.rect(self.image, body_color, (w//4, h//4, w//2, h//2))  # Main body
        pygame.draw.rect(self.image, body_color, (w//8, h//3, w*3//4, h//3))  # Extended body
        
        # Tail (triangle-ish)
        pygame.draw.rect(self.image, body_color, (2, h//3, w//6, h//3))
        
        # Fins
        fin_color = (100, 75, 50)
        pygame.draw.rect(self.image, fin_color, (w//2, h//6, w//6, h//4))  # Top fin
        pygame.draw.rect(self.image, fin_color, (w//2, h*2//3, w//6, h//4))  # Bottom fin
        
        # Eye
        pygame.draw.rect(self.image, (0, 0, 0), (w*3//4, h//3, 2, 2))
    
    def ai_move(self):
        """Simple swimming movement."""
        self.swim_timer += 1
        
        if self.swim_timer >= self.swim_duration:
            self.direction = random.choice([-1, 1])
            self.swim_timer = 0
            self.swim_duration = FPS * random.uniform(2, 5)
        
        self.vel_x = self.direction * self.speed
        self.vel_y = 0  # Fish stay at same depth mostly
    
    def update(self, WORLD_MAP, player, MOBS):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
    
    def die(self, all_mobs=None):
        """Drops cod."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 156, 1))  # Cod
        self.kill()


class Salmon(Mob):
    """A red fish that swims in oceans and drops salmon."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 2, BLOCK_SIZE * 0.8, (220, 80, 60))  # 2 blocks long red fish
        self.health = 3
        self.max_health = 3
        self.speed = 2.5  # Slightly faster than cod
        self.drop_id = 158  # Salmon
        self.is_aquatic = True  # Fish don't drown
        
        # Swimming AI
        self.swim_timer = 0
        self.swim_duration = FPS * random.uniform(2, 5)
        self.direction = random.choice([-1, 1])
        
        # Drawing - red salmon fish
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 0.9)
        h = int(BLOCK_SIZE * 0.5)
        
        # Body (long oval shape using rectangles)
        body_color = (220, 80, 60)  # Red/pink
        pygame.draw.rect(self.image, body_color, (w//4, h//4, w//2, h//2))  # Main body
        pygame.draw.rect(self.image, body_color, (w//8, h//3, w*3//4, h//3))  # Extended body
        
        # Tail (triangle-ish)
        pygame.draw.rect(self.image, body_color, (2, h//3, w//6, h//3))
        
        # Fins
        fin_color = (180, 60, 40)  # Darker red
        pygame.draw.rect(self.image, fin_color, (w//2, h//6, w//6, h//4))  # Top fin
        pygame.draw.rect(self.image, fin_color, (w//2, h*2//3, w//6, h//4))  # Bottom fin
        
        # Eye
        pygame.draw.rect(self.image, (0, 0, 0), (w*3//4, h//3, 2, 2))
    
    def ai_move(self):
        """Simple swimming movement."""
        self.swim_timer += 1
        
        if self.swim_timer >= self.swim_duration:
            self.direction = random.choice([-1, 1])
            self.swim_timer = 0
            self.swim_duration = FPS * random.uniform(2, 5)
        
        self.vel_x = self.direction * self.speed
        self.vel_y = 0  # Fish stay at same depth mostly
    
    def update(self, WORLD_MAP, player, MOBS):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
    
    def die(self, all_mobs=None):
        """Drops salmon."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 158, 1))  # Salmon
        self.kill()


class TropicalFish(Mob):
    """A colorful fish in 16 sheep colors, comes in 2 sizes, drops tropical fish meat."""
    # Reuse sheep colors for tropical fish
    FISH_COLORS = {
        0: (255, 255, 255),   # White
        1: (255, 165, 0),     # Orange  
        2: (200, 0, 200),     # Magenta
        3: (100, 150, 255),   # Light Blue
        4: (255, 255, 0),     # Yellow
        5: (0, 255, 0),       # Lime
        6: (255, 180, 200),   # Pink
        7: (80, 80, 80),      # Gray
        8: (160, 160, 160),   # Light Gray
        9: (0, 150, 150),     # Cyan
        10: (150, 0, 200),    # Purple
        11: (0, 0, 255),      # Blue
        12: (139, 69, 19),    # Brown
        13: (0, 128, 0),      # Green
        14: (255, 0, 0),      # Red
        15: (0, 0, 0),        # Black
    }
    
    def __init__(self, x, y, is_large=False):
        # Small rabbit-sized (0.5 blocks) or 1 block sized
        size = BLOCK_SIZE * 1.0 if is_large else BLOCK_SIZE * 0.5
        color_id = random.randint(0, 15)
        super().__init__(x, y, size, size * 0.5, self.FISH_COLORS[color_id])
        self.health = 2
        self.max_health = 2
        self.speed = 2.2
        self.drop_id = 165  # Tropical Fish Meat
        self.is_aquatic = True
        self.is_large = is_large
        self.color_id = color_id
        
        # Swimming AI
        self.swim_timer = 0
        self.swim_duration = FPS * random.uniform(1, 3)
        self.swim_direction_x = random.choice([-1, 1])
        self.swim_direction_y = random.choice([-1, 1])
    
    def ai_move(self):
        """Tropical fish swim in random directions."""
        self.swim_timer += 1
        if self.swim_timer >= self.swim_duration:
            # Change swim direction
            self.swim_direction_x = random.choice([-1, 1])
            self.swim_direction_y = random.choice([-1, 1])
            self.swim_timer = 0
            self.swim_duration = FPS * random.uniform(1, 3)
        
        # Apply swim movement
        self.vel_x = self.swim_direction_x * self.speed
        # Vertical swimming
        if not self.is_on_ground:
            self.vel_y = self.swim_direction_y * (self.speed * 0.5)
    
    def update(self, world_map, player, all_mobs=None):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
    
    def die(self, all_mobs=None):
        """Drops tropical fish meat."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 165, 1))  # Tropical Fish Meat
        self.kill()


class Dolphin(Mob):
    """A friendly 4-block ocean creature that can lead players to shipwrecks when fed fish."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 4, BLOCK_SIZE * 1.5, (100, 180, 255))  # Light blue
        self.health = 10
        self.max_health = 10
        self.speed = 3.0
        self.is_aquatic = True
        
        # Behavior state
        self.is_fed = False
        self.shipwreck_location = None  # Will be set when fed
        self.leading_timer = 0
        self.leading_duration = FPS * 30  # Lead for 30 seconds
        
        # Swimming AI
        self.swim_timer = 0
        self.swim_duration = FPS * random.uniform(2, 5)
        self.swim_direction_x = random.choice([-1, 1])
        self.swim_direction_y = random.choice([-1, 1])
    
    def feed_fish(self, player):
        """Feed the dolphin fish to make it lead you to a shipwreck."""
        if not self.is_fed:
            # Dolphin accepts cod (156) or salmon (158) or tropical fish meat (165)
            fish_ids = [156, 158, 165]
            for fish_id in fish_ids:
                if player.consume_item(fish_id, 1):
                    self.is_fed = True
                    self.leading_timer = 0
                    # Find nearest shipwreck or create one nearby
                    # For now, just set a random nearby location
                    self.shipwreck_location = (self.rect.centerx + random.randint(-1000, 1000),
                                                 self.rect.centery)
                    print("🐬 Dolphin is leading you to a shipwreck!")
                    return True
            return False
    
    def right_click_interact(self, player):
        """Feed the dolphin when right-clicked."""
        return self.feed_fish(player)
    
    def ai_move(self):
        """Dolphins swim playfully, or lead player to shipwreck if fed."""
        if self.is_fed and self.leading_timer < self.leading_duration:
            self.leading_timer += 1
            # Move toward shipwreck location
            if self.shipwreck_location:
                dx = self.shipwreck_location[0] - self.rect.centerx
                if abs(dx) > 50:
                    self.vel_x = (1 if dx > 0 else -1) * self.speed * 0.5
                else:
                    self.vel_x = 0
                    print("🐬 Shipwreck should be nearby!")
        else:
            # Normal swimming behavior
            self.swim_timer += 1
            if self.swim_timer >= self.swim_duration:
                self.swim_direction_x = random.choice([-1, 1])
                self.swim_direction_y = random.choice([-1, 1])
                self.swim_timer = 0
                self.swim_duration = FPS * random.uniform(2, 5)
            
            self.vel_x = self.swim_direction_x * self.speed
            if not self.is_on_ground:
                self.vel_y = self.swim_direction_y * (self.speed * 0.3)
    
    def update(self, world_map, player, all_mobs=None):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)


class Shark(Mob):
    """An 8-block aggressive ocean predator similar to lions, 40 HP."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 8, BLOCK_SIZE * 2.5, (100, 100, 120))  # Gray
        self.health = 40
        self.max_health = 40
        self.speed = 2.0
        self.attack_damage = 8  # 4 hearts
        self.drop_id = 165  # Tropical Fish Meat
        self.is_aquatic = True
        
        # Aggression state (like lion)
        self.is_aggressive = False
        self.aggro_timer = 0
        self.aggro_duration = FPS * 20
        self.attack_cooldown = FPS * 1.2
        self.attack_timer = 0
        self.charge_speed = 4.0
        self.is_charging = False
        
        # Patrol AI
        self.swim_timer = 0
        self.swim_duration = FPS * random.uniform(3, 6)
        self.swim_direction_x = random.choice([-1, 1])
    
    def ai_move(self):
        """Sharks patrol until they detect player, then charge aggressively."""
        # Decrease timers
        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.aggro_timer < self.aggro_duration:
            self.aggro_timer += 1
        else:
            self.is_aggressive = False
            self.is_charging = False
        
        # Check for player proximity
        if hasattr(self, 'target_player'):
            player = self.target_player
            dx = abs(player.rect.centerx - self.rect.centerx)
            dy = abs(player.rect.centery - self.rect.centery)
            distance = (dx**2 + dy**2) ** 0.5
            
            # Become aggressive if player within 10 blocks
            if distance < BLOCK_SIZE * 10:
                self.is_aggressive = True
                self.aggro_timer = 0
                self.is_charging = True
            
            if self.is_aggressive:
                # Chase player
                if player.rect.centerx > self.rect.centerx:
                    self.vel_x = self.charge_speed if self.is_charging else self.speed
                elif player.rect.centerx < self.rect.centerx:
                    self.vel_x = -self.charge_speed if self.is_charging else -self.speed
                
                # Attack if in range
                if distance < BLOCK_SIZE * 1.5 and self.attack_timer == 0:
                    player.take_damage(self.attack_damage)
                    self.attack_timer = self.attack_cooldown
                    print(f"🦈 Shark attacked for {self.attack_damage} damage!")
            else:
                # Patrol
                self.swim_timer += 1
                if self.swim_timer >= self.swim_duration:
                    self.swim_direction_x = random.choice([-1, 1])
                    self.swim_timer = 0
                    self.swim_duration = FPS * random.uniform(3, 6)
                self.vel_x = self.swim_direction_x * self.speed
        else:
            # No player target, just patrol
            self.swim_timer += 1
            if self.swim_timer >= self.swim_duration:
                self.swim_direction_x = random.choice([-1, 1])
                self.swim_timer = 0
                self.swim_duration = FPS * random.uniform(3, 6)
            self.vel_x = self.swim_direction_x * self.speed
    
    def update(self, world_map, player, all_mobs=None):
        self.target_player = player
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
    
    def take_damage(self, damage, all_mobs=None):
        """Sharks become aggressive when damaged."""
        super().take_damage(damage, all_mobs)
        if self.health > 0:
            self.is_aggressive = True
            self.aggro_timer = 0
            self.is_charging = True
    
    def die(self, all_mobs=None):
        """Drops tropical fish meat."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 165, 1))
        self.kill()


class Whale(Mob):
    """A massive 20-block peaceful ocean creature with 200 HP, elephant-like behavior."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 20, BLOCK_SIZE * 6, (80, 100, 140))  # Blue-gray
        self.health = 200
        self.max_health = 200
        self.speed = 0.5  # Very slow
        self.is_aquatic = True
        
        # Peaceful AI (like elephant)
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(4, 8)
        self.stop_duration = FPS * random.uniform(5, 10)
        self.is_moving = True
        self.direction = random.choice([-1, 1])
    
    def ai_move(self):
        """Whales slowly swim back and forth, peaceful giants."""
        self.move_timer += 1
        
        if self.is_moving:
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.vel_x = 0
            else:
                self.vel_x = self.direction * self.speed
        else:
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.direction = random.choice([-1, 1])
    
    def update(self, world_map, player, all_mobs=None):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)


class Nautilus(Mob):
    """A rideable ocean mount that can be controlled underwater."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 2, BLOCK_SIZE * 2, (200, 150, 255))  # Purple/pink shell
        self.health = 20
        self.max_health = 20
        self.speed = 1.5
        self.drop_id = 164  # Nautilus Shell
        self.is_aquatic = True
        
        # Rideable attributes (like horse/camel)
        self.rider = None
        self.is_tamed = False
        
        # Swimming AI
        self.swim_timer = 0
        self.swim_duration = FPS * random.uniform(2, 4)
        self.swim_direction_x = random.choice([-1, 1])
    
    def right_click_interact(self, player):
        """Mount/dismount the nautilus."""
        if self.rider is None:
            # Mount the nautilus
            self.rider = player
            player.riding = self
            player.vel_y = 0
            print("🐚 Mounted nautilus!")
            return True
        elif self.rider == player:
            # Dismount
            self.rider.riding = None
            self.rider = None
            print("🐚 Dismounted nautilus!")
            return True
        return False
    
    def ai_move(self):
        """If ridden, player controls; otherwise swim randomly."""
        if self.rider is not None:
            # Player controls the nautilus
            keys = pygame.key.get_pressed()
            self.vel_x = 0
            self.vel_y = 0
            
            if keys[pygame.K_a]:
                self.vel_x = -self.speed * 2
            if keys[pygame.K_d]:
                self.vel_x = self.speed * 2
            if keys[pygame.K_w]:
                self.vel_y = -self.speed * 1.5
            if keys[pygame.K_s]:
                self.vel_y = self.speed * 1.5
            
            # Keep rider on nautilus
            self.rider.rect.centerx = self.rect.centerx
            self.rider.rect.bottom = self.rect.centery
        else:
            # Normal swimming
            self.swim_timer += 1
            if self.swim_timer >= self.swim_duration:
                self.swim_direction_x = random.choice([-1, 1])
                self.swim_timer = 0
                self.swim_duration = FPS * random.uniform(2, 4)
            self.vel_x = self.swim_direction_x * self.speed
    
    def update(self, world_map, player, all_mobs=None):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
    
    def die(self, all_mobs=None):
        """Drops nautilus shell and dismounts rider."""
        if self.rider is not None:
            self.rider.riding = None
            self.rider = None
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 164, 1))  # Nautilus Shell
        self.kill()


class Rabbit(Mob):
    """A small, fast-hopping desert mob that drops rabbit meat."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 0.5, BLOCK_SIZE * 0.5, (200, 180, 150))  # Small like chickens
        self.health = 3
        self.max_health = 3
        self.speed = 3.5  # Very fast
        self.drop_id = 145  # Rabbit Meat
        
        # Hopping AI
        self.hop_timer = random.randint(10, 30)
        self.hop_cooldown = 0
        self.direction = random.choice([-1, 1])
        
        # Drawing - small rabbit
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 0.5)
        h = int(BLOCK_SIZE * 0.5)
        
        # Body (tan/brown)
        body_color = (200, 180, 150)
        pygame.draw.rect(self.image, body_color, (w//4, h//3, w//2, h//2))
        
        # Head (round)
        pygame.draw.rect(self.image, body_color, (w - w//3, h//6, w//3, w//3))
        
        # Long ears (iconic!)
        ear_color = (180, 160, 130)
        pygame.draw.rect(self.image, ear_color, (w - w//4, 0, w//8, h//3))  # Left ear
        pygame.draw.rect(self.image, ear_color, (w - w//8, 0, w//8, h//3))  # Right ear
        
        # Eyes (black dots)
        pygame.draw.rect(self.image, (0, 0, 0), (w - w//4, h//5, 2, 2))
        
        # Tiny legs
        leg_color = (180, 160, 130)
        pygame.draw.rect(self.image, leg_color, (w//3, h - 6, 3, 6))
        pygame.draw.rect(self.image, leg_color, (w - w//3 - 3, h - 6, 3, 6))
        
        # Fluffy tail
        pygame.draw.rect(self.image, (255, 255, 255), (2, h//2, 4, 4))
    
    def ai_move(self):
        """Fast hopping movement."""
        self.hop_timer -= 1
        self.hop_cooldown = max(0, self.hop_cooldown - 1)
        
        # Random direction changes
        if self.hop_timer <= 0:
            self.direction = random.choice([-1, 1])
            self.hop_timer = random.randint(20, 50)
        
        # Hop frequently
        if self.is_on_ground and self.hop_cooldown == 0:
            self.vel_y = -7  # High jump
            self.vel_x = self.direction * self.speed
            self.hop_cooldown = random.randint(15, 35)
        elif not self.is_on_ground:
            self.vel_x = self.direction * self.speed
        else:
            self.vel_x = self.direction * (self.speed * 0.3)  # Slow walk between hops
    
    def update(self, WORLD_MAP, player, MOBS):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
    
    def die(self, all_mobs=None):
        """Drops rabbit meat when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 145, 1))  # Rabbit Meat
        self.kill()


class Horse(Mob):
    """A rideable plains mob in black, brown, or white colors."""
    def __init__(self, x, y):
        # Random color variant
        self.color_variant = random.choice(['black', 'brown', 'white'])
        if self.color_variant == 'black':
            color = (40, 40, 40)
        elif self.color_variant == 'brown':
            color = (120, 80, 50)
        else:  # white
            color = (240, 240, 240)
        
        super().__init__(x, y, BLOCK_SIZE * 1.8, BLOCK_SIZE * 1.8, color)
        self.health = 15
        self.max_health = 15
        self.speed = 2.5
        self.drop_id = 14  # Leather
        
        # Riding system (like camel)
        self.rider = None
        self.mount_cooldown = 0
        
        # AI state
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(2, 5)
        self.stop_duration = FPS * random.uniform(1, 3)
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Drawing - horse
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 1.8)
        h = int(BLOCK_SIZE * 1.8)
        
        # Legs (4 long legs)
        leg_color = tuple(max(0, c - 30) for c in color)  # Darker than body
        pygame.draw.rect(self.image, leg_color, (10, h - 28, 7, 28))  # Front left
        pygame.draw.rect(self.image, leg_color, (w - 17, h - 28, 7, 28))  # Front right
        pygame.draw.rect(self.image, leg_color, (22, h - 28, 7, 28))  # Back left
        pygame.draw.rect(self.image, leg_color, (w - 29, h - 28, 7, 28))  # Back right
        
        # Body (large, rectangular)
        pygame.draw.rect(self.image, color, (8, h - 45, w - 16, 20))
        
        # Neck (upright)
        pygame.draw.rect(self.image, color, (w - 22, h - 60, 12, 20))
        
        # Head
        pygame.draw.rect(self.image, color, (w - 24, h - 70, 16, 14))
        
        # Snout/nose
        snout_color = tuple(min(255, c + 20) for c in color)
        pygame.draw.rect(self.image, snout_color, (w - 20, h - 62, 12, 8))
        
        # Ears (pointy)
        pygame.draw.rect(self.image, color, (w - 22, h - 74, 5, 6))
        pygame.draw.rect(self.image, color, (w - 11, h - 74, 5, 6))
        
        # Eyes (dark)
        pygame.draw.rect(self.image, (0, 0, 0), (w - 20, h - 68, 3, 3))
        pygame.draw.rect(self.image, (0, 0, 0), (w - 12, h - 68, 3, 3))
        
        # Mane (darker, flowing)
        mane_color = tuple(max(0, c - 40) for c in color)
        for i in range(5):
            pygame.draw.rect(self.image, mane_color, (w - 20 + i * 2, h - 62 - i * 2, 3, 8))
        
        # Tail (flowing)
        pygame.draw.rect(self.image, mane_color, (4, h - 42, 4, 16))
        pygame.draw.rect(self.image, mane_color, (2, h - 34, 6, 12))
    
    def ai_move(self):
        """Wandering AI when not being ridden."""
        if self.rider:
            return  # Don't move autonomously when being ridden
        
        self.move_timer += 1
        
        if self.is_moving:
            self.vel_x = self.direction * self.speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(1, 3)
                self.vel_x = 0
        else:
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(2, 5)
                self.direction = random.choice([-1, 1])
    
    def mount(self, player):
        """Player mounts the horse."""
        if self.mount_cooldown == 0 and self.rider is None:
            self.rider = player
            player.is_riding = True
            player.mount = self
            self.mount_cooldown = 30
            print(f"🐴 Mounted {self.color_variant} horse!")
            return True
        return False
    
    def dismount(self):
        """Player dismounts the horse."""
        if self.rider:
            self.rider.is_riding = False
            self.rider.mount = None
            self.rider = None
            print("🐴 Dismounted horse!")
    
    def update(self, WORLD_MAP, player, MOBS):
        if self.mount_cooldown > 0:
            self.mount_cooldown -= 1
        
        if self.rider:
            # Sync position with rider
            self.rect.centerx = self.rider.rect.centerx
            self.rect.bottom = self.rider.rect.bottom
            self.vel_x = self.rider.vel_x
            self.vel_y = self.rider.vel_y
        else:
            self.ai_move()
        
        super().update(WORLD_MAP, player, MOBS)
    
    def die(self, all_mobs=None):
        """Drops leather when killed."""
        if self.rider:
            self.dismount()
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 14, random.randint(0, 2)))  # Leather
        self.kill()


class ZombieHorse(Mob):
    """A hostile mob: green horse ridden by a zombie holding a spear. Spawns at night."""
    def __init__(self, x, y):
        # Green horse color
        color = (100, 150, 80)
        
        super().__init__(x, y, BLOCK_SIZE * 1.8, BLOCK_SIZE * 2.5, color)
        self.health = 30
        self.max_health = 30
        self.speed = 3.0  # Faster than normal horse
        self.aggro_range = BLOCK_SIZE * 12
        self.attack_damage = 6  # Spear damage
        self.attack_cooldown = FPS * 2
        self.attack_timer = 0
        self.drop_id = 14  # Leather
        self.direction = random.choice([-1, 1])
        
        # Drawing - green horse with zombie rider
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 1.8)
        h = int(BLOCK_SIZE * 2.5)
        
        # HORSE BODY
        # Legs (4 long legs) - darker green
        leg_color = (70, 120, 60)
        pygame.draw.rect(self.image, leg_color, (10, h - 28, 7, 28))  # Front left
        pygame.draw.rect(self.image, leg_color, (w - 17, h - 28, 7, 28))  # Front right
        pygame.draw.rect(self.image, leg_color, (22, h - 28, 7, 28))  # Back left
        pygame.draw.rect(self.image, leg_color, (w - 29, h - 28, 7, 28))  # Back right
        
        # Body (green, rectangular)
        pygame.draw.rect(self.image, color, (8, h - 45, w - 16, 20))
        
        # Neck (upright)
        pygame.draw.rect(self.image, color, (w - 22, h - 60, 12, 20))
        
        # Head (green, undead horse)
        pygame.draw.rect(self.image, color, (w - 24, h - 70, 16, 14))
        
        # Glowing red eyes (undead)
        pygame.draw.rect(self.image, (255, 0, 0), (w - 20, h - 68, 3, 3))
        pygame.draw.rect(self.image, (255, 0, 0), (w - 12, h - 68, 3, 3))
        
        # ZOMBIE RIDER (on top of horse)
        rider_y = h - 60  # Sitting on horse
        rider_x = w // 2 - 8
        
        # Zombie body (green)
        zombie_color = (70, 120, 70)
        # Legs hanging down sides
        pygame.draw.rect(self.image, zombie_color, (rider_x - 4, rider_y + 10, 5, 12))  # Left leg
        pygame.draw.rect(self.image, zombie_color, (rider_x + 15, rider_y + 10, 5, 12))  # Right leg
        
        # Torso
        pygame.draw.rect(self.image, zombie_color, (rider_x, rider_y, 16, 12))
        
        # Arms (holding spear)
        pygame.draw.rect(self.image, zombie_color, (rider_x - 5, rider_y + 3, 5, 8))  # Left arm
        pygame.draw.rect(self.image, zombie_color, (rider_x + 16, rider_y + 3, 5, 8))  # Right arm
        
        # Head
        pygame.draw.rect(self.image, zombie_color, (rider_x + 3, rider_y - 10, 10, 10))
        
        # Red glowing eyes
        pygame.draw.rect(self.image, (255, 0, 0), (rider_x + 5, rider_y - 7, 2, 2))
        pygame.draw.rect(self.image, (255, 0, 0), (rider_x + 9, rider_y - 7, 2, 2))
        
        # SPEAR (held by zombie)
        spear_color = (139, 69, 19)  # Brown handle
        spear_tip_color = (180, 180, 180)  # Silver tip
        # Spear shaft (diagonal, pointing forward)
        pygame.draw.rect(self.image, spear_color, (rider_x + 18, rider_y - 5, 3, 20))
        # Spear tip (triangle approximation)
        pygame.draw.polygon(self.image, spear_tip_color, [
            (rider_x + 19, rider_y - 10),
            (rider_x + 17, rider_y - 5),
            (rider_x + 21, rider_y - 5)
        ])
    
    def attack(self, player):
        """Zombie horse charges and attacks with spear."""
        if self.attack_timer <= 0:
            player.take_damage(self.attack_damage, attacker=self)
            print(f"⚔️ Zombie Horse speared for {self.attack_damage} damage!")
            self.attack_timer = self.attack_cooldown
    
    def ai_move(self, player, WORLD_MAP):
        """Hostile AI: Chase and attack player."""
        player_dist_x = player.rect.centerx - self.rect.centerx
        player_dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(player_dist_x**2 + player_dist_y**2)
        
        self.vel_x = 0
        
        # Reduce aggro range if player is crouching
        effective_aggro_range = self.aggro_range
        if player.is_crouching:
            effective_aggro_range = self.aggro_range * 0.5
        
        # Chase player
        if distance < effective_aggro_range:
            if abs(player_dist_x) > BLOCK_SIZE * 0.1:
                if player_dist_x > 0:
                    self.vel_x = self.speed
                else:
                    self.vel_x = -self.speed
            else:
                self.vel_x = 0
            
            # Attack if close enough
            if distance < BLOCK_SIZE * 2:
                self.attack(player)
        else:
            # Wander when not chasing
            if random.random() < 0.01:
                self.direction = random.choice([-1, 1])
            self.vel_x = self.direction * (self.speed * 0.3)
        
        # Cliff avoidance
        if self.vel_x != 0:
            direction = 1 if self.vel_x > 0 else -1
            check_col = int((self.rect.centerx + direction * BLOCK_SIZE) // BLOCK_SIZE)
            check_row = int(self.rect.bottom // BLOCK_SIZE)
            
            if 0 <= check_col < len(WORLD_MAP[0]) and check_row + 1 < GRID_HEIGHT:
                if WORLD_MAP[check_row][check_col] == AIR_ID and WORLD_MAP[check_row + 1][check_col] == AIR_ID:
                    self.direction *= -1
                    self.vel_x = self.direction * self.speed * 0.3
    
    def update(self, WORLD_MAP, player, MOBS):
        if self.attack_timer > 0:
            self.attack_timer -= 1
        
        self.ai_move(player, WORLD_MAP)
        super().update(WORLD_MAP, player, MOBS)
    
    def die(self, all_mobs=None):
        """Drops leather and rotten flesh when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 14, random.randint(1, 3)))  # Leather
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx + 10, self.rect.bottom - 10, 13, random.randint(1, 2)))  # Rotten Flesh
        self.kill()

        
class Penguin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Slightly larger, rounder penguin (2023 mob vote style)
        self.image = pygame.Surface([BLOCK_SIZE * 0.8, BLOCK_SIZE]) 
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 0.8)
        h = int(BLOCK_SIZE)
        
        # Body (rounded/blocky black body)
        pygame.draw.rect(self.image, (20, 20, 30), (w // 4, h // 5, w // 2, h * 3 // 5))
        
        # White belly (large, round)
        belly_w = int(w * 0.4)
        belly_h = int(h * 0.5)
        pygame.draw.rect(self.image, (255, 255, 255), (w // 2 - belly_w // 2, h // 3, belly_w, belly_h), border_radius=4)
        
        # Head (integrated with body, blocky)
        pygame.draw.rect(self.image, (20, 20, 30), (w // 3, 2, w // 3, h // 4))
        
        # Large cute eyes (white circles with black pupils)
        eye_size = 5
        pygame.draw.rect(self.image, (255, 255, 255), (w // 3 + 2, h // 8, eye_size, eye_size))
        pygame.draw.rect(self.image, (0, 0, 0), (w // 3 + 3, h // 8 + 1, 3, 3))
        pygame.draw.rect(self.image, (255, 255, 255), (w * 2 // 3 - 6, h // 8, eye_size, eye_size))
        pygame.draw.rect(self.image, (0, 0, 0), (w * 2 // 3 - 5, h // 8 + 1, 3, 3))
        
        # Orange beak (small blocky)
        pygame.draw.rect(self.image, (255, 140, 0), (w // 2 - 3, h // 5, 6, 4))
        
        # Flippers (wings) - angled downward
        pygame.draw.rect(self.image, (30, 30, 40), (w // 4 - 6, h // 3, 6, h // 4))
        pygame.draw.rect(self.image, (30, 30, 40), (w * 3 // 4, h // 3, 6, h // 4))
        
        # Feet (orange, wider)
        pygame.draw.rect(self.image, (255, 140, 0), (w // 3, h - 6, w // 6, 6))
        pygame.draw.rect(self.image, (255, 140, 0), (w // 2, h - 6, w // 6, 6))

        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 1.0  # Waddle speed
        self.gravity = 0.5
        self.health = 8
        self.max_health = 8
        self.is_passive = True
        self.wandering_timer = random.randint(30, 120)
        self.on_ground = False
        
    def take_damage(self, amount, all_mobs=None):
        """Handle taking damage."""
        self.health -= amount
        if self.health <= 0:
            self.die(all_mobs)
    
    def collide_x(self):
        """Handle horizontal collisions with blocks"""
        global WORLD_MAP
        
        left_col = self.rect.left // BLOCK_SIZE
        right_col = self.rect.right // BLOCK_SIZE
        top_row = self.rect.top // BLOCK_SIZE
        bottom_row = self.rect.bottom // BLOCK_SIZE
        
        for row in range(max(0, top_row), min(GRID_HEIGHT, bottom_row + 1)):
            for col in range(max(0, left_col), min(GRID_WIDTH, right_col + 1)):
                block_id = WORLD_MAP[row][col]
                # Only collide with solid blocks that are not water
                if block_id != AIR_ID and block_id != WATER_ID and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                    block_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    if self.rect.colliderect(block_rect):
                        if self.vel_x > 0:
                            self.rect.right = block_rect.left
                        elif self.vel_x < 0:
                            self.rect.left = block_rect.right
                        self.vel_x = 0
                        return
    
    def collide_y(self):
        """Handle vertical collisions with blocks"""
        global WORLD_MAP
        
        left_col = self.rect.left // BLOCK_SIZE
        right_col = self.rect.right // BLOCK_SIZE
        top_row = self.rect.top // BLOCK_SIZE
        bottom_row = self.rect.bottom // BLOCK_SIZE
        
        self.on_ground = False
        
        # Check blocks that the Penguin is currently occupying or about to enter
        for row in range(max(0, top_row), min(GRID_HEIGHT, bottom_row + 1)):
            for col in range(max(0, left_col), min(GRID_WIDTH, right_col + 1)):
                block_id = WORLD_MAP[row][col]
                # Only collide with solid blocks that are not water
                if block_id != AIR_ID and block_id != WATER_ID and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                    block_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    if self.rect.colliderect(block_rect):
                        if self.vel_y > 0: # Falling
                            self.rect.bottom = block_rect.top
                            self.vel_y = 0
                            self.on_ground = True
                        elif self.vel_y < 0: # Jumping/hitting ceiling
                            self.rect.top = block_rect.bottom
                            self.vel_y = 0
                        return
                        
        # Check if in water (for different movement/gravity)
        is_in_water = False
        # Check the block the penguin's center is in or bottom is in
        center_col = (self.rect.centerx) // BLOCK_SIZE
        bottom_center_row = (self.rect.bottom) // BLOCK_SIZE
        if 0 <= bottom_center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
             if WORLD_MAP[bottom_center_row][center_col] == WATER_ID:
                 is_in_water = True
        
        # Special water physics for penguin
        if is_in_water:
            self.gravity = 0.2 # Reduced gravity in water
            if self.vel_y > 0.5: # Limit falling speed in water
                self.vel_y = 0.5
            # Can 'swim' up
            if pygame.key.get_pressed()[pygame.K_SPACE]: # Example, or internal logic for swimming
                self.vel_y = -self.speed / 2 # Swim up slowly
        else:
            self.gravity = 0.5 # Normal gravity out of water


    # CRITICAL FIX: Update the signature to accept all three arguments!
    def update(self, world_map, player, all_mobs):
        
        # NOTE: If your Penguin AI relies on player or all_mobs,
        # you can use them here, but you must pass them to the base class call.
        
        # 1. Run Penguin's custom AI/Movement logic
        # If your movement logic is complex, it might look like this:
        # self.ai_move(world_map, player) 
        
        # 2. Call the base Mob update for physics, gravity, and final movement
        super().update(world_map, player)
        self.wandering_timer -= 1
        if self.wandering_timer <= 0:
            direction = random.choice([-1, 0, 1])
            self.vel_x = direction * self.speed
            self.wandering_timer = random.randint(60, 200)
        
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > 10:
            self.vel_y = 10
        
        self.rect.x += self.vel_x
        self.collide_x()
        
        self.rect.y += self.vel_y
        self.collide_y()

        # Keep within world bounds
        self.rect.x = max(0, min(self.rect.x, GRID_WIDTH * BLOCK_SIZE - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, GRID_HEIGHT * BLOCK_SIZE - self.rect.height))
    
    def die(self, all_mobs=None):
        """Drops flipper when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 59, 1))  # Flipper (ID 59)
        self.kill()

import random # Ensure this is at the top of your file

class Fox(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 0.8, (255, 100, 0)) 
        self.health = 4
        self.max_health = 4
        self.jump_timer = random.randint(30, 120)
        self.jump_strength = 8
        
        # Minecraft fox design - orange body with white belly and black legs
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = BLOCK_SIZE
        h = int(BLOCK_SIZE * 0.8)
        
        # Legs (black like Minecraft)
        leg_color = (40, 35, 30)
        pygame.draw.rect(self.image, leg_color, (6, h - 8, 5, 8))
        pygame.draw.rect(self.image, leg_color, (w - 11, h - 8, 5, 8))
        pygame.draw.rect(self.image, leg_color, (16, h - 8, 5, 8))
        pygame.draw.rect(self.image, leg_color, (w - 21, h - 8, 5, 8))
        
        # Body - orange top
        body_color = (212, 95, 45)  # Minecraft fox orange
        pygame.draw.rect(self.image, body_color, (4, h - 20, w - 8, 8))
        
        # White belly (bottom half of body)
        pygame.draw.rect(self.image, (255, 255, 255), (4, h - 12, w - 8, 6))
        
        # Head - orange
        pygame.draw.rect(self.image, body_color, (w - 14, h - 30, 12, 10))
        
        # Snout (white)
        pygame.draw.rect(self.image, (255, 255, 255), (w - 12, h - 25, 10, 5))
        
        # Ears (pointed, black-tipped)
        pygame.draw.rect(self.image, body_color, (w - 13, h - 34, 4, 6))
        pygame.draw.rect(self.image, body_color, (w - 5, h - 34, 4, 6))
        pygame.draw.rect(self.image, (30, 25, 20), (w - 13, h - 34, 4, 2))  # Black tips
        pygame.draw.rect(self.image, (30, 25, 20), (w - 5, h - 34, 4, 2))
        
        # Eyes (black)
        pygame.draw.rect(self.image, (0, 0, 0), (w - 11, h - 27, 2, 2))
        pygame.draw.rect(self.image, (0, 0, 0), (w - 5, h - 27, 2, 2))
        
        # Tail (bushy orange with white tip like Minecraft)
        pygame.draw.rect(self.image, body_color, (0, h - 20, 7, 14))
        pygame.draw.rect(self.image, (255, 255, 255), (0, h - 10, 7, 4))  # White tip
    
    # CORRECTED: Takes all 3 required arguments
    def update(self, world_map, player, all_mobs):
        # NOTE: self.on_ground/self.is_on_ground must be set by super().update or Mob physics logic
        
        self.jump_timer -= 1
        # Use 'self.on_ground' if that's what your base Mob class uses
        if self.is_on_ground and self.jump_timer <= 0:
            self.vel_y = -self.jump_strength * 0.8
            self.vel_x = random.choice([-1, 1]) * 1.5 
            self.jump_timer = random.randint(90, 240)
            
        # Call base Mob update for physics, movement, and gravity
        super().update(world_map, player)

    def take_damage(self, damage, all_mobs=None):
        self.target = None 
        super().take_damage(damage, all_mobs)

class Wolf(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 1.2, (150, 150, 150)) 
        self.health = 8
        self.max_health = 8
        self.is_tamed = False
        self.is_neutral = True  # Won't attack player unless provoked
        self.provoked = False  # Becomes True when player attacks
        self.target = None
        self.move_speed = 2.5
        self.attack_damage = 2
        self.attack_cooldown = FPS * 2
        self.attack_timer = 0
        self.attack_range = BLOCK_SIZE * 0.75
        self.jump_strength = 10
        
        # Minecraft wolf design - light gray with darker accents
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = BLOCK_SIZE
        h = int(BLOCK_SIZE * 1.2)
        
        # Legs (light gray like Minecraft wolf)
        leg_color = (213, 213, 213)
        pygame.draw.rect(self.image, leg_color, (6, h - 12, 6, 12))  # Front left
        pygame.draw.rect(self.image, leg_color, (w - 12, h - 12, 6, 12))  # Front right
        pygame.draw.rect(self.image, leg_color, (16, h - 12, 6, 12))  # Back left
        pygame.draw.rect(self.image, leg_color, (w - 22, h - 12, 6, 12))  # Back right
        
        # Body (light gray)
        body_color = (213, 213, 213)
        pygame.draw.rect(self.image, body_color, (4, h - 26, w - 8, 16))
        
        # Darker gray back/top accent
        pygame.draw.rect(self.image, (150, 150, 150), (4, h - 26, w - 8, 6))
        
        # Head (light gray)
        pygame.draw.rect(self.image, body_color, (w - 14, h - 38, 12, 12))
        
        # Darker top of head
        pygame.draw.rect(self.image, (150, 150, 150), (w - 14, h - 38, 12, 4))
        
        # Snout (slightly darker)
        pygame.draw.rect(self.image, (180, 180, 180), (w - 12, h - 33, 10, 6))
        
        # Ears (pointed upward)
        pygame.draw.rect(self.image, (150, 150, 150), (w - 13, h - 42, 4, 6))
        pygame.draw.rect(self.image, (150, 150, 150), (w - 5, h - 42, 4, 6))
        
        # Eyes (dark, Minecraft style)
        pygame.draw.rect(self.image, (40, 40, 40), (w - 11, h - 35, 2, 2))
        pygame.draw.rect(self.image, (40, 40, 40), (w - 6, h - 35, 2, 2))
        
        # Tail (upright, darker gray)
        pygame.draw.rect(self.image, (150, 150, 150), (2, h - 30, 5, 12))
        
    def right_click_interact(self, player):
        """Tries to tame the wolf."""
        TAMING_ITEM_ID = 11 # Bones
        
        if not self.is_tamed:
            # Check for taming item in hotbar and inventory
            has_item = False
            for item_id, count in player.hotbar_slots:
                if item_id == TAMING_ITEM_ID and count > 0:
                    has_item = True
                    break
            if not has_item:
                for item_id, count in player.inventory:
                    if item_id == TAMING_ITEM_ID and count > 0:
                        has_item = True
                        break
            
            if has_item:
                # Consume taming item
                player.consume_item(TAMING_ITEM_ID, 1)
                    
                self.is_tamed = True
                self.provoked = False  # Reset provoked state when tamed
                self.color = (100, 100, 100) # Change color to signify taming
                print("🐺 Wolf tamed!")
                return True
        return False
    
    def take_damage(self, damage, all_mobs=None):
        """Take damage and become provoked if not tamed."""
        if not self.is_tamed:
            self.provoked = True  # Now hostile to player
        super().take_damage(damage, all_mobs)
        
    # CRITICAL FIX: The update method must accept all three arguments!
    def update(self, world_map, player, all_mobs):
        # 1. Apply base physics and movement
        # NOTE: Ensure your base Mob.update() also correctly handles these arguments.
        super().update(world_map, player) 
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if self.is_tamed:
            # --- TAMED WOLF AI ---
            
            # 2. Targeting Logic: Find new hostile target if none is set or target is dead
            if self.target is None or not self.target.alive: 
                self.target = self.find_hostile_target(all_mobs)
            
            if self.target:
                # 3. Attack: Chase and attack the hostile target
                self.chase_target(self.target, self.attack_range)
            else:
                # 4. Follow: If no target, follow the player loosely
                self.follow_target(player, follow_distance=BLOCK_SIZE * 8)
        else:
            # --- UNTAMED WOLF BEHAVIOR ---
            # If provoked, attack player
            if self.provoked:
                # Chase and attack the player
                dx = abs(player.rect.centerx - self.rect.centerx)
                dy = abs(player.rect.centery - self.rect.centery)
                distance = (dx**2 + dy**2) ** 0.5
                
                if distance < self.attack_range:
                    self.vel_x = 0
                    if self.attack_cooldown <= 0:
                        player.take_damage(self.attack_damage)
                        self.attack_cooldown = 30
                else:
                    # Chase player
                    if player.rect.centerx < self.rect.centerx:
                        self.vel_x = -self.move_speed
                    else:
                        self.vel_x = self.move_speed
            else:
                # Neutral - passively roam (handled by base Mob logic)
                if random.random() < 0.01:
                    self.vel_x = random.choice([-self.move_speed * 0.5, 0, self.move_speed * 0.5])
                
    
    # --- WOLF AI HELPER METHODS: ---

    def find_hostile_target(self, all_mobs):
        """Finds the nearest hostile mob within a 15-block radius."""
        # Include all hostile mobs that wolves should attack
        HOSTILE_TYPES = (Zombie, Skeleton, Creeper, Slime, Witch) 
        nearest_target = None
        min_dist_sq = (BLOCK_SIZE * 15) ** 2 # Search radius
        
        for mob in all_mobs:
            # Check if mob is alive, not the wolf itself, and is a hostile type
            if mob.alive and mob != self and isinstance(mob, HOSTILE_TYPES):
                dist_sq = (mob.rect.centerx - self.rect.centerx)**2 + \
                          (mob.rect.centery - self.rect.centery)**2
                
                if dist_sq < min_dist_sq:
                    nearest_target = mob
                    min_dist_sq = dist_sq
                    
        return nearest_target

    def chase_target(self, target, attack_range):
        """Chases a hostile target and attacks when within range."""
        
        dx = abs(target.rect.centerx - self.rect.centerx)
        dy = abs(target.rect.centery - self.rect.centery)
        distance = (dx**2 + dy**2) ** 0.5
        
        if distance < attack_range:
            self.vel_x = 0
            if self.attack_cooldown <= 0:
                # Attack: Deal damage to the target
                target.take_damage(self.attack_damage)
                self.attack_cooldown = 30 # Half-second attack speed
        else:
            # Chase logic: Move toward the target
            if target.rect.centerx < self.rect.centerx:
                self.vel_x = -self.move_speed
            else:
                self.vel_x = self.move_speed
            
            # Simple jump logic to cross small gaps 
            if self.on_ground and abs(target.rect.centerx - self.rect.centerx) > BLOCK_SIZE:
                 self.vel_y = -self.jump_strength

    def follow_target(self, target, follow_distance):
        """Moves the tamed wolf toward the player if they are too far away."""
        
        dx = abs(target.rect.centerx - self.rect.centerx)
        dy = abs(target.rect.centery - self.rect.centery)
        distance = (dx**2 + dy**2) ** 0.5
        
        if distance > follow_distance:
            # Move towards the player
            if target.rect.centerx < self.rect.centerx:
                self.vel_x = -self.move_speed * 0.7 
            else:
                self.vel_x = self.move_speed * 0.7
        elif distance < BLOCK_SIZE * 3:
            # Stop if too close
            self.vel_x = 0
        else:
            # Idle movement
            self.vel_x = 0
            
class Frog(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 0.7, BLOCK_SIZE * 0.6, (100, 150, 50)) 
        self.health = 2
        self.max_health = 2
        self.jump_timer = random.randint(60, 120)
        self.jump_strength = 7
        self.is_aquatic = True  # Frogs don't drown (amphibious)
        
        # Blocky frog design
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 0.7)
        h = int(BLOCK_SIZE * 0.6)
        
        # Body (wide, squat)
        body_color = (100, 180, 60)
        pygame.draw.rect(self.image, body_color, (w // 6, h // 3, w * 2 // 3, h * 2 // 3))
        
        # Head (merged with body, wide)
        pygame.draw.rect(self.image, body_color, (w // 8, h // 6, w * 3 // 4, h // 2))
        
        # Large bulging eyes on top
        eye_color = (255, 220, 0)
        pygame.draw.rect(self.image, eye_color, (w // 4, 0, w // 6, h // 3))
        pygame.draw.rect(self.image, eye_color, (w * 7 // 12, 0, w // 6, h // 3))
        pygame.draw.rect(self.image, (0, 0, 0), (w // 4 + 2, h // 12, w // 12, w // 12))
        pygame.draw.rect(self.image, (0, 0, 0), (w * 7 // 12 + 2, h // 12, w // 12, w // 12))
        
        # Mouth line
        pygame.draw.rect(self.image, (80, 140, 40), (w // 4, h // 2, w // 2, 2))
        
        # Legs (wide, flat)
        pygame.draw.rect(self.image, (90, 160, 50), (0, h - 6, w // 4, 6))
        pygame.draw.rect(self.image, (90, 160, 50), (w * 3 // 4, h - 6, w // 4, 6))
        
    def update(self, world_map, player, all_mobs):
        super().update(world_map, player) # Call first to apply physics/gravity
        
        # Frog jump logic
        self.jump_timer -= 1
        if self.is_on_ground and self.jump_timer <= 0:
            self.vel_y = -self.jump_strength 
            self.vel_x = random.choice([-2, 0, 2])
            self.jump_timer = random.randint(30, 90)

class Turtle(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 1.2, BLOCK_SIZE * 0.9, (100, 180, 80))
        self.health = 4
        self.max_health = 4
        self.base_speed = 0.5  # Slow on land
        self.water_speed = 2.0  # Fast in water
        self.direction_change_timer = random.randint(120, 240)
        self.is_aquatic = True  # Turtles don't drown (aquatic)
        
        # Blocky turtle design
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 1.2)
        h = int(BLOCK_SIZE * 0.9)
        
        # Shell (lime green dome)
        shell_color = (100, 180, 80)
        pygame.draw.rect(self.image, shell_color, (w // 6, h // 4, w * 2 // 3, h * 3 // 4))
        
        # Shell pattern (hexagons simplified to squares) - darker green
        pattern_color = (70, 140, 60)
        pygame.draw.rect(self.image, pattern_color, (w // 4, h // 3, w // 6, w // 6))
        pygame.draw.rect(self.image, pattern_color, (w * 7 // 12, h // 3, w // 6, w // 6))
        pygame.draw.rect(self.image, pattern_color, (w * 5 // 12, h // 2, w // 6, w // 6))
        
        # Head (small, lime greenish)
        head_color = (120, 200, 100)
        pygame.draw.rect(self.image, head_color, (0, h // 3, w // 5, h // 4))
        
        # Eyes on head
        pygame.draw.rect(self.image, (0, 0, 0), (w // 20, h // 3 + 2, 3, 3))
        
        # Flippers (flat rectangles on sides) - lime green
        flipper_color = (110, 170, 90)
        pygame.draw.rect(self.image, flipper_color, (0, h * 2 // 3, w // 4, h // 6))  # Left front
        pygame.draw.rect(self.image, flipper_color, (w * 3 // 4, h * 2 // 3, w // 4, h // 6))  # Right front
        
    def update(self, world_map, player, all_mobs):
        super().update(world_map, player)  # Apply physics/gravity
        
        # Check if in water
        center_x = int(self.rect.centerx // BLOCK_SIZE)
        center_y = int(self.rect.centery // BLOCK_SIZE)
        in_water = False
        
        if 0 <= center_y < len(world_map) and 0 <= center_x < len(world_map[0]):
            if world_map[center_y][center_x] in FLUID_BLOCKS:
                in_water = True
        
        # Random wandering behavior
        self.direction_change_timer -= 1
        if self.direction_change_timer <= 0:
            self.vel_x = random.choice([-1, 0, 1]) * (self.water_speed if in_water else self.base_speed)
            self.direction_change_timer = random.randint(120, 240)

class Monkey(Mob):
    """A passive mob that spawns on vines in jungle biomes, holds bananas."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 0.8, BLOCK_SIZE * 1.2, (139, 69, 19))
        self.health = 8
        self.max_health = 8
        self.speed = 2.0
        self.climb_speed = 3.0
        self.jump_timer = random.randint(30, 90)
        self.direction = random.choice([-1, 1])
        
        # Blocky monkey design
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 0.8)
        h = int(BLOCK_SIZE * 1.2)
        
        # Brown fur color
        fur_color = (139, 69, 19)
        light_fur = (160, 100, 50)
        
        # Body
        pygame.draw.rect(self.image, fur_color, (w // 4, h // 3, w // 2, h // 3))
        
        # Head
        pygame.draw.rect(self.image, fur_color, (w // 4, h // 6, w // 2, h // 4))
        
        # Face (lighter)
        pygame.draw.rect(self.image, light_fur, (w // 3, h // 5, w // 3, h // 6))
        
        # Eyes
        pygame.draw.rect(self.image, (0, 0, 0), (w // 3 + 2, h // 5 + 2, 3, 3))
        pygame.draw.rect(self.image, (0, 0, 0), (w * 2 // 3 - 5, h // 5 + 2, 3, 3))
        
        # Arms (thin rectangles)
        pygame.draw.rect(self.image, fur_color, (0, h // 3 + 5, w // 5, h // 6))
        pygame.draw.rect(self.image, fur_color, (w * 4 // 5, h // 3 + 5, w // 5, h // 6))
        
        # Legs
        pygame.draw.rect(self.image, fur_color, (w // 4, h * 2 // 3, w // 6, h // 4))
        pygame.draw.rect(self.image, fur_color, (w * 7 // 12, h * 2 // 3, w // 6, h // 4))
        
        # Tail (curved approximation with rectangles)
        pygame.draw.rect(self.image, fur_color, (w * 2 // 3, h // 4, 3, h // 3))
        
        # Banana in hand (yellow)
        pygame.draw.rect(self.image, (255, 255, 0), (w // 6, h // 3 + 8, 4, 10))
        
    def update(self, world_map, player, all_mobs):
        super().update(world_map, player)
        
        # Check if on vines, ladder, or tree blocks (wood)
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        on_vine = False
        on_tree = False
        
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < len(world_map[0]):
            block_id = world_map[center_row][center_col]
            if block_id == VINES_ID:
                on_vine = True
            # Check if on wood blocks (tree trunks: oak=19, birch=80, jungle=121, bamboo=133, acacia=147)
            elif block_id in [19, 80, 121, 133, 147]:
                on_tree = True
        
        # Monkeys stick to trees and vines - don't fall off
        if on_vine or on_tree:
            # Random climbing/moving behavior on trees
            self.jump_timer -= 1
            if self.jump_timer <= 0:
                self.vel_y = random.choice([-self.climb_speed, 0, self.climb_speed, 0])  # More chance to stay still
                self.vel_x = random.choice([-self.speed * 0.5, 0, self.speed * 0.5, 0])
                self.jump_timer = random.randint(30, 90)
            
            # Cancel gravity when on trees/vines
            if on_tree:
                self.vel_y = min(self.vel_y, 2)  # Allow downward movement but not falling
        else:
            # Random wandering on ground
            self.jump_timer -= 1
            if self.jump_timer <= 0:
                self.vel_x = random.choice([-self.speed, 0, self.speed])
                if self.is_on_ground:
                    self.vel_y = -5  # Small jump
                self.jump_timer = random.randint(60, 120)
    
    def die(self, all_mobs=None):
        """Drops banana when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 138, 1))  # Banana
        self.kill()

class Slime(Mob):
    def __init__(self, x, y, size=3): # Size: 1 (Small), 2 (Medium), 3 (Large)
        self.size = size
        width = BLOCK_SIZE * size * 0.5
        height = BLOCK_SIZE * size * 0.5
        super().__init__(x, y, width, height, (0, 255, 0)) 
        self.health = 1 * size 
        self.max_health = 1 * size
        self.jump_timer = random.randint(60, 180)
        self.jump_strength = 6 + (size * 0.5)
        self.attack_damage = 2
        self.attack_cooldown = FPS * 2
        self.attack_timer = 0

    # CRITICAL FIX: Ensure all three arguments are present here!
    def update(self, world_map, player, all_mobs):
        # Call base Mob update for physics and movement first
        super().update(world_map, player) 
        
        # Only move/attack during night and evening
        global TIME_PHASE
        is_hostile_time = (TIME_PHASE == NIGHT_PHASE or TIME_PHASE == EVENING_PHASE)
        
        # Slime hop/movement logic - only when hostile
        self.jump_timer -= 1
        
        # NOTE: Using self.on_ground property from base Mob class
        if is_hostile_time and self.is_on_ground and self.jump_timer <= 0: 
            # Simple hop towards player
            if player.rect.centerx < self.rect.centerx:
                self.vel_x = -1.5 * self.size * 0.5
            else:
                self.vel_x = 1.5 * self.size * 0.5
            
            self.vel_y = -self.jump_strength
            self.jump_timer = random.randint(60, 180) 

    def die(self, all_mobs=None):
        """Slime splits into smaller slimes upon defeat, or drops slimeballs when size 1."""
        if self.size > 1 and all_mobs is not None:
            for _ in range(2):
                new_x = self.rect.x + random.randint(-10, 10)
                new_y = self.rect.y 
                # Spawns two smaller slimes
                all_mobs.add(Slime(new_x, new_y, self.size - 1))
        else:
            # Size 1 slimes drop slimeballs
            if 'DROPPED_ITEMS' in globals():
                drop_count = random.randint(0, 2)  # 0-2 slimeballs
                if drop_count > 0:
                    drop_x = self.rect.centerx
                    drop_y = self.rect.centery
                    DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 130, drop_count))  # 130 = slimeball
        
        # Call the base class die method to remove itself from groups
        super().die(all_mobs)
    def attack(self, player):
        """Slime attacks the player on contact (only at night/evening)."""
        global TIME_PHASE
        is_hostile_time = (TIME_PHASE == NIGHT_PHASE or TIME_PHASE == EVENING_PHASE)
        
        if not is_hostile_time:
            return  # Passive during day/dawn
        
        if self.size == 3:
            if self.attack_timer <= 0:
                player.take_damage(self.attack_damage + 1, attacker=self)
                self.attack_timer = self.attack_cooldown
        elif self.size == 2:
            if self.attack_timer <= 0:
                player.take_damage(self.attack_damage - 1, attacker=self)
                self.attack_timer = self.attack_cooldown
        elif self.size == 1:
            if self.attack_timer <= 0:
                player.take_damage(self.attack_damage - 3, attacker=self)
                self.attack_timer = self.attack_cooldown

class Zombie(Mob):
    """A hostile mob that chases and damages the player."""
    def __init__(self, x, y, biome_type=0):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 2, (0, 100, 0)) # Green
        self.health = 20
        self.max_health = 20
        self.speed = 2.0
        self.aggro_range = BLOCK_SIZE * 8
        self.attack_damage = 2
        self.attack_cooldown = FPS * 2
        self.attack_timer = 0
        self.drop_id = 13 # Rotten Flesh
        self.direction = random.choice([-1, 1])  # For wandering behavior
        self.is_aquatic = True  # Undead don't drown
        self.underwater_timer = 0  # Timer for zombie -> drowned conversion
        self.conversion_time = FPS * 20  # 20 seconds at 60 FPS = 1200 frames
        self.on_fire = False  # Track fire status for water avoidance
        
        # Enhanced drawing with body parts
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        # Determine if this is a husk (desert zombie)
        is_husk = (biome_type == 1)  # 1 = DESERT_BIOME
        self.is_husk = is_husk  # Store as attribute for sunlight immunity
        self.name = "Husk" if is_husk else "Zombie"  # Display name
        
        if is_husk:
            # HUSK - darker brown skin, yellow hair, black eyes, YELLOW clothes
            leg_color = (101, 67, 33)  # Darker brown skin
            shirt_color = (255, 215, 0)  # Yellow clothes
            arm_color = (101, 67, 33)  # Darker brown skin
            head_color = (101, 67, 33)  # Darker brown skin
            eye_color = (0, 0, 0)  # Black eyes
        else:
            # NORMAL ZOMBIE - green
            leg_color = (50, 100, 50)
            shirt_color = (40, 80, 70)
            arm_color = (60, 110, 60)
            head_color = (70, 120, 70)
            eye_color = (255, 0, 0)  # Red glowing eyes
        
        # Legs
        pygame.draw.rect(self.image, leg_color, (8, BLOCK_SIZE * 1.2, 10, BLOCK_SIZE * 0.8))  # Left leg
        pygame.draw.rect(self.image, leg_color, (22, BLOCK_SIZE * 1.2, 10, BLOCK_SIZE * 0.8))  # Right leg
        
        # Body (shirt)
        pygame.draw.rect(self.image, shirt_color, (5, BLOCK_SIZE * 0.5, 30, BLOCK_SIZE * 0.7))
        
        # Arms
        pygame.draw.rect(self.image, arm_color, (0, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.5))  # Left arm
        pygame.draw.rect(self.image, arm_color, (34, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.5))  # Right arm
        
        # Head
        pygame.draw.rect(self.image, head_color, (10, 2, 20, 20))
        
        # Hair (yellow for husk, dark for normal)
        hair_color = (218, 165, 32) if is_husk else (30, 30, 30)
        pygame.draw.rect(self.image, hair_color, (10, 2, 20, 4))
        
        # Eyes
        pygame.draw.rect(self.image, eye_color, (14, 10, 4, 4))  # Left eye
        pygame.draw.rect(self.image, eye_color, (22, 10, 4, 4))  # Right eye
        
        # Mouth (dark line)
        pygame.draw.rect(self.image, (30, 30, 30), (14, 17, 12, 2))        
    def attack(self, player):
        """Zombie attacks the player on contact."""
        if self.attack_timer <= 0:
            player.take_damage(self.attack_damage, attacker=self)
            self.attack_timer = self.attack_cooldown
        
    def die(self, all_mobs=None):
        """Drops rotten flesh when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 13, random.randint(0, 2)))  # Rotten Flesh (ID 13)
        self.kill()
    
    def ai_move(self, player, WORLD_MAP):
        """Hostile AI: Chase player if in range (ONLY AT NIGHT), otherwise wander. Avoid water unless on fire."""
        
        # Only aggressive during night and evening
        global TIME_PHASE
        is_hostile_time = (TIME_PHASE == NIGHT_PHASE or TIME_PHASE == EVENING_PHASE)
        # Husks are always hostile (immune to sunlight), regular zombies only at night
        is_aggressive = is_hostile_time or (hasattr(self, 'is_husk') and self.is_husk)
        
        player_dist_x = player.rect.centerx - self.rect.centerx
        player_dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(player_dist_x**2 + player_dist_y**2)
        
        self.vel_x = 0
        
        # Reduce aggro range if player is crouching
        effective_aggro_range = self.aggro_range
        if player.is_crouching:
            effective_aggro_range = self.aggro_range * 0.5  # Half detection range when crouching
        
        # Only chase if it's hostile time (night/evening) OR if this is a husk (always hostile)
        if is_aggressive and distance < effective_aggro_range:
            # 1. Aggro Mode: Chase player
            if abs(player_dist_x) > BLOCK_SIZE * 0.1:
                if player_dist_x > 0:
                    self.vel_x = self.speed
                else:
                    self.vel_x = -self.speed
            else:
                self.vel_x = 0
        
        else:
            # 2. Wandering Mode (during day or far from player)
            self.attack_timer += 1
            if self.attack_timer % (FPS * 3) == 0: 
                self.direction = random.choice([-1, 1])
                self.vel_x = self.direction * (self.speed * 0.5)
        
        # Water avoidance (unless on fire)
        if self.vel_x != 0 and not self.on_fire:
            direction = 1 if self.vel_x > 0 else -1
            check_x = self.rect.centerx + direction * BLOCK_SIZE
            check_y = self.rect.centery
            
            check_col = check_x // BLOCK_SIZE
            check_row = check_y // BLOCK_SIZE
            
            if (0 <= check_row < GRID_HEIGHT and 0 <= check_col < len(WORLD_MAP[0])):
                if WORLD_MAP[check_row][check_col] in FLUID_BLOCKS:
                    self.vel_x = 0  # Stop before entering water
                    if not is_hostile_time:
                        self.direction *= -1  # Turn around when wandering
        
        # Cliff/Wall avoidance logic (same as Spider)
        if self.vel_x != 0 and (not is_hostile_time or distance >= effective_aggro_range) and self.is_on_ground:
            direction = 1 if self.vel_x > 0 else -1
            check_x = self.rect.centerx + direction * BLOCK_SIZE
            check_y = self.rect.bottom + 1
            
            check_col = check_x // BLOCK_SIZE
            check_row = check_y // BLOCK_SIZE
            
            if (0 <= check_row < GRID_HEIGHT and 
                0 <= check_col < len(WORLD_MAP[0]) and 
                WORLD_MAP[check_row][check_col] == 0):
                self.vel_x = 0 

    def update(self, WORLD_MAP, player, MOBS): # <-- CORRECTED SIGNATURE
        if self.attack_timer > 0:
            self.attack_timer -= 1
        
        # Check if zombie is underwater (for drowned conversion)
        center_x = int(self.rect.centerx // BLOCK_SIZE)
        head_y = int((self.rect.top + 5) // BLOCK_SIZE)  # Check head position
        is_underwater = False
        if 0 <= head_y < GRID_HEIGHT and 0 <= center_x < GRID_WIDTH:
            is_underwater = WORLD_MAP[head_y][center_x] in FLUID_BLOCKS
        
        # Convert to Drowned after 20 seconds underwater
        if is_underwater:
            self.underwater_timer += 1
            if self.underwater_timer >= self.conversion_time:
                # Transform into Drowned (friendly conversion)
                drowned = Drowned(self.rect.x, self.rect.y)
                drowned.converted_from_zombie = True  # Mark as friendly
                MOBS.add(drowned)
                self.kill()  # Remove zombie
                return  # Don't continue updating
        else:
            # Reset timer when not underwater
            self.underwater_timer = 0
            
        self.ai_move(player, WORLD_MAP) # <-- ERROR HERE: ai_move only takes 'player' now
        
        # FIX: The call to ai_move must also be updated to:
        # self.ai_move(player, WORLD_MAP) 
        
        super().update(WORLD_MAP, player, MOBS)

class Drowned(Mob):
    """An underwater zombie variant that spawns in water, with cyan skin and blue eyes. Can spawn with trident."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 2, (0, 140, 140)) # Cyan
        self.health = 20
        self.max_health = 20
        self.speed = 1.5  # Slower on land
        self.swim_speed = 2.5  # Faster in water
        self.aggro_range = BLOCK_SIZE * 8
        self.attack_damage = 3
        self.melee_damage = 9  # Trident jab damage
        self.ranged_damage = 12  # Trident throw damage (increased)
        self.attack_cooldown = FPS * 3  # 3 second cooldown
        self.attack_timer = 0
        self.attack_range = BLOCK_SIZE * 6  # Range for throwing trident
        self.drop_id = 13  # Rotten Flesh
        self.is_aquatic = True  # Doesn't drown
        self.direction = random.choice([-1, 1])
        self.converted_from_zombie = False  # Track if this drowned was converted (friendly)
        
        # 10% chance to hold a trident
        self.has_trident = random.random() < 0.1
        
        # Enhanced drawing with drowned body
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        # Cyan/aqua colored zombie
        leg_color = (0, 120, 120)
        shirt_color = (0, 100, 100)
        arm_color = (0, 130, 130)
        head_color = (0, 140, 140)
        
        # Legs
        pygame.draw.rect(self.image, leg_color, (8, BLOCK_SIZE * 1.2, 10, BLOCK_SIZE * 0.8))
        pygame.draw.rect(self.image, leg_color, (22, BLOCK_SIZE * 1.2, 10, BLOCK_SIZE * 0.8))
        
        # Body
        pygame.draw.rect(self.image, shirt_color, (5, BLOCK_SIZE * 0.5, 30, BLOCK_SIZE * 0.7))
        
        # Arms
        pygame.draw.rect(self.image, arm_color, (0, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.5))
        pygame.draw.rect(self.image, arm_color, (34, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.5))
        
        # Head
        pygame.draw.rect(self.image, head_color, (10, 2, 20, 20))
        
        # Blue glowing eyes
        pygame.draw.rect(self.image, (50, 150, 255), (14, 10, 4, 4))
        pygame.draw.rect(self.image, (50, 150, 255), (22, 10, 4, 4))
        0
        # Mouth
        pygame.draw.rect(self.image, (0, 80, 80), (14, 17, 12, 2))
        
        # Draw trident if holding one
        if self.has_trident:
            # Trident in right hand (cyan color)
            pygame.draw.rect(self.image, (0, 180, 200), (35, BLOCK_SIZE * 0.8, 3, BLOCK_SIZE * 0.4))
            # Trident prongs
            pygame.draw.polygon(self.image, (0, 180, 200), [
                (34, BLOCK_SIZE * 0.8),
                (36, BLOCK_SIZE * 0.75),
                (38, BLOCK_SIZE * 0.8)
            ])
    
    def attack(self, player):
        """Drowned attacks with trident throw (ranged) or jab (melee). Only hostile at night."""
        global TIME_PHASE, TRIDENTS
        
        # Converted drowned are always friendly - don't attack
        if self.converted_from_zombie:
            return
        
        # Normal drowned only attack at night
        is_hostile_time = (TIME_PHASE == NIGHT_PHASE or TIME_PHASE == EVENING_PHASE)
        if not is_hostile_time:
            return  # Passive during day/dawn
        
        if self.attack_timer <= 0:
            if self.has_trident:
                # Calculate distance to player
                player_dist_x = player.rect.centerx - self.rect.centerx
                player_dist_y = player.rect.centery - self.rect.centery
                distance = math.sqrt(player_dist_x**2 + player_dist_y**2)
                
                # Throw trident if at range, jab if close
                if distance > BLOCK_SIZE * 3 and distance < self.attack_range:  # Ranged attack
                    TRIDENTS.add(Trident(
                        self.rect.centerx,
                        self.rect.centery,
                        player.rect.centerx,
                        player.rect.centery,
                        self.ranged_damage
                    ))
                    print(f"🔱 Drowned threw trident!")
                else:  # Melee jab
                    player.take_damage(self.melee_damage, attacker=self)
                    print(f"🔱 Drowned jabbed with trident for {self.melee_damage} damage!")
            else:
                # Normal melee without trident
                player.take_damage(self.attack_damage, attacker=self)
                print(f"👊 Drowned punched for {self.attack_damage} damage!")
            
            self.attack_timer = self.attack_cooldown
    
    def die(self, all_mobs=None):
        """Drops rotten flesh and trident if holding one."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 13, random.randint(0, 2)))  # Rotten Flesh
            if self.has_trident:
                DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 134, 1))  # Trident (ID 134)
        self.kill()
    
    def ai_move(self, player, WORLD_MAP):
        """Hostile AI at night, passive during day. Swims in water, walks on land."""
        # Converted drowned are always friendly (just wander)
        if self.converted_from_zombie:
            # Peaceful wandering behavior
            self.attack_timer += 1
            if self.attack_timer % (FPS * 3) == 0:
                self.direction = random.choice([-1, 1])
                self.vel_x = self.direction * (self.speed * 0.5)
            return
        
        # Only aggressive during night and evening (NOT passive at all times)
        global TIME_PHASE
        is_hostile_time = (TIME_PHASE == NIGHT_PHASE or TIME_PHASE == EVENING_PHASE)
        
        # If it's daytime and drowned is NOT converted, they are still PASSIVE (not hostile)
        if not is_hostile_time:
            # Wander peacefully during day
            self.attack_timer += 1
            if self.attack_timer % (FPS * 3) == 0:
                self.direction = random.choice([-1, 1])
                self.vel_x = self.direction * (self.speed * 0.5)
            return
        
        player_dist_x = player.rect.centerx - self.rect.centerx
        player_dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(player_dist_x**2 + player_dist_y**2)
        
        self.vel_x = 0
        
        # Check if in water
        center_x = int(self.rect.centerx // BLOCK_SIZE)
        center_y = int(self.rect.centery // BLOCK_SIZE)
        in_water = False
        if 0 <= center_y < GRID_HEIGHT and 0 <= center_x < GRID_WIDTH:
            in_water = WORLD_MAP[center_y][center_x] in FLUID_BLOCKS
        
        # Use swim speed in water, normal speed on land
        current_speed = self.swim_speed if in_water else self.speed
        
        # Rotate drowned to horizontal when swimming
        if not hasattr(self, 'is_swimming'):
            self.is_swimming = False
        self.is_swimming = in_water  # Horizontal when in water
        
        # Reduce aggro range if player is crouching
        effective_aggro_range = self.aggro_range
        if player.is_crouching:
            effective_aggro_range = self.aggro_range * 0.5
        
        # Only chase player if it's hostile time (night/evening)
        if is_hostile_time and distance < effective_aggro_range:
            if abs(player_dist_x) > BLOCK_SIZE * 0.1:
                if player_dist_x > 0:
                    self.vel_x = current_speed
                else:
                    self.vel_x = -current_speed
            else:
                self.vel_x = 0
        else:
            # Wander when not chasing
            self.attack_timer += 1
            if self.attack_timer % (FPS * 3) == 0:
                self.direction = random.choice([-1, 1])
                self.vel_x = self.direction * (current_speed * 0.5)
        
        # Cliff avoidance (only on land, not in water)
        if self.vel_x != 0 and not in_water and self.is_on_ground:
            direction = 1 if self.vel_x > 0 else -1
            check_x = self.rect.centerx + direction * BLOCK_SIZE
            check_y = self.rect.bottom + 1
            
            check_col = check_x // BLOCK_SIZE
            check_row = check_y // BLOCK_SIZE
            
            if (0 <= check_row < GRID_HEIGHT and 
                0 <= check_col < len(WORLD_MAP[0]) and 
                WORLD_MAP[check_row][check_col] == 0):
                self.vel_x = 0
    
    def update(self, WORLD_MAP, player, MOBS):
        if self.attack_timer > 0:
            self.attack_timer -= 1
            
        self.ai_move(player, WORLD_MAP)
        super().update(WORLD_MAP, player, MOBS)

class Spider(Mob):
    """A hostile mob that is wide, short, and pounces."""
    def __init__(self, x, y):
        # The correct super() call from earlier steps
        super().__init__(x, y, BLOCK_SIZE * 2, BLOCK_SIZE, (40, 40, 40)) # Dark Gray
        self.health = 16
        self.max_health = 16
        self.speed = 2.2 
        self.aggro_range = BLOCK_SIZE * 9
        self.attack_damage = 1
        self.attack_cooldown = FPS * 2
        self.attack_timer = 0
        self.drop_id = 0 
        
        # Pounce AI
        self.pounce_timer = 0
        self.pounce_cooldown = FPS * 2
        
        # Aggression tracking for retaliation
        self.aggro_on_player = False
        self.aggro_timer = 0
        
        # Blocky spider design
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = BLOCK_SIZE * 2
        h = BLOCK_SIZE
        
        # Body (two segments)
        # Abdomen (larger, back)
        pygame.draw.rect(self.image, (40, 40, 40), (10, h // 4, w // 2 - 5, h // 2))
        # Head (smaller, front)
        pygame.draw.rect(self.image, (50, 50, 50), (w // 2 + 5, h // 3, w // 3, h // 3))
        
        # 8 legs - simplified blocky style
        leg_color = (30, 30, 30)
        leg_w = 12
        leg_h = 4
        
        # Left side (4 legs)
        pygame.draw.rect(self.image, leg_color, (0, h // 4, leg_w, leg_h))
        pygame.draw.rect(self.image, leg_color, (0, h // 4 + 6, leg_w, leg_h))
        pygame.draw.rect(self.image, leg_color, (0, h // 4 + 12, leg_w, leg_h))
        pygame.draw.rect(self.image, leg_color, (0, h // 4 + 18, leg_w, leg_h))
        
        # Right side (4 legs)
        pygame.draw.rect(self.image, leg_color, (w - leg_w, h // 4, leg_w, leg_h))
        pygame.draw.rect(self.image, leg_color, (w - leg_w, h // 4 + 6, leg_w, leg_h))
        pygame.draw.rect(self.image, leg_color, (w - leg_w, h // 4 + 12, leg_w, leg_h))
        pygame.draw.rect(self.image, leg_color, (w - leg_w, h // 4 + 18, leg_w, leg_h))
        
        # Eyes (8 red glowing eyes in 2 rows)
        eye_size = 3
        eye_y1 = h // 3 + 2
        eye_y2 = h // 3 + 6
        eye_start_x = w // 2 + 8
        
        # Top row (4 eyes)
        for i in range(4):
            pygame.draw.rect(self.image, (255, 0, 0), (eye_start_x + i * 5, eye_y1, eye_size, eye_size))
        # Bottom row (4 eyes, slightly smaller)
        for i in range(4):
            pygame.draw.rect(self.image, (200, 0, 0), (eye_start_x + i * 5, eye_y2, eye_size - 1, eye_size - 1))

    def ai_move(self, player):
        """Hostile AI: Chase player and pounce (ONLY AT NIGHT or if provoked)."""
        
        # Decrement aggro timer if active
        if self.aggro_timer > 0:
            self.aggro_timer -= 1
            if self.aggro_timer <= 0:
                self.aggro_on_player = False
        
        # Only aggressive during night/evening OR if provoked
        global TIME_PHASE
        is_hostile_time = (TIME_PHASE == NIGHT_PHASE or TIME_PHASE == EVENING_PHASE)
        is_aggressive = is_hostile_time or self.aggro_on_player
        
        player_dist_x = player.rect.centerx - self.rect.centerx
        player_dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(player_dist_x**2 + player_dist_y**2)
        
        self.vel_x = 0
        if self.pounce_timer > 0:
            self.pounce_timer -= 1
        
        # Reduce aggro range if player is crouching
        effective_aggro_range = self.aggro_range
        if player.is_crouching:
            effective_aggro_range = self.aggro_range * 0.5  # Half detection range when crouching
        
        # Only chase if aggressive (night/evening or provoked)
        if is_aggressive and distance < effective_aggro_range:
            # 1. Aggro Mode: Chase
            if player_dist_x > 0:
                self.vel_x = self.speed
            else:
                self.vel_x = -self.speed
                
            # 2. Pounce/Jump Attack Logic
            # Pounce when on the ground and close to the player's horizontal position
            if self.is_on_ground and self.pounce_timer <= 0 and abs(player_dist_x) < BLOCK_SIZE * 3:
                # Add a vertical boost for the pounce
                self.vel_y = -8
                self.pounce_timer = self.pounce_cooldown

        else:
            # 2. Wandering Mode (Simple: stay put) - passive during day
            self.vel_x = 0
            
    def attack(self, target):
        """Performs a damage-dealing attack."""
        if self.attack_timer <= 0:
            target.take_damage(self.attack_damage, attacker=self)
            self.attack_timer = self.attack_cooldown
    
    def take_damage(self, amount, all_mobs=None):
        """Override take_damage to become aggressive when hit during daytime."""
        self.health -= amount
        global TIME_PHASE
        # If hit during day/dawn, become aggressive for 30 seconds
        if TIME_PHASE == DAY_PHASE or TIME_PHASE == DAWN_PHASE:
            self.aggro_on_player = True
            self.aggro_timer = FPS * 30  # 30 seconds of aggression
        if self.health <= 0:
            self.die(all_mobs)
            
    def update(self, WORLD_MAP, player, MOBS): # <--- CORRECTED SIGNATURE
        if self.attack_timer > 0:
            self.attack_timer -= 1
            
        self.ai_move(player) # ai_move uses player
        
        super().update(WORLD_MAP, player, MOBS) # <--- PASS ARGS TO SUPER
        
        # Check for contact attack
        if self.rect.colliderect(player.rect):
            self.attack(player)
        
        # Check for contact attack
        if self.rect.colliderect(player.rect):
            self.attack(player)
    
    def die(self, all_mobs=None):
        """Drops string when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 52, random.randint(0, 2)))  # String (ID 52)
        self.kill()

class Parched(Mob):
    """A desert skeleton variant with gray bones and yellow bandage wrappings."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 2.5, (160, 160, 160))  # Gray bones
        
        self.max_health = 20
        self.health = 20
        self.speed = 1.6  # Slightly slower than skeleton
        self.aggro_range = BLOCK_SIZE * 12
        self.attack_range = BLOCK_SIZE * 8
        self.attack_damage = 3
        self.attack_cooldown = FPS * 2
        self.attack_timer = self.attack_cooldown
        self.drop_id = 0
        self.is_aquatic = True  # Undead don't drown
        
        # Draw mummy with gray bones and yellow wrappings
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        bone_color = (160, 160, 160)  # Gray bones
        wrap_color = (255, 220, 100)  # Yellow bandage wrappings
        dark_bone = (130, 130, 130)
        eye_glow = (255, 200, 50)  # Yellow glow
        
        # Legs (gray bones)
        pygame.draw.rect(self.image, bone_color, (10, BLOCK_SIZE * 1.5, 8, BLOCK_SIZE))
        pygame.draw.rect(self.image, bone_color, (22, BLOCK_SIZE * 1.5, 8, BLOCK_SIZE))
        
        # Yellow wrappings on legs (horizontal stripes)
        for i in range(0, int(BLOCK_SIZE), 12):
            pygame.draw.rect(self.image, wrap_color, (10, BLOCK_SIZE * 1.5 + i, 8, 4))
            pygame.draw.rect(self.image, wrap_color, (22, BLOCK_SIZE * 1.5 + i, 8, 4))
        
        # Pelvis
        pygame.draw.rect(self.image, dark_bone, (8, BLOCK_SIZE * 1.4, 24, 6))
        
        # Spine
        pygame.draw.rect(self.image, dark_bone, (17, BLOCK_SIZE * 0.5, 6, BLOCK_SIZE * 0.9))
        
        # Ribcage wrapped in bandages
        for i in range(5):
            pygame.draw.rect(self.image, bone_color, (10, BLOCK_SIZE * 0.6 + i * 6, 20, 3))
        # Yellow wrappings across torso
        pygame.draw.rect(self.image, wrap_color, (8, BLOCK_SIZE * 0.7, 24, 4))
        pygame.draw.rect(self.image, wrap_color, (8, BLOCK_SIZE * 1.0, 24, 4))
        
        # Shoulders
        pygame.draw.rect(self.image, dark_bone, (5, BLOCK_SIZE * 0.5, 30, 6))
        
        # Arms with wrappings
        pygame.draw.rect(self.image, bone_color, (2, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.7))
        pygame.draw.rect(self.image, bone_color, (32, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.7))
        # Arm wrappings
        for i in range(0, int(BLOCK_SIZE * 0.7), 10):
            pygame.draw.rect(self.image, wrap_color, (2, BLOCK_SIZE * 0.6 + i, 6, 3))
            pygame.draw.rect(self.image, wrap_color, (32, BLOCK_SIZE * 0.6 + i, 6, 3))
        
        # Skull (gray)
        pygame.draw.rect(self.image, bone_color, (8, 2, 24, 18))
        
        # Yellow wrappings on head (horizontal stripes)
        pygame.draw.rect(self.image, wrap_color, (8, 6, 24, 3))
        pygame.draw.rect(self.image, wrap_color, (8, 14, 24, 3))
        
        # Eye sockets with yellow glow
        pygame.draw.rect(self.image, (0, 0, 0), (12, 8, 6, 6))
        pygame.draw.rect(self.image, (0, 0, 0), (22, 8, 6, 6))
        pygame.draw.rect(self.image, eye_glow, (14, 10, 3, 3))
        pygame.draw.rect(self.image, eye_glow, (24, 10, 3, 3))
        
        # Nose hole
        pygame.draw.rect(self.image, (0, 0, 0), (17, 14, 6, 3))
        
        # Bow in hand
        bow_color = (101, 67, 33)
        string_color = (200, 200, 200)
        pygame.draw.rect(self.image, bow_color, (34, BLOCK_SIZE * 0.7, 3, 20))
        pygame.draw.rect(self.image, string_color, (36, BLOCK_SIZE * 0.7, 1, 20))
        pygame.draw.rect(self.image, (139, 69, 19), (30, BLOCK_SIZE * 0.8, 8, 2))
    
    def attack(self, target, arrows_group):
        """Shoots arrows like a skeleton."""
        if self.attack_timer <= 0:
            arrow = Arrow(
                self.rect.centerx,
                self.rect.centery,
                target.rect.centerx,
                target.rect.centery,
                self.attack_damage,
                is_from_stray=False
            )
            arrows_group.add(arrow)
            self.attack_timer = self.attack_cooldown
    
    def ai_move(self, player, arrows_group):
        """Similar to skeleton AI."""
        global TIME_PHASE
        is_hostile_time = (TIME_PHASE == NIGHT_PHASE or TIME_PHASE == EVENING_PHASE)
        
        player_dist_x = player.rect.centerx - self.rect.centerx
        player_dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(player_dist_x**2 + player_dist_y**2)
        
        self.vel_x = 0
        
        effective_aggro_range = self.aggro_range
        if player.is_crouching:
            effective_aggro_range = self.aggro_range * 0.5
        
        if is_hostile_time and distance < effective_aggro_range:
            if distance > self.attack_range:
                # Move closer
                if abs(player_dist_x) > BLOCK_SIZE * 0.1:
                    if player_dist_x > 0:
                        self.vel_x = self.speed
                    else:
                        self.vel_x = -self.speed
            else:
                # In attack range - stop and shoot
                self.vel_x = 0
                self.attack(player, arrows_group)
        else:
            # Wander
            self.attack_timer += 1
            if self.attack_timer % (FPS * 3) == 0:
                self.direction = random.choice([-1, 1])
                self.vel_x = self.direction * (self.speed * 0.5)
    
    def die(self, all_mobs=None):
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 146, random.randint(0, 2)))  # Feather
        self.kill()

class ZombieCamel(Mob):
    """A hostile brown zombie camel that attacks players."""
    def __init__(self, x, y):
        # Large camel size
        super().__init__(x, y, BLOCK_SIZE * 2, BLOCK_SIZE * 2, (140, 100, 60))
        
        self.max_health = 25
        self.health = 25
        self.speed = 2.0  # Fast hostile camel
        self.aggro_range = BLOCK_SIZE * 10
        self.attack_damage = 4  # Bite/kick damage
        self.attack_cooldown = FPS * 2
        self.attack_timer = 0
        self.drop_id = 13  # Rotten flesh
        self.direction = random.choice([-1, 1])
        self.is_aquatic = True  # Undead
        
        # Draw brown zombie camel
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 2)
        h = int(BLOCK_SIZE * 2)
        
        # Brown zombie camel colors
        camel_color = (100, 70, 40)  # Dark brown (zombie)
        leg_color = (80, 55, 30)
        eye_color = (255, 0, 0)  # Red zombie eyes
        
        # Legs (4 blocky legs)
        leg_width = 10
        leg_height = 25
        pygame.draw.rect(self.image, leg_color, (10, h - leg_height, leg_width, leg_height))
        pygame.draw.rect(self.image, leg_color, (w - 20, h - leg_height, leg_width, leg_height))
        pygame.draw.rect(self.image, leg_color, (25, h - leg_height, leg_width, leg_height))
        pygame.draw.rect(self.image, leg_color, (w - 35, h - leg_height, leg_width, leg_height))
        
        # Body (main rectangular body)
        pygame.draw.rect(self.image, camel_color, (10, h - 50, w - 20, 30))
        
        # Hump (blocky rectangles stacked)
        pygame.draw.rect(self.image, leg_color, (w // 2 - 12, h - 60, 24, 15))
        pygame.draw.rect(self.image, leg_color, (w // 2 - 8, h - 68, 16, 8))
        
        # Neck (vertical rectangle)
        pygame.draw.rect(self.image, camel_color, (w - 25, h - 70, 15, 25))
        
        # Head (small rectangle)
        pygame.draw.rect(self.image, camel_color, (w - 25, h - 78, 15, 12))
        
        # Red zombie eyes
        pygame.draw.rect(self.image, eye_color, (w - 23, h - 75, 3, 3))
        pygame.draw.rect(self.image, eye_color, (w - 17, h - 75, 3, 3))
    
    def attack(self, player):
        """Bites player."""
        if self.attack_timer <= 0:
            player.take_damage(self.attack_damage, attacker=self)
            self.attack_timer = self.attack_cooldown
    
    def die(self, all_mobs=None):
        """Drops rotten flesh."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 13, random.randint(0, 2)))  # Rotten flesh
        self.kill()
    
    def ai_move(self, player, WORLD_MAP):
        """Aggressive AI - charges at player."""
        player_dist_x = player.rect.centerx - self.rect.centerx
        player_dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(player_dist_x**2 + player_dist_y**2)
        
        self.vel_x = 0
        
        effective_aggro_range = self.aggro_range
        if player.is_crouching:
            effective_aggro_range = self.aggro_range * 0.5
        
        if distance < effective_aggro_range:
            # Charge at player
            if abs(player_dist_x) > BLOCK_SIZE * 0.5:
                if player_dist_x > 0:
                    self.vel_x = self.speed
                else:
                    self.vel_x = -self.speed
        else:
            # Wander
            self.attack_timer += 1
            if self.attack_timer % (FPS * 3) == 0:
                self.direction = random.choice([-1, 1])
                self.vel_x = self.direction * (self.speed * 0.5)

class Creeper(Mob):
    """A hostile mob that chases the player and explodes."""
    def __init__(self, x, y):
        # Use a very dark gray/black base color for max contrast
        CREEPER_COLOR = (10, 10, 10)
        super().__init__(x, y, BLOCK_SIZE * 0.8, BLOCK_SIZE * 1.5, CREEPER_COLOR)
        
        self.max_health = 20
        self.health = 20
        self.speed = 3
        self.aggro_range = BLOCK_SIZE * 10  # Chase from farther away
        self.explode_range = BLOCK_SIZE * 1.5  # Only explode when very close
        self.explosion_radius = BLOCK_SIZE * 6  # Much bigger explosion
        
        self.fuse_time = FPS * 1.0  # 1 second fuse time
        self.fuse_timer = -1 
        
        # --- Draw Enhanced Creeper with Body Parts ---
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = self.rect.width
        h = self.rect.height
        
        green = (10, 60, 10)
        dark_green = (8, 45, 8)
        face_color = (0, 0, 0)
        
        # Four blocky feet
        pygame.draw.rect(self.image, dark_green, (2, h - 12, 10, 12))  # Front left
        pygame.draw.rect(self.image, dark_green, (w - 12, h - 12, 10, 12))  # Front right
        pygame.draw.rect(self.image, dark_green, (2, h - 28, 10, 12))  # Back left
        pygame.draw.rect(self.image, dark_green, (w - 12, h - 28, 10, 12))  # Back right
        
        # Body (main rectangular body)
        pygame.draw.rect(self.image, green, (4, h * 0.3, w - 8, h * 0.5))
        
        # Head (slightly larger block on top)
        pygame.draw.rect(self.image, green, (2, 2, w - 4, h * 0.35))
        
        # Eyes (Two black squares)
        eye_width = w // 5
        eye_height = h // 12
        pygame.draw.rect(self.image, face_color, (w * 0.2, h * 0.12, eye_width, eye_height))
        pygame.draw.rect(self.image, face_color, (w * 0.8 - eye_width, h * 0.12, eye_width, eye_height))

        # Mouth (iconic T-shape frown)
        pygame.draw.rect(self.image, face_color, (w * 0.45, h * 0.22, w * 0.1, h * 0.12))  # Vertical
        pygame.draw.rect(self.image, face_color, (w * 0.3, h * 0.32, w * 0.4, h * 0.06))  # Horizontal

    def get_image(self):
        """Returns the Creeper image, flashing white when fusing."""
        original_image = self.image.copy()
        
        if self.fuse_timer > 0:
            # Flash white every 5 frames (1/12th of a second)
            if self.fuse_timer % 5 < 3: 
                original_image.fill((255, 255, 255))
            else:
                # Use the dark green when not flashing white
                original_image.fill((10, 60, 10))
                
        return original_image
        
    def explode(self, player, all_mobs=None):
        """Handles the explosion effect: damages the player, knocks them back, damages mobs, AND destroys blocks."""
        
        # Damage player
        damage_distance = math.sqrt(
            (self.rect.centerx - player.rect.centerx)**2 + 
            (self.rect.centery - player.rect.centery)**2
        )
        
        if damage_distance < self.explosion_radius:
            # Damage calculation
            damage = max(1, 15 - int(15 * (damage_distance / self.explosion_radius)))
            player.take_damage(damage)
            
            # Knockback calculation (2-4 blocks)
            knockback_strength = random.uniform(BLOCK_SIZE * 2, BLOCK_SIZE * 4)
            # Calculate direction from creeper to player
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # Normalize and apply knockback
                player.vel_x = (dx / distance) * knockback_strength * 0.3  # Horizontal knockback
                player.vel_y = -knockback_strength * 0.2  # Upward knockback
        
        # Damage nearby mobs (except self)
        if all_mobs:
            for mob in all_mobs:
                if mob == self:
                    continue
                
                mob_distance = math.sqrt(
                    (self.rect.centerx - mob.rect.centerx)**2 + 
                    (self.rect.centery - mob.rect.centery)**2
                )
                
                if mob_distance < self.explosion_radius:
                    # Same damage formula as player
                    mob_damage = max(1, 15 - int(15 * (mob_distance / self.explosion_radius)))
                    mob.take_damage(mob_damage, all_mobs)
            
        # --- BLOCK DESTRUCTION LOGIC ---
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        radius_blocks = int(self.explosion_radius // BLOCK_SIZE)
        
        for r in range(center_row - radius_blocks, center_row + radius_blocks + 1):
            for c in range(center_col - radius_blocks, center_col + radius_blocks + 1):
                
                # Check bounds and only destroy blocks within a sphere-like radius
                if (0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH and 
                    (r - center_row)**2 + (c - center_col)**2 <= radius_blocks**2):
                    
                    # Do not destroy unmineable blocks like Bedrock (ID 4)
                    if WORLD_MAP[r][c] != 0 and WORLD_MAP[r][c] != 4:
                        WORLD_MAP[r][c] = 0 # Set to Air        
    
    def update(self, WORLD_MAP, player, MOBS): # <--- CORRECTED SIGNATURE
        # Creepers are ALWAYS hostile (day and night)
        distance_sq = (self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2
        distance = math.sqrt(distance_sq)
        
        # Check if player is in aggro range (creepers are always aggressive)
        if distance < self.aggro_range:
            
            # Check if close enough to start fuse
            if distance < self.explode_range:
                # Start/Continue fuse
                if self.fuse_timer == -1:
                    self.fuse_timer = self.fuse_time
                
                if self.fuse_timer > 0:
                    self.fuse_timer -= 1
                    self.vel_x = 0 # Freeze movement while fusing
                    
                    if self.fuse_timer <= 0:
                        self.explode(player, MOBS)
                        self.kill()
                        return
            else:
                # Chase player if not close enough to explode
                self.fuse_timer = -1  # Reset fuse
                if self.rect.centerx < player.rect.centerx:
                    self.vel_x = self.speed
                elif self.rect.centerx > player.rect.centerx:
                    self.vel_x = -self.speed
        else:
            # Out of range - stop moving
            self.vel_x = 0
            self.fuse_timer = -1 # Reset fuse if player leaves range

        # Apply general Mob physics (gravity and collision)
        super().update(WORLD_MAP, player, MOBS)

    def die(self, all_mobs=None):
        """Drops gunpowder when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 56, random.randint(0, 2)))  # Gunpowder (ID 56)
        self.kill()

# --- Arrow Projectile Class ---
class Arrow(pygame.sprite.Sprite):
    """Arrow projectile shot by skeletons with gravity and collision."""
    def __init__(self, x, y, target_x, target_y, damage=3, is_from_stray=False):
        super().__init__()
        self.image = pygame.Surface([8, 3])
        self.image.fill((139, 69, 19))  # Brown arrow
        self.rect = self.image.get_rect(center=(x, y))
        
        self.damage = damage
        self.gravity = 0.15
        self.is_from_stray = is_from_stray
        
        # Calculate initial velocity toward target
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            speed = 8  # Arrow speed
            self.vel_x = (dx / distance) * speed
            self.vel_y = (dy / distance) * speed
        else:
            self.vel_x = 0
            self.vel_y = 0
    
    def update(self, WORLD_MAP, player, all_mobs=None):
        """Update arrow position with gravity and check collisions."""
        # Apply gravity
        self.vel_y += self.gravity
        
        # Move arrow
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Check collision with player
        if self.rect.colliderect(player.rect):
            player.take_damage(self.damage)
            # Apply slowness effect if from stray
            if self.is_from_stray:
                player.slowness_timer = FPS * 5  # 5 seconds of slowness
                player.slowness_strength = 0.5  # Move at 50% speed
            self.kill()
            return
        
        # Check collision with mobs
        if all_mobs:
            for mob in all_mobs:
                if self.rect.colliderect(mob.rect):
                    mob.take_damage(self.damage, all_mobs)
                    self.kill()
                    return
        
        # Check collision with blocks
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
            block_id = WORLD_MAP[center_row][center_col]
            if block_id != 0 and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                self.kill()
                return
        
        # Remove if out of bounds
        if (self.rect.x < 0 or self.rect.x > GRID_WIDTH * BLOCK_SIZE or
            self.rect.y < 0 or self.rect.y > GRID_HEIGHT * BLOCK_SIZE):
            self.kill()

class SplashPotion(pygame.sprite.Sprite):
    """Splash potion projectile thrown by player or witch."""
    def __init__(self, x, y, direction, potion_id):
        super().__init__()
        potion_color = BLOCK_TYPES[potion_id].get("color", (255, 100, 100))
        self.image = pygame.Surface([12, 12])
        self.image.fill(potion_color)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.potion_id = potion_id
        self.gravity = 0.3
        self.vel_x = direction * 6  # Throw horizontally
        self.vel_y = -4  # Throw upward in arc
        self.splash_radius = BLOCK_SIZE * 2  # 2 block radius
    
    def update(self, WORLD_MAP, player, all_mobs):
        """Update potion position and check for impact."""
        # Apply gravity
        self.vel_y += self.gravity
        
        # Move potion
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Check collision with blocks
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        
        hit_block = False
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
            block_id = WORLD_MAP[center_row][center_col]
            if block_id != 0 and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                hit_block = True
        
        # Check collision with mobs
        hit_mob = False
        for mob in all_mobs:
            if self.rect.colliderect(mob.rect):
                hit_mob = True
                break
        
        # Splash on impact
        if hit_block or hit_mob:
            self.splash_effect(player, all_mobs)
            self.kill()
            return
        
        # Remove if out of bounds
        if (self.rect.x < 0 or self.rect.x > GRID_WIDTH * BLOCK_SIZE or
            self.rect.y < 0 or self.rect.y > GRID_HEIGHT * BLOCK_SIZE):
            self.kill()
    
    def splash_effect(self, player, all_mobs):
        """Apply area effect on splash."""
        heal_amount = BLOCK_TYPES[self.potion_id].get("heal_amount", 0)
        damage_amount = BLOCK_TYPES[self.potion_id].get("damage_amount", 0)
        
        # Check player in radius
        player_distance = math.sqrt(
            (self.rect.centerx - player.rect.centerx) ** 2 +
            (self.rect.centery - player.rect.centery) ** 2
        )
        if player_distance <= self.splash_radius:
            if heal_amount > 0:
                player.health = min(player.max_health, player.health + heal_amount)
                print(f"❤️ Splash healed player {heal_amount} HP!")
            elif damage_amount > 0:
                player.take_damage(damage_amount)
                print(f"💥 Splash poisoned player {damage_amount} damage!")
        
        # Check mobs in radius
        for mob in all_mobs:
            mob_distance = math.sqrt(
                (self.rect.centerx - mob.rect.centerx) ** 2 +
                (self.rect.centery - mob.rect.centery) ** 2
            )
            if mob_distance <= self.splash_radius:
                if heal_amount > 0:
                    mob.health = min(mob.max_health, mob.health + heal_amount)
                elif damage_amount > 0:
                    mob.take_damage(damage_amount, all_mobs)

class Trident(pygame.sprite.Sprite):
    """Trident projectile thrown by drowned or player."""
    def __init__(self, x, y, target_x, target_y, damage=12, thrown_by_player=False):
        super().__init__()
        self.image = pygame.Surface([6, 20])
        self.image.fill((0, 180, 200))  # Cyan trident
        self.rect = self.image.get_rect(center=(x, y))
        
        self.damage = damage
        self.gravity = 0.1  # Light gravity for trident
        self.thrown_by_player = thrown_by_player  # Track who threw it
        
        # Calculate initial velocity toward target
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            speed = 12  # Trident speed (increased from 10)
            self.vel_x = (dx / distance) * speed
            self.vel_y = (dy / distance) * speed
        else:
            self.vel_x = 0
            self.vel_y = 0
    
    def update(self, WORLD_MAP, player, all_mobs=None):
        """Update trident position with gravity and check collisions."""
        # Apply gravity
        self.vel_y += self.gravity
        
        # Move trident
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        
        # Check collision with player (only if thrown by mob, not player)
        if not self.thrown_by_player and self.rect.colliderect(player.rect):
            player.take_damage(self.damage)
            print(f"🔱 Trident hit player for {self.damage} damage!")
            self.kill()
            return
        
        # Check collision with mobs
        if all_mobs:
            for mob in all_mobs:
                # Player tridents hit all mobs, Drowned tridents only hit non-Drowned mobs
                if self.rect.colliderect(mob.rect):
                    if self.thrown_by_player or not isinstance(mob, Drowned):
                        mob.take_damage(self.damage, all_mobs)
                        self.kill()
                        return
        
        # Check collision with blocks
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
            block_id = WORLD_MAP[center_row][center_col]
            if block_id != 0 and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                self.kill()
                return
        
        # Remove if out of bounds
        if (self.rect.x < 0 or self.rect.x > GRID_WIDTH * BLOCK_SIZE or
            self.rect.y < 0 or self.rect.y > GRID_HEIGHT * BLOCK_SIZE):
            self.kill()

class Skeleton(Mob):
    """A hostile mob that shoots arrows at the player from a distance."""
    def __init__(self, x, y, is_stray=False):
        # Bone white color, 1 block wide, 2.5 blocks high (slightly taller than Zombie/Player)
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 2.5, (200, 200, 200)) 
        
        self.max_health = 20
        self.health = 20
        self.speed = 1.8 # Slower walking speed
        self.aggro_range = BLOCK_SIZE * 12 # Aggro from farther away (ranged mob)
        self.attack_range = BLOCK_SIZE * 8 # Will stop moving to shoot from this distance
        self.attack_damage = 3
        self.attack_cooldown = FPS * 2 # Shoots every 2 seconds
        self.attack_timer = self.attack_cooldown
        self.drop_id = 0 # No drop in this simple version (could drop sticks/bones)
        self.is_stray = is_stray  # Store stray status
        self.is_aquatic = True  # Undead don't drown
        self.name = "Stray" if is_stray else "Skeleton"  # Display name
        
        # Enhanced drawing with skeletal body parts
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        # Stray variant (icy blue tint) or normal skeleton
        if is_stray:
            bone_color = (180, 220, 255)  # Icy blue-white
            dark_bone = (140, 180, 220)  # Darker icy blue
            eye_glow = (150, 200, 255)  # Bright icy glow
        else:
            bone_color = (200, 200, 200)
            dark_bone = (170, 170, 170)
            eye_glow = (100, 150, 255)  # Dim blue glow
        
        # Legs (bone legs)
        pygame.draw.rect(self.image, bone_color, (10, BLOCK_SIZE * 1.5, 8, BLOCK_SIZE))  # Left leg
        pygame.draw.rect(self.image, bone_color, (22, BLOCK_SIZE * 1.5, 8, BLOCK_SIZE))  # Right leg
        
        # Pelvis (small horizontal bone)
        pygame.draw.rect(self.image, dark_bone, (8, BLOCK_SIZE * 1.4, 24, 6))
        
        # Spine (vertical line)
        pygame.draw.rect(self.image, dark_bone, (17, BLOCK_SIZE * 0.5, 6, BLOCK_SIZE * 0.9))
        
        # Ribcage (horizontal lines)
        for i in range(5):
            pygame.draw.rect(self.image, bone_color, (10, BLOCK_SIZE * 0.6 + i * 6, 20, 3))
        
        # Shoulders
        pygame.draw.rect(self.image, dark_bone, (5, BLOCK_SIZE * 0.5, 30, 6))
        
        # Arms (bone arms)
        pygame.draw.rect(self.image, bone_color, (2, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.7))  # Left arm
        pygame.draw.rect(self.image, bone_color, (32, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.7))  # Right arm
        
        # Skull (blocky head)
        pygame.draw.rect(self.image, bone_color, (8, 2, 24, 18))
        
        # Eye sockets (black hollow eyes)
        pygame.draw.rect(self.image, (0, 0, 0), (12, 8, 6, 6))  # Left eye
        pygame.draw.rect(self.image, (0, 0, 0), (22, 8, 6, 6))  # Right eye
        
        # Glowing eye effect (dim blue glow in sockets)
        pygame.draw.rect(self.image, eye_glow, (14, 10, 3, 3))  # Left glow
        pygame.draw.rect(self.image, eye_glow, (24, 10, 3, 3))  # Right glow
        
        # Nose hole (small triangle represented as rect)
        pygame.draw.rect(self.image, (0, 0, 0), (17, 14, 6, 3)) 
        
        # BOW - Draw a bow in the skeleton's hand
        bow_color = (101, 67, 33)  # Brown bow
        string_color = (200, 200, 200)  # White string
        # Bow body (curved)
        pygame.draw.rect(self.image, bow_color, (34, BLOCK_SIZE * 0.7, 3, 20))
        # Bow string
        pygame.draw.rect(self.image, string_color, (36, BLOCK_SIZE * 0.7, 1, 20))
        # Arrow (when not shooting)
        pygame.draw.rect(self.image, (139, 69, 19), (30, BLOCK_SIZE * 0.8, 8, 2))
        
        # BLUE CLOTH DRAPING (only for strays)
        if is_stray:
            cloth_color = (100, 150, 200)  # Blue cloth
            # Cloth draped over shoulders and back
            pygame.draw.rect(self.image, cloth_color, (6, BLOCK_SIZE * 0.5, 28, BLOCK_SIZE * 1.2), 0)  # Main drape
            # Make it semi-transparent looking with darker edges
            pygame.draw.rect(self.image, (70, 120, 170), (6, BLOCK_SIZE * 0.5, 28, BLOCK_SIZE * 1.2), 2)  # Border
        
    def attack(self, target, arrows_group):
        """Shoots an actual arrow projectile."""
        if self.attack_timer <= 0:
            # Create and fire arrow
            arrow = Arrow(
                self.rect.centerx, 
                self.rect.centery,
                target.rect.centerx,
                target.rect.centery,
                self.attack_damage,
                is_from_stray=self.is_stray
            )
            arrows_group.add(arrow)
            self.attack_timer = self.attack_cooldown
            
    def ai_move(self, player, arrows_group):
        """Hostile AI: Chase player if outside attack range, stop and shoot if inside (ONLY AT NIGHT). Avoid water unless on fire."""
        
        # Only aggressive during night and evening
        global TIME_PHASE
        is_hostile_time = (TIME_PHASE == NIGHT_PHASE or TIME_PHASE == EVENING_PHASE)
        
        player_dist_x = player.rect.centerx - self.rect.centerx
        player_dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(player_dist_x**2 + player_dist_y**2)
        
        self.vel_x = 0
        
        # Reduce aggro range if player is crouching
        effective_aggro_range = self.aggro_range
        if player.is_crouching:
            effective_aggro_range = self.aggro_range * 0.5  # Half detection range when crouching
        
        # Only attack if it's hostile time (night/evening)
        if is_hostile_time and distance < effective_aggro_range:
            
            # 1. Attack Mode: If within shooting range, stop and shoot.
            if distance < self.attack_range:
                self.vel_x = 0
                self.attack(player, arrows_group) # Attempt to attack every frame (cooldown controls rate)
            
            # 2. Chase Mode: If outside shooting range, chase.
            else: 
                if player_dist_x > 0:
                    self.vel_x = self.speed
                else:
                    self.vel_x = -self.speed
        
        # Water avoidance (unless on fire)
        if self.vel_x != 0 and not self.on_fire:
            direction = 1 if self.vel_x > 0 else -1
            check_x = self.rect.centerx + direction * BLOCK_SIZE
            check_y = self.rect.centery
            
            check_col = check_x // BLOCK_SIZE
            check_row = check_y // BLOCK_SIZE
            
            if (0 <= check_row < GRID_HEIGHT and 0 <= check_col < len(WORLD_MAP[0])):
                if WORLD_MAP[check_row][check_col] in FLUID_BLOCKS:
                    self.vel_x = 0  # Stop before entering water
        
        # Apply standard wall/cliff avoidance logic
        if self.vel_x != 0 and self.is_on_ground:
            direction = 1 if self.vel_x > 0 else -1
            check_x = self.rect.centerx + direction * BLOCK_SIZE
            check_y = self.rect.bottom + 1
            
            check_col = check_x // BLOCK_SIZE
            check_row = check_y // BLOCK_SIZE
            
            if (0 <= check_row < GRID_HEIGHT and 
                0 <= check_col < len(WORLD_MAP[0]) and 
                WORLD_MAP[check_row][check_col] == 0):
                self.vel_x = 0 

    def update(self, WORLD_MAP, player, MOBS, arrows_group): # <--- ADDED arrows_group
        if self.attack_timer > 0:
            self.attack_timer -= 1
            
        self.ai_move(player, arrows_group)
        
        super().update(WORLD_MAP, player, MOBS)

    def die(self, all_mobs=None):
        """Drops arrows, bones, and rarely a bow."""
        if 'DROPPED_ITEMS' in globals():
            # Always drop arrows and bones
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx - 5, self.rect.bottom - 10, 53, random.randint(0, 2)))  # Arrows (ID 53)
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx + 5, self.rect.bottom - 10, 54, random.randint(0, 2)))  # Bones (ID 54)
            # Rare bow drop (2.5% chance)
            if random.random() < 0.025:
                DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 55, 1))  # Bow (ID 55)
        self.kill()

class Narwhal(Mob):
    """A peaceful aquatic mob that swims in water."""
    def __init__(self, x, y):
        # White/light gray color, long and thin
        super().__init__(x, y, BLOCK_SIZE * 1.5, BLOCK_SIZE * 0.5, (230, 230, 255)) 
        
        self.max_health = 10
        self.health = 10
        self.speed = 1.5 
        self.gravity = 0 # No gravity for narwhals (overridden when in water)
        self.swim_timer = random.randint(FPS, FPS * 3) 
        self.vertical_timer = random.randint(FPS, FPS * 2)
        self.drop_id = 0 
        self.is_aquatic = True  # Narwhals don't drown 
        
        # Blocky narwhal - simple block with horn
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 1.5)
        h = int(BLOCK_SIZE * 0.5)
        
        # Main body
        body_color = (230, 230, 255)
        pygame.draw.rect(self.image, body_color, (10, 0, w - 20, h))
        
        # Darker back (top shading)
        pygame.draw.rect(self.image, (200, 200, 230), (15, 0, w - 30, h // 3))
        
        # Spots (gray spots on body)
        spot_color = (180, 180, 200)
        pygame.draw.rect(self.image, spot_color, (20, h // 3, 6, 4))
        pygame.draw.rect(self.image, spot_color, (30, h // 4, 5, 3))
        pygame.draw.rect(self.image, spot_color, (w - 25, h // 2, 4, 3))
        
        # Head (slightly lighter)
        pygame.draw.rect(self.image, (240, 240, 255), (w - 15, 2, 12, h - 4))
        
        # Eye (small black dot)
        pygame.draw.rect(self.image, (0, 0, 0), (w - 10, h // 3, 2, 2))
        
        # Tusk (long spiral horn - iconic narwhal feature!)
        tusk_color = (200, 200, 180)
        pygame.draw.rect(self.image, tusk_color, (w - 5, h // 2 - 1, 15, 2))  # Main tusk
        
        # Tusk spiral detail (darker lines)
        for i in range(3):
            pygame.draw.rect(self.image, (160, 160, 140), (w + i * 4, h // 2 - 1, 1, 2))
        
        # Flippers (two side fins)
        flipper_color = (210, 210, 235)
        pygame.draw.rect(self.image, flipper_color, (22, h - 2, 10, 3))  # Left flipper
        pygame.draw.rect(self.image, flipper_color, (w - 30, h - 2, 10, 3))  # Right flipper
        
        # Tail fluke (horizontal tail fin)
        pygame.draw.rect(self.image, body_color, (5, h // 2 - 3, 8, 6))  # Left tail
        pygame.draw.rect(self.image, body_color, (3, h // 2 - 2, 4, 4))  # Tail tip
        
        # Start swimming right or left
        self.vel_x = self.speed * random.choice([-1, 1]) 
        self.vel_y = random.uniform(-0.5, 0.5)

    def ai_move(self, world_map):
        """Aquatic AI: Swim in water with both horizontal and vertical movement."""
        
        self.swim_timer -= 1
        self.vertical_timer -= 1
        
        # Check if in water (using center point for simplicity)
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        in_water = False
        
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
             # Assuming WATER_ID is 5 (from your previous code)
            in_water = world_map[center_row][center_col] == 5 
        
        if not in_water:
            # Out of water: Let base Mob physics and gravity take over
            return False 
        else:
            # Change horizontal direction periodically
            if self.swim_timer <= 0:
                self.vel_x *= -1
                self.swim_timer = random.randint(FPS * 2, FPS * 5)
            
            # Change vertical direction periodically
            if self.vertical_timer <= 0:
                self.vel_y = random.uniform(-1.5, 1.5)
                self.vertical_timer = random.randint(FPS, FPS * 3)
            
            # Wall detection (check one block ahead for solid blocks)
            direction = 1 if self.vel_x > 0 else -1
            check_x = self.rect.centerx + direction * int(self.rect.width * 0.75)
            
            check_points = [self.rect.top, self.rect.centery, self.rect.bottom - 1]
            should_turn = False
            
            for check_y in check_points:
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                if not (0 <= check_row < GRID_HEIGHT and 0 <= check_col < len(WORLD_MAP[0])):
                    should_turn = True
                    break
                
                block_id = world_map[check_row][check_col]
                
                # If hitting a solid block (not Air 0 or Water 5), turn around
                if block_id != 0 and block_id != 5:
                    should_turn = True
                    break
            
            if should_turn:
                self.vel_x *= -1
                self.swim_timer = FPS * 2
                
            return True # In water, handled custom movement

    # CRITICAL FIX: The update method must accept all three arguments!
    def update(self, world_map, player, all_mobs):
        
        # Custom aquatic movement logic
        is_swimming = self.ai_move(world_map)
        
        if is_swimming:
            # Handle collisions/movement specific to water
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y
            
            # Check for vertical collisions against solid blocks
            check_row = int((self.rect.y + self.vel_y) // BLOCK_SIZE)
            
            vertical_collision = False
            for check_col in [self.rect.left // BLOCK_SIZE, self.rect.right // BLOCK_SIZE]:
                 if 0 <= check_row < GRID_HEIGHT and 0 <= check_col < len(WORLD_MAP[0]):
                    block_id = world_map[check_row][check_col] 
                    if block_id != 0 and block_id != 5:
                        vertical_collision = True
                        break
                        
            if vertical_collision:
                self.vel_y *= -1
                self.vertical_timer = FPS * 2

            # Keep narwhal within world bounds (simplified)
            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(GRID_WIDTH * BLOCK_SIZE, self.rect.right)
            self.rect.top = max(0, self.rect.top)
            self.rect.bottom = min(GRID_HEIGHT * BLOCK_SIZE, self.rect.bottom)
            
        else:
            # Out of water: Apply gravity and fall down
            self.gravity = 0.5  # Re-enable gravity
            self.vel_y += self.gravity
            if self.vel_y > 10:
                self.vel_y = 10
            
            # Use standard Mob physics (gravity, ground collisions)
            super().update(world_map, player, all_mobs) 

    def take_damage(self, damage, all_mobs=None):
        # Narwhal takes damage
        super().take_damage(damage, all_mobs)
        # Optional: Aggressive behavior if attacked (e.g., swim away faster)
        if self.health > 0:
            self.vel_x = random.choice([-3, 3]) # Quick dash to escape
            self.speed = 3.0 # Temporarily increased speed
    
    def die(self, all_mobs=None):
        """Drops narwhal horn when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 58, 1))  # Narwhal Horn (ID 58)
        self.kill()

# --- Mob Classes (Add this after Player, or near the other Mobs) ---
class Deer(Mob):
    """A peaceful forest mob that wanders and drops leather."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 2, BLOCK_SIZE * 1.3, (139, 90, 43))
        self.health = 10
        self.max_health = 10
        self.speed = 2.0
        self.drop_id = 14  # Leather
        
        # AI state
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(1, 4)
        self.stop_duration = FPS * random.uniform(1, 3)
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Blocky deer design
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 2)
        h = int(BLOCK_SIZE * 1.3)
        
        # Legs (4 brown legs)
        leg_color = (101, 67, 33)
        pygame.draw.rect(self.image, leg_color, (8, h - 18, 6, 18))  # Front left
        pygame.draw.rect(self.image, leg_color, (w - 14, h - 18, 6, 18))  # Front right
        pygame.draw.rect(self.image, leg_color, (18, h - 18, 6, 18))  # Back left
        pygame.draw.rect(self.image, leg_color, (w - 24, h - 18, 6, 18))  # Back right
        
        # Body (brown/tan)
        body_color = (160, 110, 70)
        pygame.draw.rect(self.image, body_color, (6, h - 32, w - 12, 16))
        
        # Neck
        pygame.draw.rect(self.image, body_color, (w - 14, h - 42, 10, 14))
        
        # Head (blocky)
        head_color = (139, 90, 43)
        pygame.draw.rect(self.image, head_color, (w - 15, h - 50, 12, 10))
        
        # Snout
        pygame.draw.rect(self.image, (120, 80, 40), (w - 12, h - 46, 8, 6))
        
        # Ears (triangular, blocky)
        pygame.draw.rect(self.image, head_color, (w - 14, h - 52, 4, 4))
        pygame.draw.rect(self.image, head_color, (w - 6, h - 52, 4, 4))
        
        # MASSIVE BULKY HORNS
        horn_color = (240, 240, 220)
        horn_dark = (200, 200, 180)  # Shading
        
        # Left horn - MASSIVE and BULKY
        pygame.draw.rect(self.image, horn_color, (w - 18, h - 70, 8, 20))  # Main stem (thick)
        pygame.draw.rect(self.image, horn_dark, (w - 18, h - 70, 2, 20))  # Shading on stem
        pygame.draw.rect(self.image, horn_color, (w - 22, h - 62, 6, 10))  # Large left branch
        pygame.draw.rect(self.image, horn_color, (w - 16, h - 68, 6, 8))  # Large right branch
        pygame.draw.rect(self.image, horn_color, (w - 20, h - 75, 4, 8))  # Top tip (bulky)
        
        # Right horn - MASSIVE and BULKY
        pygame.draw.rect(self.image, horn_color, (w - 2, h - 70, 8, 20))  # Main stem (thick)
        pygame.draw.rect(self.image, horn_dark, (w, h - 70, 2, 20))  # Shading on stem
        pygame.draw.rect(self.image, horn_color, (w + 4, h - 62, 6, 10))  # Large right branch
        pygame.draw.rect(self.image, horn_color, (w - 4, h - 68, 6, 8))  # Large left branch
        pygame.draw.rect(self.image, horn_color, (w + 4, h - 75, 4, 8))  # Top tip (bulky)
        
        # Eyes
        pygame.draw.rect(self.image, (0, 0, 0), (w - 12, h - 48, 2, 2))
        pygame.draw.rect(self.image, (0, 0, 0), (w - 6, h - 48, 2, 2))
        
        # Tail
        pygame.draw.rect(self.image, (120, 80, 40), (2, h - 28, 4, 6))

    def ai_move(self):
        """Simple wandering AI."""
        self.move_timer += 1
        
        if self.is_moving:
            self.vel_x = self.direction * self.speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(1, 3)
                self.vel_x = 0
                
            if self.is_on_ground:
                check_x = self.rect.centerx + self.direction * BLOCK_SIZE
                check_y = self.rect.bottom + 1
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                if (0 <= check_row < GRID_HEIGHT and 
                    0 <= check_col < len(WORLD_MAP[0]) and 
                    WORLD_MAP[check_row][check_col] == 0):
                    self.direction *= -1
                    self.move_timer = 0
                    self.is_moving = False
                    self.vel_x = 0
        else:
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(1, 4)
                self.direction = random.choice([-1, 1])
                
    def update(self, WORLD_MAP, player, MOBS):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
        
    def die(self, all_mobs=None):
        """Drops deer horn when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 57, 1))  # Deer Horn (ID 57)
        self.kill()

class Panda(Mob):
    """A peaceful jungle mob that sits and eats bamboo."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 1.5, BLOCK_SIZE * 1.5, (255, 255, 255))
        self.health = 20
        self.max_health = 20
        self.speed = 1.0
        self.drop_id = 127  # Bamboo
        
        # AI state
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(1, 3)
        self.stop_duration = FPS * random.uniform(3, 8)  # Sits longer
        self.is_moving = False  # Pandas sit more than move
        self.direction = random.choice([-1, 1])
        
        # Panda design - iconic black and white
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 1.5)
        h = int(BLOCK_SIZE * 1.5)
        
        # Body (white/light gray)
        body_color = (240, 240, 240)
        pygame.draw.rect(self.image, body_color, (w//4, h//3, w//2, h//2))
        
        # Black legs
        leg_color = (20, 20, 20)
        pygame.draw.rect(self.image, leg_color, (w//4 - 2, h - 16, 8, 16))  # Front left
        pygame.draw.rect(self.image, leg_color, (w - w//4 - 6, h - 16, 8, 16))  # Front right
        
        # Head (white with black ears and eyes)
        pygame.draw.rect(self.image, body_color, (w//3, h//6, w//3, w//3))
        
        # Black ears (round)
        pygame.draw.rect(self.image, leg_color, (w//3 - 2, h//8, 8, 8))
        pygame.draw.rect(self.image, leg_color, (w - w//3 - 6, h//8, 8, 8))
        
        # Black eye patches
        pygame.draw.rect(self.image, leg_color, (w//3 + 2, h//5, 10, 8))
        pygame.draw.rect(self.image, leg_color, (w - w//3 - 12, h//5, 10, 8))
        
        # White eyes in patches
        pygame.draw.rect(self.image, (255, 255, 255), (w//3 + 5, h//5 + 2, 3, 3))
        pygame.draw.rect(self.image, (255, 255, 255), (w - w//3 - 8, h//5 + 2, 3, 3))
        
        # Black nose
        pygame.draw.rect(self.image, leg_color, (w//2 - 2, h//4 + 8, 4, 3))
    
    def ai_move(self):
        """Simple sitting/wandering AI."""
        self.move_timer += 1
        
        if self.is_moving:
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.vel_x = 0
                self.move_timer = 0
            else:
                self.vel_x = self.direction * self.speed
        else:
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.direction = random.choice([-1, 1])
                self.move_timer = 0
    
    def update(self, world_map, player, all_mobs):
        self.ai_move()
        super().update(world_map, player, all_mobs)


class Bear(Mob):
    """A neutral forest mob that only attacks when provoked."""
    def __init__(self, x, y, is_polar=False):
        # Bears are large (2x2 blocks)
        super().__init__(x, y, BLOCK_SIZE * 2, BLOCK_SIZE * 2, (101, 67, 33))
        self.health = 40
        self.max_health = 40
        self.speed = 1.5
        self.drop_id = 14  # Leather
        self.is_polar = is_polar
        
        # Neutral AI state
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(2, 5)
        self.stop_duration = FPS * random.uniform(2, 4)
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Aggression state (only attacks when provoked)
        self.is_aggressive = False
        self.aggro_timer = 0
        self.aggro_duration = FPS * 15  # Stay aggressive for 15 seconds after being hit
        self.attack_cooldown = FPS * 1.5  # 1.5 seconds between attacks
        self.attack_timer = 0
        
        # Draw bear
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = BLOCK_SIZE * 2
        h = BLOCK_SIZE * 2
        
        # Color based on type
        if is_polar:
            body_color = (255, 255, 255)  # White
            dark_color = (230, 230, 230)  # Light gray
        else:
            body_color = (101, 67, 33)  # Brown
            dark_color = (80, 50, 25)  # Dark brown
        
        # Legs (4 thick legs)
        pygame.draw.rect(self.image, dark_color, (10, h - 25, 12, 25))  # Front left
        pygame.draw.rect(self.image, dark_color, (w - 22, h - 25, 12, 25))  # Front right
        pygame.draw.rect(self.image, dark_color, (26, h - 25, 12, 25))  # Back left
        pygame.draw.rect(self.image, dark_color, (w - 38, h - 25, 12, 25))  # Back right
        
        # Body (large, bulky)
        pygame.draw.rect(self.image, body_color, (8, h - 50, w - 16, 28))
        
        # Head (large, rounded)
        pygame.draw.rect(self.image, body_color, (w - 28, h - 65, 24, 20))
        
        # Snout
        snout_color = (80, 50, 30) if not is_polar else (200, 200, 200)
        pygame.draw.rect(self.image, snout_color, (w - 22, h - 55, 16, 12))
        
        # Nose (black)
        pygame.draw.rect(self.image, (0, 0, 0), (w - 16, h - 50, 6, 4))
        
        # Ears (rounded)
        pygame.draw.rect(self.image, body_color, (w - 26, h - 70, 8, 8))
        pygame.draw.rect(self.image, body_color, (w - 12, h - 70, 8, 8))
        
        # Eyes (black)
        pygame.draw.rect(self.image, (0, 0, 0), (w - 24, h - 62, 3, 3))
        pygame.draw.rect(self.image, (0, 0, 0), (w - 12, h - 62, 3, 3))
        
        # Claws on front paws
        claw_color = (240, 240, 240) if is_polar else (220, 220, 200)
        for i in range(3):
            pygame.draw.rect(self.image, claw_color, (12 + i * 3, h - 4, 2, 4))
            pygame.draw.rect(self.image, claw_color, (w - 20 + i * 3, h - 4, 2, 4))

    def ai_move(self):
        """Wanders peacefully unless aggressive."""
        self.move_timer += 1
        
        # Update aggro timer
        if self.is_aggressive:
            self.aggro_timer += 1
            if self.aggro_timer >= self.aggro_duration:
                self.is_aggressive = False
                self.aggro_timer = 0
        
        if self.is_moving:
            # Move faster when aggressive
            current_speed = self.speed * 2 if self.is_aggressive else self.speed
            self.vel_x = self.direction * current_speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(1, 3)
                self.vel_x = 0
                
            if self.is_on_ground:
                check_x = self.rect.centerx + self.direction * BLOCK_SIZE
                check_y = self.rect.bottom + 1
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                if (0 <= check_row < GRID_HEIGHT and 
                    0 <= check_col < len(WORLD_MAP[0]) and 
                    WORLD_MAP[check_row][check_col] == 0):
                    self.direction *= -1
                    self.move_timer = 0
                    self.is_moving = False
                    self.vel_x = 0
        else:
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(2, 5)
                self.direction = random.choice([-1, 1])
    
    def attack(self, player):
        """Only attacks if aggressive."""
        if not self.is_aggressive:
            return
            
        if self.attack_timer <= 0:
            # Deal damage (bears hit hard)
            damage = 6  # 3 hearts
            player.take_damage(damage, attacker=self)
            self.attack_timer = self.attack_cooldown
    
    def update(self, WORLD_MAP, player, MOBS):
        # Decrease attack cooldown
        if self.attack_timer > 0:
            self.attack_timer -= 1
        
        # If aggressive, chase the player
        if self.is_aggressive:
            if player.rect.centerx < self.rect.centerx:
                self.direction = -1
            else:
                self.direction = 1
            self.is_moving = True
        
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
    
    def take_damage(self, damage, all_mobs=None):
        """When hit, become aggressive."""
        super().take_damage(damage, all_mobs)
        if self.health > 0:
            self.is_aggressive = True
            self.aggro_timer = 0  # Reset aggro timer
        
    def die(self, all_mobs=None):
        """Drops leather when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 14, random.randint(0, 2)))  # Leather
        self.kill()

class Lion(Mob):
    """A neutral savannah mob that charges when provoked or player gets too close."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 1.6, BLOCK_SIZE * 1.4, (210, 180, 140))
        self.health = 40
        self.max_health = 40
        self.speed = 1.8
        self.attack_damage = 6  # 3 hearts
        self.drop_id = 14  # Leather
        
        # Neutral AI state
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(2, 5)
        self.stop_duration = FPS * random.uniform(2, 4)
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Aggression state (attacks when hit or player within 2 blocks)
        self.is_aggressive = False
        self.aggro_timer = 0
        self.aggro_duration = FPS * 20  # Stay aggressive for 20 seconds
        self.attack_cooldown = FPS * 1.2
        self.attack_timer = 0
        
        # Charge mechanics
        self.is_charging = False
        self.charge_speed = 4.5
        self.jump_cooldown = FPS * 3
        self.jump_timer = 0
        
        # Draw lion
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 1.6)
        h = int(BLOCK_SIZE * 1.4)
        
        body_color = (210, 180, 140)  # Tan
        mane_color = (160, 120, 80)   # Dark brown mane
        
        # Legs
        pygame.draw.rect(self.image, body_color, (8, h - 20, 6, 20))  # Front left
        pygame.draw.rect(self.image, body_color, (w - 14, h - 20, 6, 20))  # Front right
        pygame.draw.rect(self.image, body_color, (18, h - 20, 6, 20))  # Back left
        pygame.draw.rect(self.image, body_color, (w - 24, h - 20, 6, 20))  # Back right
        
        # Body
        pygame.draw.rect(self.image, body_color, (6, h - 32, w - 12, 16))
        
        # Head with mane
        pygame.draw.circle(self.image, mane_color, (w - 12, h - 36), 12)  # Mane (larger circle)
        pygame.draw.rect(self.image, body_color, (w - 20, h - 42, 14, 12))  # Face
        
        # Ears
        pygame.draw.rect(self.image, body_color, (w - 22, h - 48, 5, 5))
        pygame.draw.rect(self.image, body_color, (w - 10, h - 48, 5, 5))
        
        # Eyes (fierce)
        pygame.draw.rect(self.image, (0, 0, 0), (w - 18, h - 40, 3, 3))
        pygame.draw.rect(self.image, (0, 0, 0), (w - 10, h - 40, 3, 3))
        
        # Tail
        pygame.draw.rect(self.image, body_color, (4, h - 28, 3, 14))
        pygame.draw.circle(self.image, mane_color, (5, h - 16), 4)  # Tail tuft
    
    def ai_move(self):
        """Wanders peacefully unless aggressive."""
        self.move_timer += 1
        self.jump_timer = max(0, self.jump_timer - 1)
        
        # Update aggro timer
        if self.is_aggressive:
            self.aggro_timer += 1
            if self.aggro_timer >= self.aggro_duration:
                self.is_aggressive = False
                self.aggro_timer = 0
                self.is_charging = False
        
        if self.is_moving:
            # Move faster when aggressive/charging
            if self.is_charging:
                current_speed = self.charge_speed
            elif self.is_aggressive:
                current_speed = self.speed * 1.5
            else:
                current_speed = self.speed
            
            self.vel_x = self.direction * current_speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(1, 3)
                self.vel_x = 0
                self.is_charging = False
                
            if self.is_on_ground:
                check_x = self.rect.centerx + self.direction * BLOCK_SIZE
                check_y = self.rect.bottom + 1
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                if (0 <= check_row < GRID_HEIGHT and 
                    0 <= check_col < len(WORLD_MAP[0]) and 
                    WORLD_MAP[check_row][check_col] == 0):
                    self.direction *= -1
                    self.move_timer = 0
                    self.is_moving = False
                    self.vel_x = 0
                    self.is_charging = False
        else:
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(2, 5)
                self.direction = random.choice([-1, 1])
    
    def attack(self, player):
        """Attacks with strong knockback."""
        if not self.is_aggressive:
            return
            
        if self.attack_timer <= 0:
            player.take_damage(self.attack_damage, attacker=self)
            
            # Strong knockback
            dx = player.rect.centerx - self.rect.centerx
            distance = max(abs(dx), 1)
            knockback_strength = 12  # Extra strong
            player.vel_x += (dx / distance) * knockback_strength
            
            self.attack_timer = self.attack_cooldown
    
    def update(self, WORLD_MAP, player, MOBS):
        # Decrease attack cooldown
        if self.attack_timer > 0:
            self.attack_timer -= 1
        
        # Check if player is within 2 blocks (becomes aggressive)
        dx = abs(player.rect.centerx - self.rect.centerx)
        if dx < BLOCK_SIZE * 2 and not self.is_aggressive:
            self.is_aggressive = True
            self.aggro_timer = 0
            self.is_charging = True
        
        # If aggressive, chase the player
        if self.is_aggressive:
            if player.rect.centerx < self.rect.centerx:
                self.direction = -1
            else:
                self.direction = 1
            self.is_moving = True
            
            # Can jump when chasing and on ground
            if self.is_on_ground and self.jump_timer == 0 and random.random() < 0.02:
                self.vel_y = -12  # Jump
                self.jump_timer = self.jump_cooldown
        
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
    
    def take_damage(self, damage, all_mobs=None):
        """When hit, become aggressive."""
        super().take_damage(damage, all_mobs)
        if self.health > 0:
            self.is_aggressive = True
            self.aggro_timer = 0
            self.is_charging = True

class Rhino(Mob):
    """A neutral savannah mob that charges when provoked."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 2, BLOCK_SIZE * 1.6, (120, 120, 120))
        self.health = 40
        self.max_health = 40
        self.speed = 1.2
        self.attack_damage = 8  # 4 hearts
        self.drop_id = 14  # Leather
        
        # Neutral AI state
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(2, 5)
        self.stop_duration = FPS * random.uniform(3, 6)
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Aggression state
        self.is_aggressive = False
        self.aggro_timer = 0
        self.aggro_duration = FPS * 25
        self.attack_cooldown = FPS * 2
        self.attack_timer = 0
        
        # Charge mechanics
        self.is_charging = False
        self.charge_speed = 5
        
        # Draw rhino
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 2)
        h = int(BLOCK_SIZE * 1.6)
        
        body_color = (120, 120, 120)  # Gray
        dark_color = (80, 80, 80)
        
        # Legs (thick)
        pygame.draw.rect(self.image, dark_color, (12, h - 24, 10, 24))  # Front left
        pygame.draw.rect(self.image, dark_color, (w - 22, h - 24, 10, 24))  # Front right
        pygame.draw.rect(self.image, dark_color, (28, h - 24, 10, 24))  # Back left
        pygame.draw.rect(self.image, dark_color, (w - 38, h - 24, 10, 24))  # Back right
        
        # Body (large, bulky)
        pygame.draw.rect(self.image, body_color, (10, h - 40, w - 20, 20))
        
        # Head (large)
        pygame.draw.rect(self.image, body_color, (w - 30, h - 50, 26, 18))
        
        # Horn (large, prominent)
        horn_color = (200, 200, 180)
        pygame.draw.polygon(self.image, horn_color, [(w - 14, h - 52), (w - 10, h - 62), (w - 6, h - 52)])
        
        # Ears
        pygame.draw.rect(self.image, body_color, (w - 28, h - 54, 6, 6))
        pygame.draw.rect(self.image, body_color, (w - 10, h - 54, 6, 6))
        
        # Eyes
        pygame.draw.rect(self.image, (0, 0, 0), (w - 24, h - 48, 3, 3))
        pygame.draw.rect(self.image, (0, 0, 0), (w - 12, h - 48, 3, 3))
        
        # Tail
        pygame.draw.rect(self.image, dark_color, (6, h - 36, 4, 12))
    
    def ai_move(self):
        """Wanders peacefully unless aggressive."""
        self.move_timer += 1
        
        # Update aggro timer
        if self.is_aggressive:
            self.aggro_timer += 1
            if self.aggro_timer >= self.aggro_duration:
                self.is_aggressive = False
                self.aggro_timer = 0
                self.is_charging = False
        
        if self.is_moving:
            # Move faster when charging
            if self.is_charging:
                current_speed = self.charge_speed
            elif self.is_aggressive:
                current_speed = self.speed * 1.3
            else:
                current_speed = self.speed
            
            self.vel_x = self.direction * current_speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(2, 5)
                self.vel_x = 0
                self.is_charging = False
                
            if self.is_on_ground:
                check_x = self.rect.centerx + self.direction * BLOCK_SIZE
                check_y = self.rect.bottom + 1
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                if (0 <= check_row < GRID_HEIGHT and 
                    0 <= check_col < len(WORLD_MAP[0]) and 
                    WORLD_MAP[check_row][check_col] == 0):
                    self.direction *= -1
                    self.move_timer = 0
                    self.is_moving = False
                    self.vel_x = 0
                    self.is_charging = False
        else:
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(2, 5)
                self.direction = random.choice([-1, 1])
    
    def attack(self, player):
        """Attacks with massive knockback."""
        if not self.is_aggressive:
            return
            
        if self.attack_timer <= 0:
            player.take_damage(self.attack_damage, attacker=self)
            
            # Massive knockback
            dx = player.rect.centerx - self.rect.centerx
            distance = max(abs(dx), 1)
            knockback_strength = 15  # Very strong
            player.vel_x += (dx / distance) * knockback_strength
            
            self.attack_timer = self.attack_cooldown
    
    def update(self, WORLD_MAP, player, MOBS):
        # Decrease attack cooldown
        if self.attack_timer > 0:
            self.attack_timer -= 1
        
        # If aggressive, charge at player
        if self.is_aggressive:
            if player.rect.centerx < self.rect.centerx:
                self.direction = -1
            else:
                self.direction = 1
            self.is_moving = True
            self.is_charging = True
        
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
    
    def take_damage(self, damage, all_mobs=None):
        """When hit, become aggressive and charge."""
        super().take_damage(damage, all_mobs)
        if self.health > 0:
            self.is_aggressive = True
            self.aggro_timer = 0
            self.is_charging = True

class Ostrich(Mob):
    """A rideable savannah mob, similar to horse/camel."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 1.4, BLOCK_SIZE * 2.2, (220, 200, 180))
        self.health = 18
        self.max_health = 18
        self.speed = 3.5  # Fastest rideable mob
        self.drop_id = 14  # Leather
        
        # Riding system
        self.rider = None
        self.mount_cooldown = 0
        
        # AI state
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(1, 3)
        self.stop_duration = FPS * random.uniform(1, 2)
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Draw ostrich
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 1.4)
        h = int(BLOCK_SIZE * 2.2)
        
        body_color = (220, 200, 180)  # Tan/beige
        dark_color = (180, 160, 140)
        
        # Legs (very long and thin)
        pygame.draw.rect(self.image, dark_color, (w // 2 - 10, h - 45, 4, 45))  # Left leg
        pygame.draw.rect(self.image, dark_color, (w // 2 + 6, h - 45, 4, 45))   # Right leg
        
        # Body (small, round)
        pygame.draw.ellipse(self.image, body_color, (w // 2 - 14, h - 60, 28, 18))
        
        # Neck (very long, thin)
        pygame.draw.rect(self.image, body_color, (w // 2 + 8, h - 100, 6, 42))
        
        # Head (small)
        pygame.draw.rect(self.image, body_color, (w // 2 + 6, h - 108, 10, 10))
        
        # Beak (orange/yellow)
        pygame.draw.polygon(self.image, (255, 200, 0), 
                          [(w // 2 + 16, h - 104), (w // 2 + 22, h - 102), (w // 2 + 16, h - 100)])
        
        # Eye
        pygame.draw.circle(self.image, (0, 0, 0), (w // 2 + 12, h - 105), 2)
        
        # Tail feathers (fluffy)
        feather_color = (255, 240, 220)
        for i in range(3):
            pygame.draw.rect(self.image, feather_color, (w // 2 - 16 - i * 2, h - 56, 3, 8))
        
        # Wings (small)
        pygame.draw.rect(self.image, dark_color, (w // 2 - 12, h - 58, 8, 12))
        pygame.draw.rect(self.image, dark_color, (w // 2 + 4, h - 58, 8, 12))
    
    def ai_move(self):
        """Wandering AI when not being ridden."""
        if self.rider:
            return  # Don't move autonomously when being ridden
        
        self.move_timer += 1
        
        if self.is_moving:
            self.vel_x = self.direction * self.speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(1, 2)
                self.vel_x = 0
        else:
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(1, 3)
                self.direction = random.choice([-1, 1])
    
    def mount(self, player):
        """Player mounts the ostrich."""
        if self.mount_cooldown == 0 and self.rider is None:
            self.rider = player
            player.is_riding = True
            player.mount = self
            self.mount_cooldown = 30
            print(f"🦢 Mounted ostrich!")
            return True
        return False
    
    def dismount(self):
        """Player dismounts the ostrich."""
        if self.rider:
            self.rider.is_riding = False
            self.rider.mount = None
            self.rider = None
            print("🦢 Dismounted ostrich!")
    
    def update(self, WORLD_MAP, player, MOBS):
        # Decrease mount cooldown
        if self.mount_cooldown > 0:
            self.mount_cooldown -= 1
        
        # If being ridden, match player position
        if self.rider:
            self.rect.centerx = self.rider.rect.centerx
            self.rect.bottom = self.rider.rect.bottom
            self.vel_x = self.rider.vel_x
            self.vel_y = self.rider.vel_y
        else:
            self.ai_move()
        
        super().update(WORLD_MAP, player, MOBS)

class Elephant(Mob):
    """A massive passive savannah mob, 7 blocks wide and tall."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 7, BLOCK_SIZE * 7, (160, 160, 160))
        self.health = 100  # Very tanky
        self.max_health = 100
        self.speed = 0.8  # Slow
        self.drop_id = 14  # Leather (lots)
        
        # AI state (passive, just wanders)
        self.move_timer = 0
        self.move_duration = FPS * random.uniform(3, 7)
        self.stop_duration = FPS * random.uniform(4, 8)
        self.is_moving = True
        self.direction = random.choice([-1, 1])
        
        # Draw elephant (massive)
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = BLOCK_SIZE * 7
        h = BLOCK_SIZE * 7
        
        body_color = (160, 160, 160)  # Gray
        dark_color = (120, 120, 120)
        
        # Legs (4 massive legs)
        leg_width = 28
        leg_height = h // 2
        pygame.draw.rect(self.image, dark_color, (20, h - leg_height, leg_width, leg_height))  # Front left
        pygame.draw.rect(self.image, dark_color, (w - 48, h - leg_height, leg_width, leg_height))  # Front right
        pygame.draw.rect(self.image, dark_color, (60, h - leg_height, leg_width, leg_height))  # Back left
        pygame.draw.rect(self.image, dark_color, (w - 88, h - leg_height, leg_width, leg_height))  # Back right
        
        # Body (massive, blocky rectangular body)
        body_height = h // 2 + 20
        pygame.draw.rect(self.image, body_color, (16, h - body_height - 40, w - 32, body_height))
        
        # Head (large, blocky at front)
        head_size = 80
        pygame.draw.rect(self.image, body_color, (w - head_size - 10, h - 140, head_size, 60))
        
        # Trunk (long, segmented rectangles going down)
        trunk_segments = 6
        trunk_y_start = h - 80
        for i in range(trunk_segments):
            trunk_x = w - 45
            trunk_y = trunk_y_start + i * 12
            trunk_width = 12
            pygame.draw.rect(self.image, dark_color, (trunk_x, trunk_y, trunk_width, 10))
        
        # Ears (huge, blocky)
        pygame.draw.rect(self.image, body_color, (w - 120, h - 160, 50, 70))  # Left ear
        pygame.draw.rect(self.image, body_color, (w - 30, h - 160, 50, 70))   # Right ear
        
        # Tusks (white, rectangular)
        tusk_color = (255, 255, 240)
        pygame.draw.rect(self.image, tusk_color, (w - 70, h - 90, 8, 25))  # Left tusk
        pygame.draw.rect(self.image, tusk_color, (w - 20, h - 90, 8, 25))  # Right tusk
        
        # Eyes (small relative to size)
        pygame.draw.rect(self.image, (0, 0, 0), (w - 68, h - 128, 6, 6))
        pygame.draw.rect(self.image, (0, 0, 0), (w - 28, h - 128, 6, 6))
        
        # Tail (thin, with blocky tuft at end)
        pygame.draw.rect(self.image, dark_color, (14, h - 160, 6, 50))
        pygame.draw.rect(self.image, dark_color, (10, h - 115, 14, 8))  # Tail tuft (rectangular)
    
    def ai_move(self):
        """Slow, peaceful wandering."""
        self.move_timer += 1
        
        if self.is_moving:
            self.vel_x = self.direction * self.speed
            
            if self.move_timer >= self.move_duration:
                self.is_moving = False
                self.move_timer = 0
                self.stop_duration = FPS * random.uniform(4, 8)
                self.vel_x = 0
                
            if self.is_on_ground:
                check_x = self.rect.centerx + self.direction * BLOCK_SIZE
                check_y = self.rect.bottom + 1
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                if (0 <= check_row < GRID_HEIGHT and 
                    0 <= check_col < len(WORLD_MAP[0]) and 
                    WORLD_MAP[check_row][check_col] == 0):
                    self.direction *= -1
                    self.move_timer = 0
                    self.is_moving = False
                    self.vel_x = 0
        else:
            if self.move_timer >= self.stop_duration:
                self.is_moving = True
                self.move_timer = 0
                self.move_duration = FPS * random.uniform(3, 7)
                self.direction = random.choice([-1, 1])
    
    def update(self, WORLD_MAP, player, MOBS):
        self.ai_move()
        super().update(WORLD_MAP, player, MOBS)
    
    def die(self, all_mobs=None):
        """Drops lots of leather when killed."""
        if 'DROPPED_ITEMS' in globals():
            DROPPED_ITEMS.add(DroppedItem(self.rect.centerx, self.rect.bottom - 10, 14, random.randint(4, 8)))  # Lots of leather
        self.kill()

class Villager(pygame.sprite.Sprite):
    def __init__(self, x, y, villager_type="farmer"):
        super().__init__()
        # Villagers are slightly taller than the player (1.5 blocks)
        self.image = pygame.Surface([BLOCK_SIZE, BLOCK_SIZE * 1.5])
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        self.villager_type = villager_type  # "farmer", "librarian", "nitwit", or "smoker"
        
        # Skin Color & Features
        skin_color = (250, 220, 180)
        
        # Different robe colors based on type
        if villager_type == "farmer":
            robe_color = (139, 69, 19)  # Brown for farmer
        elif villager_type == "librarian":
            robe_color = (139, 69, 19)  # Brown for librarian
        elif villager_type == "smoker":
            robe_color = (80, 80, 80)  # Gray for smoker
        elif villager_type == "nitwit":
            robe_color = (50, 150, 50)  # Green for nitwit
        else:
            robe_color = (139, 69, 19)  # Brown for default
        
        # Body (Robe)
        pygame.draw.rect(self.image, robe_color, (5, BLOCK_SIZE * 0.5, 30, BLOCK_SIZE))
        
        # Arms (hidden in robe for simplicity)
        
        # Head (Oversized, balding)
        pygame.draw.rect(self.image, skin_color, (10, 0, 20, 20)) 
        
        # Nose (SMALLER - The defining feature!) - Dark brown
        nose_color = (101, 67, 33)  # Dark brown
        pygame.draw.rect(self.image, nose_color, (18, 12, 4, 6))  # Changed from (18, 10, 4, 10)
        
        # Eyes
        pygame.draw.circle(self.image, (0, 0, 0), (16, 10), 2)
        pygame.draw.circle(self.image, (0, 0, 0), (24, 10), 2)
        
        # Unibrow/Forehead
        pygame.draw.rect(self.image, (60, 40, 20), (12, 5, 16, 3))
        
        # Hat for farmer
        if villager_type == "farmer":
            hat_color = (160, 120, 80)  # Straw hat color
            pygame.draw.rect(self.image, hat_color, (8, -2, 24, 4))  # Brim
            pygame.draw.rect(self.image, hat_color, (12, -6, 16, 4))  # Top
        
        # Hat and monocle for librarian
        if villager_type == "librarian":
            hat_color = (60, 40, 20)  # Dark brown hat
            pygame.draw.rect(self.image, hat_color, (10, -4, 20, 6))  # Top hat
            # Monocle on right eye
            pygame.draw.circle(self.image, (200, 200, 200), (24, 10), 4, 1)  # Glass circle
        
        # Bandanna for smoker
        if villager_type == "smoker":
            bandanna_color = (200, 50, 50)  # Red bandanna
            pygame.draw.rect(self.image, bandanna_color, (12, 14, 16, 8))  # Over nose/mouth
        
        # Apron for smoker
        if villager_type == "smoker":
            apron_color = (60, 60, 60)  # Dark gray apron
            pygame.draw.rect(self.image, apron_color, (8, BLOCK_SIZE * 0.7, 24, BLOCK_SIZE * 0.5))
            # Small furnace icon on apron
            pygame.draw.rect(self.image, (90, 90, 90), (14, BLOCK_SIZE * 0.8, 12, 10))
        
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 1.5 # Slower than the player
        self.gravity = 0.5
        self.health = 10
        self.max_health = 10
        self.is_passive = True
        self.is_village_mob = True  # Prevent despawning
        self.wandering_timer = random.randint(30, 120)
        self.on_ground = False
        
        # Trading system
        self.has_trade = True
        self.trade_cooldown = 0  # Frames until can trade again
        self.trade_cooldown_max = 300  # 5 seconds at 60 FPS

    def take_damage(self, amount, all_mobs=None):
        """Handle taking damage."""
        self.health -= amount
        if self.health <= 0:
            self.kill()  # Remove from all sprite groups
            
    def can_trade(self):
        """Check if the villager can currently trade."""
        return self.has_trade and self.trade_cooldown == 0
    
    def attempt_trade(self, player):
        """
        Attempt to trade with the player.
        Farmer: 1 Emerald for 3 Wheat OR 3 Carrots
        Librarian: 1 Emerald for 1 Book OR 1 Emerald for 1 Glass
        Smoker: 1 Emerald for 1 Raw Meat OR 1 Raw Meat for 1 Emerald OR Raw Meat for Cooked Meat
        Nitwit: No trades
        Returns: True if trade successful, False otherwise
        """
        if not self.can_trade():
            return False
        
        # Nitwits don't trade
        if self.villager_type == "nitwit":
            print("🤷 Nitwit villager doesn't trade!")
            return False
        
        EMERALD_ID = 23
        
        if self.villager_type == "farmer":
            # Farmer has two trades - randomly choose one
            # Trade 1: 1 Emerald → 3 Wheat (ID 93)
            # Trade 2: 1 Emerald → 3 Carrots (ID 94)
            WHEAT_ID = 93
            CARROT_ID = 94
            emerald_count = 0
            for item_id, count in player.hotbar_slots:
                if item_id == EMERALD_ID:
                    emerald_count += count
            for item_id, count in player.inventory:
                if item_id == EMERALD_ID:
                    emerald_count += count
            
            if emerald_count >= 1:
                # Consume 1 emerald
                player.consume_item(EMERALD_ID, 1)
                # 50/50 chance for wheat or carrots
                if random.random() < 0.5:
                    player.add_to_inventory(WHEAT_ID, 3)
                    print("✅ Trade successful! 1 Emerald → 3 Wheat")
                else:
                    player.add_to_inventory(CARROT_ID, 3)
                    print("✅ Trade successful! 1 Emerald → 3 Carrots")
                self.trade_cooldown = self.trade_cooldown_max
                return True
            else:
                print(f"❌ Trade failed! Need 1 Emerald, you have {emerald_count}")
                return False
                
        elif self.villager_type == "librarian":
            # Librarian has two trades
            # Trade 1: 1 Emerald → 1 Book (ID 97)
            # Trade 2: 1 Emerald → 1 Glass (ID 86)
            BOOK_ID = 97
            GLASS_ID = 86
            emerald_count = 0
            for item_id, count in player.hotbar_slots:
                if item_id == EMERALD_ID:
                    emerald_count += count
            for item_id, count in player.inventory:
                if item_id == EMERALD_ID:
                    emerald_count += count
            
            if emerald_count >= 1:
                # Consume 1 emerald
                player.consume_item(EMERALD_ID, 1)
                # 50/50 chance for book or glass
                if random.random() < 0.5:
                    player.add_to_inventory(BOOK_ID, 1)
                    print("✅ Trade successful! 1 Emerald → 1 Book")
                else:
                    player.add_to_inventory(GLASS_ID, 1)
                    print("✅ Trade successful! 1 Emerald → 1 Glass")
                self.trade_cooldown = self.trade_cooldown_max
                return True
            else:
                print("❌ Trade failed! Need 1 Emerald")
                return False
        
        elif self.villager_type == "smoker":
            # Smoker has multiple meat trades
            # Trade 1: 1 Emerald → 1 Random Raw Meat (beef/mutton/chicken/pork)
            # Trade 2: 1 Raw Meat → 1 Emerald
            BEEF_ID = 51
            MUTTON_ID = 50
            CHICKEN_ID = 81
            PORK_ID = 82
            
            # Count player's items
            emerald_count = 0
            meat_counts = {BEEF_ID: 0, MUTTON_ID: 0, CHICKEN_ID: 0, PORK_ID: 0}
            
            for item_id, count in player.hotbar_slots:
                if item_id == EMERALD_ID:
                    emerald_count += count
                elif item_id in meat_counts:
                    meat_counts[item_id] += count
            for item_id, count in player.inventory:
                if item_id == EMERALD_ID:
                    emerald_count += count
                elif item_id in meat_counts:
                    meat_counts[item_id] += count
            
            total_meat = sum(meat_counts.values())
            
            # Prioritize meat → emerald trade if player has meat
            if total_meat > 0:
                # Find first available meat type
                for meat_id in [BEEF_ID, MUTTON_ID, CHICKEN_ID, PORK_ID]:
                    if meat_counts[meat_id] > 0:
                        player.consume_item(meat_id, 1)
                        player.add_to_inventory(EMERALD_ID, 1)
                        print(f"✅ Trade successful! 1 {BLOCK_TYPES[meat_id]['name']} → 1 Emerald")
                        self.trade_cooldown = self.trade_cooldown_max
                        return True
            # Otherwise emerald → meat trade
            elif emerald_count >= 1:
                player.consume_item(EMERALD_ID, 1)
                # Random meat type
                meat_id = random.choice([BEEF_ID, MUTTON_ID, CHICKEN_ID, PORK_ID])
                player.add_to_inventory(meat_id, 1)
                print(f"✅ Trade successful! 1 Emerald → 1 {BLOCK_TYPES[meat_id]['name']}")
                self.trade_cooldown = self.trade_cooldown_max
                return True
            else:
                print("❌ Trade failed! Need 1 Emerald or 1 Raw Meat")
                return False
        
        return False
        

    def collide_x(self):
        """Handle horizontal collisions with blocks"""
        global WORLD_MAP
        
        # Calculate which grid cells the villager overlaps
        left_col = self.rect.left // BLOCK_SIZE
        right_col = self.rect.right // BLOCK_SIZE
        top_row = self.rect.top // BLOCK_SIZE
        bottom_row = self.rect.bottom // BLOCK_SIZE
        
        # Check collisions with solid blocks
        for row in range(max(0, top_row), min(GRID_HEIGHT, bottom_row + 1)):
            for col in range(max(0, left_col), min(GRID_WIDTH, right_col + 1)):
                block_id = WORLD_MAP[row][col]
                # Check if block is solid (not air or water)
                if block_id not in [AIR_ID, WATER_ID]:
                    block_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    if self.rect.colliderect(block_rect):
                        # Push villager out of the block
                        if self.vel_x > 0:  # Moving right
                            self.rect.right = block_rect.left
                        elif self.vel_x < 0:  # Moving left
                            self.rect.left = block_rect.right
                        self.vel_x = 0
                        return
        
    def collide_y(self):
        """Handle vertical collisions with blocks"""
        global WORLD_MAP
        
        # Calculate which grid cells the villager overlaps
        left_col = self.rect.left // BLOCK_SIZE
        right_col = self.rect.right // BLOCK_SIZE
        top_row = self.rect.top // BLOCK_SIZE
        bottom_row = self.rect.bottom // BLOCK_SIZE
        
        self.on_ground = False
        
        # Check collisions with solid blocks
        for row in range(max(0, top_row), min(GRID_HEIGHT, bottom_row + 1)):
            for col in range(max(0, left_col), min(GRID_WIDTH, right_col + 1)):
                block_id = WORLD_MAP[row][col]
                # Check if block is solid (not air or water)
                if block_id not in [AIR_ID, WATER_ID]:
                    block_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    if self.rect.colliderect(block_rect):
                        # Push villager out of the block
                        if self.vel_y > 0:  # Falling
                            self.rect.bottom = block_rect.top
                            self.vel_y = 0
                            self.on_ground = True
                        elif self.vel_y < 0:  # Jumping/moving up
                            self.rect.top = block_rect.bottom
                            self.vel_y = 0
                        return

    def update(self, WORLD_MAP, player, MOBS):
        # Update trade cooldown
        if self.trade_cooldown > 0:
            self.trade_cooldown -= 1
        
        # Basic wandering behavior
        self.wandering_timer -= 1
        if self.wandering_timer <= 0:
            direction = random.choice([-1, 0, 1])
            self.vel_x = direction * self.speed
            self.wandering_timer = random.randint(60, 200)

        # Check for doors in front of villager and open them
        if self.vel_x != 0:
            # Calculate position ahead of villager
            check_col = (self.rect.centerx + (BLOCK_SIZE if self.vel_x > 0 else -BLOCK_SIZE)) // BLOCK_SIZE
            check_row = self.rect.centery // BLOCK_SIZE
            
            # Check if there's a door ahead
            if 0 <= check_col < len(WORLD_MAP[0]) and 0 <= check_row < GRID_HEIGHT:
                if WORLD_MAP[check_row][check_col] == 91:  # Door block
                    # Open the door (set to air)
                    WORLD_MAP[check_row][check_col] = 0
                    # Also open the other half
                    if check_row - 1 >= 0 and WORLD_MAP[check_row - 1][check_col] == 91:
                        WORLD_MAP[check_row - 1][check_col] = 0
                    elif check_row + 1 < GRID_HEIGHT and WORLD_MAP[check_row + 1][check_col] == 91:
                        WORLD_MAP[check_row + 1][check_col] = 0

        # Apply gravity (simple non-player version)
        self.vel_y += self.gravity
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.x += self.vel_x
        self.collide_x()
        
        self.rect.y += self.vel_y
        self.collide_y()

import math # Make sure math is imported at the top of your file

class Witch(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 2, (50, 20, 50)) 
        self.health = 26
        self.max_health = 26
        self.attack_cooldown = 0
        self.attack_range = BLOCK_SIZE * 5
        self.base_damage = 2
        
        # Potion system - witch holds one potion
        self.held_potion = random.choice([131, 132, 133])  # Healing, Splash Healing, or Splash Poison
        self.drinking_timer = 0  # Frames spent drinking
        self.drink_duration = FPS * 2  # 2 seconds to drink
        self.heal_threshold = 0.5  # Drink healing potion when below 50% health
        
        # Blocky witch design
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = BLOCK_SIZE
        h = BLOCK_SIZE * 2
        
        # Legs
        pygame.draw.rect(self.image, (40, 10, 40), (10, h - 24, 10, 24))
        pygame.draw.rect(self.image, (40, 10, 40), (w - 20, h - 24, 10, 24))
        
        # Robe (purple/dark)
        pygame.draw.rect(self.image, (60, 30, 80), (5, h // 2, w - 10, h // 2 - 24))
        
        # Body/torso
        pygame.draw.rect(self.image, (50, 25, 60), (8, h // 3, w - 16, h // 4))
        
        # Head (green-tinted skin)
        head_color = (100, 140, 100)
        pygame.draw.rect(self.image, head_color, (10, h // 6, w - 20, h // 6))
        
        # Witch hat (iconic pointy hat)
        hat_color = (40, 10, 50)
        # Brim
        pygame.draw.rect(self.image, hat_color, (5, h // 6, w - 10, 4))
        # Cone (stacked rectangles getting smaller)
        pygame.draw.rect(self.image, hat_color, (12, h // 8, w - 24, h // 12))
        pygame.draw.rect(self.image, hat_color, (16, h // 16, w - 32, h // 12))
        pygame.draw.rect(self.image, hat_color, (18, 0, w - 36, h // 16))
        
        # Long nose
        pygame.draw.rect(self.image, (90, 120, 90), (w - 8, h // 6 + 6, 6, 8))
        
        # Eyes (glowing)
        pygame.draw.rect(self.image, (150, 0, 200), (14, h // 6 + 4, 3, 3))
        pygame.draw.rect(self.image, (150, 0, 200), (w - 17, h // 6 + 4, 3, 3))
        
        # Wart on nose
        pygame.draw.rect(self.image, (80, 100, 80), (w - 6, h // 6 + 8, 2, 2))
        
    def update(self, world_map, player, all_mobs):
        # Calls the base Mob update for physics and gravity
        super().update(world_map, player)
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        distance = math.sqrt(
            (self.rect.centerx - player.rect.centerx) ** 2 +
            (self.rect.centery - player.rect.centery) ** 2
        )
        
        # Only use potions when player is in range
        if distance < self.attack_range:
            # Throw splash healing potion at self if low health
            if self.health < self.max_health * self.heal_threshold and self.attack_cooldown <= 0:
                if self.held_potion in [131, 132]:  # Has a splash healing potion
                    if 'SPLASH_POTIONS' in globals():
                        # Throw splash healing at own feet
                        SPLASH_POTIONS.add(SplashPotion(
                            self.rect.centerx,
                            self.rect.centery,
                            0,  # No horizontal direction, just drop
                            132  # Splash Healing Potion
                        ))
                        print(f"🧙 Witch threw Splash Healing Potion at self!")
                        self.held_potion = random.choice([131, 132, 133])  # Get new potion
                        self.attack_cooldown = 180
                return
            
            # Attack player with splash poison
            if self.attack_cooldown <= 0:
                self.attack_player(player)
                self.attack_cooldown = 180 # 3-second cooldown (assuming 60 FPS)

    def attack_player(self, player):
        """Throws splash poison potion at player."""
        # Throw splash poison potion
        direction = 1 if player.rect.centerx > self.rect.centerx else -1
        
        if 'SPLASH_POTIONS' in globals():
            SPLASH_POTIONS.add(SplashPotion(
                self.rect.centerx,
                self.rect.centery,
                direction,
                133  # Splash Poison Potion
            ))
            print(f"🧙 Witch threw Splash Poison Potion!")
        # You need to implement player.apply_dot_effect() in your Player class!
        
        # Example of the intended DoT function call:
        # player.apply_dot_effect(duration_frames=600, damage_per_tick=1, tick_interval=30)
        
        print("☠️ Witch applies a Poison/Wither DoT effect (Placeholder).")

        # 3. Add knockback to push the player away
        if player.rect.centerx < self.rect.centerx:
             player.vel_x = -4
        else:
             player.vel_x = 4
    
    def die(self, all_mobs=None):
        """Drops currently held potion when killed."""
        if 'DROPPED_ITEMS' in globals():
            # If witch was drinking a potion, drop it
            if self.held_potion and self.drinking_timer > 0:
                DROPPED_ITEMS.add(DroppedItem(
                    self.rect.centerx,
                    self.rect.centery,
                    self.held_potion
                ))
                print(f"💀 Witch dropped {BLOCK_TYPES[self.held_potion]['name']} while drinking!")
            
            # Also drop some random witch materials (1-2 items)
            possible_drops = [
                (60, "Redstone Dust"), (61, "Glass Bottle"), (151, "Glowstone Dust"),  # Updated glowstone dust ID
                (56, "Gunpowder"), (64, "Sugar"), (10, "Stick")
            ]
            for _ in range(random.randint(1, 2)):
                drop_id, _ = random.choice(possible_drops)
                DROPPED_ITEMS.add(DroppedItem(
                    self.rect.centerx + random.randint(-10, 10),
                    self.rect.bottom - 10,
                    drop_id,
                    random.randint(1, 2)
                ))
        self.kill()

class IronGolem(Mob):
    """Iron Golem - neutral village protector that attacks hostile mobs only."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 1.2, BLOCK_SIZE * 2.5, (180, 180, 180))
        self.health = 100
        self.max_health = 100
        self.speed = 1.0
        self.attack_cooldown = 0
        self.attack_range = BLOCK_SIZE * 2
        self.detection_range = BLOCK_SIZE * 15
        self.damage = 15
        self.target = None
        self.is_village_mob = True  # Prevent despawning
        self.is_neutral = True  # Won't attack player unless provoked
        self.provoked = False  # Becomes True when player attacks
        
        # Draw iron golem
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 1.2)
        h = int(BLOCK_SIZE * 2.5)
        
        iron_color = (180, 180, 180)
        dark_iron = (120, 120, 120)
        vine_green = (50, 150, 50)
        
        # Legs (thick)
        pygame.draw.rect(self.image, dark_iron, (5, h - 30, 12, 30))
        pygame.draw.rect(self.image, dark_iron, (w - 17, h - 30, 12, 30))
        
        # Body (large rectangular torso - villager-like but bigger)
        pygame.draw.rect(self.image, iron_color, (6, h // 2 - 5, w - 12, h // 2 - 20))
        
        # Arms (very long and thick - reaching down like villager but bigger)
        pygame.draw.rect(self.image, dark_iron, (-2, h // 2, 10, h // 2 - 10))
        pygame.draw.rect(self.image, dark_iron, (w - 8, h // 2, 10, h // 2 - 10))
        
        # BIG HANDS at end of arms
        pygame.draw.rect(self.image, iron_color, (-4, h - 15, 14, 12))
        pygame.draw.rect(self.image, iron_color, (w - 10, h - 15, 14, 12))
        
        # Vines hanging from arms (multiple green strips)
        for offset in [0, 4, 8]:
            pygame.draw.rect(self.image, vine_green, (2 + offset, h // 2 + 20, 2, 25))
            pygame.draw.rect(self.image, vine_green, (w - 10 + offset, h // 2 + 20, 2, 25))
        
        # Head (rectangular, villager-like)
        pygame.draw.rect(self.image, iron_color, (10, h // 6, w - 20, h // 4))
        
        # Eyes (glowing red)
        pygame.draw.rect(self.image, (255, 0, 0), (14, h // 6 + 8, 4, 4))
        pygame.draw.rect(self.image, (255, 0, 0), (w - 18, h // 6 + 8, 4, 4))
        
        # Nose (villager-style nose)
        pygame.draw.rect(self.image, (150, 150, 150), (w // 2 - 2, h // 6 + 16, 4, 6))
    
    def update(self, world_map, player, all_mobs):
        super().update(world_map, player)
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # If provoked, attack player
        if hasattr(self, 'provoked') and self.provoked:
            dx = player.rect.centerx - self.rect.centerx
            distance = abs(dx)
            
            if distance < self.attack_range and self.attack_cooldown <= 0:
                # Attack player!
                player.take_damage(self.damage)
                self.attack_cooldown = 60  # 1 second cooldown
                print(f"🤖 Iron Golem attacks Player!")
            elif distance > 10:
                # Chase player
                if dx > 0:
                    self.vel_x = self.speed
                else:
                    self.vel_x = -self.speed
            else:
                self.vel_x = 0
            return
        
        # Find hostile mobs to attack
        if self.target is None or not self.target.alive():
            self.target = self.find_hostile_target(all_mobs)
        
        if self.target and self.target.alive():
            # Move towards target
            dx = self.target.rect.centerx - self.rect.centerx
            distance = abs(dx)
            
            if distance < self.attack_range and self.attack_cooldown <= 0:
                # Attack!
                self.target.take_damage(self.damage, all_mobs)
                self.attack_cooldown = 60  # 1 second cooldown
                print(f"🤖 Iron Golem attacks {self.target.__class__.__name__}!")
            elif distance > 10:
                # Chase
                if dx > 0:
                    self.vel_x = self.speed
                else:
                    self.vel_x = -self.speed
            else:
                self.vel_x = 0
        else:
            # Wander
            if random.random() < 0.01:
                self.vel_x = random.choice([-self.speed, 0, self.speed])
    
    def find_hostile_target(self, all_mobs):
        """Find the nearest hostile mob within detection range."""
        closest_hostile = None
        closest_distance = self.detection_range
        
        for mob in all_mobs:
            # Target zombies, skeletons, creepers, spiders, witches
            if isinstance(mob, (Zombie, Skeleton, Creeper, Spider, Witch)):
                distance = abs(mob.rect.centerx - self.rect.centerx)
                if distance < closest_distance:
                    closest_hostile = mob
                    closest_distance = distance
        
        return closest_hostile
    
    def take_damage(self, damage, all_mobs=None):
        """Take damage and become provoked if attacked by player."""
        self.provoked = True  # Now hostile to player
        super().take_damage(damage, all_mobs)
    
    def die(self, all_mobs=None):
        """Drop iron ingots when killed."""
        if 'DROPPED_ITEMS' in globals():
            # Drop 3-5 iron ingots
            for _ in range(random.randint(3, 5)):
                DROPPED_ITEMS.add(DroppedItem(
                    self.rect.centerx + random.randint(-10, 10),
                    self.rect.bottom - 10,
                    108,  # Iron Ingot
                    1
                ))
        self.kill()

# --- World Drawing ---
def update_water_flow():
    """Makes water flow and spread to adjacent blocks."""
    global WORLD_MAP
    
    # We need to track changes separately to avoid modifying while iterating
    changes = []
    
    for row in range(GRID_HEIGHT - 1):  # Don't check bottom row
        for col in range(GRID_WIDTH):
            block_type = WORLD_MAP[row][col]
            if block_type in FLUID_BLOCKS:  # If current block is any water type (regular or swamp)
                
                # 1. Water ALWAYS flows down if there's air below
                if row + 1 < GRID_HEIGHT and WORLD_MAP[row + 1][col] == 0:
                    changes.append((row + 1, col, block_type))  # Water flows down (preserve type)
                
                # 2. Water spreads horizontally (and can still flow down from those positions)
                else:
                    # Only spread horizontally if water has support below (is sitting on something)
                    # Spread left
                    if col > 0 and WORLD_MAP[row][col - 1] == 0:
                        changes.append((row, col - 1, block_type))  # Spread left (can flow down from there later)
                    
                    # Spread right
                    if col < GRID_WIDTH - 1 and WORLD_MAP[row][col + 1] == 0:
                        changes.append((row, col + 1, block_type))  # Spread right (can flow down from there later)
    
    # Apply all changes
    for row, col, block_id in changes:
        WORLD_MAP[row][col] = block_id

def update_falling_blocks():
    """Makes sand and gravel fall down and suffocate players underneath."""
    global WORLD_MAP
    
    changes = []
    FALLING_BLOCKS = [19, 26]  # Sand (19) and Gravel (26)
    
    for row in range(GRID_HEIGHT - 2, -1, -1):  # Start from bottom, go up
        for col in range(GRID_WIDTH):
            if WORLD_MAP[row][col] in FALLING_BLOCKS:
                # Check if there's air or water below
                if row + 1 < GRID_HEIGHT:
                    block_below = WORLD_MAP[row + 1][col]
                    if block_below == 0 or block_below == 5 or block_below == 31:  # Air, water, or swamp water
                        changes.append((row, col, 0))  # Remove from current position
                        changes.append((row + 1, col, WORLD_MAP[row][col]))  # Place below
    
    # Apply all changes
    for row, col, block_id in changes:
        WORLD_MAP[row][col] = block_id

def draw_world(camera_x, camera_y, player=None):
    """Draws only the visible portion of the world map to the screen."""
    # Increase render distance when sprinting
    extra_distance = 0
    if player and player.is_sprinting:
        extra_distance = BLOCK_SIZE * 10  # See 10 blocks further when sprinting
    
    start_col = max(0, (camera_x - extra_distance) // BLOCK_SIZE)
    end_col = min(GRID_WIDTH, (camera_x + SCREEN_WIDTH + extra_distance) // BLOCK_SIZE + 1)
    
    start_row = max(0, (camera_y - extra_distance) // BLOCK_SIZE)
    end_row = min(GRID_HEIGHT, (camera_y + SCREEN_HEIGHT + extra_distance) // BLOCK_SIZE + 1)
    
    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            block_id = WORLD_MAP[row][col]
            
            if block_id != 0:
                block_color = BLOCK_TYPES[block_id]["color"]
                screen_x = col * BLOCK_SIZE - camera_x
                screen_y = row * BLOCK_SIZE - camera_y
                pygame.draw.rect(screen, block_color, (screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE))
                
                # Add black spots to birch wood (ID 83)
                if block_id == 83:
                    spot_color = (0, 0, 0)
                    # Draw 3-4 small black spots on the birch wood
                    pygame.draw.rect(screen, spot_color, (screen_x + 5, screen_y + 8, 3, 4))
                    pygame.draw.rect(screen, spot_color, (screen_x + BLOCK_SIZE - 10, screen_y + 15, 4, 3))
                    pygame.draw.rect(screen, spot_color, (screen_x + 12, screen_y + BLOCK_SIZE - 12, 3, 3))

def calculate_camera_offset(player_rect):
    """Calculates the camera offset to center on the player."""
    camera_x = player_rect.centerx - SCREEN_WIDTH // 2
    camera_y = player_rect.centery - SCREEN_HEIGHT // 2
    
    camera_x = max(0, min(camera_x, GRID_WIDTH * BLOCK_SIZE - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, GRID_HEIGHT * BLOCK_SIZE - SCREEN_HEIGHT))
    
    return camera_x, camera_y

# --- Interaction Handling ---
def get_nearest_hostile_mob(player, mobs):
    """Returns the nearest hostile mob to the player, or None if none exist."""
    hostile_types = (Zombie, Skeleton, Spider, Creeper, Witch, Slime, Drowned)
    nearest_mob = None
    nearest_distance = float('inf')
    
    for mob in mobs:
        if isinstance(mob, hostile_types):
            dx = mob.rect.centerx - player.rect.centerx
            dy = mob.rect.centery - player.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_mob = mob
    
    if nearest_mob:
        return nearest_mob, nearest_distance
    return None, None

def get_nearest_meat_mob(player, mobs):
    """Returns the nearest meat-dropping mob to the player, or None if none exist."""
    meat_types = (Cow, Pig, Sheep, Chicken, Rabbit)
    nearest_mob = None
    nearest_distance = float('inf')
    
    for mob in mobs:
        if isinstance(mob, meat_types):
            dx = mob.rect.centerx - player.rect.centerx
            dy = mob.rect.centery - player.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_mob = mob
    
    if nearest_mob:
        return nearest_mob, nearest_distance
    return None, None

def get_nearest_mob(player, mobs):
    """Returns the nearest mob of any type to the player, or None if none exist."""
    nearest_mob = None
    nearest_distance = float('inf')
    
    for mob in mobs:
        dx = mob.rect.centerx - player.rect.centerx
        dy = mob.rect.centery - player.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_mob = mob
    
    if nearest_mob:
        return nearest_mob, nearest_distance
    return None, None

def handle_interaction(player, mobs, event, camera_x, camera_y, MOBS):
    """Handles mining blocks, placing blocks, attacking mobs, and trading with villagers."""
    if event.button not in [1, 3]:
        return
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    target_world_x = mouse_x + camera_x
    target_world_y = mouse_y + camera_y
    target_col = target_world_x // BLOCK_SIZE
    target_row = target_world_y // BLOCK_SIZE

    if not (0 <= target_row < GRID_HEIGHT and 0 <= target_col < GRID_WIDTH):
        return
    
    player_col = player.rect.centerx // BLOCK_SIZE
    player_row = player.rect.centery // BLOCK_SIZE
    
    if max(abs(target_col - player_col), abs(target_row - player_row)) > 4:
        return
    
    # Left Click: Mine Block OR Attack Mob
    if event.button == 1:
        # Check if clicking on a mob
        target_rect = pygame.Rect(target_world_x, target_world_y, 1, 1)
        hit_mob = None
        
        for mob in mobs:
            if mob.rect.collidepoint(target_world_x, target_world_y):
                hit_mob = mob
                break
        
        if hit_mob:
            # Attack the mob
            damage = 1  # Base damage
            attack_range_bonus = 0  # Normal attack range
            
            # Check if player is holding a tool/weapon
            held_id = player.held_block
            if held_id in BLOCK_TYPES:
                block_data = BLOCK_TYPES[held_id]
                
                # Add damage bonus from weapons
                if "damage_bonus" in block_data:
                    damage += block_data["damage_bonus"]
                
                # Check attack range for spear
                if "attack_range" in block_data:
                    attack_range_bonus = block_data["attack_range"] * BLOCK_SIZE
                
                # Apply tool durability damage
                if "durability" in block_data:
                    # Get current durability
                    slot_key = ('hotbar', player.active_slot)
                    current_durability = player.tool_durability.get(slot_key, block_data["durability"])
                    current_durability -= 1
                    
                    if current_durability <= 0:
                        # Tool broke
                        player.hotbar_slots[player.active_slot] = (0, 0)
                        player.held_block = 0
                        if slot_key in player.tool_durability:
                            del player.tool_durability[slot_key]
                        print(f"💔 {block_data['name']} broke!")
                    else:
                        player.tool_durability[slot_key] = current_durability
            
            hit_mob.take_damage(damage, mobs)
            
            # Apply knockback (not when crouching)
            if not player.is_crouching:
                # Calculate knockback direction
                knockback_strength = 2  # Reduced base knockback
                if player.is_sprinting:
                    knockback_strength = 3.5  # Reduced sprint knockback
                
                # Direction from player to mob (horizontal only)
                dx = hit_mob.rect.centerx - player.rect.centerx
                if dx > 0:
                    hit_mob.vel_x = knockback_strength
                elif dx < 0:
                    hit_mob.vel_x = -knockback_strength
        else:
            # Mine the block
            block_id = WORLD_MAP[target_row][target_col]
            
            if block_id != 0:
                block_data = BLOCK_TYPES.get(block_id, {})
                
                if block_data.get("mineable", False):
                    required_level = block_data.get("min_tool_level", 0)
                    held_id = player.held_block
                    
                    # Check if player is holding the right tool
                    tool_level = 0
                    
                    if held_id in BLOCK_TYPES:
                        tool_data = BLOCK_TYPES[held_id]
                        if "tool_level" in tool_data:
                            tool_level = tool_data["tool_level"]
                    
                    if tool_level >= required_level:
                        # Remove from light sources if it emits light
                        if BLOCK_TYPES.get(block_id, {}).get("emits_light", False):
                            LIGHT_SOURCES.discard((target_col, target_row))
                        
                        # Normal mining (instant for now, will add hold-to-mine later)
                        WORLD_MAP[target_row][target_col] = 0
                        
                        # Special case: Breaking bamboo breaks all bamboo above it
                        if block_id == 127:  # BAMBOO_ID
                            # Break all bamboo blocks above this one
                            check_row = target_row - 1
                            while check_row >= 0 and WORLD_MAP[check_row][target_col] == 127:
                                WORLD_MAP[check_row][target_col] = 0
                                # Drop item for each bamboo broken
                                if 'DROPPED_ITEMS' in globals():
                                    drop_x = target_col * BLOCK_SIZE + BLOCK_SIZE // 4
                                    drop_y = check_row * BLOCK_SIZE + BLOCK_SIZE // 4
                                    DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 127, 1))
                                check_row -= 1
                        
                        # Drop item
                        if 'DROPPED_ITEMS' in globals():
                            drop_x = target_col * BLOCK_SIZE + BLOCK_SIZE // 4
                            drop_y = target_row * BLOCK_SIZE + BLOCK_SIZE // 4
                            
                            # Handle leaf drops with saplings, sticks, and fruits
                            if block_id in [6, 84, 83, 126, 149]:  # Leaves (Oak, Birch, Spruce, Jungle, Acacia)
                                # Determine biome for fruit type
                                biome_type = BIOME_MAP[target_col] if target_col < len(BIOME_MAP) else OAK_FOREST_BIOME
                                
                                # 15% chance for sapling
                                if random.random() < 0.15:
                                    if block_id == 6:  # Oak leaves
                                        DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 139, 1))  # Oak Sapling
                                    elif block_id == 84:  # Birch leaves
                                        DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 140, 1))  # Birch Sapling
                                    elif block_id == 83:  # Spruce leaves
                                        DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 141, 1))  # Spruce Sapling
                                    elif block_id == 126:  # Jungle leaves
                                        DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 142, 1))  # Jungle Sapling
                                    elif block_id == 149:  # Acacia leaves
                                        DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 150, 1))  # Acacia Sapling
                                
                                # 15% chance for sticks
                                if random.random() < 0.15:
                                    DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 10, random.randint(1, 2)))  # 1-2 Sticks
                                
                                # 15% chance for fruit (biome-dependent, not in taiga)
                                if random.random() < 0.15 and biome_type != TAIGA_BIOME:
                                    if block_id == 6:  # Oak leaves
                                        DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 136, 1))  # Apple
                                    elif block_id == 84:  # Birch leaves
                                        DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 137, 1))  # Orange
                                    elif block_id == 126:  # Jungle leaves
                                        DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 138, 1))  # Banana
                            elif block_id == 143:  # Berry Bush
                                DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 144, random.randint(1, 3)))  # 1-3 Berries
                            elif block_id == 22:
                                DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 10, random.randint(0, 2)))
                            elif block_id == 11:
                                DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 85, 1))
                            elif block_id == 95:
                                DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 93, 1))
                            elif block_id == 96:
                                DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, 94, 1))
                            else:
                                DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, block_id, 1))
    
    # Right Click: Place Block OR Mount Camel OR Trade with Villager OR Open Door
    elif event.button == 3:
        # First check if clicking on a door to toggle it
        if 0 <= target_row < GRID_HEIGHT and 0 <= target_col < GRID_WIDTH:
            clicked_block = WORLD_MAP[target_row][target_col]
            if clicked_block == 91:  # Closed door
                # Open door (make it passable by setting solid to False, but keep the block)
                # Instead of removing the door, we'll just change collision
                # For now, swap to air but remember it's a door
                WORLD_MAP[target_row][target_col] = 0  # Open (air)
                # Mark the other half too
                if target_row - 1 >= 0 and WORLD_MAP[target_row - 1][target_col] == 91:
                    WORLD_MAP[target_row - 1][target_col] = 0
                elif target_row + 1 < GRID_HEIGHT and WORLD_MAP[target_row + 1][target_col] == 91:
                    WORLD_MAP[target_row + 1][target_col] = 0
                
                # Set a timer to auto-close the door after 3 seconds
                global OPEN_DOORS
                if 'OPEN_DOORS' not in globals():
                    OPEN_DOORS = []
                OPEN_DOORS.append({"col": target_col, "row": target_row, "timer": FPS * 3})
                return
            elif clicked_block == 0:  # Air - check if this is where a closed door should be
                # Check for door context (planks on sides, stone below)
                has_plank_left = target_col - 1 >= 0 and WORLD_MAP[target_row][target_col - 1] == 8
                has_plank_right = target_col + 1 < GRID_WIDTH and WORLD_MAP[target_row][target_col + 1] == 8
                has_stone_below = target_row + 1 < GRID_HEIGHT and WORLD_MAP[target_row + 1][target_col] == 3
                
                # If this looks like an open door position, close it
                if (has_plank_left or has_plank_right) and has_stone_below:
                    WORLD_MAP[target_row][target_col] = 91  # Close door
                    # Close the top half too
                    if target_row - 1 >= 0 and WORLD_MAP[target_row - 1][target_col] == 0:
                        WORLD_MAP[target_row - 1][target_col] = 91
                    return
        
        # Check if holding trident to throw it
        held_id = player.held_block
        if held_id == 107 and held_id in BLOCK_TYPES and BLOCK_TYPES[held_id].get("can_throw", False):
            # Throw trident toward mouse cursor
            mouse_x, mouse_y = pygame.mouse.get_pos()
            target_world_x = mouse_x + camera_x
            target_world_y = mouse_y + camera_y
            
            # Get damage from trident
            trident_damage = BLOCK_TYPES[held_id].get("damage_bonus", 9) + 3  # +3 for thrown damage bonus
            
            # Create trident projectile
            if 'TRIDENTS' in globals():
                TRIDENTS.add(Trident(
                    player.rect.centerx,
                    player.rect.centery,
                    target_world_x,
                    target_world_y,
                    trident_damage,
                    thrown_by_player=True  # Mark as thrown by player
                ))
                print(f"🔱 Threw trident with {trident_damage} damage!")
                
                # Consume trident from inventory (uses durability)
                slot_key = ('hotbar', player.active_slot)
                block_data = BLOCK_TYPES[held_id]
                current_durability = player.tool_durability.get(slot_key, block_data["durability"])
                current_durability -= 10  # Throwing uses more durability
                
                if current_durability <= 0:
                    # Trident broke
                    player.hotbar_slots[player.active_slot] = (0, 0)
                    player.held_block = 0
                    if slot_key in player.tool_durability:
                        del player.tool_durability[slot_key]
                    print(f"💔 Trident broke!")
                else:
                    player.tool_durability[slot_key] = current_durability
            return
        
        # Check if holding spear to initiate charge
        held_id = player.held_block
        if held_id in BLOCK_TYPES and BLOCK_TYPES[held_id].get("can_charge", False):
            # Start charging with spear
            player.is_charging = True
            # Charge velocity based on player's current speed direction
            charge_direction = 1 if player.vel_x >= 0 else -1
            player.charge_velocity = charge_direction * 15  # Fast charge speed
            player.charge_timer = player.max_charge_time  # Reset timer
            player.charge_hit_mobs = set()  # Reset hit tracking
            return
        
        # Check if clicking on a villager to trade
        clicked_villager = None
        
        for mob in mobs:
            if isinstance(mob, Villager) and mob.rect.collidepoint(target_world_x, target_world_y):
                clicked_villager = mob
                break
        
        if clicked_villager:
            # Open trading GUI with the villager
            player.trading_open = True
            player.trading_villager = clicked_villager
            return
        
        # Check if clicking on a camel to mount
        target_rect = pygame.Rect(target_world_x, target_world_y, 1, 1)
        clicked_camel = None
        clicked_horse = None
        clicked_ostrich = None
        
        for mob in mobs:
            if isinstance(mob, Camel) and mob.rect.collidepoint(target_world_x, target_world_y):
                clicked_camel = mob
                break
            if isinstance(mob, Horse) and mob.rect.collidepoint(target_world_x, target_world_y):
                clicked_horse = mob
                break
            if isinstance(mob, Ostrich) and mob.rect.collidepoint(target_world_x, target_world_y):
                clicked_ostrich = mob
                break
        
        if clicked_camel and player.mounted_camel is None:
            # Mount the camel
            player.mount_camel(clicked_camel)
            return
        
        if clicked_horse and not player.is_riding:
            # Mount the horse
            clicked_horse.mount(player)
            return
        
        if clicked_ostrich and not player.is_riding:
            # Mount the ostrich
            clicked_ostrich.mount(player)
            return
        
        # Check if clicking on a furnace to open GUI
        if 0 <= target_row < GRID_HEIGHT and 0 <= target_col < GRID_WIDTH:
            clicked_block = WORLD_MAP[target_row][target_col]
            if clicked_block == 16:  # Furnace ID
                global FURNACE_OPEN, FURNACE_POS
                FURNACE_OPEN = True
                FURNACE_POS = (target_col, target_row)
                return
        
        # Otherwise, place a block
        held_id = player.held_block
        
        if held_id != 0 and WORLD_MAP[target_row][target_col] in [0, 5]:  # Allow placing in air or water
            block_data = BLOCK_TYPES.get(held_id, {})
            
            # Check if the item can be placed (not a tool or drop item)
            if block_data.get("mineable", True) and block_data.get("solid", True):
                # Check if not placing inside the player
                player_blocks = [
                    (player.rect.left // BLOCK_SIZE, player.rect.top // BLOCK_SIZE),
                    (player.rect.right // BLOCK_SIZE, player.rect.top // BLOCK_SIZE),
                    (player.rect.left // BLOCK_SIZE, player.rect.bottom // BLOCK_SIZE),
                    (player.rect.right // BLOCK_SIZE, player.rect.bottom // BLOCK_SIZE)
                ]
                
                if (target_col, target_row) not in player_blocks:
                    # Check if torch is being placed in water
                    if held_id == 15 and WORLD_MAP[target_row][target_col] == 5:  # Torch in water
                        print("💧 Torches break in water!")
                        if player.consume_item(held_id, 1):
                            pass  # Torch is consumed but not placed
                    elif player.consume_item(held_id, 1):
                        WORLD_MAP[target_row][target_col] = held_id
                        
                        # Add to light sources if it emits light
                        if block_data.get("emits_light", False):
                            LIGHT_SOURCES.add((target_col, target_row))
                        
                        # Track sapling growth
                        if held_id in [139, 140, 141, 142, 150]:  # Saplings (added acacia)
                            SAPLING_GROWTH[(target_col, target_row)] = (held_id, TIME_OF_DAY)
# --- HUD Drawing ---
def draw_hud(player):
    """Draws the hotbar, health hearts, hunger bars, oxygen bubbles, and held item name."""
    SLOT_SIZE = 50
    HOTBAR_START_X = (SCREEN_WIDTH - (SLOT_SIZE * 9)) // 2
    HOTBAR_Y = SCREEN_HEIGHT - SLOT_SIZE - 10
    
    # Draw Hotbar Slots
    for i in range(9):
        slot_x = HOTBAR_START_X + i * SLOT_SIZE
        slot_rect = pygame.Rect(slot_x, HOTBAR_Y, SLOT_SIZE, SLOT_SIZE)
        
        # Highlight active slot
        if i == player.active_slot:
            pygame.draw.rect(screen, (255, 255, 0), slot_rect, 3)
        else:
            pygame.draw.rect(screen, (100, 100, 100), slot_rect, 2)
        
        # Draw item in slot (hotbar now stores tuples: (item_id, count))
        item_id, count = player.hotbar_slots[i]
        if item_id != 0 and item_id in BLOCK_TYPES:
            inner_rect = pygame.Rect(slot_x + 5, HOTBAR_Y + 5, SLOT_SIZE - 10, SLOT_SIZE - 10)
            # Use custom tool drawing for tools, otherwise draw colored square
            if item_id in [9, 99, 100, 101, 102, 107]:  # Tool IDs
                draw_tool_icon(screen, inner_rect, item_id)
            else:
                block_color = BLOCK_TYPES[item_id]["color"]
                pygame.draw.rect(screen, block_color, inner_rect)
            
            # Draw item count
            if count > 1:
                count_text = FONT_SMALL.render(str(count), True, (255, 255, 255))
                screen.blit(count_text, (slot_x + SLOT_SIZE - count_text.get_width() - 2, 
                                        HOTBAR_Y + SLOT_SIZE - count_text.get_height() - 2))
    
    # Draw Hearts (Health) on the LEFT
    heart_size = 18
    heart_spacing = 20
    hearts_x = 10
    hearts_y = SCREEN_HEIGHT - 30
    
    # Calculate total armor points
    total_armor = 0
    for armor_slot in ['helmet', 'chestplate', 'leggings', 'boots']:
        armor_id = player.armor_slots.get(armor_slot, 0)
        if armor_id in BLOCK_TYPES:
            total_armor += BLOCK_TYPES[armor_id].get('armor_points', 0)
    
    # Draw Armor icons above hearts
    if total_armor > 0:
        armor_icon_size = 16
        armor_icon_spacing = 20
        armor_y = hearts_y - 22
        
        for i in range(10):  # Up to 10 armor points (20 total armor / 2)
            x = hearts_x + i * armor_icon_spacing
            # Draw armor background
            pygame.draw.rect(screen, (50, 50, 50), (x, armor_y, armor_icon_size, armor_icon_size))
            pygame.draw.rect(screen, (100, 100, 100), (x, armor_y, armor_icon_size, armor_icon_size), 1)
            
            # Draw filled armor if player has armor points
            if total_armor > i * 2:
                if total_armor >= (i + 1) * 2:
                    # Full armor icon - chestplate shape
                    pygame.draw.rect(screen, (200, 200, 200), (x + 3, armor_y + 2, armor_icon_size - 6, armor_icon_size - 4))
                    pygame.draw.rect(screen, (160, 160, 160), (x + 2, armor_y + 6, armor_icon_size - 4, 4))
                    pygame.draw.rect(screen, (180, 180, 180), (x + 5, armor_y + 3, 2, 2))
                    pygame.draw.rect(screen, (180, 180, 180), (x + armor_icon_size - 7, armor_y + 3, 2, 2))
                else:
                    # Half armor icon
                    pygame.draw.rect(screen, (200, 200, 200), (x + 3, armor_y + 2, (armor_icon_size - 6) // 2, armor_icon_size - 4))
                    pygame.draw.rect(screen, (160, 160, 160), (x + 2, armor_y + 6, (armor_icon_size - 4) // 2, 4))
    
    for i in range(10):  # 10 hearts for 20 health
        x = hearts_x + i * heart_spacing
        # Draw heart background (empty)
        pygame.draw.rect(screen, (50, 50, 50), (x, hearts_y, heart_size, heart_size))
        pygame.draw.rect(screen, (100, 100, 100), (x, hearts_y, heart_size, heart_size), 1)
        
        # Draw filled heart if player has health
        if player.health > i * 2:
            # Full or half heart
            if player.health >= (i + 1) * 2:
                # Full heart - red with classic heart shape
                pygame.draw.polygon(screen, (255, 0, 0), [
                    (x + heart_size // 2, hearts_y + heart_size - 3),
                    (x + 2, hearts_y + 6),
                    (x + 2, hearts_y + 4),
                    (x + 6, hearts_y + 2),
                    (x + heart_size // 2, hearts_y + 4),
                    (x + heart_size - 6, hearts_y + 2),
                    (x + heart_size - 2, hearts_y + 4),
                    (x + heart_size - 2, hearts_y + 6)
                ])
            else:
                # Half heart
                pygame.draw.polygon(screen, (255, 0, 0), [
                    (x + heart_size // 2, hearts_y + heart_size - 3),
                    (x + 2, hearts_y + 6),
                    (x + 2, hearts_y + 4),
                    (x + 6, hearts_y + 2),
                    (x + heart_size // 2, hearts_y + 4)
                ])
    
    # Draw Hunger Bars (Ham/Meat) on the RIGHT
    hunger_size = 18
    hunger_spacing = 20
    hunger_x = SCREEN_WIDTH - 10 - (10 * hunger_spacing)
    hunger_y = SCREEN_HEIGHT - 30
    
    for i in range(10):  # 10 hunger bars for 20 hunger
        x = hunger_x + i * hunger_spacing
        # Draw hunger background (empty)
        pygame.draw.rect(screen, (50, 50, 50), (x, hunger_y, hunger_size, hunger_size))
        pygame.draw.rect(screen, (100, 100, 100), (x, hunger_y, hunger_size, hunger_size), 1)
        
        # Draw filled hunger if player has hunger
        if player.hunger > i * 2:
            # Full or half hunger (ham/meat icon)
            if player.hunger >= (i + 1) * 2:
                # Full ham - pink/brown meat color
                pygame.draw.rect(screen, (210, 105, 105), (x + 3, hunger_y + 3, hunger_size - 6, hunger_size - 9))
                pygame.draw.rect(screen, (139, 69, 19), (x + 5, hunger_y + 8, hunger_size - 10, hunger_size - 11))
                pygame.draw.rect(screen, (255, 255, 255), (x + 7, hunger_y + 5, 3, 3))  # Bone highlight
            else:
                # Half ham
                pygame.draw.rect(screen, (210, 105, 105), (x + 3, hunger_y + 3, (hunger_size - 6) // 2, hunger_size - 9))
                pygame.draw.rect(screen, (139, 69, 19), (x + 5, hunger_y + 8, (hunger_size - 10) // 2, hunger_size - 11))
    
    # Draw Oxygen Bubbles (above hearts when underwater)
    head_col = player.rect.centerx // BLOCK_SIZE
    head_row = (player.rect.top + 5) // BLOCK_SIZE
    head_underwater = False
    
    if 0 <= head_row < GRID_HEIGHT and 0 <= head_col < GRID_WIDTH:
        if WORLD_MAP[head_row][head_col] == 5:  # Water
            head_underwater = True
    
    if head_underwater:
        bubble_size = 16
        bubble_spacing = 18
        bubbles_x = 10
        bubbles_y = SCREEN_HEIGHT - 55
        
        for i in range(10):  # 10 bubbles for 10 oxygen
            x = bubbles_x + i * bubble_spacing
            # Draw bubble background
            pygame.draw.rect(screen, (50, 50, 50), (x, bubbles_y, bubble_size, bubble_size))
            pygame.draw.rect(screen, (100, 100, 100), (x, bubbles_y, bubble_size, bubble_size), 1)
            
            # Draw filled bubble if player has oxygen
            if player.oxygen > i:
                pygame.draw.circle(screen, (173, 216, 230), (x + bubble_size // 2, bubbles_y + bubble_size // 2), bubble_size // 2 - 2)
                pygame.draw.circle(screen, (255, 255, 255), (x + bubble_size // 2 - 2, bubbles_y + bubble_size // 2 - 2), 2)  # Highlight
    
    # Draw Held Item Name
    held_id = player.held_block
    if held_id != 0 and held_id in BLOCK_TYPES:
        held_name = BLOCK_TYPES[held_id]["name"]
        name_text = FONT_BIG.render(held_name, True, (255, 255, 255))
        name_x = SCREEN_WIDTH // 2 - name_text.get_width() // 2
        name_y = SCREEN_HEIGHT - SLOT_SIZE - 50
        screen.blit(name_text, (name_x, name_y))
    
    # Draw Riding Status
    if player.mounted_camel is not None:
        riding_text = FONT_SMALL.render("Riding Camel - Press SHIFT to dismount", True, (255, 255, 255))
        text_x = SCREEN_WIDTH // 2 - riding_text.get_width() // 2
        text_y = 80
        # Background for visibility
        bg_rect = pygame.Rect(text_x - 5, text_y - 2, riding_text.get_width() + 10, riding_text.get_height() + 4)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
        screen.blit(riding_text, (text_x, text_y))
    
    # Draw Movement Status Indicators (top right)
    status_x = SCREEN_WIDTH - 150
    status_y = 10
    
    if player.is_sprinting:
        sprint_text = FONT_SMALL.render("SPRINTING", True, (0, 255, 0))
        screen.blit(sprint_text, (status_x, status_y))
        status_y += 20
    
    if player.is_crouching:
        crouch_text = FONT_SMALL.render("CROUCHING", True, (255, 165, 0))
        screen.blit(crouch_text, (status_x, status_y))
        status_y += 20
    
    # Draw Coordinates and Biome (top left)
    coords_x = 10
    coords_y = 10
    
    # Get player position in blocks (relative to spawn at 0,0)
    spawn_col = GRID_WIDTH // 2
    spawn_row = GRID_HEIGHT // 2
    player_block_x = (player.rect.centerx // BLOCK_SIZE) - spawn_col
    player_block_y = (player.rect.centery // BLOCK_SIZE) - spawn_row
    
    # Get current biome
    biome_names = {
        0: "Oak Forest",
        1: "Desert",
        2: "Snow Biome",
        3: "Swamp",
        4: "Taiga",
        5: "Plains",
        6: "Birch Forest",
        7: "Lake",
        8: "Jungle",
        9: "Bamboo Jungle",
        10: "Savannah",
        11: "Ocean"
    }
    
    # Use absolute position for biome lookup
    absolute_x = player.rect.centerx // BLOCK_SIZE
    if 0 <= absolute_x < len(BIOME_MAP):
        current_biome = BIOME_MAP[absolute_x]
        biome_name = biome_names.get(current_biome, "Unknown")
    else:
        biome_name = "Unknown"
    
    # Draw background for readability (show column instead of block position)
    coords_text = FONT_SMALL.render(f"X: {absolute_x}  Y: {player_block_y}", True, (255, 255, 255))
    biome_text = FONT_SMALL.render(f"Biome: {biome_name}", True, (255, 255, 255))
    
    # Get hovered block name
    mouse_x, mouse_y = pygame.mouse.get_pos()
    camera_x, camera_y = calculate_camera_offset(player.rect)
    target_world_x = mouse_x + camera_x
    target_world_y = mouse_y + camera_y
    target_col = target_world_x // BLOCK_SIZE
    target_row = target_world_y // BLOCK_SIZE
    
    hovered_block_name = "Air"
    if 0 <= target_row < GRID_HEIGHT and 0 <= target_col < GRID_WIDTH:
        player_col = player.rect.centerx // BLOCK_SIZE
        player_row = player.rect.centery // BLOCK_SIZE
        if max(abs(target_col - player_col), abs(target_row - player_row)) <= 4:
            hovered_block_id = WORLD_MAP[target_row][target_col]
            if hovered_block_id in BLOCK_TYPES:
                hovered_block_name = BLOCK_TYPES[hovered_block_id]["name"]
    
    block_text = FONT_SMALL.render(f"Block: {hovered_block_name}", True, (255, 255, 255))
    
    # Mob count info
    mob_count_text = FONT_SMALL.render(f"Mobs: {len(MOBS)}", True, (200, 200, 255))
    
    bg_width = max(coords_text.get_width(), biome_text.get_width(), block_text.get_width(), mob_count_text.get_width()) + 10
    bg_height = coords_text.get_height() + biome_text.get_height() + block_text.get_height() + mob_count_text.get_height() + 10
    bg_rect = pygame.Rect(coords_x - 5, coords_y - 5, bg_width, bg_height)
    pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
    pygame.draw.rect(screen, (100, 100, 100), bg_rect, 1)
    
    screen.blit(coords_text, (coords_x, coords_y))
    screen.blit(biome_text, (coords_x, coords_y + coords_text.get_height()))
    screen.blit(block_text, (coords_x, coords_y + coords_text.get_height() + biome_text.get_height()))
    screen.blit(mob_count_text, (coords_x, coords_y + coords_text.get_height() + biome_text.get_height() + block_text.get_height()))
    
    # Draw Mob Trackers below coordinates
    tracker_y = coords_y + coords_text.get_height() + biome_text.get_height() + block_text.get_height() + mob_count_text.get_height() + 10
    
    # Draw Hostile Mob Tracker
    nearest_hostile, hostile_distance = get_nearest_hostile_mob(player, MOBS)
    if nearest_hostile:
        mob_name = nearest_hostile.__class__.__name__
        distance_blocks = int(hostile_distance // BLOCK_SIZE)
        
        # Color based on distance
        if distance_blocks < 10:
            tracker_color = (255, 0, 0)  # Red - danger
        elif distance_blocks < 30:
            tracker_color = (255, 165, 0)  # Orange - caution
        else:
            tracker_color = (255, 255, 0)  # Yellow - aware
        
        tracker_text = FONT_SMALL.render(f"⚠ {mob_name}: {distance_blocks} blocks", True, tracker_color)
        
        # Draw background
        tracker_bg = pygame.Rect(coords_x - 5, tracker_y - 5, tracker_text.get_width() + 10, tracker_text.get_height() + 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), tracker_bg)
        pygame.draw.rect(screen, tracker_color, tracker_bg, 2)
        
        screen.blit(tracker_text, (coords_x, tracker_y))
        
        # Draw direction arrow
        dx = nearest_hostile.rect.centerx - player.rect.centerx
        if abs(dx) > BLOCK_SIZE:
            arrow_x = coords_x - 15
            arrow_y = tracker_y + 8
            if dx > 0:
                pygame.draw.polygon(screen, tracker_color, [
                    (arrow_x, arrow_y), (arrow_x + 10, arrow_y + 5), (arrow_x, arrow_y + 10)
                ])
            else:
                pygame.draw.polygon(screen, tracker_color, [
                    (arrow_x + 10, arrow_y), (arrow_x, arrow_y + 5), (arrow_x + 10, arrow_y + 10)
                ])
        tracker_y += 25
    
    # Draw Meat Mob Tracker
    nearest_meat, meat_distance = get_nearest_meat_mob(player, MOBS)
    if nearest_meat:
        mob_name = nearest_meat.__class__.__name__
        distance_blocks = int(meat_distance // BLOCK_SIZE)
        meat_color = (100, 200, 100)  # Green for food
        
        meat_text = FONT_SMALL.render(f"🍖 {mob_name}: {distance_blocks} blocks", True, meat_color)
        
        # Draw background
        meat_bg = pygame.Rect(coords_x - 5, tracker_y - 5, meat_text.get_width() + 10, meat_text.get_height() + 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), meat_bg)
        pygame.draw.rect(screen, meat_color, meat_bg, 2)
        
        screen.blit(meat_text, (coords_x, tracker_y))
        tracker_y += 25
    
    # Draw Nearest Mob Overall
    nearest_any, any_distance = get_nearest_mob(player, MOBS)
    if nearest_any:
        mob_name = nearest_any.__class__.__name__
        any_color = (200, 200, 200)  # Gray
        
        any_text = FONT_SMALL.render(f"Nearest: {mob_name}", True, any_color)
        
        # Draw background
        any_bg = pygame.Rect(coords_x - 5, tracker_y - 5, any_text.get_width() + 10, any_text.get_height() + 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), any_bg)
        pygame.draw.rect(screen, any_color, any_bg, 2)
        
        screen.blit(any_text, (coords_x, tracker_y))
    
    # Display structure spawn notifications
    global STRUCTURE_NOTIFICATIONS
    notification_y = coords_y + coords_text.get_height() + biome_text.get_height() + block_text.get_height() + 10
    for notification in STRUCTURE_NOTIFICATIONS[:]:
        struct_name, struct_col, timer = notification
        notif_text = FONT_SMALL.render(f"{struct_name} at X: {struct_col}", True, (255, 255, 0))
        
        # Draw background
        notif_bg = pygame.Rect(coords_x - 5, notification_y - 5, notif_text.get_width() + 10, notif_text.get_height() + 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), notif_bg)
        pygame.draw.rect(screen, (255, 255, 0), notif_bg, 1)
        
        screen.blit(notif_text, (coords_x, notification_y))
        notification_y += notif_text.get_height() + 5
        
        # Decrement timer
        notification[2] -= 1
        if notification[2] <= 0:
            STRUCTURE_NOTIFICATIONS.remove(notification)

# --- Crafting Functions ---
def get_craftable_item():
    """Checks if the current crafting grid matches any recipe. Requires EXACT amounts only."""
    # Create a dictionary of grid contents
    grid_contents = {}
    for i in range(4):
        item_id = CRAFTING_GRID[i]
        amount = CRAFTING_AMOUNTS[i]
        
        if item_id != 0 and amount > 0:
            if item_id in grid_contents:
                grid_contents[item_id] += amount
            else:
                grid_contents[item_id] = amount
    
    if not grid_contents:
        return None
    
    # Check each recipe to see if we have EXACT match
    for recipe_ingredients, (output_id, output_count) in CRAFTING_RECIPES.items():
        # Convert recipe to dict for easier comparison
        recipe_dict = dict(recipe_ingredients)
        
        # Check if grid contents EXACTLY match recipe (same items and same amounts)
        if len(grid_contents) != len(recipe_dict):
            continue
        
        exact_match = True
        for required_id, required_count in recipe_dict.items():
            if required_id not in grid_contents or grid_contents[required_id] != required_count:
                exact_match = False
                break
        
        if exact_match:
            # Return output without multiplier - exact recipe only
            return (output_id, output_count)
    
    return None

def draw_crafting_menu(player):
    """Draws the crafting menu overlay with a 2x2 grid."""
    global CRAFTING_SLOT_RECTS
    CRAFTING_SLOT_RECTS = [] # Reset for each frame
    
    # 1. Draw Semi-Transparent Background
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((50, 50, 50))
    screen.blit(overlay, (0, 0))
    
    # 2. Draw Menu Title
    title_text = FONT_BIG.render("Crafting", True, (255, 255, 255))
    title_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
    title_y = 50
    screen.blit(title_text, (title_x, title_y))
    
    # 3. Draw Crafting Grid (2x2)
    SLOT_SIZE = max(40, min(60, SCREEN_HEIGHT // 12))  # Scale with screen size
    MENU_X = SCREEN_WIDTH // 2 - SLOT_SIZE - 50
    MENU_Y = SCREEN_HEIGHT // 2 - SLOT_SIZE
    
    for i in range(4):
        row = i // 2
        col = i % 2
        slot_x = MENU_X + col * (SLOT_SIZE + 10)
        slot_y = MENU_Y + row * (SLOT_SIZE + 10)
        
        slot_rect = pygame.Rect(slot_x, slot_y, SLOT_SIZE, SLOT_SIZE)
        CRAFTING_SLOT_RECTS.append(slot_rect)
        
        # Draw slot background
        pygame.draw.rect(screen, (100, 100, 100), slot_rect, 2)
        
        # Draw item in slot
        item_id = CRAFTING_GRID[i]
        amount = CRAFTING_AMOUNTS[i]
        
        if item_id != 0 and item_id in BLOCK_TYPES:
            block_color = BLOCK_TYPES[item_id]["color"]
            inner_rect = pygame.Rect(slot_x + 5, slot_y + 5, SLOT_SIZE - 10, SLOT_SIZE - 10)
            pygame.draw.rect(screen, block_color, inner_rect)
            
            # Draw amount if more than 1
            if amount > 1:
                count_text = FONT_SMALL.render(str(amount), True, (255, 255, 255))
                screen.blit(count_text, (slot_x + SLOT_SIZE - count_text.get_width() - 2, 
                                       slot_y + SLOT_SIZE - count_text.get_height() - 2))

    # 4. Draw Arrow (Adjusted position)
    pygame.draw.line(screen, (255, 255, 255), (MENU_X + 220, MENU_Y + 120), (MENU_X + 290, MENU_Y + 120), 3) 
    pygame.draw.polygon(screen, (255, 255, 255), [(MENU_X + 290, MENU_Y + 120), (MENU_X + 280, MENU_Y + 115), (MENU_X + 280, MENU_Y + 125)])

    # 5. Draw Output Slot (Adjusted position)
    output_rect = pygame.Rect(MENU_X + 300, MENU_Y + 100, SLOT_SIZE, SLOT_SIZE) 
    CRAFTING_SLOT_RECTS.append(output_rect) # Index 4 for output click detection (2x2 grid = 0,1,2,3 inputs, 4 is output)

    # Check if a craftable item is available
    craftable = get_craftable_item()
    
    if craftable:
        output_id, output_count = craftable
        
        # Draw the output slot with a highlight
        pygame.draw.rect(screen, (0, 255, 0), output_rect, 3)
        
        # Draw the craftable item
        if output_id in BLOCK_TYPES:
            block_color = BLOCK_TYPES[output_id]["color"]
            inner_rect = pygame.Rect(output_rect.x + 5, output_rect.y + 5, SLOT_SIZE - 10, SLOT_SIZE - 10)
            pygame.draw.rect(screen, block_color, inner_rect)
            
            # Draw output count
            if output_count > 1:
                count_text = FONT_SMALL.render(str(output_count), True, (255, 255, 255))
                screen.blit(count_text, (output_rect.x + SLOT_SIZE - count_text.get_width() - 2, 
                                       output_rect.y + SLOT_SIZE - count_text.get_height() - 2))
    else:
        # Draw empty output slot
        pygame.draw.rect(screen, (100, 100, 100), output_rect, 2)
        
    # 6. Draw Instructions
    instructions = [
        "Left Click: Add Item",
        "Right Click: Remove Item",
        "Press E to Close"
    ]
    
    inst_y = MENU_Y + 200
    for line in instructions:
        inst_text = FONT_SMALL.render(line, True, (255, 255, 255))
        inst_x = SCREEN_WIDTH // 2 - inst_text.get_width() // 2
        screen.blit(inst_text, (inst_x, inst_y))
        inst_y += 20

def draw_inventory_menu(player):
    """Draws a Minecraft-style inventory menu with crafting area and clickable slots."""
    global INVENTORY_SLOT_RECTS
    INVENTORY_SLOT_RECTS = []  # Reset for each frame
    
    # 1. Draw Semi-Transparent Background
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((50, 50, 50))
    screen.blit(overlay, (0, 0))
    
    # 2. Draw Menu Title
    title_text = FONT_BIG.render("Inventory", True, (255, 255, 255))
    title_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
    title_y = 30
    screen.blit(title_text, (title_x, title_y))
    
    SLOT_SIZE = max(35, min(45, SCREEN_HEIGHT // 15))  # Scale with screen size
    
    # 3. Draw Crafting Area (2x2 grid on the left)
    craft_title = FONT_SMALL.render("Crafting:", True, (255, 255, 255))
    craft_x = 100
    craft_y = 100
    screen.blit(craft_title, (craft_x, craft_y))
    
    # Draw 2x2 crafting grid
    for i in range(4):
        row = i // 2
        col = i % 2
        slot_x = craft_x + col * (SLOT_SIZE + 5)
        slot_y = craft_y + 25 + row * (SLOT_SIZE + 5)
        
        slot_rect = pygame.Rect(slot_x, slot_y, SLOT_SIZE, SLOT_SIZE)
        INVENTORY_SLOT_RECTS.append(('craft', i, slot_rect))
        
        pygame.draw.rect(screen, (100, 100, 100), slot_rect, 2)
        
        # Draw crafting grid item
        item_id = CRAFTING_GRID[i]
        if item_id != 0 and item_id in BLOCK_TYPES:
            block_color = BLOCK_TYPES[item_id]["color"]
            inner_rect = pygame.Rect(slot_x + 3, slot_y + 3, SLOT_SIZE - 6, SLOT_SIZE - 6)
            pygame.draw.rect(screen, block_color, inner_rect)
            if CRAFTING_AMOUNTS[i] > 1:
                count_text = FONT_SMALL.render(str(CRAFTING_AMOUNTS[i]), True, (255, 255, 255))
                screen.blit(count_text, (slot_x + SLOT_SIZE - count_text.get_width() - 2, 
                                       slot_y + SLOT_SIZE - count_text.get_height() - 2))
    
    # Crafting output slot
    output_x = craft_x + 120
    output_y = craft_y + 45
    output_rect = pygame.Rect(output_x, output_y, SLOT_SIZE, SLOT_SIZE)
    INVENTORY_SLOT_RECTS.append(('craft_output', 4, output_rect))
    
    craftable = get_craftable_item()
    if craftable:
        pygame.draw.rect(screen, (0, 255, 0), output_rect, 3)
        output_id, output_count = craftable
        if output_id in BLOCK_TYPES:
            block_color = BLOCK_TYPES[output_id]["color"]
            inner_rect = pygame.Rect(output_x + 3, output_y + 3, SLOT_SIZE - 6, SLOT_SIZE - 6)
            pygame.draw.rect(screen, block_color, inner_rect)
            if output_count > 1:
                count_text = FONT_SMALL.render(str(output_count), True, (255, 255, 255))
                screen.blit(count_text, (output_x + SLOT_SIZE - count_text.get_width() - 2, 
                                       output_y + SLOT_SIZE - count_text.get_height() - 2))
    else:
        pygame.draw.rect(screen, (100, 100, 100), output_rect, 2)
    
    # --- Armor Slots (below crafting grid) ---
    armor_title = FONT_SMALL.render("Armor:", True, (255, 255, 255))
    armor_x = craft_x
    armor_y = craft_y + 135
    screen.blit(armor_title, (armor_x, armor_y))
    
    armor_slot_names = ['helmet', 'chestplate', 'leggings', 'boots']
    armor_labels = ['Helmet', 'Chest', 'Legs', 'Boots']
    
    for i, (slot_name, label) in enumerate(zip(armor_slot_names, armor_labels)):
        slot_x = armor_x
        slot_y = armor_y + 20 + i * (SLOT_SIZE + 5)
        
        slot_rect = pygame.Rect(slot_x, slot_y, SLOT_SIZE, SLOT_SIZE)
        INVENTORY_SLOT_RECTS.append(('armor', i, slot_rect))
        
        # Draw slot border
        pygame.draw.rect(screen, (150, 150, 0), slot_rect, 2)
        
        # Draw armor item if equipped
        armor_id = player.armor_slots[slot_name]
        if armor_id != 0 and armor_id in BLOCK_TYPES:
            block_color = BLOCK_TYPES[armor_id]["color"]
            inner_rect = pygame.Rect(slot_x + 3, slot_y + 3, SLOT_SIZE - 6, SLOT_SIZE - 6)
            pygame.draw.rect(screen, block_color, inner_rect)
        
        # Draw label
        label_text = FONT_SMALL.render(label, True, (200, 200, 200))
        screen.blit(label_text, (slot_x + SLOT_SIZE + 5, slot_y + SLOT_SIZE // 2 - label_text.get_height() // 2))
    
    # 4. Draw Main Inventory Grid (9 columns x 3 rows on the right)
    inv_title = FONT_SMALL.render("Inventory:", True, (255, 255, 255))
    START_X = 300
    START_Y = 100
    screen.blit(inv_title, (START_X, START_Y))
    
    # Draw the 27 inventory slots (separate from hotbar)
    for row in range(3):
        for col in range(9):
            slot_index = row * 9 + col
            slot_x = START_X + col * (SLOT_SIZE + 5)
            slot_y = START_Y + 25 + row * (SLOT_SIZE + 5)
            
            slot_rect = pygame.Rect(slot_x, slot_y, SLOT_SIZE, SLOT_SIZE)
            INVENTORY_SLOT_RECTS.append(('inventory', slot_index, slot_rect))
            
            pygame.draw.rect(screen, (100, 100, 100), slot_rect, 2)
            
            # Get item from inventory slot
            item_id, stack_amount = player.inventory[slot_index]
            if item_id != 0 and item_id in BLOCK_TYPES:
                block_color = BLOCK_TYPES[item_id]["color"]
                inner_rect = pygame.Rect(slot_x + 3, slot_y + 3, SLOT_SIZE - 6, SLOT_SIZE - 6)
                pygame.draw.rect(screen, block_color, inner_rect)
                if stack_amount > 1:
                    count_text = FONT_SMALL.render(str(stack_amount), True, (255, 255, 255))
                    screen.blit(count_text, (slot_x + SLOT_SIZE - count_text.get_width() - 2, 
                                           slot_y + SLOT_SIZE - count_text.get_height() - 2))
    
    # 5. Draw Hotbar Section
    hotbar_y = START_Y + 3 * (SLOT_SIZE + 5) + 40
    hotbar_text = FONT_SMALL.render("Hotbar (1-9):", True, (255, 255, 255))
    screen.blit(hotbar_text, (START_X, hotbar_y))
    
    hotbar_y += 25
    for i in range(9):
        slot_x = START_X + i * (SLOT_SIZE + 5)
        slot_y = hotbar_y
        
        slot_rect = pygame.Rect(slot_x, slot_y, SLOT_SIZE, SLOT_SIZE)
        INVENTORY_SLOT_RECTS.append(('hotbar', i, slot_rect))
        
        if i == player.active_slot:
            pygame.draw.rect(screen, (255, 255, 0), slot_rect, 3)
        else:
            pygame.draw.rect(screen, (100, 100, 100), slot_rect, 2)
        
        # Get item from hotbar slot
        item_id, stack_count = player.hotbar_slots[i]
        if item_id != 0 and item_id in BLOCK_TYPES:
            block_color = BLOCK_TYPES[item_id]["color"]
            inner_rect = pygame.Rect(slot_x + 3, slot_y + 3, SLOT_SIZE - 6, SLOT_SIZE - 6)
            pygame.draw.rect(screen, block_color, inner_rect)
            if stack_count > 1:
                count_text = FONT_SMALL.render(str(stack_count), True, (255, 255, 255))
                screen.blit(count_text, (slot_x + SLOT_SIZE - count_text.get_width() - 2, 
                                       slot_y + SLOT_SIZE - count_text.get_height() - 2))
    
    # 6. Draw held item (follows cursor)
    global HELD_ITEM
    if 'HELD_ITEM' in globals() and HELD_ITEM[0] != 0:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        held_id, held_count = HELD_ITEM
        if held_id in BLOCK_TYPES:
            block_color = BLOCK_TYPES[held_id]["color"]
            held_rect = pygame.Rect(mouse_x - 20, mouse_y - 20, 40, 40)
            pygame.draw.rect(screen, block_color, held_rect)
            pygame.draw.rect(screen, (255, 255, 255), held_rect, 2)
            if held_count > 1:
                count_text = FONT_SMALL.render(str(held_count), True, (255, 255, 255))
                screen.blit(count_text, (mouse_x - 10, mouse_y + 15))
    
    # 7. Draw Instructions
    instructions = [
        "Left Click: Pick up/Place items",
        "Right Click: Select hotbar slot",
        "Press E to Close"
    ]
    
    inst_y = hotbar_y + SLOT_SIZE + 20
    for line in instructions:
        inst_text = FONT_SMALL.render(line, True, (200, 200, 200))
        inst_x = SCREEN_WIDTH // 2 - inst_text.get_width() // 2
        screen.blit(inst_text, (inst_x, inst_y))
        inst_y += 20

def handle_crafting_interaction(player, event):
    """Handles clicks inside the crafting menu using drag-and-drop with HELD_ITEM."""
    global CRAFTING_GRID, CRAFTING_AMOUNTS, HELD_ITEM
    
    # Initialize held item if not exists
    if 'HELD_ITEM' not in globals():
        HELD_ITEM = (0, 0)
    
    # 1. Check Input Slots (Indices 0-3)
    for i in range(4):
        if CRAFTING_SLOT_RECTS[i].collidepoint(event.pos):
            
            if event.button == 1: # LMB: Place/pickup item
                if HELD_ITEM[0] == 0 and CRAFTING_GRID[i] != 0 and CRAFTING_AMOUNTS[i] > 0:
                    # Pick up entire stack from crafting slot
                    HELD_ITEM = (CRAFTING_GRID[i], CRAFTING_AMOUNTS[i])
                    CRAFTING_GRID[i] = 0
                    CRAFTING_AMOUNTS[i] = 0
                elif HELD_ITEM[0] != 0:
                    # Place entire stack in crafting slot
                    if CRAFTING_GRID[i] == 0:
                        CRAFTING_GRID[i] = HELD_ITEM[0]
                        CRAFTING_AMOUNTS[i] = HELD_ITEM[1]
                        HELD_ITEM = (0, 0)
                    elif CRAFTING_GRID[i] == HELD_ITEM[0]:
                        # Same item - merge stacks
                        CRAFTING_AMOUNTS[i] += HELD_ITEM[1]
                        HELD_ITEM = (0, 0)
                    else:
                        # Different item - swap
                        old_id, old_amount = CRAFTING_GRID[i], CRAFTING_AMOUNTS[i]
                        CRAFTING_GRID[i] = HELD_ITEM[0]
                        CRAFTING_AMOUNTS[i] = HELD_ITEM[1]
                        HELD_ITEM = (old_id, old_amount)

            elif event.button == 3: # RMB: Place/remove one item
                if HELD_ITEM[0] == 0 and CRAFTING_GRID[i] != 0 and CRAFTING_AMOUNTS[i] > 0:
                    # Pick up one item from crafting slot
                    HELD_ITEM = (CRAFTING_GRID[i], 1)
                    CRAFTING_AMOUNTS[i] -= 1
                    if CRAFTING_AMOUNTS[i] <= 0:
                        CRAFTING_GRID[i] = 0
                        CRAFTING_AMOUNTS[i] = 0
                elif HELD_ITEM[0] != 0:
                    # Place one item in crafting slot
                    if CRAFTING_GRID[i] == 0 or CRAFTING_GRID[i] == HELD_ITEM[0]:
                        CRAFTING_GRID[i] = HELD_ITEM[0]
                        CRAFTING_AMOUNTS[i] += 1
                        HELD_ITEM = (HELD_ITEM[0], HELD_ITEM[1] - 1) if HELD_ITEM[1] > 1 else (0, 0)
            return

    # 2. Check Output Slot (Index 4)
    if len(CRAFTING_SLOT_RECTS) > 4 and CRAFTING_SLOT_RECTS[4].collidepoint(event.pos) and event.button == 1:
        craftable = get_craftable_item()
        if craftable:
            output_id, output_count = craftable
            
            # Find the matching recipe to consume exact amounts
            for recipe_ingredients, (recipe_output_id, recipe_output_count) in CRAFTING_RECIPES.items():
                recipe_dict = dict(recipe_ingredients)
                
                if recipe_output_id == output_id:
                    # Consume the exact recipe amounts
                    for i in range(4):
                        if CRAFTING_GRID[i] != 0:
                            item_id = CRAFTING_GRID[i]
                            if item_id in recipe_dict:
                                CRAFTING_AMOUNTS[i] -= recipe_dict[item_id]
                                if CRAFTING_AMOUNTS[i] <= 0:
                                    CRAFTING_GRID[i] = 0
                                    CRAFTING_AMOUNTS[i] = 0
                    break
            
            # Add the crafted item to the player's inventory
            player.add_to_inventory(output_id, output_count)
            return

def handle_inventory_interaction(player, event):
    """Handles clicks inside the inventory menu - click to pick up, click to place."""
    global CRAFTING_GRID, CRAFTING_AMOUNTS, HELD_ITEM
    
    # Initialize held item if not exists
    if 'HELD_ITEM' not in globals():
        HELD_ITEM = (0, 0)  # (item_id, count)
    
    for slot_type, slot_index, slot_rect in INVENTORY_SLOT_RECTS:
        if slot_rect.collidepoint(event.pos):
            
            # Handle crafting slots
            if slot_type == 'craft':
                if event.button == 1:  # LMB: Place/pickup entire stack
                    if HELD_ITEM[0] == 0 and CRAFTING_GRID[slot_index] != 0 and CRAFTING_AMOUNTS[slot_index] > 0:
                        # Pick up entire stack from crafting slot
                        HELD_ITEM = (CRAFTING_GRID[slot_index], CRAFTING_AMOUNTS[slot_index])
                        CRAFTING_GRID[slot_index] = 0
                        CRAFTING_AMOUNTS[slot_index] = 0
                    elif HELD_ITEM[0] != 0:
                        # Place entire stack in crafting slot
                        if CRAFTING_GRID[slot_index] == 0:
                            CRAFTING_GRID[slot_index] = HELD_ITEM[0]
                            CRAFTING_AMOUNTS[slot_index] = HELD_ITEM[1]
                            HELD_ITEM = (0, 0)
                        elif CRAFTING_GRID[slot_index] == HELD_ITEM[0]:
                            # Same item - merge stacks
                            CRAFTING_AMOUNTS[slot_index] += HELD_ITEM[1]
                            HELD_ITEM = (0, 0)
                        else:
                            # Different item - swap
                            old_id, old_amount = CRAFTING_GRID[slot_index], CRAFTING_AMOUNTS[slot_index]
                            CRAFTING_GRID[slot_index] = HELD_ITEM[0]
                            CRAFTING_AMOUNTS[slot_index] = HELD_ITEM[1]
                            HELD_ITEM = (old_id, old_amount)
                elif event.button == 3:  # RMB: Place/remove one item
                    if HELD_ITEM[0] == 0 and CRAFTING_GRID[slot_index] != 0 and CRAFTING_AMOUNTS[slot_index] > 0:
                        # Pick up one item from crafting slot
                        HELD_ITEM = (CRAFTING_GRID[slot_index], 1)
                        CRAFTING_AMOUNTS[slot_index] -= 1
                        if CRAFTING_AMOUNTS[slot_index] <= 0:
                            CRAFTING_GRID[slot_index] = 0
                            CRAFTING_AMOUNTS[slot_index] = 0
                    elif HELD_ITEM[0] != 0:
                        # Place one item in crafting slot
                        if CRAFTING_GRID[slot_index] == 0 or CRAFTING_GRID[slot_index] == HELD_ITEM[0]:
                            CRAFTING_GRID[slot_index] = HELD_ITEM[0]
                            CRAFTING_AMOUNTS[slot_index] += 1
                            HELD_ITEM = (HELD_ITEM[0], HELD_ITEM[1] - 1) if HELD_ITEM[1] > 1 else (0, 0)
            
            # Handle craft output
            elif slot_type == 'craft_output':
                if event.button == 1:
                    craftable = get_craftable_item()
                    if craftable:
                        output_id, output_count = craftable
                        
                        # Find the matching recipe to consume ingredients
                        grid_contents = {}
                        for i in range(4):
                            item_id = CRAFTING_GRID[i]
                            amount = CRAFTING_AMOUNTS[i]
                            if item_id != 0 and amount > 0:
                                if item_id in grid_contents:
                                    grid_contents[item_id] += amount
                                else:
                                    grid_contents[item_id] = amount
                        
                        # Find matching recipe and consume exact amounts
                        for recipe_ingredients, (recipe_output_id, recipe_output_count) in CRAFTING_RECIPES.items():
                            recipe_dict = dict(recipe_ingredients)
                            
                            if recipe_output_id == output_id:
                                # Consume the exact recipe amounts
                                for i in range(4):
                                    if CRAFTING_GRID[i] != 0:
                                        item_id = CRAFTING_GRID[i]
                                        if item_id in recipe_dict:
                                            CRAFTING_AMOUNTS[i] -= recipe_dict[item_id]
                                            if CRAFTING_AMOUNTS[i] <= 0:
                                                CRAFTING_GRID[i] = 0
                                                CRAFTING_AMOUNTS[i] = 0
                                break
                        
                        player.add_to_inventory(output_id, output_count)
            
            # Handle inventory slots - click to pick up/place items
            elif slot_type == 'inventory':
                if event.button == 1:  # LMB: Pick up/place item
                    item_id, count = player.inventory[slot_index]
                    if HELD_ITEM[0] == 0:  # Not holding anything - pick up
                        HELD_ITEM = (item_id, count)
                        player.inventory[slot_index] = (0, 0)
                    elif item_id == 0:  # Empty slot - place held item
                        player.inventory[slot_index] = HELD_ITEM
                        HELD_ITEM = (0, 0)
                    elif item_id == HELD_ITEM[0]:  # Same item - try to merge
                        total = count + HELD_ITEM[1]
                        if total <= 64:
                            player.inventory[slot_index] = (item_id, total)
                            HELD_ITEM = (0, 0)
                        else:
                            player.inventory[slot_index] = (item_id, 64)
                            HELD_ITEM = (item_id, total - 64)
                    else:  # Different item - swap
                        HELD_ITEM, player.inventory[slot_index] = (item_id, count), HELD_ITEM
            
            # Handle hotbar slots
            elif slot_type == 'hotbar':
                if event.button == 1:  # LMB: Pick up/place item
                    item_id, count = player.hotbar_slots[slot_index]
                    if HELD_ITEM[0] == 0:  # Not holding anything - pick up
                        HELD_ITEM = (item_id, count)
                        player.hotbar_slots[slot_index] = (0, 0)
                    elif item_id == 0:  # Empty slot - place held item
                        player.hotbar_slots[slot_index] = HELD_ITEM
                        HELD_ITEM = (0, 0)
                    elif item_id == HELD_ITEM[0]:  # Same item - try to merge
                        total = count + HELD_ITEM[1]
                        if total <= 64:
                            player.hotbar_slots[slot_index] = (item_id, total)
                            HELD_ITEM = (0, 0)
                        else:
                            player.hotbar_slots[slot_index] = (item_id, 64)
                            HELD_ITEM = (item_id, total - 64)
                    else:  # Different item - swap
                        HELD_ITEM, player.hotbar_slots[slot_index] = (item_id, count), HELD_ITEM
                    
                    # Update held block if this is the active slot
                    player.held_block = player.hotbar_slots[player.active_slot][0]
                    
                elif event.button == 3:  # RMB: Select this slot
                    player.active_slot = slot_index
                    player.held_block = player.hotbar_slots[slot_index][0]
            
            # Handle armor slots
            elif slot_type == 'armor':
                armor_slot_names = ['helmet', 'chestplate', 'leggings', 'boots']
                slot_name = armor_slot_names[slot_index]
                
                if event.button == 1:  # LMB: Equip held item or swap
                    held_id = player.held_block
                    current_armor = player.armor_slots[slot_name]
                    
                    if held_id != 0:
                        # Check if held item is armor and matches this slot type
                        if held_id in BLOCK_TYPES:
                            held_armor_type = BLOCK_TYPES[held_id].get('armor_type')
                            if held_armor_type == slot_name:
                                # Equip held item
                                player.armor_slots[slot_name] = held_id
                                # Remove from hotbar
                                player.hotbar_slots[player.active_slot] = 0
                                player.held_block = 0
                                # If there was armor before, return it to hotbar
                                if current_armor != 0:
                                    player.hotbar_slots[player.active_slot] = current_armor
                                    player.held_block = current_armor
                    elif current_armor != 0:
                        # No held item, but armor equipped - select it
                        for i in range(9):
                            if player.hotbar_slots[i] == current_armor:
                                player.active_slot = i
                                player.held_block = current_armor
                                return
                        # Add to first empty hotbar slot
                        for i in range(9):
                            if player.hotbar_slots[i] == 0:
                                player.hotbar_slots[i] = current_armor
                                player.active_slot = i
                                player.held_block = current_armor
                                return
                
                elif event.button == 3:  # RMB: Unequip armor
                    if player.armor_slots[slot_name] != 0:
                        player.armor_slots[slot_name] = 0
            
            return  # Only handle one slot click per event

def reset_crafting_grid(player):
    """Returns items from grid to player inventory when menu closes."""
    global CRAFTING_GRID, CRAFTING_AMOUNTS
    
    for i in range(4):
        item_id = CRAFTING_GRID[i]
        amount = CRAFTING_AMOUNTS[i]
        
        if item_id != 0 and amount > 0:
            player.add_to_inventory(item_id, amount)
            
    # Clear the grid state
    CRAFTING_GRID = [0, 0, 0, 0]
    CRAFTING_AMOUNTS = [0, 0, 0, 0]

def draw_trading_menu(player):
    """Draws the trading GUI showing available trades with a villager."""
    if not player.trading_open or player.trading_villager is None:
        return
    
    villager = player.trading_villager
    
    # Dark semi-transparent background
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Trading menu box
    menu_width = min(400, SCREEN_WIDTH - 100)  # Responsive width
    menu_height = min(300, SCREEN_HEIGHT - 100)  # Responsive height
    menu_x = (SCREEN_WIDTH - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    
    pygame.draw.rect(screen, (60, 40, 20), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, (200, 180, 150), (menu_x, menu_y, menu_width, menu_height), 3)
    
    # Title
    villager_type_name = villager.villager_type.capitalize()
    title_text = FONT_BIG.render(f"Trading with {villager_type_name}", True, (255, 255, 255))
    screen.blit(title_text, (menu_x + (menu_width - title_text.get_width()) // 2, menu_y + 10))
    
    # Close instruction
    close_text = FONT_SMALL.render("Press ESC to close", True, (200, 200, 200))
    screen.blit(close_text, (menu_x + (menu_width - close_text.get_width()) // 2, menu_y + menu_height - 30))
    
    # Trades
    if villager.villager_type == "nitwit":
        no_trade_text = FONT_SMALL.render("This villager doesn't trade!", True, (255, 100, 100))
        screen.blit(no_trade_text, (menu_x + (menu_width - no_trade_text.get_width()) // 2, menu_y + 120))
    else:
        # Define trades based on type
        trades = []
        if villager.villager_type == "farmer":
            trades.append({"give": (23, 1), "get": (60, 3), "name": "1 Emerald → 3 Wheat/Carrots"})
        elif villager.villager_type == "librarian":
            trades.append({"give": (23, 1), "get": (62, 1), "name": "1 Emerald → 1 Book/Glass"})
        elif villager.villager_type == "smoker":
            trades.append({"give": (23, 1), "get": (51, 1), "name": "1 Emerald → 1 Raw Meat"})
            trades.append({"give": (51, 1), "get": (23, 1), "name": "1 Raw Meat → 1 Emerald"})
        
        # Draw trade boxes
        trade_y = menu_y + 60
        for i, trade in enumerate(trades):
            trade_box_height = 80
            trade_box_y = trade_y + i * (trade_box_height + 10)
            
            # Trade box background
            pygame.draw.rect(screen, (80, 60, 40), (menu_x + 20, trade_box_y, menu_width - 40, trade_box_height))
            pygame.draw.rect(screen, (150, 130, 100), (menu_x + 20, trade_box_y, menu_width - 40, trade_box_height), 2)
            
            # Trade text
            trade_text = FONT_SMALL.render(trade["name"], True, (255, 255, 255))
            screen.blit(trade_text, (menu_x + 40, trade_box_y + 10))
            
            # Draw give item
            give_id, give_count = trade["give"]
            give_color = BLOCK_TYPES[give_id]["color"]
            pygame.draw.rect(screen, give_color, (menu_x + 50, trade_box_y + 35, 30, 30))
            give_text = FONT_SMALL.render(f"x{give_count}", True, (255, 255, 255))
            screen.blit(give_text, (menu_x + 85, trade_box_y + 40))
            
            # Arrow
            arrow_text = FONT_BIG.render("→", True, (255, 255, 255))
            screen.blit(arrow_text, (menu_x + menu_width // 2 - 15, trade_box_y + 35))
            
            # Draw get item
            get_id, get_count = trade["get"]
            get_color = BLOCK_TYPES[get_id]["color"]
            pygame.draw.rect(screen, get_color, (menu_x + menu_width - 120, trade_box_y + 35, 30, 30))
            get_text = FONT_SMALL.render(f"x{get_count}", True, (255, 255, 255))
            screen.blit(get_text, (menu_x + menu_width - 85, trade_box_y + 40))
            
            # Click to trade button
            button_text = FONT_SMALL.render("CLICK TO TRADE", True, (0, 255, 0))
            button_rect = button_text.get_rect(center=(menu_x + menu_width // 2, trade_box_y + trade_box_height - 15))
            screen.blit(button_text, button_rect)

def handle_trading_interaction(player, event):
    """Handles mouse clicks in the trading GUI."""
    if not player.trading_open or player.trading_villager is None:
        return
    
    villager = player.trading_villager
    
    if event.button == 1:  # Left click
        mouse_x, mouse_y = event.pos
        
        # Check if clicked on trade button
        menu_width = 400
        menu_height = 300
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        
        if villager.villager_type != "nitwit":
            trade_box_height = 80
            trade_y = menu_y + 60
            
            # Check click on first trade (only one trade per villager for now)
            button_y = trade_y + trade_box_height - 15
            button_rect = pygame.Rect(menu_x + menu_width // 2 - 60, button_y - 10, 120, 20)
            
            if button_rect.collidepoint(mouse_x, mouse_y):
                # Attempt trade
                villager.attempt_trade(player)

def draw_furnace_gui(screen, player):
    """Draws the furnace smelting GUI."""
    global FURNACE_INPUT, FURNACE_FUEL, FURNACE_OUTPUT, FURNACE_PROGRESS
    
    menu_width = 300
    menu_height = 350
    menu_x = (SCREEN_WIDTH - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    
    # Background
    pygame.draw.rect(screen, (90, 90, 90), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, (60, 60, 60), (menu_x, menu_y, menu_width, menu_height), 4)
    
    # Title
    title_text = FONT_BIG.render("Furnace", True, (255, 255, 255))
    screen.blit(title_text, (menu_x + (menu_width - title_text.get_width()) // 2, menu_y + 10))
    
    # Close instruction
    close_text = FONT_SMALL.render("Press ESC to close", True, (200, 200, 200))
    screen.blit(close_text, (menu_x + (menu_width - close_text.get_width()) // 2, menu_y + menu_height - 30))
    
    # Slot positions
    input_x = menu_x + 50
    input_y = menu_y + 80
    fuel_x = menu_x + 50
    fuel_y = menu_y + 180
    output_x = menu_x + 200
    output_y = menu_y + 130
    slot_size = 50
    
    # Draw Input slot (top)
    pygame.draw.rect(screen, (50, 50, 50), (input_x, input_y, slot_size, slot_size))
    pygame.draw.rect(screen, (150, 150, 150), (input_x, input_y, slot_size, slot_size), 2)
    input_label = FONT_SMALL.render("Input", True, (255, 255, 255))
    screen.blit(input_label, (input_x, input_y - 20))
    if FURNACE_INPUT[0] != 0:
        color = BLOCK_TYPES[FURNACE_INPUT[0]]["color"]
        pygame.draw.rect(screen, color, (input_x + 5, input_y + 5, slot_size - 10, slot_size - 10))
        if FURNACE_INPUT[1] > 1:
            count_text = FONT_SMALL.render(str(FURNACE_INPUT[1]), True, (255, 255, 255))
            screen.blit(count_text, (input_x + slot_size - 15, input_y + slot_size - 15))
    
    # Draw Fuel slot (bottom)
    pygame.draw.rect(screen, (50, 50, 50), (fuel_x, fuel_y, slot_size, slot_size))
    pygame.draw.rect(screen, (150, 150, 150), (fuel_x, fuel_y, slot_size, slot_size), 2)
    fuel_label = FONT_SMALL.render("Fuel", True, (255, 255, 255))
    screen.blit(fuel_label, (fuel_x, fuel_y - 20))
    if FURNACE_FUEL[0] != 0:
        color = BLOCK_TYPES[FURNACE_FUEL[0]]["color"]
        pygame.draw.rect(screen, color, (fuel_x + 5, fuel_y + 5, slot_size - 10, slot_size - 10))
        if FURNACE_FUEL[1] > 1:
            count_text = FONT_SMALL.render(str(FURNACE_FUEL[1]), True, (255, 255, 255))
            screen.blit(count_text, (fuel_x + slot_size - 15, fuel_y + slot_size - 15))
    
    # Draw arrow (progress indicator)
    arrow_x = menu_x + 120
    arrow_y = menu_y + 140
    pygame.draw.polygon(screen, (100, 100, 100), [
        (arrow_x, arrow_y), (arrow_x + 40, arrow_y + 15), (arrow_x, arrow_y + 30)
    ])
    # Progress fill
    if FURNACE_PROGRESS > 0:
        progress_width = int(40 * (FURNACE_PROGRESS / 100))
        pygame.draw.polygon(screen, (255, 150, 0), [
            (arrow_x, arrow_y), (arrow_x + progress_width, arrow_y + 15 * (progress_width / 40)), 
            (arrow_x, arrow_y + 30 * (progress_width / 40))
        ])
    
    # Draw Output slot (right)
    pygame.draw.rect(screen, (50, 50, 50), (output_x, output_y, slot_size, slot_size))
    pygame.draw.rect(screen, (150, 150, 150), (output_x, output_y, slot_size, slot_size), 2)
    output_label = FONT_SMALL.render("Output", True, (255, 255, 255))
    screen.blit(output_label, (output_x, output_y - 20))
    if FURNACE_OUTPUT[0] != 0:
        color = BLOCK_TYPES[FURNACE_OUTPUT[0]]["color"]
        pygame.draw.rect(screen, color, (output_x + 5, output_y + 5, slot_size - 10, slot_size - 10))
        if FURNACE_OUTPUT[1] > 1:
            count_text = FONT_SMALL.render(str(FURNACE_OUTPUT[1]), True, (255, 255, 255))
            screen.blit(count_text, (output_x + slot_size - 15, output_y + slot_size - 15))
    
    # Draw dragged item if any
    if HELD_ITEM[0] != 0:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        color = BLOCK_TYPES[HELD_ITEM[0]]["color"]
        pygame.draw.rect(screen, color, (mouse_x - 15, mouse_y - 15, 30, 30))
        if HELD_ITEM[1] > 1:
            count_text = FONT_SMALL.render(str(HELD_ITEM[1]), True, (255, 255, 255))
            screen.blit(count_text, (mouse_x, mouse_y))

def update_furnace():
    """Updates furnace smelting progress."""
    global FURNACE_INPUT, FURNACE_FUEL, FURNACE_OUTPUT, FURNACE_PROGRESS, FURNACE_FUEL_TIME
    
    # Check if we have fuel burning
    if FURNACE_FUEL_TIME > 0:
        FURNACE_FUEL_TIME -= 1
    
    # Check if we can start smelting
    if FURNACE_INPUT[0] != 0 and FURNACE_INPUT[0] in SMELTING_RECIPES:
        # Need fuel to smelt
        if FURNACE_FUEL_TIME <= 0 and FURNACE_FUEL[0] != 0 and FURNACE_FUEL[0] in FUEL_ITEMS:
            # Consume 1 fuel
            fuel_id = FURNACE_FUEL[0]
            FURNACE_FUEL = (fuel_id, FURNACE_FUEL[1] - 1)
            if FURNACE_FUEL[1] <= 0:
                FURNACE_FUEL = (0, 0)
            FURNACE_FUEL_TIME = FUEL_ITEMS[fuel_id]
        
        # Smelt if we have fuel burning
        if FURNACE_FUEL_TIME > 0:
            FURNACE_PROGRESS += 2  # Progress speed (100 / 50 = 2 per frame for ~1 second smelting)
            
            if FURNACE_PROGRESS >= 100:
                # Smelting complete!
                output_id = SMELTING_RECIPES[FURNACE_INPUT[0]]
                FURNACE_INPUT = (FURNACE_INPUT[0], FURNACE_INPUT[1] - 1)
                if FURNACE_INPUT[1] <= 0:
                    FURNACE_INPUT = (0, 0)
                
                # Add to output
                if FURNACE_OUTPUT[0] == 0 or FURNACE_OUTPUT[0] == output_id:
                    FURNACE_OUTPUT = (output_id, FURNACE_OUTPUT[1] + 1)
                
                FURNACE_PROGRESS = 0
    else:
        # No valid input, reset progress
        FURNACE_PROGRESS = 0

def handle_furnace_click(player, event):
    """Handles mouse clicks in the furnace GUI."""
    global FURNACE_INPUT, FURNACE_FUEL, FURNACE_OUTPUT, HELD_ITEM
    
    if event.button != 1:  # Only left click
        return
    
    menu_width = 300
    menu_height = 350
    menu_x = (SCREEN_WIDTH - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    
    mouse_x, mouse_y = event.pos
    
    input_rect = pygame.Rect(menu_x + 50, menu_y + 80, 50, 50)
    fuel_rect = pygame.Rect(menu_x + 50, menu_y + 180, 50, 50)
    output_rect = pygame.Rect(menu_x + 200, menu_y + 130, 50, 50)
    
    # Input slot click
    if input_rect.collidepoint(mouse_x, mouse_y):
        if HELD_ITEM[0] == 0 and FURNACE_INPUT[0] != 0:
            # Pick up from input
            HELD_ITEM = FURNACE_INPUT
            FURNACE_INPUT = (0, 0)
        elif HELD_ITEM[0] != 0:
            # Place in input
            if FURNACE_INPUT[0] == 0 or FURNACE_INPUT[0] == HELD_ITEM[0]:
                FURNACE_INPUT = (HELD_ITEM[0], FURNACE_INPUT[1] + HELD_ITEM[1])
                HELD_ITEM = (0, 0)
    
    # Fuel slot click
    elif fuel_rect.collidepoint(mouse_x, mouse_y):
        if HELD_ITEM[0] == 0 and FURNACE_FUEL[0] != 0:
            # Pick up from fuel
            HELD_ITEM = FURNACE_FUEL
            FURNACE_FUEL = (0, 0)
        elif HELD_ITEM[0] != 0 and HELD_ITEM[0] in FUEL_ITEMS:
            # Place in fuel (only if it's a valid fuel)
            if FURNACE_FUEL[0] == 0 or FURNACE_FUEL[0] == HELD_ITEM[0]:
                FURNACE_FUEL = (HELD_ITEM[0], FURNACE_FUEL[1] + HELD_ITEM[1])
                HELD_ITEM = (0, 0)
    
    # Output slot click
    elif output_rect.collidepoint(mouse_x, mouse_y):
        if HELD_ITEM[0] == 0 and FURNACE_OUTPUT[0] != 0:
            # Pick up from output
            HELD_ITEM = FURNACE_OUTPUT
            FURNACE_OUTPUT = (0, 0)

def get_sky_color():
    """Returns sky color based on current time of day."""
    global TIME_PHASE
    
    if TIME_PHASE == DAY_PHASE:
        return (135, 206, 235)  # Bright blue sky
    elif TIME_PHASE == EVENING_PHASE:
        return (255, 140, 60)  # Orange evening sky
    elif TIME_PHASE == NIGHT_PHASE:
        return (10, 10, 30)  # Dark night sky
    elif TIME_PHASE == DAWN_PHASE:
        return (255, 182, 193)  # Pink dawn sky
    return (135, 206, 235)  # Default to day

def draw_crafting_table_gui(screen, player):
    """Draws the crafting table GUI with 3x3 grid and output slot."""
    menu_width = 400
    menu_height = 400
    menu_x = (SCREEN_WIDTH - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    
    # Background
    pygame.draw.rect(screen, (139, 90, 50), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(screen, (0, 0, 0), (menu_x, menu_y, menu_width, menu_height), 3)
    
    # Title
    title = FONT_SMALL.render("Crafting Table", True, (255, 255, 255))
    screen.blit(title, (menu_x + menu_width // 2 - title.get_width() // 2, menu_y + 10))
    
    # Draw 3x3 grid
    grid_start_x = menu_x + 50
    grid_start_y = menu_y + 60
    slot_size = 50
    slot_gap = 10
    
    for row in range(3):
        for col in range(3):
            slot_index = row * 3 + col
            slot_x = grid_start_x + col * (slot_size + slot_gap)
            slot_y = grid_start_y + row * (slot_size + slot_gap)
            
            # Draw slot
            pygame.draw.rect(screen, (100, 70, 40), (slot_x, slot_y, slot_size, slot_size))
            pygame.draw.rect(screen, (0, 0, 0), (slot_x, slot_y, slot_size, slot_size), 2)
            
            # Draw item in slot
            item_id, count = CRAFTING_TABLE_GRID[slot_index]
            if item_id != 0 and item_id in BLOCK_TYPES:
                if item_id in [9, 99, 100, 101, 102, 107]:  # Tools
                    draw_tool_icon(screen, pygame.Rect(slot_x + 5, slot_y + 5, slot_size - 10, slot_size - 10), item_id)
                else:
                    item_color = BLOCK_TYPES[item_id]["color"]
                    pygame.draw.rect(screen, item_color, (slot_x + 5, slot_y + 5, slot_size - 10, slot_size - 10))
                if count > 1:
                    count_text = FONT_SMALL.render(str(count), True, (255, 255, 255))
                    screen.blit(count_text, (slot_x + slot_size - count_text.get_width() - 2, slot_y + slot_size - count_text.get_height() - 2))
    
    # Draw arrow pointing to output
    arrow_x = menu_x + 220
    arrow_y = menu_y + 140
    pygame.draw.polygon(screen, (255, 255, 255), [
        (arrow_x, arrow_y),
        (arrow_x + 30, arrow_y + 10),
        (arrow_x, arrow_y + 20)
    ])
    
    # Draw output slot
    output_x = menu_x + 270
    output_y = menu_y + 130
    pygame.draw.rect(screen, (100, 70, 40), (output_x, output_y, slot_size, slot_size))
    pygame.draw.rect(screen, (255, 200, 0), (output_x, output_y, slot_size, slot_size), 3)  # Gold border
    
    # Draw output item
    item_id, count = CRAFTING_TABLE_OUTPUT
    if item_id != 0 and item_id in BLOCK_TYPES:
        if item_id in [9, 99, 100, 101, 102, 107]:  # Tools
            draw_tool_icon(screen, pygame.Rect(output_x + 5, output_y + 5, slot_size - 10, slot_size - 10), item_id)
        else:
            item_color = BLOCK_TYPES[item_id]["color"]
            pygame.draw.rect(screen, item_color, (output_x + 5, output_y + 5, slot_size - 10, slot_size - 10))
        if count > 1:
            count_text = FONT_SMALL.render(str(count), True, (255, 255, 255))
            screen.blit(count_text, (output_x + slot_size - count_text.get_width() - 2, output_y + slot_size - count_text.get_height() - 2))
    
    # Draw held item cursor
    if HELD_ITEM[0] != 0:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if HELD_ITEM[0] in [9, 99, 100, 101, 102, 107]:  # Tools
            draw_tool_icon(screen, pygame.Rect(mouse_x - 15, mouse_y - 15, 30, 30), HELD_ITEM[0])
        else:
            item_color = BLOCK_TYPES[HELD_ITEM[0]]["color"]
            pygame.draw.rect(screen, item_color, (mouse_x - 15, mouse_y - 15, 30, 30))
        if HELD_ITEM[1] > 1:
            count_text = FONT_SMALL.render(str(HELD_ITEM[1]), True, (255, 255, 255))
            screen.blit(count_text, (mouse_x + 10, mouse_y + 10))
    
    # ESC instruction
    esc_text = FONT_SMALL.render("Press ESC to close", True, (255, 255, 255))
    screen.blit(esc_text, (menu_x + menu_width // 2 - esc_text.get_width() // 2, menu_y + menu_height - 30))
    
    # Draw player's hotbar at bottom
    hotbar_y = menu_y + menu_height - 80
    hotbar_x = menu_x + 20
    for i in range(9):
        slot_x = hotbar_x + i * (slot_size + 5)
        pygame.draw.rect(screen, (80, 60, 40), (slot_x, hotbar_y, slot_size, slot_size))
        pygame.draw.rect(screen, (0, 0, 0), (slot_x, hotbar_y, slot_size, slot_size), 2)
        
        item_id, count = player.hotbar_slots[i]
        if item_id != 0 and item_id in BLOCK_TYPES:
            if item_id in [9, 99, 100, 101, 102, 107]:  # Tools
                draw_tool_icon(screen, pygame.Rect(slot_x + 5, hotbar_y + 5, slot_size - 10, slot_size - 10), item_id)
            else:
                item_color = BLOCK_TYPES[item_id]["color"]
                pygame.draw.rect(screen, item_color, (slot_x + 5, hotbar_y + 5, slot_size - 10, slot_size - 10))
            if count > 1:
                count_text = FONT_SMALL.render(str(count), True, (255, 255, 255))
                screen.blit(count_text, (slot_x + slot_size - count_text.get_width() - 2, hotbar_y + slot_size - count_text.get_height() - 2))

def handle_crafting_table_click(player, event):
    """Handles mouse clicks in the crafting table GUI."""
    global CRAFTING_TABLE_GRID, CRAFTING_TABLE_OUTPUT, HELD_ITEM
    
    if event.button != 1:  # Only left click
        return
    
    menu_width = 400
    menu_height = 400
    menu_x = (SCREEN_WIDTH - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    
    mouse_x, mouse_y = event.pos
    
    grid_start_x = menu_x + 50
    grid_start_y = menu_y + 60
    slot_size = 50
    slot_gap = 10
    
    # Check player hotbar slots first
    hotbar_y = menu_y + menu_height - 80
    hotbar_x = menu_x + 20
    for i in range(9):
        slot_x = hotbar_x + i * (slot_size + 5)
        slot_rect = pygame.Rect(slot_x, hotbar_y, slot_size, slot_size)
        
        if slot_rect.collidepoint(mouse_x, mouse_y):
            item_id, count = player.hotbar_slots[i]
            if HELD_ITEM[0] == 0 and item_id != 0:
                # Pick up from hotbar
                HELD_ITEM = (item_id, count)
                player.hotbar_slots[i] = (0, 0)
                player.held_block = 0
            elif HELD_ITEM[0] != 0:
                # Place in hotbar
                if item_id == 0 or item_id == HELD_ITEM[0]:
                    player.hotbar_slots[i] = (HELD_ITEM[0], count + HELD_ITEM[1])
                    HELD_ITEM = (0, 0)
                else:
                    # Swap items
                    player.hotbar_slots[i] = HELD_ITEM
                    HELD_ITEM = (item_id, count)
                player.held_block = player.hotbar_slots[player.active_slot][0]
            return
    
    # Check grid slots
    for row in range(3):
        for col in range(3):
            slot_index = row * 3 + col
            slot_x = grid_start_x + col * (slot_size + slot_gap)
            slot_y = grid_start_y + row * (slot_size + slot_gap)
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            
            if slot_rect.collidepoint(mouse_x, mouse_y):
                # Handle grid slot interaction
                if HELD_ITEM[0] == 0 and CRAFTING_TABLE_GRID[slot_index][0] != 0:
                    # Pick up from grid
                    HELD_ITEM = CRAFTING_TABLE_GRID[slot_index]
                    CRAFTING_TABLE_GRID[slot_index] = (0, 0)
                elif HELD_ITEM[0] != 0:
                    # Place one item in grid (right-click places one, left-click places all)
                    if CRAFTING_TABLE_GRID[slot_index][0] == 0:
                        # Empty slot - place one item
                        CRAFTING_TABLE_GRID[slot_index] = (HELD_ITEM[0], 1)
                        if HELD_ITEM[1] > 1:
                            HELD_ITEM = (HELD_ITEM[0], HELD_ITEM[1] - 1)
                        else:
                            HELD_ITEM = (0, 0)
                    elif CRAFTING_TABLE_GRID[slot_index][0] == HELD_ITEM[0]:
                        # Same item - add one
                        CRAFTING_TABLE_GRID[slot_index] = (HELD_ITEM[0], CRAFTING_TABLE_GRID[slot_index][1] + 1)
                        if HELD_ITEM[1] > 1:
                            HELD_ITEM = (HELD_ITEM[0], HELD_ITEM[1] - 1)
                        else:
                            HELD_ITEM = (0, 0)
                
                # Check for recipe match
                check_crafting_table_recipe()
                return
    
    # Check output slot
    output_x = menu_x + 270
    output_y = menu_y + 130
    output_rect = pygame.Rect(output_x, output_y, slot_size, slot_size)
    
    if output_rect.collidepoint(mouse_x, mouse_y):
        if HELD_ITEM[0] == 0 and CRAFTING_TABLE_OUTPUT[0] != 0:
            # Pick up from output
            HELD_ITEM = CRAFTING_TABLE_OUTPUT
            CRAFTING_TABLE_OUTPUT = (0, 0)
            # Clear grid after taking output
            CRAFTING_TABLE_GRID = [(0, 0) for _ in range(9)]

def draw_tool_icon(screen, rect, item_id):
    """Draw custom icons for tools instead of plain squares."""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    
    if item_id == 9:  # Wooden Pickaxe
        # Handle
        pygame.draw.rect(screen, (101, 67, 33), (x + w//2 - 2, y + h//2, 4, h//2 - 5))
        # Pickaxe head
        pygame.draw.polygon(screen, (120, 80, 40), [
            (x + w//4, y + h//4),
            (x + 3*w//4, y + h//4),
            (x + 3*w//4 - 3, y + h//2),
            (x + w//4 + 3, y + h//2)
        ])
        # Left spike
        pygame.draw.polygon(screen, (100, 70, 35), [
            (x + w//4, y + h//4),
            (x + w//4 + 3, y + h//2),
            (x + 5, y + h//3)
        ])
        # Right spike
        pygame.draw.polygon(screen, (100, 70, 35), [
            (x + 3*w//4, y + h//4),
            (x + 3*w//4 - 3, y + h//2),
            (x + w - 5, y + h//3)
        ])
    elif item_id == 99:  # Wooden Sword
        # Handle
        pygame.draw.rect(screen, (101, 67, 33), (x + w//2 - 2, y + 3*h//4, 4, h//4 - 5))
        # Guard
        pygame.draw.rect(screen, (80, 60, 30), (x + w//4, y + 3*h//4 - 3, w//2, 3))
        # Blade
        pygame.draw.polygon(screen, (160, 120, 70), [
            (x + w//2, y + 5),
            (x + w//2 + 5, y + 3*h//4 - 3),
            (x + w//2 - 5, y + 3*h//4 - 3)
        ])
    elif item_id == 100:  # Wooden Shovel
        # Handle
        pygame.draw.rect(screen, (101, 67, 33), (x + w//2 - 2, y + h//3, 4, 2*h//3 - 5))
        # Shovel head
        pygame.draw.polygon(screen, (140, 100, 60), [
            (x + w//3, y + h//3),
            (x + 2*w//3, y + h//3),
            (x + w//2, y + 5)
        ])
        pygame.draw.rect(screen, (120, 85, 50), (x + w//3 + 2, y + h//3, w//3 - 4, 3))
    elif item_id == 101:  # Wooden Spear
        # Shaft
        pygame.draw.rect(screen, (101, 67, 33), (x + w//2 - 2, y + h//4, 4, 3*h//4 - 5))
        # Spear tip
        pygame.draw.polygon(screen, (80, 60, 40), [
            (x + w//2, y + 3),
            (x + w//2 + 4, y + h//4),
            (x + w//2 - 4, y + h//4)
        ])
    elif item_id == 102:  # Wooden Axe
        # Handle
        pygame.draw.rect(screen, (101, 67, 33), (x + w//2 - 2, y + h//2, 4, h//2 - 5))
        # Axe head
        pygame.draw.polygon(screen, (130, 90, 50), [
            (x + w//2 - 3, y + h//2),
            (x + w//2 + 3, y + h//2),
            (x + w - 5, y + h//3),
            (x + w - 5, y + h//2 + 5)
        ])
        # Axe blade edge
        pygame.draw.line(screen, (110, 75, 40), (x + w - 5, y + h//3), (x + w - 5, y + h//2 + 5), 2)
    elif item_id == 107:  # Trident
        # Shaft (cyan/aqua color)
        pygame.draw.rect(screen, (0, 160, 180), (x + w//2 - 2, y + h//3, 4, 2*h//3 - 5))
        # Trident head - three prongs
        pygame.draw.polygon(screen, (0, 180, 200), [
            (x + w//2, y + 3),
            (x + w//2 + 3, y + h//3),
            (x + w//2 - 3, y + h//3)
        ])
        # Left prong
        pygame.draw.polygon(screen, (0, 180, 200), [
            (x + w//2 - 6, y + h//4),
            (x + w//2 - 8, y + 8),
            (x + w//2 - 4, y + h//3)
        ])
        # Right prong
        pygame.draw.polygon(screen, (0, 180, 200), [
            (x + w//2 + 6, y + h//4),
            (x + w//2 + 8, y + 8),
            (x + w//2 + 4, y + h//3)
        ])
    # Stone tools (109-113)
    elif item_id in [109, 110, 111, 112, 113]:
        stone_color = (128, 128, 128)
        dark_stone = (90, 90, 90)
        light_stone = (160, 160, 160)
        handle_color = (101, 67, 33)
        
        if item_id == 109:  # Stone Pickaxe
            # Handle
            pygame.draw.rect(screen, handle_color, (x + w//2 - 2, y + h//2, 4, h//2 - 5))
            # Pickaxe head base
            pygame.draw.polygon(screen, stone_color, [
                (x + w//4, y + h//4),
                (x + 3*w//4, y + h//4),
                (x + 3*w//4 - 3, y + h//2),
                (x + w//4 + 3, y + h//2)
            ])
            # Left spike with shading
            pygame.draw.polygon(screen, dark_stone, [
                (x + w//4, y + h//4),
                (x + w//4 + 3, y + h//2),
                (x + 5, y + h//3)
            ])
            pygame.draw.line(screen, light_stone, (x + w//4, y + h//4), (x + w//4 + 2, y + h//2 - 2), 1)
            # Right spike with shading
            pygame.draw.polygon(screen, dark_stone, [
                (x + 3*w//4, y + h//4),
                (x + 3*w//4 - 3, y + h//2),
                (x + w - 5, y + h//3)
            ])
            pygame.draw.line(screen, light_stone, (x + 3*w//4, y + h//4), (x + 3*w//4 - 2, y + h//2 - 2), 1)
        elif item_id == 110:  # Stone Sword
            # Handle
            pygame.draw.rect(screen, handle_color, (x + w//2 - 2, y + 3*h//4, 4, h//4 - 5))
            # Guard
            pygame.draw.rect(screen, dark_stone, (x + w//4, y + 3*h//4 - 3, w//2, 3))
            # Blade with detail
            pygame.draw.polygon(screen, stone_color, [
                (x + w//2, y + 5),
                (x + w//2 + 5, y + 3*h//4 - 3),
                (x + w//2 - 5, y + 3*h//4 - 3)
            ])
            # Blade edge highlight
            pygame.draw.line(screen, light_stone, (x + w//2, y + 5), (x + w//2 - 3, y + 3*h//4 - 3), 1)
        elif item_id == 111:  # Stone Shovel
            # Handle
            pygame.draw.rect(screen, handle_color, (x + w//2 - 2, y + h//3, 4, 2*h//3 - 5))
            # Shovel head
            pygame.draw.polygon(screen, stone_color, [
                (x + w//3, y + h//3),
                (x + 2*w//3, y + h//3),
                (x + w//2, y + 5)
            ])
            pygame.draw.rect(screen, dark_stone, (x + w//3 + 2, y + h//3, w//3 - 4, 3))
            pygame.draw.line(screen, light_stone, (x + w//2 - 2, y + 8), (x + w//2 - 4, y + h//3), 1)
        elif item_id == 112:  # Stone Spear
            # Shaft
            pygame.draw.rect(screen, handle_color, (x + w//2 - 2, y + h//4, 4, 3*h//4 - 5))
            # Spear tip with detail
            pygame.draw.polygon(screen, stone_color, [
                (x + w//2, y + 3),
                (x + w//2 + 4, y + h//4),
                (x + w//2 - 4, y + h//4)
            ])
            pygame.draw.line(screen, light_stone, (x + w//2, y + 3), (x + w//2 - 2, y + h//4 - 2), 1)
            pygame.draw.line(screen, dark_stone, (x + w//2, y + 3), (x + w//2 + 2, y + h//4 - 2), 1)
        elif item_id == 113:  # Stone Axe
            # Handle
            pygame.draw.rect(screen, handle_color, (x + w//2 - 2, y + h//2, 4, h//2 - 5))
            # Axe head with detail
            pygame.draw.polygon(screen, stone_color, [
                (x + w//2 - 3, y + h//2),
                (x + w//2 + 3, y + h//2),
                (x + w - 5, y + h//3),
                (x + w - 5, y + h//2 + 5)
            ])
            # Axe blade edge
            pygame.draw.line(screen, dark_stone, (x + w - 5, y + h//3), (x + w - 5, y + h//2 + 5), 2)
            pygame.draw.line(screen, light_stone, (x + w//2 + 2, y + h//2 + 1), (x + w - 7, y + h//3 + 2), 1)
    # Iron tools (114-118)
    elif item_id in [114, 115, 116, 117, 118]:
        iron_color = (200, 200, 200)
        dark_iron = (140, 140, 140)
        light_iron = (240, 240, 240)
        handle_color = (101, 67, 33)
        
        if item_id == 114:  # Iron Pickaxe
            # Handle
            pygame.draw.rect(screen, handle_color, (x + w//2 - 2, y + h//2, 4, h//2 - 5))
            # Pickaxe head with metallic look
            pygame.draw.polygon(screen, iron_color, [
                (x + w//4, y + h//4),
                (x + 3*w//4, y + h//4),
                (x + 3*w//4 - 3, y + h//2),
                (x + w//4 + 3, y + h//2)
            ])
            # Left spike with shine
            pygame.draw.polygon(screen, dark_iron, [
                (x + w//4, y + h//4),
                (x + w//4 + 3, y + h//2),
                (x + 5, y + h//3)
            ])
            pygame.draw.line(screen, light_iron, (x + w//4 + 1, y + h//4 + 1), (x + w//4 + 3, y + h//2 - 3), 1)
            # Right spike with shine
            pygame.draw.polygon(screen, dark_iron, [
                (x + 3*w//4, y + h//4),
                (x + 3*w//4 - 3, y + h//2),
                (x + w - 5, y + h//3)
            ])
            pygame.draw.line(screen, light_iron, (x + 3*w//4 - 1, y + h//4 + 1), (x + 3*w//4 - 3, y + h//2 - 3), 1)
        elif item_id == 115:  # Iron Sword
            # Handle
            pygame.draw.rect(screen, handle_color, (x + w//2 - 2, y + 3*h//4, 4, h//4 - 5))
            # Guard
            pygame.draw.rect(screen, dark_iron, (x + w//4, y + 3*h//4 - 3, w//2, 3))
            pygame.draw.rect(screen, light_iron, (x + w//4, y + 3*h//4 - 3, w//2, 1))
            # Blade with metallic shine
            pygame.draw.polygon(screen, iron_color, [
                (x + w//2, y + 5),
                (x + w//2 + 5, y + 3*h//4 - 3),
                (x + w//2 - 5, y + 3*h//4 - 3)
            ])
            # Blade shine line
            pygame.draw.line(screen, light_iron, (x + w//2, y + 6), (x + w//2 - 2, y + 3*h//4 - 4), 1)
        elif item_id == 116:  # Iron Shovel
            # Handle
            pygame.draw.rect(screen, handle_color, (x + w//2 - 2, y + h//3, 4, 2*h//3 - 5))
            # Shovel head with shine
            pygame.draw.polygon(screen, iron_color, [
                (x + w//3, y + h//3),
                (x + 2*w//3, y + h//3),
                (x + w//2, y + 5)
            ])
            pygame.draw.rect(screen, dark_iron, (x + w//3 + 2, y + h//3, w//3 - 4, 3))
            pygame.draw.line(screen, light_iron, (x + w//2 - 1, y + 7), (x + w//2 - 3, y + h//3 - 1), 1)
        elif item_id == 117:  # Iron Spear
            # Shaft
            pygame.draw.rect(screen, handle_color, (x + w//2 - 2, y + h//4, 4, 3*h//4 - 5))
            # Spear tip with metallic detail
            pygame.draw.polygon(screen, iron_color, [
                (x + w//2, y + 3),
                (x + w//2 + 4, y + h//4),
                (x + w//2 - 4, y + h//4)
            ])
            # Shine on tip
            pygame.draw.line(screen, light_iron, (x + w//2, y + 4), (x + w//2 - 2, y + h//4 - 3), 1)
            pygame.draw.line(screen, dark_iron, (x + w//2 + 1, y + 5), (x + w//2 + 3, y + h//4 - 2), 1)
        elif item_id == 118:  # Iron Axe
            # Handle
            pygame.draw.rect(screen, handle_color, (x + w//2 - 2, y + h//2, 4, h//2 - 5))
            # Axe head with metallic look
            pygame.draw.polygon(screen, iron_color, [
                (x + w//2 - 3, y + h//2),
                (x + w//2 + 3, y + h//2),
                (x + w - 5, y + h//3),
                (x + w - 5, y + h//2 + 5)
            ])
            # Blade edge with shine
            pygame.draw.line(screen, dark_iron, (x + w - 5, y + h//3), (x + w - 5, y + h//2 + 5), 2)
            pygame.draw.line(screen, light_iron, (x + w//2 + 2, y + h//2 + 1), (x + w - 7, y + h//3 + 3), 1)
    else:
        # Default: draw as colored square
        if item_id in BLOCK_TYPES:
            block_color = BLOCK_TYPES[item_id]["color"]
            pygame.draw.rect(screen, block_color, rect)

def check_crafting_table_recipe():
    """Checks if items in the crafting table grid match any recipe."""
    global CRAFTING_TABLE_OUTPUT
    
    # Get the current grid as a 3x3 pattern
    grid = [CRAFTING_TABLE_GRID[i][0] for i in range(9)]  # Just IDs
    
    # Check specific patterns
    # Define plank types that can be used
    plank_types = [8, 105, 106, 125, 129]  # Oak, Birch, Spruce, Jungle, Bamboo planks
    
    # Sticks: [P . .] [P . .] [. . .] - 2 planks vertically = 4 sticks (any plank type)
    if (grid[0] in plank_types and grid[1] == 0 and grid[2] == 0 and
        grid[3] in plank_types and grid[4] == 0 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 0 and grid[8] == 0 and
        grid[0] == grid[3]):
        CRAFTING_TABLE_OUTPUT = (10, 4)
        return
    
    # Wooden Pickaxe: [W W W] [. S .] [. S .] - uses WOOD not planks
    if (grid[0] == 18 and grid[1] == 18 and grid[2] == 18 and
        grid[3] == 0 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (9, 1)
        return
    
    # Also accept planks for pickaxe
    if (grid[0] in plank_types and grid[1] in plank_types and grid[2] in plank_types and
        grid[3] == 0 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0 and
        grid[0] == grid[1] == grid[2]):
        CRAFTING_TABLE_OUTPUT = (9, 1)
        return
    
    # Wooden Sword: [. P .] [. P .] [. S .] (any plank type)
    if (grid[0] == 0 and grid[1] in plank_types and grid[2] == 0 and
        grid[3] == 0 and grid[4] in plank_types and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0 and
        grid[1] == grid[4]):
        CRAFTING_TABLE_OUTPUT = (99, 1)
        return
    
    # Wooden Shovel: [. W .] [. S .] [. S .] - accepts wood or planks
    wood_types = [18, 8, 105, 106]  # Wood, Oak planks, Birch planks, Spruce planks
    if (grid[0] == 0 and grid[1] in wood_types and grid[2] == 0 and
        grid[3] == 0 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (100, 1)
        return
    
    # Wooden Spear (diagonal): [. . W] [. S .] [S . .] - accepts wood or planks
    if (grid[0] == 0 and grid[1] == 0 and grid[2] in wood_types and
        grid[3] == 0 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 10 and grid[7] == 0 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (101, 1)
        return
    
    # Wooden Axe: [P P .] [P S .] [. S .] (any plank type)
    if (grid[0] in plank_types and grid[1] in plank_types and grid[2] == 0 and
        grid[3] in plank_types and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0 and
        grid[0] == grid[1] == grid[3]):
        CRAFTING_TABLE_OUTPUT = (102, 1)
        return
    
    # Bread: [W W W] [. . .] [. . .]
    if (grid[0] == 93 and grid[1] == 93 and grid[2] == 93 and
        grid[3] == 0 and grid[4] == 0 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 0 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (103, 1)
        return
    
    # === STONE TOOLS ===
    # Stone Pickaxe: [C C C] [. S .] [. S .]
    if (grid[0] == 3 and grid[1] == 3 and grid[2] == 3 and
        grid[3] == 0 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (109, 1)
        return
    
    # Stone Sword: [. C .] [. C .] [. S .]
    if (grid[0] == 0 and grid[1] == 3 and grid[2] == 0 and
        grid[3] == 0 and grid[4] == 3 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (110, 1)
        return
    
    # Stone Shovel: [. C .] [. S .] [. S .]
    if (grid[0] == 0 and grid[1] == 3 and grid[2] == 0 and
        grid[3] == 0 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (111, 1)
        return
    
    # Stone Spear: [. . C] [. S .] [S . .]
    if (grid[0] == 0 and grid[1] == 0 and grid[2] == 3 and
        grid[3] == 0 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 10 and grid[7] == 0 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (112, 1)
        return
    
    # Stone Axe: [C C .] [C S .] [. S .]
    if (grid[0] == 3 and grid[1] == 3 and grid[2] == 0 and
        grid[3] == 3 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (113, 1)
        return
    
    # === IRON TOOLS ===
    # Iron Pickaxe: [I I I] [. S .] [. S .]
    if (grid[0] == 108 and grid[1] == 108 and grid[2] == 108 and
        grid[3] == 0 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (114, 1)
        return
    
    # Iron Sword: [. I .] [. I .] [. S .]
    if (grid[0] == 0 and grid[1] == 108 and grid[2] == 0 and
        grid[3] == 0 and grid[4] == 108 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (115, 1)
        return
    
    # Iron Shovel: [. I .] [. S .] [. S .]
    if (grid[0] == 0 and grid[1] == 108 and grid[2] == 0 and
        grid[3] == 0 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (116, 1)
        return
    
    # Iron Spear: [. . I] [. S .] [S . .]
    if (grid[0] == 0 and grid[1] == 0 and grid[2] == 108 and
        grid[3] == 0 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 10 and grid[7] == 0 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (117, 1)
        return
    
    # Iron Axe: [I I .] [I S .] [. S .]
    if (grid[0] == 108 and grid[1] == 108 and grid[2] == 0 and
        grid[3] == 108 and grid[4] == 10 and grid[5] == 0 and
        grid[6] == 0 and grid[7] == 10 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (118, 1)
        return
    
    # === IRON ARMOR ===
    # Iron Helmet: [I I I] [I . I] [. . .]
    if (grid[0] == 108 and grid[1] == 108 and grid[2] == 108 and
        grid[3] == 108 and grid[4] == 0 and grid[5] == 108 and
        grid[6] == 0 and grid[7] == 0 and grid[8] == 0):
        CRAFTING_TABLE_OUTPUT = (119, 1)
        return
    
    # Iron Chestplate: [I . I] [I I I] [I I I]
    if (grid[0] == 108 and grid[1] == 0 and grid[2] == 108 and
        grid[3] == 108 and grid[4] == 108 and grid[5] == 108 and
        grid[6] == 108 and grid[7] == 108 and grid[8] == 108):
        CRAFTING_TABLE_OUTPUT = (120, 1)
        return
    
    # Iron Leggings: [I I I] [I . I] [I . I]
    if (grid[0] == 108 and grid[1] == 108 and grid[2] == 108 and
        grid[3] == 108 and grid[4] == 0 and grid[5] == 108 and
        grid[6] == 108 and grid[7] == 0 and grid[8] == 108):
        CRAFTING_TABLE_OUTPUT = (121, 1)
        return
    
    # Iron Boots: [. . .] [I . I] [I . I]
    if (grid[0] == 0 and grid[1] == 0 and grid[2] == 0 and
        grid[3] == 108 and grid[4] == 0 and grid[5] == 108 and
        grid[6] == 108 and grid[7] == 0 and grid[8] == 108):
        CRAFTING_TABLE_OUTPUT = (122, 1)
        return
    
    # No match
    CRAFTING_TABLE_OUTPUT = (0, 0)

def spawn_night_mobs():
    """Spawns hostile mobs across the entire world when night begins."""
    print("=" * 60)
    print("🌙 SPAWN_NIGHT_MOBS FUNCTION CALLED!")
    print("=" * 60)
    
    mobs_spawned = 0
    total_checked = 0
    skipped_surface = 0
    skipped_sky = 0
    
    print(f"🌙 Starting night mob spawn... GRID_WIDTH={GRID_WIDTH}, checking every 20 blocks")
    
    for col in range(0, GRID_WIDTH, 20):  # Every 20 blocks
        total_checked += 1
        ground_row = 0
        for row in range(GRID_HEIGHT - 1, -1, -1):
            if WORLD_MAP[row][col] != 0:
                ground_row = row
                break
        
        # Check if valid surface block
        surface_block = WORLD_MAP[ground_row][col]
        is_valid_surface = (surface_block == GRASS_ID or surface_block == SAND_ID or
                            surface_block == SNOW_ID or surface_block == ICE_ID or
                            surface_block == MUD_ID or surface_block == COARSE_DIRT_ID or
                            surface_block == 123)  # Podzol
        
        # Check for sky access (at least 3 air blocks above)
        has_sky_access = True
        if ground_row >= 3:
            for check_row in range(ground_row - 3, ground_row):
                if WORLD_MAP[check_row][col] != AIR_ID:
                    has_sky_access = False
                    break
        
        # Skip if not valid surface or no sky access
        if not is_valid_surface:
            skipped_surface += 1
            continue
        if not has_sky_access:
            skipped_sky += 1
            continue
        
        spawn_x = col * BLOCK_SIZE
        spawn_y = (ground_row - 2) * BLOCK_SIZE
        biome_type = BIOME_MAP[col]
        
        # Spawn hostile mobs based on biome (100% chance at each location)
        if biome_type == DESERT_BIOME:
            if random.random() < 0.5:
                MOBS.add(Zombie(spawn_x, spawn_y, biome_type=DESERT_BIOME))  # Creates Husk
                mobs_spawned += 1
            if random.random() < 0.4:
                MOBS.add(Parched(spawn_x, spawn_y))  # Gray skeleton with yellow wrappings
                mobs_spawned += 1
            if random.random() < 0.2:
                MOBS.add(ZombieCamel(spawn_x, spawn_y))  # Brown zombie camel
                mobs_spawned += 1
            if random.random() < 0.2:
                MOBS.add(Spider(spawn_x, spawn_y))
                mobs_spawned += 1
        elif biome_type == SNOW_BIOME:
            if random.random() < 0.5:
                MOBS.add(Skeleton(spawn_x, spawn_y, is_stray=True))  # Creates Stray
                mobs_spawned += 1
            if random.random() < 0.3:
                MOBS.add(Bear(spawn_x, spawn_y))  # Bear instead of PolarBear
                mobs_spawned += 1
        elif biome_type == SWAMP_BIOME:
            if random.random() < 0.8:  # Increased from 0.5 to 0.8
                MOBS.add(Drowned(spawn_x, spawn_y))
                mobs_spawned += 1
            if random.random() < 0.3:
                MOBS.add(Witch(spawn_x, spawn_y))
                mobs_spawned += 1
        elif biome_type == LAKE_BIOME:  # Also spawn drowned in lakes
            if random.random() < 0.7:
                MOBS.add(Drowned(spawn_x, spawn_y))
                mobs_spawned += 1
        elif biome_type == JUNGLE_BIOME or biome_type == BAMBOO_JUNGLE_BIOME:
            if random.random() < 0.6:
                MOBS.add(Zombie(spawn_x, spawn_y))
                mobs_spawned += 1
            if random.random() < 0.4:
                MOBS.add(Creeper(spawn_x, spawn_y))
                mobs_spawned += 1
        else:  # Default biomes (plains, forest, taiga, etc.)
            if random.random() < 0.6:
                MOBS.add(Zombie(spawn_x, spawn_y))
                mobs_spawned += 1
            if random.random() < 0.4:
                MOBS.add(Skeleton(spawn_x, spawn_y))
                mobs_spawned += 1
            if random.random() < 0.3:
                MOBS.add(Creeper(spawn_x, spawn_y))
                mobs_spawned += 1
            if random.random() < 0.05:  # 5% chance for zombie horse
                MOBS.add(ZombieHorse(spawn_x, spawn_y))
                mobs_spawned += 1
                print(f"🐴💀 Zombie Horse spawned at ({col}, {ground_row})!")
    
    print(f"   📊 Checked {total_checked} locations, skipped {skipped_surface} (invalid surface) + {skipped_sky} (no sky access)")
    print(f"   ✅ Spawned {mobs_spawned} hostile mobs! Total mobs in world: {len(MOBS)}")

def update_time_of_day():
    """Updates the global time counter and phase. Spawns all hostile mobs when night begins."""
    global TIME_OF_DAY, TIME_PHASE
    
    previous_phase = TIME_PHASE
    TIME_OF_DAY = (TIME_OF_DAY + 1) % TOTAL_CYCLE_LENGTH
    
    # Determine current phase
    if TIME_OF_DAY < DAY_LENGTH:
        TIME_PHASE = DAY_PHASE
    elif TIME_OF_DAY < DAY_LENGTH + EVENING_LENGTH:
        TIME_PHASE = EVENING_PHASE
    elif TIME_OF_DAY < DAY_LENGTH + EVENING_LENGTH + NIGHT_LENGTH:
        TIME_PHASE = NIGHT_PHASE
    else:
        TIME_PHASE = DAWN_PHASE
    
    # Debug: Print phase transitions
    if previous_phase != TIME_PHASE:
        phase_names = {DAY_PHASE: "DAY", EVENING_PHASE: "EVENING", NIGHT_PHASE: "NIGHT", DAWN_PHASE: "DAWN"}
        print(f"⏰ TIME PHASE CHANGED: {phase_names.get(previous_phase, 'UNKNOWN')} → {phase_names.get(TIME_PHASE, 'UNKNOWN')} (Frame: {TIME_OF_DAY}/{TOTAL_CYCLE_LENGTH})")
    
    # When transitioning from evening to night, instantly spawn all hostile mobs
    if previous_phase == EVENING_PHASE and TIME_PHASE == NIGHT_PHASE:
        print("🌙 NIGHT BEGINS! Spawning all hostile mobs instantly...")
        print(f"   previous_phase={previous_phase}, TIME_PHASE={TIME_PHASE}")
        spawn_night_mobs()
    else:
        # Debug when NOT spawning
        if previous_phase != TIME_PHASE:
            print(f"   ℹ️ Not spawning mobs: previous_phase={previous_phase}, TIME_PHASE={TIME_PHASE}")


# --- Game Loop Setup ---

# Respawn timer (5 minutes = 300 seconds * 60 FPS = 18,000 frames)
RESPAWN_TIMER = 0
RESPAWN_INTERVAL = 18000  # 5 minutes

# Structure spawn notifications (list of [name, column, timer])
STRUCTURE_NOTIFICATIONS = []

# Initial World and Mob Generation
WORLD_MAP, MOBS, BIOME_MAP = generate_world()

# Find a safe spawn spot
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

# Arrow projectiles group
ARROWS = pygame.sprite.Group()

# Splash potion projectiles group
SPLASH_POTIONS = pygame.sprite.Group()

# Trident projectiles group
TRIDENTS = pygame.sprite.Group()

# Dropped items group
DROPPED_ITEMS = pygame.sprite.Group()

# Sapling growth tracking: {(col, row): (sapling_id, planted_time)}
SAPLING_GROWTH = {}

# Light sources tracking: {(col, row)} - blocks that emit light
LIGHT_SOURCES = set()

# Open doors tracking (for auto-close)
OPEN_DOORS = []

running = True
water_flow_timer = 0  # Timer to control water flow updates

# --- Main Game Loop ---
while running:
    
    # Update day/night cycle
    update_time_of_day()
    
    # Check and load chunks based on player position
    player_col = player.rect.centerx // BLOCK_SIZE
    shift_player = check_and_load_chunks(player_col)
    
    # If a chunk was added to the left, shift player position right
    if shift_player:
        player.rect.x += CHUNK_SIZE * BLOCK_SIZE
        print(f"🔀 Shifted player right by {CHUNK_SIZE} blocks to account for new left chunk")
    
    # 1. EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle window resize
        if event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH = event.w
            SCREEN_HEIGHT = event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if CRAFTING_TABLE_OPEN:
                    # Return items from crafting table to player inventory
                    for item_id, count in CRAFTING_TABLE_GRID:
                        if item_id != 0:
                            player.add_to_inventory(item_id, count)
                    if CRAFTING_TABLE_OUTPUT[0] != 0:
                        player.add_to_inventory(CRAFTING_TABLE_OUTPUT[0], CRAFTING_TABLE_OUTPUT[1])
                    if HELD_ITEM[0] != 0:
                        player.add_to_inventory(HELD_ITEM[0], HELD_ITEM[1])
                    CRAFTING_TABLE_OPEN = False
                    CRAFTING_TABLE_GRID = [(0, 0) for _ in range(9)]
                    CRAFTING_TABLE_OUTPUT = (0, 0)
                    HELD_ITEM = (0, 0)
                elif FURNACE_OPEN:
                    # Return items from furnace to player inventory
                    if FURNACE_INPUT[0] != 0:
                        player.add_to_inventory(FURNACE_INPUT[0], FURNACE_INPUT[1])
                    if FURNACE_FUEL[0] != 0:
                        player.add_to_inventory(FURNACE_FUEL[0], FURNACE_FUEL[1])
                    if FURNACE_OUTPUT[0] != 0:
                        player.add_to_inventory(FURNACE_OUTPUT[0], FURNACE_OUTPUT[1])
                    if HELD_ITEM[0] != 0:
                        player.add_to_inventory(HELD_ITEM[0], HELD_ITEM[1])
                    FURNACE_OPEN = False
                    FURNACE_INPUT = (0, 0)
                    FURNACE_FUEL = (0, 0)
                    FURNACE_OUTPUT = (0, 0)
                    FURNACE_PROGRESS = 0
                    HELD_ITEM = (0, 0)
                elif player.trading_open:
                    player.trading_open = False
                    player.trading_villager = None
                elif player.is_crafting:
                    reset_crafting_grid(player) # Cleanup on Escape
                    player.is_crafting = False
                elif player.inventory_open:
                    reset_crafting_grid(player)  # Return crafting items when closing inventory
                    player.inventory_open = False
                else:
                    running = False
            
            # C key to open crafting from inventory
            if event.key == pygame.K_c and player.inventory_open and not player.is_crafting:
                player.is_crafting = True
            
            # E key to open crafting table when hovering over it
            if event.key == pygame.K_e and not player.inventory_open and not player.is_crafting:
                # Get target block
                mouse_x, mouse_y = pygame.mouse.get_pos()
                camera_x, camera_y = calculate_camera_offset(player.rect)
                target_world_x = mouse_x + camera_x
                target_world_y = mouse_y + camera_y
                target_col = int(target_world_x // BLOCK_SIZE)
                target_row = int(target_world_y // BLOCK_SIZE)
                
                if 0 <= target_row < GRID_HEIGHT and 0 <= target_col < GRID_WIDTH:
                    if WORLD_MAP[target_row][target_col] == 92:  # Crafting table ID
                        CRAFTING_TABLE_OPEN = True
                        CRAFTING_TABLE_POS = (target_col, target_row)
            
            # Q key to throw/drop items
            if event.key == pygame.K_q:
                # Drop the currently held item from hotbar
                if player.held_block != 0:
                    # Find the item in hotbar
                    for i in range(9):
                        item_id, count = player.hotbar_slots[i]
                        if item_id == player.held_block and count > 0:
                            drop_x = player.rect.centerx
                            drop_y = player.rect.centery
                            DROPPED_ITEMS.add(DroppedItem(drop_x, drop_y, item_id, 1))
                            # Remove one from hotbar slot
                            new_count = count - 1
                            if new_count <= 0:
                                player.hotbar_slots[i] = (0, 0)
                                player.held_block = 0
                            else:
                                player.hotbar_slots[i] = (item_id, new_count)
                            break
            
            # No instant eat on key press - moved to hold F logic below
        
        # Mouse Interaction (Mining/Placing/Attacking OR Crafting OR Inventory OR Trading OR Crafting Table)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if CRAFTING_TABLE_OPEN:
                handle_crafting_table_click(player, event)
            elif FURNACE_OPEN:
                handle_furnace_click(player, event)
            elif player.trading_open:
                handle_trading_interaction(player, event)
            elif player.is_crafting:
                handle_crafting_interaction(player, event)
            elif player.inventory_open:
                handle_inventory_interaction(player, event)
            else:
                camera_x, camera_y = calculate_camera_offset(player.rect)
                handle_interaction(player, MOBS, event, camera_x, camera_y, MOBS)

    # 2. INPUT PROCESSING
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    
    # Handle spear charging
    if player.is_charging:
        # Apply charge velocity
        player.vel_x = player.charge_velocity
        
        # Decrease charge timer
        player.charge_timer -= 1
        
        # End charge if timer runs out
        if player.charge_timer <= 0 or abs(player.charge_velocity) < 1:
            player.is_charging = False
            player.charge_velocity = 0
            player.charge_hit_mobs = set()
        else:
            # Check for mob collisions during charge - extended hitbox for spear
            held_id = player.held_block
            if held_id in BLOCK_TYPES:
                tool_data = BLOCK_TYPES[held_id]
                attack_range = tool_data.get("attack_range", 1) * BLOCK_SIZE
                damage = tool_data.get("damage_bonus", 2) + 3  # Base damage + bonus
                
                # Determine charge direction based on velocity
                charge_dir = 1 if player.charge_velocity > 0 else -1
                
                # Create extended hitbox in front of player for spear reach
                spear_hitbox = pygame.Rect(
                    player.rect.centerx + (attack_range if charge_dir > 0 else -attack_range),
                    player.rect.top,
                    attack_range,
                    player.rect.height
                )
                
                # Check all mobs for collision with spear hitbox
                for mob in MOBS:
                    if mob not in player.charge_hit_mobs:
                        if spear_hitbox.colliderect(mob.rect):
                            mob.take_damage(damage, MOBS)
                            player.charge_hit_mobs.add(mob)  # Mark as hit so we don't hit again
                            print(f"⚔️ Charge attack hit {mob.__class__.__name__}! {damage} damage!")
                
                # Apply durability damage periodically during charge
                if player.charge_timer % 10 == 0:
                    if held_id in BLOCK_TYPES and "durability" in BLOCK_TYPES[held_id]:
                        slot_key = ('hotbar', player.active_slot)
                        current_durability = player.tool_durability.get(slot_key, BLOCK_TYPES[held_id]["durability"])
                        current_durability -= 1
                        
                        if current_durability <= 0:
                            player.hotbar_slots[player.active_slot] = (0, 0)
                            player.held_block = 0
                            if slot_key in player.tool_durability:
                                del player.tool_durability[slot_key]
                            player.is_charging = False
                            player.charge_velocity = 0
                            print(f"💔 {BLOCK_TYPES[held_id]['name']} broke!")
                        else:
                            player.tool_durability[slot_key] = current_durability
                
                # Decelerate charge over time
                player.charge_velocity *= 0.95
    
    # Hold F to eat food (1 second) or drink/throw potions (2 seconds)
    if keys[pygame.K_f] and player.held_block != 0:
        # Define food items and their hunger restoration
        food_items = {
            94: 2,   # Carrot: +2 hunger
            13: 1,   # Rotten Flesh: +1 hunger
            50: 3,   # Mutton: +3 hunger
            51: 3,   # Beef: +3 hunger
            81: 2,   # Chicken: +2 hunger
            82: 3,   # Pork: +3 hunger
            87: 5,   # Cooked Beef: +5 hunger
            88: 5,   # Cooked Mutton: +5 hunger
            89: 4,   # Cooked Chicken: +4 hunger
            90: 5,   # Cooked Pork: +5 hunger
            103: 4,  # Bread: +4 hunger
            136: 3,  # Apple: +3 hunger
            137: 3,  # Orange: +3 hunger
            138: 3,  # Banana: +3 hunger
            144: 1,  # Berry: +1 hunger
            154: 2,  # Bird Meat: +2 hunger
            155: 4,  # Cooked Bird Meat: +4 hunger
            156: 2,  # Cod: +2 hunger
            157: 5,  # Cooked Cod: +5 hunger
            158: 2,  # Salmon: +2 hunger
            159: 6,  # Cooked Salmon: +6 hunger
            165: 1,  # Tropical Fish Meat: +1 hunger
        }
        
        # Potion items (drinkable and splash)
        potion_items = [131, 132, 133]  # Healing Potion, Splash Healing, Splash Poison
        
        if player.held_block in food_items:
            player.eating_timer += 1
            if player.eating_timer >= player.eating_duration:
                # Find and consume the item
                for i in range(9):
                    item_id, count = player.hotbar_slots[i]
                    if item_id == player.held_block and count > 0:
                        # Eat the food
                        hunger_gain = food_items[player.held_block]
                        player.hunger = min(player.max_hunger, player.hunger + hunger_gain)
                        print(f"🍖 Ate {BLOCK_TYPES[player.held_block]['name']}! +{hunger_gain} hunger")
                        
                        # Remove one from hotbar
                        new_count = count - 1
                        if new_count <= 0:
                            player.hotbar_slots[i] = (0, 0)
                            player.held_block = 0
                        else:
                            player.hotbar_slots[i] = (item_id, new_count)
                        player.eating_timer = 0
                        break
        elif player.held_block in potion_items:
            player.drinking_timer += 1
            if player.drinking_timer >= player.drinking_duration:
                # Find and use the potion
                for i in range(9):
                    item_id, count = player.hotbar_slots[i]
                    if item_id == player.held_block and count > 0:
                        potion_type = BLOCK_TYPES[player.held_block].get("potion_type", "drinkable")
                        
                        if potion_type == "drinkable":
                            # Drink healing potion
                            heal_amount = BLOCK_TYPES[player.held_block].get("heal_amount", 6)
                            player.health = min(player.max_health, player.health + heal_amount)
                            print(f"❤️ Drank {BLOCK_TYPES[player.held_block]['name']}! +{heal_amount} HP")
                        else:  # splash potion
                            # Throw splash potion
                            direction = 1 if not hasattr(player, 'facing_left') or not player.facing_left else -1
                            if 'SPLASH_POTIONS' in globals():
                                SPLASH_POTIONS.add(SplashPotion(
                                    player.rect.centerx,
                                    player.rect.centery,
                                    direction,
                                    player.held_block
                                ))
                                print(f"🧪 Threw {BLOCK_TYPES[player.held_block]['name']}!")
                        
                        # Remove one from hotbar
                        new_count = count - 1
                        if new_count <= 0:
                            player.hotbar_slots[i] = (0, 0)
                            player.held_block = 0
                        else:
                            player.hotbar_slots[i] = (item_id, new_count)
                        player.drinking_timer = 0
                        break
        else:
            player.eating_timer = 0
            player.drinking_timer = 0
    else:
        player.eating_timer = 0
        player.drinking_timer = 0

    # 3. GAME LOGIC UPDATE
    if not player.is_crafting and not player.inventory_open: 
        player.update()
        
        # Sunlight damage for hostile mobs only (zombies, skeletons, witches)
        if TIME_PHASE == DAY_PHASE:
            for mob in MOBS:
                # Only burn hostile mobs (skip all passive/neutral mobs and special cases)
                if isinstance(mob, (Cow, Pig, Sheep, Chicken, Rabbit, Horse, Camel, Penguin, Fox, Wolf, Frog, Slime, 
                                   Deer, Bear, Spider, Creeper, Narwhal, Turtle, Panda, Monkey, Villager, IronGolem, Drowned,
                                   Lion, Rhino, Ostrich, Elephant, Bird)):
                    continue
                
                # Skip zombie horses (undead but immune to sunlight)
                if isinstance(mob, ZombieHorse):
                    continue
                
                # Check if husk (husks don't burn) - skip husks
                if isinstance(mob, Zombie) and hasattr(mob, 'is_husk') and mob.is_husk:
                    continue
                
                # All other mobs (zombies, skeletons, witches, etc.) burn in sunlight
                mob_col = mob.rect.centerx // BLOCK_SIZE
                mob_row = mob.rect.top // BLOCK_SIZE
                
                if 0 <= mob_col < GRID_WIDTH and 0 <= mob_row < GRID_HEIGHT:
                    # Check all blocks above for sky exposure
                    exposed_to_sky = True
                    for check_row in range(0, mob_row):
                        if WORLD_MAP[check_row][mob_col] != 0:  # Found a block above
                            exposed_to_sky = False
                            break
                    
                    # Apply burn damage every second
                    if exposed_to_sky and not hasattr(mob, 'sunlight_timer'):
                        mob.sunlight_timer = 0
                    
                    if exposed_to_sky:
                        mob.sunlight_timer = getattr(mob, 'sunlight_timer', 0) + 1
                        if mob.sunlight_timer >= FPS * 1:  # Every second
                            mob.take_damage(1)
                            mob.sunlight_timer = 0
        
        # Update mobs (special handling for skeletons with arrows)
        for mob in MOBS:
            if isinstance(mob, Skeleton):
                mob.update(WORLD_MAP, player, MOBS, ARROWS)
            else:
                mob.update(WORLD_MAP, player, MOBS)
        
        # Update arrows
        ARROWS.update(WORLD_MAP, player, MOBS)
        
        # Update splash potions
        SPLASH_POTIONS.update(WORLD_MAP, player, MOBS)
        
        # Update tridents
        TRIDENTS.update(WORLD_MAP, player, MOBS)
        
        # Update furnace smelting
        if FURNACE_OPEN:
            update_furnace()
        
        # Update dropped items
        DROPPED_ITEMS.update()
        
        # Update sapling growth (1 day cycle = 12 minutes = 43,200 frames)
        for (col, row), (sapling_id, planted_time) in list(SAPLING_GROWTH.items()):
            growth_time = TIME_OF_DAY - planted_time
            if growth_time < 0:  # Handle day cycle wrap-around
                growth_time += TOTAL_CYCLE_LENGTH
            
            # Grow into tree after 1 full day cycle (43,200 frames)
            if growth_time >= TOTAL_CYCLE_LENGTH:
                # Remove sapling
                if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                    if WORLD_MAP[row][col] in [139, 140, 141, 142]:  # Is still a sapling
                        WORLD_MAP[row][col] = 0  # Remove sapling
                        
                        # Grow tree based on sapling type
                        tree_type = BLOCK_TYPES[sapling_id].get("tree_type", "oak")
                        if tree_type == "oak":
                            generate_tree(WORLD_MAP, col, row - 1, OAK_FOREST_BIOME)
                        elif tree_type == "birch":
                            generate_tree(WORLD_MAP, col, row - 1, BIRCH_FOREST_BIOME)
                        elif tree_type == "spruce":
                            generate_tree(WORLD_MAP, col, row - 1, TAIGA_BIOME)
                        elif tree_type == "jungle":
                            generate_tree(WORLD_MAP, col, row - 1, JUNGLE_BIOME)
                        elif tree_type == "acacia":
                            generate_tree(WORLD_MAP, col, row - 1, SAVANNAH_BIOME)
                        
                        print(f"🌳 Sapling grew into {tree_type} tree at X:{col} Y:{row}!")
                
                # Remove from tracking
                del SAPLING_GROWTH[(col, row)]
        
        # Check player collision with dropped items
        collected_items = pygame.sprite.spritecollide(player, DROPPED_ITEMS, True)
        for dropped_item in collected_items:
            player.add_to_inventory(dropped_item.item_id, dropped_item.amount)
        
        # Respawn timer - every 5 minutes, clear and respawn mobs based on time of day
        RESPAWN_TIMER += 1
        
        # Debug: Show timer every minute
        if RESPAWN_TIMER % 3600 == 0:  # Every 60 seconds
            minutes_passed = RESPAWN_TIMER // 3600
            print(f"⏱️ Respawn timer: {minutes_passed} minute(s) / 5 minutes")
        
        if RESPAWN_TIMER >= RESPAWN_INTERVAL:
            RESPAWN_TIMER = 0
            
            print(f"⏰ RESPAWN TIMER TRIGGERED! Current mob count: {len(MOBS)}")
            
            # Only spawn hostile mobs at night, passive mobs during day
            if TIME_PHASE == NIGHT_PHASE or TIME_PHASE == EVENING_PHASE:
                print("🌙 RESPAWN TIMER (NIGHT): Spawning additional hostiles...")
                # Don't remove existing mobs - just add new ones
                
                # Immediately spawn new hostile mobs across the world
                mobs_spawned = 0
                for col in range(0, GRID_WIDTH, 20):  # Every 20 blocks
                    ground_row = 0
                    for row in range(GRID_HEIGHT - 1, -1, -1):
                        if WORLD_MAP[row][col] != 0:
                            ground_row = row
                            break
                    
                    # Check if valid surface block
                    surface_block = WORLD_MAP[ground_row][col]
                    is_valid_surface = (surface_block == GRASS_ID or surface_block == SAND_ID or
                                        surface_block == SNOW_ID or surface_block == ICE_ID or
                                        surface_block == MUD_ID or surface_block == COARSE_DIRT_ID or
                                        surface_block == 123)  # Podzol
                    
                    # Check for sky access (at least 3 air blocks above)
                    has_sky_access = True
                    if ground_row >= 3:
                        for check_row in range(ground_row - 3, ground_row):
                            if WORLD_MAP[check_row][col] != AIR_ID:
                                has_sky_access = False
                                break
                    
                    # Skip if not valid surface or no sky access
                    if not is_valid_surface or not has_sky_access:
                        continue
                    
                    spawn_x = col * BLOCK_SIZE
                    spawn_y = (ground_row - 2) * BLOCK_SIZE
                    biome_type = BIOME_MAP[col]
                    
                    # Spawn hostile mobs based on biome
                    if random.random() < 0.3:  # 30% chance per spawn point
                        if biome_type == DESERT_BIOME:
                            MOBS.add(Zombie(spawn_x, spawn_y, biome_type))  # Husk
                        elif biome_type == SNOW_BIOME:
                            MOBS.add(Skeleton(spawn_x, spawn_y, is_stray=True))
                        elif biome_type == SWAMP_BIOME:
                            MOBS.add(Zombie(spawn_x, spawn_y, biome_type))
                        else:
                            mob_choice = random.choice([Zombie, Skeleton, Spider, Creeper])
                            if mob_choice == Zombie:
                                MOBS.add(Zombie(spawn_x, spawn_y, biome_type))
                            else:
                                MOBS.add(mob_choice(spawn_x, spawn_y))
                        mobs_spawned += 1
                
                print(f"👹 Spawned {mobs_spawned} hostile mobs!")
            else:
                print("☀️ RESPAWN TIMER (DAY): No mob despawning - mobs persist...")
                # Don't remove any mobs during day
                print(f"✅ Current mob count: {len(MOBS)}")
            
            print(f"✅ Respawn cycle complete! Final mob count: {len(MOBS)}")
        
        # Continuous mob spawning within render distance
        camera_x, camera_y = calculate_camera_offset(player.rect)
        render_distance_x = SCREEN_WIDTH // 2 + BLOCK_SIZE * 15
        render_distance_y = SCREEN_HEIGHT // 2 + BLOCK_SIZE * 15
        
        # Check if hostile spawning is allowed (only at night/evening)
        is_hostile_time = (TIME_PHASE == NIGHT_PHASE or TIME_PHASE == EVENING_PHASE)
        
        # Only spawn mobs occasionally (every 10 frames) to avoid lag
        if not hasattr(player, 'spawn_check_timer'):
            player.spawn_check_timer = 0
        player.spawn_check_timer += 1
        
        if player.spawn_check_timer >= 30:  # Check every 30 frames (0.5 seconds) instead of 10
            player.spawn_check_timer = 0
            
            # Limit total mob count to prevent lag
            if len(MOBS) > 1000:
                pass  # Skip spawning if too many mobs
            else:
                # Debug: Track spawn attempts
                spawn_attempts = 0
                spawned_count = 0
                hostile_spawned = 0  # Track hostile mob spawns separately
                skipped_distance = 0
                skipped_crowded = 0
                skipped_surface = 0
                skipped_sky = 0
                
                # Iterate through world columns for spawning
                for col in range(0, GRID_WIDTH, 5):  # Check every 5 blocks instead of 10 for better spawning
                    spawn_x = col * BLOCK_SIZE
                    
                    # Only spawn if within render distance of player (but not too close)
                    distance_from_player = abs(spawn_x - player.rect.centerx)
                    if distance_from_player > render_distance_x or distance_from_player < BLOCK_SIZE * 15:
                        skipped_distance += 1
                        continue  # Don't spawn too far or too close (15 blocks minimum)
                    
                    spawn_attempts += 1
                    
                    # Check if there's already a mob nearby (within 3 blocks)
                    too_close = False
                    for mob in MOBS:
                        if abs(mob.rect.centerx - spawn_x) < BLOCK_SIZE * 3:
                            too_close = True
                            break
                    
                    if too_close:
                        skipped_crowded += 1
                        continue
                    
                    # Find ground level
                    ground_row = 0
                    for row in range(GRID_HEIGHT - 1, -1, -1):
                        if WORLD_MAP[row][col] != 0:
                            ground_row = row
                            break
                    
                    # Check if valid surface
                    surface_block = WORLD_MAP[ground_row][col]
                    is_valid_surface = (surface_block == GRASS_ID or surface_block == SAND_ID or
                                        surface_block == SNOW_ID or surface_block == ICE_ID or
                                        surface_block == MUD_ID or surface_block == COARSE_DIRT_ID or
                                        surface_block == 123)  # Podzol for jungle
                    
                    # Check for sky access (at least 3 air blocks above to prevent underground spawning)
                    has_sky_access = True
                    if ground_row >= 3:
                        for check_row in range(ground_row - 3, ground_row):
                            if WORLD_MAP[check_row][col] != AIR_ID:
                                has_sky_access = False
                                break
                    
                    if not is_valid_surface:
                        skipped_surface += 1
                    if not has_sky_access:
                        skipped_sky += 1
                    
                    if ground_row < GRID_HEIGHT and is_valid_surface and has_sky_access:
                        spawn_y = (ground_row - 2) * BLOCK_SIZE
                        
                        # Check if there's a light source nearby (prevents hostile mob spawning)
                        is_lit = False
                        for light_col, light_row in LIGHT_SOURCES:
                            light_distance = abs(light_col - col) + abs(light_row - ground_row)
                            if light_distance <= 8:  # Light radius of 8 blocks
                                is_lit = True
                                break
                        
                        # Get biome type from 1D biome map
                        biome_type = BIOME_MAP[col]
                        
                        # Random spawn chance (increased for better population)
                        if biome_type == SWAMP_BIOME:
                            r = random.random()
                            if is_hostile_time and not is_lit and r < 0.05:
                                zombie = Zombie(spawn_x, spawn_y, biome_type)
                                MOBS.add(zombie)
                                spawned_count += 1
                                hostile_spawned += 1
                                print(f"   🧟 Zombie spawned at ({col}, {ground_row}) - screen pos ({spawn_x//BLOCK_SIZE}, {spawn_y//BLOCK_SIZE})")
                            if is_hostile_time and not is_lit and r < 0.08:
                                MOBS.add(Slime(spawn_x, spawn_y))
                                spawned_count += 1
                                hostile_spawned += 1
                            if r < 0.12:
                                MOBS.add(Frog(spawn_x, spawn_y + BLOCK_SIZE))
                                spawned_count += 1
                            if is_hostile_time and not is_lit and r < 0.03:
                                MOBS.add(Witch(spawn_x, spawn_y))
                                spawned_count += 1
                                hostile_spawned += 1
                        elif biome_type == TAIGA_BIOME:
                            r = random.random()
                            if is_hostile_time and not is_lit and r < 0.02:
                                MOBS.add(Skeleton(spawn_x, spawn_y, is_stray=True))
                                spawned_count += 1
                                hostile_spawned += 1
                            if r < 0.06:
                                MOBS.add(Wolf(spawn_x, spawn_y))
                                spawned_count += 1
                            if r < 0.06:
                                MOBS.add(Fox(spawn_x, spawn_y))
                                spawned_count += 1
                        elif biome_type == DESERT_BIOME:
                            r = random.random()
                            if r < 0.08:
                                camel = Camel(spawn_x, spawn_y + BLOCK_SIZE)
                                camel.health = random.randint(5, 15)  # Spawn with damage
                                MOBS.add(camel)
                                spawned_count += 1
                            if r < 0.23:  # Rabbits - fast desert mob
                                MOBS.add(Rabbit(spawn_x, spawn_y + BLOCK_SIZE))
                                spawned_count += 1
                            if r < 0.15:  # Husks spawn anytime (immune to sunlight)
                                husk = Zombie(spawn_x, spawn_y, biome_type)
                                husk.health = random.randint(8, 18)  # Spawn with damage
                                MOBS.add(husk)
                                spawned_count += 1
                            if is_hostile_time and not is_lit and r < 0.20:
                                MOBS.add(Spider(spawn_x, spawn_y))
                                spawned_count += 1
                                hostile_spawned += 1
                        elif biome_type == SNOW_BIOME:
                            r = random.random()
                            if r < 0.15:
                                MOBS.add(Penguin(spawn_x, spawn_y + BLOCK_SIZE))
                                spawned_count += 1
                            if r < 0.20:
                                MOBS.add(Bear(spawn_x, spawn_y, is_polar=True))
                                spawned_count += 1
                            if is_hostile_time and not is_lit and r < 0.25:
                                MOBS.add(Creeper(spawn_x, spawn_y))
                                spawned_count += 1
                                hostile_spawned += 1
                            if is_hostile_time and not is_lit and r < 0.30:
                                MOBS.add(Skeleton(spawn_x, spawn_y, is_stray=True))
                                spawned_count += 1
                                hostile_spawned += 1
                        elif biome_type == PLAINS_BIOME:
                            r = random.random()
                            # REDUCED farm animal spawn rates
                            if r < 0.06:
                                MOBS.add(Sheep(spawn_x, spawn_y + BLOCK_SIZE))
                                spawned_count += 1
                            elif r < 0.12:
                                MOBS.add(Cow(spawn_x, spawn_y + BLOCK_SIZE))
                                spawned_count += 1
                            elif r < 0.18:
                                MOBS.add(Chicken(spawn_x, spawn_y + BLOCK_SIZE))
                                spawned_count += 1
                            elif r < 0.24:
                                MOBS.add(Pig(spawn_x, spawn_y + BLOCK_SIZE))
                                spawned_count += 1
                            elif r < 0.30:
                                MOBS.add(Horse(spawn_x, spawn_y + BLOCK_SIZE))
                                spawned_count += 1
                                print(f"   🐴 Horse spawned at ({col}, {ground_row})")
                            if is_hostile_time and not is_lit and r < 0.15:  # Increased from 0.50
                                MOBS.add(Zombie(spawn_x, spawn_y, biome_type))
                                spawned_count += 1
                                hostile_spawned += 1
                            if is_hostile_time and not is_lit and r < 0.20:  # Increased from 0.52
                                MOBS.add(Spider(spawn_x, spawn_y))
                                spawned_count += 1
                                hostile_spawned += 1
                            if is_hostile_time and not is_lit and r < 0.25:  # Increased from 0.54
                                MOBS.add(Creeper(spawn_x, spawn_y))
                                spawned_count += 1
                                hostile_spawned += 1
                        elif biome_type == BIRCH_FOREST_BIOME:
                            r = random.random()
                            if r < 0.10:
                                MOBS.add(Deer(spawn_x, spawn_y))
                                spawned_count += 1
                            elif r < 0.20:
                                MOBS.add(Bear(spawn_x, spawn_y, is_polar=False))
                                spawned_count += 1
                            elif is_hostile_time and not is_lit and r < 0.40:
                                MOBS.add(Zombie(spawn_x, spawn_y, biome_type))
                                spawned_count += 1
                                hostile_spawned += 1
                                print(f"   🧟 Zombie spawned at ({col}, {ground_row})")
                            elif is_hostile_time and not is_lit and r < 0.60:
                                MOBS.add(Spider(spawn_x, spawn_y))
                                spawned_count += 1
                                hostile_spawned += 1
                                print(f"   🕷 Spider spawned at ({col}, {ground_row})")
                            elif is_hostile_time and not is_lit and r < 0.80:
                                MOBS.add(Creeper(spawn_x, spawn_y))
                                spawned_count += 1
                                hostile_spawned += 1
                                print(f"   💥 Creeper spawned at ({col}, {ground_row})")
                        elif biome_type in [JUNGLE_BIOME, BAMBOO_JUNGLE_BIOME]:
                            r = random.random()
                            if r < 0.15:
                                MOBS.add(Panda(spawn_x, spawn_y))
                                spawned_count +=  DAWN_PHASE
                                print(f"   🐼 Panda spawned at ({col}, {ground_row})")
                            elif r < 0.30:
                                MOBS.add(Monkey(spawn_x, spawn_y))
                                spawned_count += 1
                                print(f"   🐵 Monkey spawned at ({col}, {ground_row})")
                            elif is_hostile_time and not is_lit and r < 0.50:
                                MOBS.add(Zombie(spawn_x, spawn_y, biome_type))
                                spawned_count += 1
                                hostile_spawned += 1
                            elif is_hostile_time and not is_lit and r < 0.70:
                                MOBS.add(Spider(spawn_x, spawn_y))
                                spawned_count += 1
                                hostile_spawned += 1
                        else:  # OAK_FOREST_BIOME
                            r = random.random()
                            if r < 0.10:
                                MOBS.add(Deer(spawn_x, spawn_y))
                                spawned_count += 1
                            elif r < 0.20:
                                MOBS.add(Bear(spawn_x, spawn_y, is_polar=False))
                                spawned_count += 1
                            elif is_hostile_time and not is_lit and r < 0.40:
                                MOBS.add(Zombie(spawn_x, spawn_y, biome_type))
                                spawned_count += 1
                                hostile_spawned += 1
                                print(f"   🧟 Zombie spawned at ({col}, {ground_row})")
                            elif is_hostile_time and not is_lit and r < 0.60:
                                MOBS.add(Spider(spawn_x, spawn_y))
                                spawned_count += 1
                                hostile_spawned += 1
                                print(f"   🕷 Spider spawned at ({col}, {ground_row})")
                            elif is_hostile_time and not is_lit and r < 0.80:
                                MOBS.add(Creeper(spawn_x, spawn_y))
                                spawned_count += 1
                                hostile_spawned += 1
                                print(f"   💥 Creeper spawned at ({col}, {ground_row})")
                
                # Debug output
                if spawn_attempts > 0 or (is_hostile_time and spawned_count == 0):
                    hostile_msg = f", {hostile_spawned} HOSTILE" if hostile_spawned > 0 else ""
                    time_msg = "🌙 NIGHT" if is_hostile_time else "☀️ DAY"
                    print(f"🐾 {time_msg} SPAWN CHECK: {len(MOBS)} mobs exist, checked {spawn_attempts} valid locations")
                    print(f"   Spawned {spawned_count} mobs{hostile_msg} | Skipped: {skipped_distance} (distance), {skipped_crowded} (crowded), {skipped_surface} (surface), {skipped_sky} (no sky)")
                    if hostile_spawned > 0:
                        print(f"   ⚠️  {hostile_spawned} hostile mobs spawned! Player at ({player.rect.centerx // BLOCK_SIZE}, {player.rect.centery // BLOCK_SIZE})")

                # Check for water spawning (Drowned in lakes/rivers)
                for col in range(0, GRID_WIDTH, 10):
                    spawn_x = col * BLOCK_SIZE
                    
                    # Only spawn if within render distance of player
                    if abs(spawn_x - player.rect.centerx) > render_distance_x:
                        continue
                    
                    # Find water level
                    ground_row = 0
                    for row in range(GRID_HEIGHT - 1, -1, -1):
                        if WORLD_MAP[row][col] != 0:
                            ground_row = row
                            break
                    
                    # Look for water blocks at spawn location
                    water_check_row = ground_row
                    if water_check_row >= 0 and water_check_row < GRID_HEIGHT:
                        if WORLD_MAP[water_check_row][col] == WATER_ID:
                            # We're in water - spawn Drowned
                            r = random.random()
                            if r < 0.008:  # 0.8% chance to spawn Drowned in water
                                water_spawn_y = water_check_row * BLOCK_SIZE
                                MOBS.add(Drowned(spawn_x, water_spawn_y))
                                spawned_count += 1

        
        # Update player position if mounted on camel
        if player.mounted_camel is not None and player.mounted_camel.alive():
            player.rect.centerx = player.mounted_camel.rect.centerx
            player.rect.bottom = player.mounted_camel.rect.top + player.mount_offset_y
    
    # Water flow update (every 10 frames to reduce lag)
    water_flow_timer += 1
    if water_flow_timer >= 10:
        update_water_flow()
        update_falling_blocks()  # Also update falling blocks
        water_flow_timer = 0
    
    # Auto-close doors after timer expires
    for door_data in OPEN_DOORS[:]:  # Copy list to safely modify during iteration
        door_data["timer"] -= 1
        if door_data["timer"] <= 0:
            # Close the door
            door_col = door_data["col"]
            door_row = door_data["row"]
            if 0 <= door_row < GRID_HEIGHT and 0 <= door_col < GRID_WIDTH:
                if WORLD_MAP[door_row][door_col] == 0:  # Still open
                    WORLD_MAP[door_row][door_col] = 91
                    # Close top half too
                    if door_row - 1 >= 0 and WORLD_MAP[door_row - 1][door_col] == 0:
                        WORLD_MAP[door_row - 1][door_col] = 91
            OPEN_DOORS.remove(door_data)
    
    # Check for suffocation from falling blocks
    player_head_col = player.rect.centerx // BLOCK_SIZE
    player_head_row = player.rect.top // BLOCK_SIZE
    if 0 <= player_head_row < GRID_HEIGHT and 0 <= player_head_col < GRID_WIDTH:
        block_at_head = WORLD_MAP[player_head_row][player_head_col]
        if block_at_head in [19, 26]:  # Sand or gravel at head position
            if player.damage_flash_timer <= 0:
                player.take_damage(1)  # Suffocation damage
    
    # Mob Attack/Damage Logic - check collision regardless of riding status (excluding skeletons who shoot arrows)
    for mob in MOBS:
        if player.rect.colliderect(mob.rect):
            if hasattr(mob, 'attack') and player.damage_flash_timer <= 0 and not isinstance(mob, Skeleton):
                mob.attack(player) 
    
    # Calculate camera offset 
    camera_x, camera_y = calculate_camera_offset(player.rect)

    # 4. DRAWING
    screen.fill(get_sky_color())  # Dynamic sky color based on time
    
    draw_world(camera_x, camera_y, player)

    # Draw block highlight 
    if not player.is_crafting and not player.inventory_open:
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

    # Draw Mobs
    for mob in MOBS:
        mob_screen_pos = (mob.rect.x - camera_x, mob.rect.y - camera_y)
        screen.blit(mob.image, mob_screen_pos)
        
        # Fire animation for burning hostile mobs (not husk/creeper/spider/drowned)
        if (hasattr(mob, 'sunlight_timer') and mob.sunlight_timer > 0 and 
            not isinstance(mob, (Spider, Creeper, Drowned)) and 
            not (isinstance(mob, Zombie) and hasattr(mob, 'is_husk') and mob.is_husk)):
            # Draw flickering fire particles above the mob
            for i in range(3):
                fire_x = mob_screen_pos[0] + random.randint(0, mob.rect.width)
                fire_y = mob_screen_pos[1] + random.randint(-10, mob.rect.height // 2)
                fire_color = random.choice([(255, 100, 0), (255, 150, 0), (255, 200, 0)])
                fire_size = random.randint(3, 6)
                pygame.draw.rect(screen, fire_color, (fire_x, fire_y, fire_size, fire_size))
        
        # Health Bar
        if mob.health < mob.max_health:
            bar_width = mob.rect.width
            bar_height = 5
            health_ratio = mob.health / mob.max_health
            pygame.draw.rect(screen, (50, 50, 50), (mob_screen_pos[0], mob_screen_pos[1] - 10, bar_width, bar_height))
            pygame.draw.rect(screen, (255, 0, 0), (mob_screen_pos[0], mob_screen_pos[1] - 10, bar_width * health_ratio, bar_height))
    
    # Draw Arrows
    for arrow in ARROWS:
        arrow_screen_pos = (arrow.rect.x - camera_x, arrow.rect.y - camera_y)
        screen.blit(arrow.image, arrow_screen_pos)
    
    # Draw Splash Potions
    for potion in SPLASH_POTIONS:
        potion_screen_pos = (potion.rect.x - camera_x, potion.rect.y - camera_y)
        screen.blit(potion.image, potion_screen_pos)
    
    # Draw Tridents
    for trident in TRIDENTS:
        trident_screen_pos = (trident.rect.x - camera_x, trident.rect.y - camera_y)
        screen.blit(trident.image, trident_screen_pos)
    
    # Draw Dropped Items
    for dropped_item in DROPPED_ITEMS:
        item_screen_pos = (dropped_item.rect.x - camera_x, dropped_item.rect.y - camera_y)
        screen.blit(dropped_item.image, item_screen_pos)
    
    # Draw the player 
    player_screen_pos = (player.rect.x - camera_x, player.rect.y - camera_y)
    screen.blit(player.get_image(), player_screen_pos)
    
    # Draw held item in player's hand
    if player.held_block != 0 and player.held_block in BLOCK_TYPES:
        item_size = 12
        # Position item in front of player based on facing direction
        hand_offset_x = 16 if player.vel_x >= 0 else -item_size - 4
        hand_offset_y = 20  # Middle of player
        
        # Lower spear during charge
        if player.is_charging and BLOCK_TYPES[player.held_block].get("can_charge", False):
            hand_offset_y += int((1 - player.charge_timer / player.max_charge_time) * 8)  # Lower as charge runs out
        
        item_x = player_screen_pos[0] + hand_offset_x
        item_y = player_screen_pos[1] + hand_offset_y
        item_rect = pygame.Rect(item_x, item_y, item_size, item_size)
        
        # Draw tool icon or colored square
        if player.held_block in [9, 99, 100, 101, 102, 107, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118]:
            draw_tool_icon(screen, item_rect, player.held_block)
        else:
            item_color = BLOCK_TYPES[player.held_block]["color"]
            pygame.draw.rect(screen, item_color, item_rect)
            pygame.draw.rect(screen, (0, 0, 0), item_rect, 1)  # Border

    # Draw the HUD elements 
    draw_hud(player)
    
    # Draw Inventory Menu OVERLAY (if active)
    if player.inventory_open and not player.is_crafting:
        draw_inventory_menu(player)
    
    # Draw Crafting Menu OVERLAY (if active)
    if player.is_crafting:
        draw_crafting_menu(player)
    
    # Draw Trading Menu OVERLAY (if active)
    if player.trading_open:
        draw_trading_menu(player)
    
    # Draw Crafting Table GUI OVERLAY (if active)
    if CRAFTING_TABLE_OPEN:
        draw_crafting_table_gui(screen, player)
    
    # Draw Furnace GUI OVERLAY (if active)
    if FURNACE_OPEN:
        draw_furnace_gui(screen, player)

    # 5. UPDATE DISPLAY & CLOCK
    pygame.display.flip()
    clock.tick(FPS) 

# --- Cleanup ---
pygame.quit()
