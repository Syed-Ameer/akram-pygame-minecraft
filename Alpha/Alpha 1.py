import pygame
import random
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 40
FPS = 60

# --- World Map Dimensions (Larger for scrolling) ---
WORLD_WIDTH_BLOCKS = 1000
WORLD_HEIGHT_BLOCKS = 150

GRID_WIDTH = WORLD_WIDTH_BLOCKS
GRID_HEIGHT = WORLD_HEIGHT_BLOCKS

# --- Block Definitions (ID and Color) ---
# NOTE: Using constants for clarity in structure functions
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

BLOCK_TYPES = {
    # ... (Your BLOCK_TYPES dictionary remains the same) ...
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
    23: {"name": "Emerald", "color": (0, 200, 80), "mineable": False, "solid": False},
    24: {"name": "Snow", "color": (255, 255, 255), "mineable": True, "min_tool_level": 0, "solid": True},
    25: {"name": "Ice", "color": (174, 221, 240), "mineable": True, "min_tool_level": 0, "solid": True}
}




# ... (CRAFTING_RECIPES remains the same) ...
CRAFTING_RECIPES = {
    frozenset([(18, 1)]): (8, 4), 
    frozenset([(8, 2)]): (10, 4), 
    frozenset([(8, 3), (10, 2)]): (9, 1),
    frozenset([(3, 3), (10, 2)]): (17, 1),
    frozenset([(3, 8)]): (16, 1),
    frozenset([(10, 1), (11, 1)]): (15, 4)
}

# ... (Pygame Initialization remains the same) ...
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Pycraft Clone (Scrolling World with Enemies and Crafting)")
clock = pygame.time.Clock()

pygame.font.init()
FONT_SMALL = pygame.font.Font(None, 16)
FONT_BIG = pygame.font.Font(None, 24)

WORLD_MAP = [] 
CRAFTING_GRID = [0, 0, 0, 0] 
CRAFTING_AMOUNTS = [0, 0, 0, 0] 
CRAFTING_SLOT_RECTS = [] 


# --- World Decoration Functions (remain the same) ---
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


# --- STRUCTURE GENERATION FUNCTIONS (CRITICAL FIX: MOVED OUTSIDE generate_world) ---
def generate_plains_village(world, height_map, col_start):
    """Generates a small village cluster with multiple houses, a farm, and Villagers."""
    
    # 1. Structure Check 
    village_width = random.randint(15, 25) # Total width needed for the cluster
    house_count = random.randint(2, 4)
    house_width_min = 4
    
    # Check for space and flatness across the entire potential village area
    for col in range(col_start, col_start + village_width):
        if col >= GRID_WIDTH or world[height_map[col]][col] != GRASS_ID:
            return 0, [] # Not enough space or wrong block type
        if abs(height_map[col] - height_map[col_start]) > 1:
            return 0, [] # Too bumpy
            
    ground_row = height_map[col_start]
    current_col = col_start
    villagers_to_spawn = []  # Store villager spawn info
    
    print(f"🏠 PLAINS VILLAGE GENERATED at column {col_start} with {house_count} houses.")

    # 2. Generate Multiple Smaller Houses
    for i in range(house_count):
        house_width = random.randint(house_width_min, 6)
        house_height = random.randint(3, 5)
        
        # Ensure the house fits within the allocated village width
        if current_col + house_width >= col_start + village_width - 5:
            break 
            
        # --- Draw Individual House ---
        house_ground_row = height_map[current_col] # Use the height at the house's start
        
        for r in range(house_ground_row - house_height, house_ground_row):
            for c in range(current_col, current_col + house_width):
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    # Clear inside to Air
                    if current_col < c < current_col + house_width - 1 and house_ground_row - house_height < r < house_ground_row - 1:
                        world[r][c] = AIR_ID
                    # Walls (Plank ID 8)
                    elif r == house_ground_row - house_height or r == house_ground_row - 1 or c == current_col or c == current_col + house_width - 1:
                        world[r][c] = PLANK_ID
                        
        # Roof (Wool ID 7)
        roof_row = house_ground_row - house_height - 1
        for c in range(current_col - 1, current_col + house_width + 1):
             if 0 <= roof_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                 world[roof_row][c] = WOOL_ID
                 
        # Door (Air)
        door_col = current_col + house_width // 2
        world[house_ground_row - 1][door_col] = AIR_ID
        world[house_ground_row - 2][door_col] = AIR_ID

        # 3. Villager Spawning (Centered)
        if len(villagers_to_spawn) < 3: # Limit villager count
            
            # Calculate the column for the center of the house floor
            spawn_col = current_col + house_width // 2 
            
            # Spawn coordinates (X is left edge of the center block, Y is two blocks above the floor)
            spawn_x = spawn_col * BLOCK_SIZE 
            spawn_y = (house_ground_row - 2) * BLOCK_SIZE
            
            if spawn_y > 0 and 0 <= spawn_col < GRID_WIDTH:
                villagers_to_spawn.append(Villager(spawn_x, spawn_y))
                print(f"   --> Villager prepared for house {i+1} at Col: {spawn_col}")
            
        # Move to the next house location
        current_col += house_width + random.randint(2, 4) # Add a gap between houses

    # 4. Generate Simple Farm (e.g., a 5x1 area of Dirt/Water/Dirt)
    farm_start_col = current_col + 1
    farm_end_col = farm_start_col + 5
    farm_row = height_map[farm_start_col] # Should be the same height
    
    if farm_end_col < col_start + village_width:
        for c in range(farm_start_col, farm_end_col):
            if c == farm_start_col + 2:
                # Center block is water
                world[farm_row][c] = WATER_ID
            else:
                # Other blocks are dirt/tilled soil
                world[farm_row][c] = DIRT_ID
            
    # Return the total width used by the village cluster AND the villagers list
    return farm_end_col - col_start + 3, villagers_to_spawn

def generate_desert_temple(world, height_map, col_start):
    """Generates a symmetrical Sandstone pyramid structure."""

    # 1. Relaxed and Randomized size selection
    temple_size = random.choice([7, 9, 11])
    # The height is determined by the size, ensuring a peak
    temple_height = temple_size // 2 + 1 
    
    max_height_diff = 3  # Allow up to 3 blocks difference in height (for dunes)
    
    # Check for space and flatness on Sand
    for col in range(col_start, col_start + temple_size):
        if col >= GRID_WIDTH or world[height_map[col]][col] != SAND_ID:
            return 0  
        
        if abs(height_map[col] - height_map[col_start]) > max_height_diff:
            return 0 # Too bumpy
            
    # --- SUCCESSFUL PLACEMENT START ---
    
    print(f"✅ DESERT TEMPLE GENERATED (Symmetrical) at column {col_start}")

    ground_row = height_map[col_start]
    
    # Store the center of the base for later reference
    base_center_col = col_start + temple_size // 2
    
    # Draw the SYMMETRICAL pyramid (Sandstone ID 20)
    for h in range(temple_height):
        # The layer width shrinks by 2 blocks for every level up
        layer_width = temple_size - 2 * h
        layer_row = ground_row - 1 - h
        
        # Layer starts to the left of the center and expands symmetrically
        start_col_layer = base_center_col - layer_width // 2
        
        # Draw the layer
        for c_offset in range(layer_width):
            c = start_col_layer + c_offset
            
            if 0 <= layer_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                if layer_row >= 0:
                    world[layer_row][c] = 20 # SANDSTONE_ID
                    
    # Add a 'hidden' room entrance (placed relative to the original center)
    entrance_row = ground_row - 1
    entrance_col = base_center_col # Place entrance directly beneath the base center
    if 0 <= entrance_row < GRID_HEIGHT and 0 <= entrance_col < GRID_WIDTH:
        world[entrance_row][entrance_col] = 0 # AIR_ID
                    
    return temple_size + 5 # Structure successfully built # Structure successfully built # Structure successfully built # Structure successfully built # No structure generated

def generate_snow_igloo(world, height_map, col_start):
    """Generates an igloo made of snow with ice floor and spawns a penguin inside."""
    
    igloo_width = 7
    igloo_height = 4
    
    # Check for space and flatness on snow
    for col in range(col_start, col_start + igloo_width):
        if col >= GRID_WIDTH or world[height_map[col]][col] != 24:
            return 0, []
        if abs(height_map[col] - height_map[col_start]) > 1:
            return 0, []
    
    ground_row = height_map[col_start]
    penguins_to_spawn = []
    
    print(f"🐧 SNOW IGLOO GENERATED at column {col_start}")
    
    # Build igloo dome
    center_col = col_start + igloo_width // 2
    
    # Floor (ice)
    for c in range(col_start, col_start + igloo_width):
        if 0 <= ground_row < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
            world[ground_row][c] = 25
    
    # Build dome using snow blocks
    for r in range(ground_row - igloo_height, ground_row):
        for c in range(col_start, col_start + igloo_width):
            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                # Distance from center
                dist_from_center = abs(c - center_col)
                height_from_ground = ground_row - r
                
                # Create dome shape
                if height_from_ground <= igloo_height - dist_from_center:
                    # Hollow inside
                    if dist_from_center > 1 or height_from_ground < igloo_height - 1:
                        world[r][c] = 24
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
        print(f"   --> Penguin spawned in igloo at Col: {center_col}")
    
    return igloo_width + 3, penguins_to_spawn

# --- Main World Generation Function (Correctly Integrated) ---
def generate_world():
    """Generates a simple 2D world map, lakes, mobs, and structures."""
    global MOBS, WORLD_MAP 

    world = []
    
    # 1. Fill with Sky/Air
    for _ in range(GRID_HEIGHT):
        world.append([0] * GRID_WIDTH)

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
    
    # --- Determine Biome Regions ---
    biome_map = [] 
    biome_size = 50 
    
    for col in range(GRID_WIDTH):
        biome_phase = (col // biome_size) % 4  # Changed to 4 for snow biome
        if biome_phase == 0:
            biome_map.append(0)  # Plains
        elif biome_phase == 1:
            biome_map.append(1)  # Desert
        elif biome_phase == 2:
            biome_map.append(2)  # Snow
        else:
            biome_map.append(0)  # Plains
        
    # --- Populate World with Blocks (Initial structure before carving) ---
    for col in range(GRID_WIDTH):
        ground_level = height_map[col]
        biome_type = biome_map[col]
        is_desert = biome_type == 1
        is_snow = biome_type == 2
        
        for row in range(ground_level, GRID_HEIGHT):
            if row == GRID_HEIGHT - 1:
                world[row][col] = BEDROCK_ID
            elif row == ground_level:
                if is_desert:
                    world[row][col] = SAND_ID
                elif is_snow:
                    world[row][col] = SNOW_ID
                else:
                    world[row][col] = GRASS_ID
            elif row <= ground_level + 2:
                if is_desert:
                    world[row][col] = SAND_ID
                elif is_snow:
                    world[row][col] = SNOW_ID
                else:
                    world[row][col] = DIRT_ID
            elif row <= ground_level + 5:
                if is_desert:
                    world[row][col] = SANDSTONE_ID
                elif is_snow:
                    world[row][col] = ICE_ID
                else:
                    world[row][col] = DIRT_ID
            else:
                block_id = STONE_ID
                
                # --- Ore and Cave Generation ---
                r = random.random()
                if r < 0.04: 
                    block_id = AIR_ID
                elif r < 0.08: 
                    block_id = 11 # Coal Ore
                elif r < 0.11: 
                    block_id = 12 # Iron Ore
                
                world[row][col] = block_id
    
    # --- MOB/LAKE VARIABLES ---
    mobs = pygame.sprite.Group() 
    zombies_spawned = 0 
    narwhals_spawned = 0 
    
    LAKE_PROBABILITY = 0.02
    MAX_LAKE_DEPTH = 5
    MAX_LAKE_WIDTH = 15
    current_lake_width = 0
    lake_bottom_row = 0
    narwhal_spawn_col = -1 # Track the column where a Narwhal *should* be spawned
    
    WORLD_MAP = world 
    
    # --- FIRST PASS: LAKE CARVING ONLY ---
    for col in range(GRID_WIDTH):
        ground_row = height_map[col]
        
        # 1. Lake Start Logic
        if current_lake_width == 0:
            if random.random() < LAKE_PROBABILITY:
                current_lake_width = random.randint(5, MAX_LAKE_WIDTH)
                
                # Calculate the bottom of the lake
                lake_bottom_row = ground_row + random.randint(3, MAX_LAKE_DEPTH) 
                lake_bottom_row = min(lake_bottom_row, GRID_HEIGHT - 5) 
                
                # CRITICAL: Set the exact column where the Narwhal will spawn
                narwhal_spawn_col = col 
        
        # 2. Carve and fill the active lake column
        if current_lake_width > 0:
            water_surface_row = ground_row 
            
            # Carve the hole and fill with water (as before)
            for r in range(water_surface_row, lake_bottom_row):
                if 0 <= r < GRID_HEIGHT:
                    # Determine block type (Dirt/Sand bottom vs. Water)
                    if r == lake_bottom_row - 1:
                        # Use dirt or sand for bottom based on biome
                        if biome_map[col] == 1:
                            WORLD_MAP[r][col] = SAND_ID
                        else:
                            WORLD_MAP[r][col] = DIRT_ID
                    else:
                        WORLD_MAP[r][col] = WATER_ID
                        
            # 3. NARWHAL SPAWN (Executed only in the designated column)
            if col == narwhal_spawn_col: 
                # Calculate spawn point 1 block below the surface for safety
                spawn_depth = water_surface_row + 1 
                
                spawn_narwhal_x = col * BLOCK_SIZE
                spawn_narwhal_y = spawn_depth * BLOCK_SIZE
                
                # Check if the calculated spawn block is actually water (ID 5)
                if WORLD_MAP[spawn_depth][col] == WATER_ID:
                    mobs.add(Narwhal(spawn_narwhal_x, spawn_narwhal_y))
                    narwhals_spawned += 1
                    print(f"🐳 NARWHAL SPAWNED at column {col}, Y-pos={spawn_narwhal_y}") 
                else:
                    print(f"⚠️ Narwhal spawn failed at {col}: Block is not water.")

            current_lake_width -= 1
            
            # Reset spawn column when the lake ends
            if current_lake_width == 0:
                narwhal_spawn_col = -1

    print(f"Total narwhals successfully spawned: {narwhals_spawned}")
    
    # --- STRUCTURE AND DECORATION PASS ---
    
    # --- 1. Targeted Structure Generation near the Center (Col 400) ---
    
    # Define a central zone to search for the Plains biome
    center_search_start = GRID_WIDTH // 2 - 50 # Start searching from Col 350
    center_search_end = GRID_WIDTH // 2 + 50 # End search at Col 450
    
    village_spawned = False
    village_end_col = 0
    
    # Attempt to find a Plains biome strip and place a village there
    for col_start in range(center_search_start, center_search_end):
        if biome_map[col_start] == 0 and not village_spawned: # Found Plains biome
            
            # FIXED: Capture both blocks_used AND villagers list
            blocks_used, villagers = generate_plains_village(WORLD_MAP, height_map, col_start)
            
            if blocks_used > 0:
                print(f"🎉 GUARANTEED PLAINS VILLAGE spawned near center (Col {col_start}).")
                # Add all villagers from the village to the mobs group
                for villager in villagers:
                    mobs.add(villager)
                village_end_col = col_start + blocks_used
                village_spawned = True
                break # Village placed, exit the search loop
            
    # If a village was spawned, start the general loop after it. Otherwise, start from the beginning.
    col = village_end_col # If 0, start at the beginning. If > 0, skip the village area.
    current_biome_start = col
    
    # --- 2. Iterate through the entire map for Decorations and other Structures ---
    
    while col < GRID_WIDTH:
        current_biome_type = biome_map[col]
        
        # Skip the area if the village was just placed there
        if village_spawned and current_biome_type == 0 and col < village_end_col:
            col = village_end_col
            current_biome_start = col
            continue 
            
        # Find the end of the current biome chunk
        col_end = col
        while col_end < GRID_WIDTH and biome_map[col_end] == current_biome_type:
            col_end += 1
            
        # Structure Placement Logic (Desert Temple and Snow Igloo)
        blocks_used = 0
        structure_entities = []
        
        # Calculate a safe range for structure placement within the biome strip
        structure_start_limit = max(col, current_biome_start) + 5
        structure_end_limit = col_end - (15 if current_biome_type == 1 else 10) 
        
        # Desert Temple
        if current_biome_type == 1 and structure_start_limit < structure_end_limit and random.random() < 0.3:
            structure_col_start = random.randint(structure_start_limit, structure_end_limit)
            blocks_used = generate_desert_temple(WORLD_MAP, height_map, structure_col_start)
        
        # Snow Igloo
        elif current_biome_type == 2 and structure_start_limit < structure_end_limit and random.random() < 0.4:
            structure_col_start = random.randint(structure_start_limit, structure_end_limit)
            blocks_used, penguins = generate_snow_igloo(WORLD_MAP, height_map, structure_col_start)
            if blocks_used > 0:
                for penguin in penguins:
                    mobs.add(penguin)
            
        # Update the decoration starting point based on the structure size
        if blocks_used > 0:
            decoration_start = structure_col_start + blocks_used
        else:
            decoration_start = col # Start decoration from the beginning of the biome chunk

        # Add decorations for the strip
        if current_biome_type == 0:  # Grassland
            add_trees(WORLD_MAP, height_map)
        elif current_biome_type == 1:  # Desert
            add_cacti(WORLD_MAP, height_map, decoration_start, col_end)
            add_dead_bushes(WORLD_MAP, height_map, decoration_start, col_end)
        # Snow biome (2) has no additional decorations
            
        current_biome_start = col_end # Move tracking to the next biome
        col = col_end # Continue the loop from the end of this biome chunk
        
    # --- SECOND PASS: MOB SPAWNING (after lakes and decorations) ---
    for col in range(GRID_WIDTH):
        ground_row = height_map[col]
        biome_type = biome_map[col]
        is_desert = biome_type == 1
        is_snow = biome_type == 2
        
        # Check if the column is suitable for spawning
        surface_block = WORLD_MAP[ground_row][col] if ground_row < GRID_HEIGHT else AIR_ID
        
        is_valid_surface = (surface_block == GRASS_ID or surface_block == SAND_ID or 
                           surface_block == PLANK_ID or surface_block == WOOL_ID or 
                           surface_block == SNOW_ID or surface_block == ICE_ID)
        
        if ground_row < GRID_HEIGHT and is_valid_surface: 
            spawn_x = col * BLOCK_SIZE
            spawn_y = (ground_row - 2) * BLOCK_SIZE 
            
            # Mob Spawning Logic
            if zombies_spawned == 0 and abs(col - GRID_WIDTH // 2) < 5:
                mobs.add(Zombie(spawn_x, spawn_y))
                zombies_spawned += 1
            else:
                r = random.random()
                if is_desert:
                    if r < 0.03: 
                        mobs.add(Camel(spawn_x, spawn_y + BLOCK_SIZE))
                    elif r < 0.04: 
                        mobs.add(Zombie(spawn_x, spawn_y))
                    elif r < 0.05: 
                        mobs.add(Spider(spawn_x, spawn_y))
                elif is_snow:
                    if r < 0.05:  # Penguins in snow biome
                        mobs.add(Penguin(spawn_x, spawn_y + BLOCK_SIZE))
                else:  # Plains
                    if r < 0.04: 
                        mobs.add(Sheep(spawn_x, spawn_y + BLOCK_SIZE)) 
                    elif r < 0.04: 
                        mobs.add(Cow(spawn_x, spawn_y + BLOCK_SIZE))
                    elif r < 0.0925: 
                        mobs.add(Zombie(spawn_x, spawn_y)) 
                    elif r < 0.0750: 
                        mobs.add(Spider(spawn_x, spawn_y)) 
                    elif r < 0.0775: 
                        mobs.add(Creeper(spawn_x, spawn_y))
                    elif r < 0.0775: 
                        mobs.add(Skeleton(spawn_x, spawn_y))
            
    MOBS = mobs
    return world, mobs
# --- Mob Classes ---
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
        self.damage_flash_timer = 0 
        self.is_crafting = False 

        # --- Fall Damage Tracking ---
        self.fall_velocity_threshold = 7  # Takes about 3 blocks of falling (reasonable with terminal velocity of 10)
        self.max_fall_vel = 0 

        # --- Riding Mechanic ---
        self.mounted_camel = None  # Reference to the camel being ridden
        self.mount_offset_y = -BLOCK_SIZE * 1.2  # Player sits on top of camel (adjusted for bigger camel)

        # --- Inventory and Hotbar ---
        # NOTE: Added a few new items to starting inventory for testing new features
        self.inventory = {1: 64, 2: 64, 3: 64, 5: 32, 6: 32, 7: 16, 11: 5, 10: 20} 
        self.hotbar_slots = [1, 2, 3, 5, 6, 7, 11, 10, 0] 
        self.active_slot = 0
        self.held_block = self.hotbar_slots[self.active_slot]
        # -----------------------------------------------------------

    def switch_active_slot(self, slot_index):
        """Switches the active hotbar slot."""
        if 0 <= slot_index <= 8:
            self.active_slot = slot_index
            self.held_block = self.hotbar_slots[self.active_slot]
            
    def add_to_inventory(self, block_id, amount=1):
        """Adds a block to the inventory."""
        if block_id not in self.inventory:
            self.inventory[block_id] = 0
        self.inventory[block_id] += amount
        
        # Update hotbar visually if the item is present
        if block_id not in self.hotbar_slots:
            try:
                empty_slot_index = self.hotbar_slots.index(0)
                self.hotbar_slots[empty_slot_index] = block_id
            except ValueError:
                pass
            
        self.held_block = self.hotbar_slots[self.active_slot]


    def consume_item(self, block_id, amount=1):
        """Consumes a block from the inventory."""
        if block_id in self.inventory and self.inventory[block_id] >= amount:
            self.inventory[block_id] -= amount
            
            if self.inventory[block_id] <= 0:
                del self.inventory[block_id]
                # Remove from hotbar when inventory is completely empty
                for i in range(len(self.hotbar_slots)):
                    if self.hotbar_slots[i] == block_id:
                        self.hotbar_slots[i] = 0
                        
            self.held_block = self.hotbar_slots[self.active_slot]
            return True
        return False

    def take_damage(self, amount):
        """Applies damage and starts the flash timer."""
        if self.damage_flash_timer <= 0:
            self.health -= amount
            self.damage_flash_timer = FPS // 2
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
        player = next(iter(self.groups())).sprites()[0] 
        super.die()
             
    def die(self):
        # Simple player death: log and remove the player sprite
        print("Player has died!")
        self.kill()

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
            
            if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
                in_water = WORLD_MAP[center_row][center_col] == 5  # Water ID is 5
            
            # Apply gravity (reduced in water)
            if in_water:
                self.vel_y += self.gravity * 0.3  # Reduced gravity in water
                if self.vel_y > 2:  # Lower terminal velocity in water
                    self.vel_y = 2
            else:
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
            self.rect.right = min(GRID_WIDTH * BLOCK_SIZE, self.rect.right)

        # --- Hunger Logic ---
        self.hunger_timer += 1
        if self.vel_x != 0 or self.vel_y < 0:
             self.hunger_timer += 0.5

        if self.hunger_timer >= FPS * 20: 
            if self.hunger > 0:
                self.hunger -= 1
            self.hunger_timer = 0
        
        if self.hunger >= 18 and self.health < self.max_health and self.hunger_timer % (FPS * 10) == 0:
            self.health = min(self.max_health, self.health + 1)
        elif self.hunger == 0 and self.hunger_timer % (FPS * 5) == 0:
            self.health = max(1, self.health - 1) 

    def jump(self):
        """Makes the player jump if on the ground, or swim up if in water."""
        if self.is_crafting: return
        
        # Check if player is in water
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        in_water = False
        
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
            in_water = WORLD_MAP[center_row][center_col] == 5  # Water ID is 5
        
        if in_water:
            # Swimming up in water
            self.vel_y = -5  # Swim up velocity
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
                
                # FIXED: Check if block is solid instead of just non-air
                if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                    block_id = WORLD_MAP[row][col]
                    if block_id != 0 and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                        on_ground = True
                        break
                    
            self.rect.y -= 2 
            
            if on_ground:
                self.vel_y = -10

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
            if 0 <= row < GRID_HEIGHT and 0 <= target_col < GRID_WIDTH:
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
            
            if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                block_id = WORLD_MAP[row][col]
                
                # FIXED: Check if block is solid instead of just non-air
                if block_id != 0 and BLOCK_TYPES.get(block_id, {}).get("solid", False):
                    # --- Collision with block found ---
                    
                    if is_falling:
                        # 1. Fall Damage Calculation (Only when landing)
                        if self.max_fall_vel > self.fall_velocity_threshold:
                            # Ensures damage is at least 1 when threshold is exceeded.
                            damage = int(self.max_fall_vel - self.fall_velocity_threshold)
                            damage = max(1, damage) # Guarantee at least 1 damage
                            self.take_damage(damage) 
                            
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
        """Sets the player's horizontal velocity and handles hotbar switching/crafting toggle."""
        
        # Dismount with SHIFT
        if keys[pygame.K_LSHIFT] and self.mounted_camel is not None:
            self.dismount_camel()
            return
        
        # Toggle Crafting Menu (E)
        if keys[pygame.K_e] and not getattr(self, '_e_pressed', False):
            # Check if closing the menu
            if self.is_crafting:
                reset_crafting_grid(self) # <-- IMPORTANT: Call cleanup BEFORE closing
            
            self.is_crafting = not self.is_crafting
            setattr(self, '_e_pressed', True)
        elif not keys[pygame.K_e]:
            setattr(self, '_e_pressed', False)
        
        # Movement is disabled while crafting
        if self.is_crafting:
            self.vel_x = 0
            return
        
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
            
        self.vel_x = 0
        if keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_d]:
            self.vel_x = self.speed
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
        
    def take_damage(self, amount):
        """Reduces health and checks if the mob dies."""
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        """Handle mob death: drop items (if any) and remove the mob sprite."""
        # Determine drop id (0 = nothing)
        drop_id = getattr(self, 'drop_id', 0)
        
        if drop_id != 0:
            drop_row = self.rect.bottom // BLOCK_SIZE
            drop_col = self.rect.centerx // BLOCK_SIZE
            
            # Find the first air block below the mob
            while drop_row < GRID_HEIGHT and WORLD_MAP[drop_row][drop_col] != 0:
                drop_row += 1
            
            if 0 <= drop_row < GRID_HEIGHT and WORLD_MAP[drop_row][drop_col] == 0:
                WORLD_MAP[drop_row][drop_col] = drop_id
        
        # Remove the mob sprite from all groups
        self.kill()
        
    def update(self, player=None):
        """Applies physics and checks collision."""
        # Apply gravity
        self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, 10)

        # Apply movement
        self.rect.x += self.vel_x
        self.collide_x()
        
        self.rect.y += self.vel_y
        self.collide_y()
        
    def collide_x(self):
        """Handles horizontal collision with solid blocks."""
        if self.vel_x == 0:
            return
            
        target_col = math.floor((self.rect.left + self.vel_x) / BLOCK_SIZE) if self.vel_x < 0 else math.floor((self.rect.right + self.vel_x) / BLOCK_SIZE)
        
        top_row = math.floor(self.rect.top / BLOCK_SIZE)
        bottom_row = math.floor((self.rect.bottom - 1) / BLOCK_SIZE)

        for row in range(top_row, bottom_row + 1):
            if 0 <= row < GRID_HEIGHT and 0 <= target_col < GRID_WIDTH:
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
            
            if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
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
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, (255, 255, 255)) 
        self.health = 8
        self.max_health = 8
        self.speed = 1.5
        self.drop_id = 7 # Wool
        
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
        
        # Body (fluffy white wool)
        pygame.draw.rect(self.image, (255, 255, 255), (3, 8, BLOCK_SIZE - 6, BLOCK_SIZE - 18), 0, 5)
        
        # Wool texture details (small squares for fluffy effect)
        pygame.draw.rect(self.image, (245, 245, 245), (8, 12, 8, 8))
        pygame.draw.rect(self.image, (245, 245, 245), (20, 12, 8, 8))
        pygame.draw.rect(self.image, (245, 245, 245), (14, 18, 8, 8))
        
        # Head (white with brown face)
        pygame.draw.rect(self.image, (255, 255, 255), (BLOCK_SIZE - 10, 5, 8, 10))  # Head
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
                    0 <= check_col < GRID_WIDTH and 
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
                
    def update(self, player=None):
        self.ai_move()
        super().update(player)
        
    def die(self):
        """Drops Wool (ID 7) into the world when killed."""
        # Drops handled by the base Mob.die() function using self.drop_id
        super().die()

class Cow(Mob):
    """A passive mob that wanders and drops leather."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, (139, 69, 19)) # Brown
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
        
        # Enhanced drawing with body parts
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        # Legs (4 brown legs)
        leg_color = (80, 50, 30)
        pygame.draw.rect(self.image, leg_color, (5, BLOCK_SIZE - 12, 6, 12))  # Front left
        pygame.draw.rect(self.image, leg_color, (BLOCK_SIZE - 11, BLOCK_SIZE - 12, 6, 12))  # Front right
        pygame.draw.rect(self.image, leg_color, (15, BLOCK_SIZE - 12, 6, 12))  # Back left
        pygame.draw.rect(self.image, leg_color, (BLOCK_SIZE - 21, BLOCK_SIZE - 12, 6, 12))  # Back right
        
        # Body (brown with spots)
        pygame.draw.rect(self.image, (139, 69, 19), (3, 8, BLOCK_SIZE - 6, BLOCK_SIZE - 20))
        
        # Spots (white/cream patches)
        pygame.draw.rect(self.image, (240, 230, 210), (6, 10, 10, 8))  # Left spot
        pygame.draw.rect(self.image, (240, 230, 210), (22, 12, 12, 10))  # Right spot
        pygame.draw.rect(self.image, (240, 230, 210), (14, 18, 8, 6))  # Middle spot
        
        # Head (brown)
        pygame.draw.rect(self.image, (139, 69, 19), (BLOCK_SIZE - 10, 4, 9, 12))
        
        # Ears (small brown rectangles)
        pygame.draw.rect(self.image, (120, 60, 18), (BLOCK_SIZE - 12, 4, 3, 4))  # Left ear
        pygame.draw.rect(self.image, (120, 60, 18), (BLOCK_SIZE - 2, 4, 3, 4))  # Right ear
        
        # Snout (lighter brown)
        pygame.draw.rect(self.image, (160, 90, 30), (BLOCK_SIZE - 10, 11, 9, 5))
        
        # Eyes (black dots)
        pygame.draw.rect(self.image, (0, 0, 0), (BLOCK_SIZE - 8, 7, 2, 2))  # Left eye
        pygame.draw.rect(self.image, (0, 0, 0), (BLOCK_SIZE - 4, 7, 2, 2))  # Right eye

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
                    0 <= check_col < GRID_WIDTH and 
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
                
    def update(self, player=None):
        self.ai_move()
        super().update(player)
        
    def die(self):
        """Drops Leather (ID 14) into the world when killed."""
        super().die()

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
        
        # Riding state
        self.is_mounted = False
        
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
                    0 <= check_col < GRID_WIDTH and 
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
                
    def update(self, player=None):
        # Don't run AI when being ridden
        if not self.is_mounted:
            self.ai_move()
        # Always apply physics (gravity and collision) even when mounted
        super().update(player)
        
    def die(self):
        """Drops Leather (ID 14) into the world when killed."""
        super().die()
class Penguin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Adjusted size for a slightly more blocky look, still small
        self.image = pygame.Surface([BLOCK_SIZE * 0.7, BLOCK_SIZE * 0.8]) 
        self.image.fill((0, 0, 0, 0)) # Transparent background
        self.image.set_colorkey((0, 0, 0))
        
        body_width = int(BLOCK_SIZE * 0.5)
        body_height = int(BLOCK_SIZE * 0.6)
        
        # Main Body (Black - a blocky rectangle)
        # Positioned slightly off-center to allow for flippers
        pygame.draw.rect(self.image, (0, 0, 0), (int(BLOCK_SIZE * 0.1), int(BLOCK_SIZE * 0.2), body_width, body_height))
        
        # White Belly (smaller rectangle on top of black body)
        belly_width = int(body_width * 0.6)
        belly_height = int(body_height * 0.8)
        pygame.draw.rect(self.image, (255, 255, 255), 
                         (int(BLOCK_SIZE * 0.1) + (body_width - belly_width) // 2, 
                          int(BLOCK_SIZE * 0.25), belly_width, belly_height))
        
        # Head (Black - more distinct from body)
        head_size = int(BLOCK_SIZE * 0.35)
        pygame.draw.rect(self.image, (0, 0, 0), (int(BLOCK_SIZE * 0.15), 0, head_size, head_size))
        
        # Eyes (Prominent white squares, then black pupils)
        eye_size = 4
        # Left Eye
        pygame.draw.rect(self.image, (255, 255, 255), (int(BLOCK_SIZE * 0.18), int(BLOCK_SIZE * 0.08), eye_size, eye_size))
        pygame.draw.rect(self.image, (0, 0, 0), (int(BLOCK_SIZE * 0.18) + 1, int(BLOCK_SIZE * 0.08) + 1, 2, 2))
        # Right Eye
        pygame.draw.rect(self.image, (255, 255, 255), (int(BLOCK_SIZE * 0.18) + head_size - eye_size - 2, int(BLOCK_SIZE * 0.08), eye_size, eye_size))
        pygame.draw.rect(self.image, (0, 0, 0), (int(BLOCK_SIZE * 0.18) + head_size - eye_size - 1, int(BLOCK_SIZE * 0.08) + 1, 2, 2))
        
        # Beak (Orange - triangular or small rectangle)
        # Simple triangular beak
        beak_x = int(BLOCK_SIZE * 0.15 + head_size / 2)
        beak_y = int(BLOCK_SIZE * 0.08 + eye_size + 2)
        pygame.draw.polygon(self.image, (255, 140, 0), [
            (beak_x, beak_y),
            (beak_x - 3, beak_y + 5),
            (beak_x + 3, beak_y + 5)
        ])
        
        # Flippers (Black - small rectangles attached to the side of the body)
        flipper_width = 5
        flipper_height = int(BLOCK_SIZE * 0.2)
        # Left flipper
        pygame.draw.rect(self.image, (0, 0, 0), (int(BLOCK_SIZE * 0.1) - flipper_width, int(BLOCK_SIZE * 0.3), flipper_width, flipper_height))
        # Right flipper
        pygame.draw.rect(self.image, (0, 0, 0), (int(BLOCK_SIZE * 0.1) + body_width, int(BLOCK_SIZE * 0.3), flipper_width, flipper_height))
        
        # Feet (Orange - small, blocky rectangles at the bottom)
        foot_width = int(BLOCK_SIZE * 0.15)
        foot_height = 4
        pygame.draw.rect(self.image, (255, 140, 0), (int(BLOCK_SIZE * 0.15), int(BLOCK_SIZE * 0.7), foot_width, foot_height))
        pygame.draw.rect(self.image, (255, 140, 0), (int(BLOCK_SIZE * 0.15) + body_width - foot_width, int(BLOCK_SIZE * 0.7), foot_width, foot_height))

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
        
    def take_damage(self, amount):
        """Handle taking damage."""
        self.health -= amount
        if self.health <= 0:
            self.kill()
    
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

    def update(self, player=None): # player argument added for compatibility if needed, not used by Penguin itself
        # Waddle around or swim
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

class Zombie(Mob):
    """A hostile mob that chases and damages the player."""
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 2, (0, 100, 0)) # Green
        self.health = 20
        self.max_health = 20
        self.speed = 2.0
        self.aggro_range = BLOCK_SIZE * 8
        self.attack_damage = 3
        self.attack_cooldown = FPS * 1
        self.attack_timer = 0
        self.drop_id = 13 # Rotten Flesh
        self.direction = random.choice([-1, 1])  # For wandering behavior
        
        # Enhanced drawing with body parts
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        # Legs (green)
        leg_color = (50, 100, 50)
        pygame.draw.rect(self.image, leg_color, (8, BLOCK_SIZE * 1.2, 10, BLOCK_SIZE * 0.8))  # Left leg
        pygame.draw.rect(self.image, leg_color, (22, BLOCK_SIZE * 1.2, 10, BLOCK_SIZE * 0.8))  # Right leg
        
        # Body (darker green shirt)
        pygame.draw.rect(self.image, (40, 80, 70), (5, BLOCK_SIZE * 0.5, 30, BLOCK_SIZE * 0.7))
        
        # Arms (green)
        pygame.draw.rect(self.image, (60, 110, 60), (0, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.5))  # Left arm
        pygame.draw.rect(self.image, (60, 110, 60), (34, BLOCK_SIZE * 0.6, 6, BLOCK_SIZE * 0.5))  # Right arm
        
        # Head (green)
        pygame.draw.rect(self.image, (70, 120, 70), (10, 2, 20, 20))
        
        # Hair (dark)
        pygame.draw.rect(self.image, (30, 30, 30), (10, 2, 20, 4))
        
        # Eyes (glowing red - zombie eyes)
        pygame.draw.rect(self.image, (255, 0, 0), (14, 10, 4, 4))  # Left eye
        pygame.draw.rect(self.image, (255, 0, 0), (22, 10, 4, 4))  # Right eye
        
        # Mouth (dark line)
        pygame.draw.rect(self.image, (30, 30, 30), (14, 17, 12, 2))        
    def attack(self, player):
        """Zombie attacks the player on contact."""
        if self.attack_timer <= 0:
            player.take_damage(self.attack_damage)
            self.attack_timer = self.attack_cooldown
        
    def die(self):
        """Drops Rotten Flesh (ID 13)."""
        super().die()
    
    def ai_move(self, player):
        """Hostile AI: Chase player if in range, otherwise wander."""
        
        player_dist_x = player.rect.centerx - self.rect.centerx
        player_dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(player_dist_x**2 + player_dist_y**2)
        
        self.vel_x = 0
        
        if distance < self.aggro_range:
            # 1. Aggro Mode: Chase player
            if abs(player_dist_x) > BLOCK_SIZE * 0.1:
                if player_dist_x > 0:
                    self.vel_x = self.speed
                else:
                    self.vel_x = -self.speed
            else:
                self.vel_x = 0
        
        else:
            # 2. Wandering Mode
            self.attack_timer += 1
            if self.attack_timer % (FPS * 3) == 0: 
                self.direction = random.choice([-1, 1])
                self.vel_x = self.direction * (self.speed * 0.5)
        
        # Cliff/Wall avoidance logic (same as Spider)
        if self.vel_x != 0 and distance >= self.aggro_range and self.is_on_ground:
            direction = 1 if self.vel_x > 0 else -1
            check_x = self.rect.centerx + direction * BLOCK_SIZE
            check_y = self.rect.bottom + 1
            
            check_col = check_x // BLOCK_SIZE
            check_row = check_y // BLOCK_SIZE
            
            if (0 <= check_row < GRID_HEIGHT and 
                0 <= check_col < GRID_WIDTH and 
                WORLD_MAP[check_row][check_col] == 0):
                self.vel_x = 0 

    def update(self, player):
        if self.attack_timer > 0:
            self.attack_timer -= 1
            
        self.ai_move(player)
        super().update(player)

class Spider(Mob):
    """A hostile mob that is wide, short, and pounces."""
    def __init__(self, x, y):
        # The correct super() call from earlier steps
        super().__init__(x, y, BLOCK_SIZE * 2, BLOCK_SIZE, (40, 40, 40)) # Dark Gray
        self.health = 16
        self.max_health = 16
        self.speed = 2.2 
        self.aggro_range = BLOCK_SIZE * 9
        self.attack_damage = 2
        self.attack_cooldown = FPS * 0.8 
        self.attack_timer = 0
        self.drop_id = 0 
        
        # Pounce AI
        self.pounce_timer = 0
        self.pounce_cooldown = FPS * 2
        
        # Enhanced drawing with body parts
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        # Body (dark gray segments)
        pygame.draw.rect(self.image, (40, 40, 40), (BLOCK_SIZE * 0.3, 5, BLOCK_SIZE * 0.7, BLOCK_SIZE - 10))  # Abdomen
        pygame.draw.rect(self.image, (50, 50, 50), (BLOCK_SIZE * 0.8, 8, BLOCK_SIZE * 0.5, BLOCK_SIZE - 16))  # Head
        
        # 8 legs (4 on each side)
        leg_color = (30, 30, 30)
        leg_thickness = 3
        
        # Left side legs
        pygame.draw.rect(self.image, leg_color, (0, 10, 15, leg_thickness))  # Front left
        pygame.draw.rect(self.image, leg_color, (0, 16, 15, leg_thickness))
        pygame.draw.rect(self.image, leg_color, (0, 22, 15, leg_thickness))
        pygame.draw.rect(self.image, leg_color, (0, 28, 15, leg_thickness))
        
        # Right side legs
        pygame.draw.rect(self.image, leg_color, (BLOCK_SIZE * 2 - 15, 10, 15, leg_thickness))  # Front right
        pygame.draw.rect(self.image, leg_color, (BLOCK_SIZE * 2 - 15, 16, 15, leg_thickness))
        pygame.draw.rect(self.image, leg_color, (BLOCK_SIZE * 2 - 15, 22, 15, leg_thickness))
        pygame.draw.rect(self.image, leg_color, (BLOCK_SIZE * 2 - 15, 28, 15, leg_thickness))
        
        # Eyes (8 red glowing eyes)
        pygame.draw.rect(self.image, (255, 0, 0), (BLOCK_SIZE * 1.4, 10, 4, 4))  # Top row
        pygame.draw.rect(self.image, (255, 0, 0), (BLOCK_SIZE * 1.5, 10, 4, 4))
        pygame.draw.rect(self.image, (255, 0, 0), (BLOCK_SIZE * 1.6, 10, 4, 4))
        pygame.draw.rect(self.image, (255, 0, 0), (BLOCK_SIZE * 1.7, 10, 4, 4))
        pygame.draw.rect(self.image, (200, 0, 0), (BLOCK_SIZE * 1.45, 16, 3, 3))  # Bottom row
        pygame.draw.rect(self.image, (200, 0, 0), (BLOCK_SIZE * 1.55, 16, 3, 3))
        pygame.draw.rect(self.image, (200, 0, 0), (BLOCK_SIZE * 1.65, 16, 3, 3))
        pygame.draw.rect(self.image, (200, 0, 0), (BLOCK_SIZE * 1.75, 16, 3, 3))

    def ai_move(self, player):
        """Hostile AI: Chase player and pounce."""
        
        player_dist_x = player.rect.centerx - self.rect.centerx
        player_dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(player_dist_x**2 + player_dist_y**2)
        
        self.vel_x = 0
        if self.pounce_timer > 0:
            self.pounce_timer -= 1
        
        if distance < self.aggro_range:
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
            # 2. Wandering Mode (Simple: stay put)
            self.vel_x = 0
            
    def attack(self, target):
        """Performs a damage-dealing attack."""
        if self.attack_timer <= 0:
            target.take_damage(self.attack_damage)
            self.attack_timer = self.attack_cooldown
            
    def update(self, player):
        if self.attack_timer > 0:
            self.attack_timer -= 1
            
        self.ai_move(player)
        super().update(player)
        
        # Check for contact attack
        if self.rect.colliderect(player.rect):
            self.attack(player)

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
        self.explosion_radius = BLOCK_SIZE * 2
        
        self.fuse_time = FPS * 1.5
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
        
    def explode(self, player):
        """Handles the explosion effect: damages the player AND destroys blocks."""
        
        damage_distance = math.sqrt(
            (self.rect.centerx - player.rect.centerx)**2 + 
            (self.rect.centery - player.rect.centery)**2
        )
        
        if damage_distance < self.explosion_radius:
            # Damage calculation
            damage = max(1, 15 - int(15 * (damage_distance / self.explosion_radius)))
            player.take_damage(damage)
            
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
    def update(self, player):
        distance_sq = (self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2
        distance = math.sqrt(distance_sq)
        
        # Check if player is in aggro range
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
                        self.explode(player)
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
            self.vel_x = 0
            self.fuse_timer = -1 # Reset fuse if player leaves range

        # Apply general Mob physics (gravity and collision)
        super().update(player)

class Skeleton(Mob):
    """A hostile mob that shoots arrows at the player from a distance."""
    def __init__(self, x, y):
        # Bone white color, 1 block wide, 2.5 blocks high (slightly taller than Zombie/Player)
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 2.5, (200, 200, 200)) 
        
        self.max_health = 20
        self.health = 20
        self.speed = 1.8 # Slower walking speed
        self.aggro_range = BLOCK_SIZE * 12 # Aggro from farther away (ranged mob)
        self.attack_range = BLOCK_SIZE * 8 # Will stop moving to shoot from this distance
        self.attack_damage = 4
        self.attack_cooldown = FPS * 2 # Shoots every 2 seconds
        self.attack_timer = self.attack_cooldown
        self.drop_id = 0 # No drop in this simple version (could drop sticks/bones)
        
        # Enhanced drawing with skeletal body parts
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        bone_color = (200, 200, 200)
        dark_bone = (170, 170, 170)
        
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
        pygame.draw.rect(self.image, (100, 150, 255), (14, 10, 3, 3))  # Left glow
        pygame.draw.rect(self.image, (100, 150, 255), (24, 10, 3, 3))  # Right glow
        
        # Nose hole (small triangle represented as rect)
        pygame.draw.rect(self.image, (0, 0, 0), (17, 14, 6, 3)) 
        
    def attack(self, target):
        """Performs a ranged attack (shoots an invisible arrow)."""
        if self.attack_timer <= 0:
            # We don't need a visible projectile; just calculate if the "arrow" hits.
            
            # Simple line-of-sight check (if the mob is roughly centered with the player)
            # A more complex check would involve collision with blocks.
            target.take_damage(self.attack_damage)
            
            # Print a message for debugging
            print(f"Skeleton shot player for {self.attack_damage} damage!")
            self.attack_timer = self.attack_cooldown
            
    def ai_move(self, player):
        """Hostile AI: Chase player if outside attack range, stop and shoot if inside."""
        
        player_dist_x = player.rect.centerx - self.rect.centerx
        player_dist_y = player.rect.centery - self.rect.centery
        distance = math.sqrt(player_dist_x**2 + player_dist_y**2)
        
        self.vel_x = 0
        
        if distance < self.aggro_range:
            
            # 1. Attack Mode: If within shooting range, stop and shoot.
            if distance < self.attack_range:
                self.vel_x = 0
                self.attack(player) # Attempt to attack every frame (cooldown controls rate)
            
            # 2. Chase Mode: If outside shooting range, chase.
            else: 
                if player_dist_x > 0:
                    self.vel_x = self.speed
                else:
                    self.vel_x = -self.speed
        
        # Apply standard wall/cliff avoidance logic
        if self.vel_x != 0 and self.is_on_ground:
            direction = 1 if self.vel_x > 0 else -1
            check_x = self.rect.centerx + direction * BLOCK_SIZE
            check_y = self.rect.bottom + 1
            
            check_col = check_x // BLOCK_SIZE
            check_row = check_y // BLOCK_SIZE
            
            if (0 <= check_row < GRID_HEIGHT and 
                0 <= check_col < GRID_WIDTH and 
                WORLD_MAP[check_row][check_col] == 0):
                self.vel_x = 0 

    def update(self, player):
        if self.attack_timer > 0:
            self.attack_timer -= 1
            
        self.ai_move(player)
        super().update(player)

    def die(self):
        """Drops are handled by the base Mob class."""
        super().die()

class Narwhal(Mob):
    """A peaceful aquatic mob that swims in water."""
    def __init__(self, x, y):
        # White/light gray color, long and thin
        # Dimensions: 1.5 blocks wide, 0.5 blocks high
        super().__init__(x, y, BLOCK_SIZE * 1.5, BLOCK_SIZE * 0.5, (230, 230, 255)) 
        
        self.max_health = 10
        self.health = 10
        self.speed = 1.5 
        self.gravity = 0  # No gravity for narwhals
        self.swim_timer = random.randint(FPS, FPS * 3) # Time before changing direction
        self.vertical_timer = random.randint(FPS, FPS * 2)  # Time before changing vertical direction
        self.drop_id = 0 
        
        # Enhanced drawing with body parts
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        w = int(BLOCK_SIZE * 1.5)
        h = int(BLOCK_SIZE * 0.5)
        
        # Body (rounded white/gray whale body)
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
        self.vel_y = random.uniform(-0.5, 0.5)  # Random vertical movement

    def ai_move(self, player):
        """Aquatic AI: Swim in water with both horizontal and vertical movement."""
        
        self.swim_timer -= 1
        self.vertical_timer -= 1
        
        # Check if in water
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        in_water = False
        
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
            in_water = WORLD_MAP[center_row][center_col] == 5
        
        if not in_water:
            # If not in water, stop moving and apply gravity to fall naturally
            # Gravity will be handled by the Mob class update method
            self.vel_y = 0  # Don't force sink, let gravity handle it
            # FIXED: Don't reset vel_x here, let it maintain direction
        else:
            # Change horizontal direction periodically
            if self.swim_timer <= 0:
                self.vel_x *= -1
                self.swim_timer = random.randint(FPS * 2, FPS * 5)
            
            # Change vertical direction periodically
            if self.vertical_timer <= 0:
                self.vel_y = random.uniform(-1.5, 1.5)  # Random vertical velocity
                self.vertical_timer = random.randint(FPS, FPS * 3)
            
            # Check one block ahead for a solid block (not water or air)
            # Check multiple points: top, center, and bottom of narwhal
            direction = 1 if self.vel_x > 0 else -1
            
            check_x = self.rect.centerx + direction * self.rect.width
            
            # Check at multiple vertical positions
            check_points = [
                self.rect.top,
                self.rect.centery,
                self.rect.bottom - 1
            ]
            
            should_turn = False
            
            for check_y in check_points:
                check_col = check_x // BLOCK_SIZE
                check_row = check_y // BLOCK_SIZE
                
                # Boundary Check
                if not (0 <= check_row < GRID_HEIGHT and 0 <= check_col < GRID_WIDTH):
                    should_turn = True
                    break
                
                block_id = WORLD_MAP[check_row][check_col]
                
                # If hitting a solid block (not Air 0 or Water 5), turn around
                if block_id != 0 and block_id != 5:
                    should_turn = True
                    break
            
            if should_turn:
                self.vel_x *= -1
                self.swim_timer = FPS * 2

    def update(self, player):
        self.ai_move(player)
        
        # Check if in water
        center_col = self.rect.centerx // BLOCK_SIZE
        center_row = self.rect.centery // BLOCK_SIZE
        in_water = False
        
        if 0 <= center_row < GRID_HEIGHT and 0 <= center_col < GRID_WIDTH:
            in_water = WORLD_MAP[center_row][center_col] == 5
        
        if in_water:
            # Check for vertical collisions before applying movement
            next_y = self.rect.centery + self.vel_y
            check_col_left = self.rect.left // BLOCK_SIZE
            check_col_right = self.rect.right // BLOCK_SIZE
            check_row = int(next_y) // BLOCK_SIZE
            
            # Check if we're about to hit a solid block vertically
            vertical_collision = False
            for check_col in [check_col_left, check_col_right]:
                if 0 <= check_row < GRID_HEIGHT and 0 <= check_col < GRID_WIDTH:
                    block_id = WORLD_MAP[check_row][check_col]
                    if block_id != 0 and block_id != 5:  # Solid block (not air or water)
                        vertical_collision = True
                        break
            
            # If vertical collision detected, reverse vertical direction
            if vertical_collision:
                self.vel_y *= -1
                self.vertical_timer = FPS * 2
            
            # Apply swimming movement (no gravity in water)
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y

            # Keep narwhal within bounds
            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(GRID_WIDTH * BLOCK_SIZE, self.rect.right)
            self.rect.top = max(0, self.rect.top)
            self.rect.bottom = min(GRID_HEIGHT * BLOCK_SIZE, self.rect.bottom)
        else:
            # Out of water - apply normal mob physics (gravity and collision)
            super().update(player)

# --- Mob Classes (Add this after Player, or near the other Mobs) ---
class Villager(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Villagers are slightly taller than the player (1.5 blocks)
        self.image = pygame.Surface([BLOCK_SIZE, BLOCK_SIZE * 1.5])
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        
        # Skin Color & Features
        skin_color = (250, 220, 180)
        robe_color = (50, 150, 50)
        
        # Body (Robe)
        pygame.draw.rect(self.image, robe_color, (5, BLOCK_SIZE * 0.5, 30, BLOCK_SIZE))
        
        # Arms (hidden in robe for simplicity)
        
        # Head (Oversized, balding)
        pygame.draw.rect(self.image, skin_color, (10, 0, 20, 20)) 
        
        # Nose (SMALLER - The defining feature!)
        pygame.draw.rect(self.image, skin_color, (18, 12, 4, 6))  # Changed from (18, 10, 4, 10)
        
        # Eyes
        pygame.draw.circle(self.image, (0, 0, 0), (16, 10), 2)
        pygame.draw.circle(self.image, (0, 0, 0), (24, 10), 2)
        
        # Unibrow/Forehead
        pygame.draw.rect(self.image, (60, 40, 20), (12, 5, 16, 3))
        
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 1.5 # Slower than the player
        self.gravity = 0.5
        self.health = 10
        self.max_health = 10
        self.is_passive = True
        self.wandering_timer = random.randint(30, 120)
        self.on_ground = False
        
        # Trading system
        self.has_trade = True
        self.trade_cooldown = 0  # Frames until can trade again
        self.trade_cooldown_max = 300  # 5 seconds at 60 FPS

    def take_damage(self, amount):
        """Handle taking damage."""
        self.health -= amount
        if self.health <= 0:
            self.kill()  # Remove from all sprite groups
            
    def can_trade(self):
        """Check if the villager can currently trade."""
        return self.has_trade and self.trade_cooldown == 0
    
    def attempt_trade(self, player_inventory):
        """
        Attempt to trade with the player.
        Trade: 5 Dirt (ID 2) for 1 Emerald (we'll use block ID 23 for emerald)
        Returns: True if trade successful, False otherwise
        """
        if not self.can_trade():
            return False
        
        # Count dirt in player inventory (inventory is a dict with block_id as key)
        dirt_count = player_inventory.get(2, 0)  # DIRT_ID = 2
        
        if dirt_count >= 5:
            # Remove 5 dirt from inventory
            player_inventory[2] = dirt_count - 5
            
            # If dirt count is now 0, remove the key
            if player_inventory[2] == 0:
                del player_inventory[2]
            
            # Add emerald to inventory
            if 23 in player_inventory:
                player_inventory[23] += 1
            else:
                player_inventory[23] = 1
            
            # Set cooldown
            self.trade_cooldown = self.trade_cooldown_max
            print("✅ Trade successful! 5 Dirt → 1 Emerald")
            return True
        else:
            print(f"❌ Trade failed! Need 5 Dirt, you have {dirt_count}")
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

    def update(self, player):
        # Update trade cooldown
        if self.trade_cooldown > 0:
            self.trade_cooldown -= 1
        
        # Basic wandering behavior
        self.wandering_timer -= 1
        if self.wandering_timer <= 0:
            direction = random.choice([-1, 0, 1])
            self.vel_x = direction * self.speed
            self.wandering_timer = random.randint(60, 200)

        # Apply gravity (simple non-player version)
        self.vel_y += self.gravity
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.x += self.vel_x
        self.collide_x()
        
        self.rect.y += self.vel_y
        self.collide_y()

# --- World Drawing ---
def update_water_flow():
    """Makes water flow and spread to adjacent blocks."""
    global WORLD_MAP
    
    # We need to track changes separately to avoid modifying while iterating
    changes = []
    
    for row in range(GRID_HEIGHT - 1):  # Don't check bottom row
        for col in range(GRID_WIDTH):
            if WORLD_MAP[row][col] == 5:  # If current block is water
                
                # 1. Water flows down if there's air below
                if row + 1 < GRID_HEIGHT and WORLD_MAP[row + 1][col] == 0:
                    changes.append((row + 1, col, 5))  # Water flows down
                
                # 2. Water spreads horizontally if there's air and it's not floating
                else:
                    # Check if water has ground below or is resting on something
                    has_support = False
                    if row + 1 < GRID_HEIGHT:
                        block_below = WORLD_MAP[row + 1][col]
                        if block_below != 0:  # Any non-air block below
                            has_support = True
                    
                    if has_support:
                        # Spread left
                        if col > 0 and WORLD_MAP[row][col - 1] == 0:
                            # Check if there's support below the left position
                            if row + 1 < GRID_HEIGHT and WORLD_MAP[row + 1][col - 1] != 0:
                                changes.append((row, col - 1, 5))
                        
                        # Spread right
                        if col < GRID_WIDTH - 1 and WORLD_MAP[row][col + 1] == 0:
                            # Check if there's support below the right position
                            if row + 1 < GRID_HEIGHT and WORLD_MAP[row + 1][col + 1] != 0:
                                changes.append((row, col + 1, 5))
    
    # Apply all changes
    for row, col, block_id in changes:
        WORLD_MAP[row][col] = block_id

def draw_world(camera_x, camera_y):
    """Draws only the visible portion of the world map to the screen."""
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

def calculate_camera_offset(player_rect):
    """Calculates the camera offset to center on the player."""
    camera_x = player_rect.centerx - SCREEN_WIDTH // 2
    camera_y = player_rect.centery - SCREEN_HEIGHT // 2
    
    camera_x = max(0, min(camera_x, GRID_WIDTH * BLOCK_SIZE - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, GRID_HEIGHT * BLOCK_SIZE - SCREEN_HEIGHT))
    
    return camera_x, camera_y

# --- Interaction Handling ---
def handle_interaction(player, mobs, event, camera_x, camera_y):
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
            damage = 1 # Base damage
            
            # Check if player is holding a tool
            held_id = player.held_block
            if held_id in BLOCK_TYPES and "tool_level" in BLOCK_TYPES[held_id]:
                tool_level = BLOCK_TYPES[held_id]["tool_level"]
                damage = 2 + tool_level # Tools do more damage
            
            hit_mob.take_damage(damage)
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
                    if held_id in BLOCK_TYPES and "tool_level" in BLOCK_TYPES[held_id]:
                        tool_level = BLOCK_TYPES[held_id]["tool_level"]
                    
                    if tool_level >= required_level:
                        WORLD_MAP[target_row][target_col] = 0
                        player.add_to_inventory(block_id, 1)
    
    # Right Click: Place Block OR Mount Camel OR Trade with Villager
    elif event.button == 3:
        # First check if clicking on a villager to trade
        clicked_villager = None
        
        for mob in mobs:
            if isinstance(mob, Villager) and mob.rect.collidepoint(target_world_x, target_world_y):
                clicked_villager = mob
                break
        
        if clicked_villager:
            # Attempt to trade with the villager
            clicked_villager.attempt_trade(player.inventory)
            return
        
        # Check if clicking on a camel to mount
        target_rect = pygame.Rect(target_world_x, target_world_y, 1, 1)
        clicked_camel = None
        
        for mob in mobs:
            if isinstance(mob, Camel) and mob.rect.collidepoint(target_world_x, target_world_y):
                clicked_camel = mob
                break
        
        if clicked_camel and player.mounted_camel is None:
            # Mount the camel
            player.mount_camel(clicked_camel)
            return
        
        # Otherwise, place a block
        held_id = player.held_block
        
        if held_id != 0 and WORLD_MAP[target_row][target_col] == 0:
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
                    if player.consume_item(held_id, 1):
                        WORLD_MAP[target_row][target_col] = held_id
# --- HUD Drawing ---
def draw_hud(player):
    """Draws the hotbar, health bar, hunger bar, and held item name."""
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
        
        # Draw item in slot
        item_id = player.hotbar_slots[i]
        if item_id != 0 and item_id in BLOCK_TYPES:
            block_color = BLOCK_TYPES[item_id]["color"]
            inner_rect = pygame.Rect(slot_x + 5, HOTBAR_Y + 5, SLOT_SIZE - 10, SLOT_SIZE - 10)
            pygame.draw.rect(screen, block_color, inner_rect)
            
            # Draw item count
            count = player.inventory.get(item_id, 0)
            if count > 1:
                count_text = FONT_SMALL.render(str(count), True, (255, 255, 255))
                screen.blit(count_text, (slot_x + SLOT_SIZE - count_text.get_width() - 2, 
                                        HOTBAR_Y + SLOT_SIZE - count_text.get_height() - 2))
    
    # Draw Health Bar
    health_bar_width = 200
    health_bar_height = 20
    health_bar_x = 10
    health_bar_y = 10
    
    pygame.draw.rect(screen, (50, 50, 50), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    health_ratio = player.health / player.max_health
    pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width * health_ratio, health_bar_height))
    
    health_text = FONT_SMALL.render(f"Health: {player.health}/{player.max_health}", True, (255, 255, 255))
    screen.blit(health_text, (health_bar_x + 5, health_bar_y + 2))
    
    # Draw Hunger Bar
    hunger_bar_y = health_bar_y + health_bar_height + 5
    
    pygame.draw.rect(screen, (50, 50, 50), (health_bar_x, hunger_bar_y, health_bar_width, health_bar_height))
    hunger_ratio = player.hunger / player.max_hunger
    pygame.draw.rect(screen, (255, 165, 0), (health_bar_x, hunger_bar_y, health_bar_width * hunger_ratio, health_bar_height))
    
    hunger_text = FONT_SMALL.render(f"Hunger: {player.hunger}/{player.max_hunger}", True, (255, 255, 255))
    screen.blit(hunger_text, (health_bar_x + 5, hunger_bar_y + 2))
    
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

# --- Crafting Functions ---
def get_craftable_item():
    """Checks if the current crafting grid matches any recipe."""
    # Create a frozenset of (block_id, count) tuples from the grid
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
    
    grid_set = frozenset(grid_contents.items())
    
    # Check against all recipes
    if grid_set in CRAFTING_RECIPES:
        return CRAFTING_RECIPES[grid_set]
    
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
    SLOT_SIZE = 60
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

def handle_crafting_interaction(player, event):
    """Handles clicks inside the crafting menu."""
    global CRAFTING_GRID, CRAFTING_AMOUNTS
    
    # 1. Check Input Slots (Indices 0-3)
    for i in range(4):
        if CRAFTING_SLOT_RECTS[i].collidepoint(event.pos):
            
            if event.button == 1: # LMB: Add item
                held_id = player.held_block
                
                # Check if held item is craftable ingredient (not a tool itself)
                if held_id != 0 and BLOCK_TYPES.get(held_id, {}).get("mineable", True): # Assume tools are non-mineable and not placed
                    
                    # Check if player has the item
                    if player.inventory.get(held_id, 0) > 0:
                        # If slot is empty or has same item
                        if CRAFTING_GRID[i] == 0 or CRAFTING_GRID[i] == held_id:
                            CRAFTING_GRID[i] = held_id
                            CRAFTING_AMOUNTS[i] += 1
                            player.consume_item(held_id, 1)

            elif event.button == 3: # RMB: Remove item
                # Remove one item from the crafting slot and return it to the player's inventory
                if CRAFTING_GRID[i] != 0 and CRAFTING_AMOUNTS[i] > 0:
                    # Give one back to the player
                    player.add_to_inventory(CRAFTING_GRID[i], 1)
                    CRAFTING_AMOUNTS[i] -= 1
                    if CRAFTING_AMOUNTS[i] <= 0:
                        CRAFTING_GRID[i] = 0
                        CRAFTING_AMOUNTS[i] = 0
            return

    # 2. Check Output Slot (Index 4)
    if len(CRAFTING_SLOT_RECTS) > 4 and CRAFTING_SLOT_RECTS[4].collidepoint(event.pos) and event.button == 1:
        craftable = get_craftable_item()
        if craftable:
            output_id, output_count = craftable
            
            # Consume all ingredients from the crafting grid
            for i in range(4):
                if CRAFTING_GRID[i] != 0:
                    CRAFTING_GRID[i] = 0
                    CRAFTING_AMOUNTS[i] = 0
            
            # Add the crafted item to the player's inventory
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
            
    # Clear the grid state
    CRAFTING_GRID = [0, 0, 0, 0]
    CRAFTING_AMOUNTS = [0, 0, 0, 0]


# --- Game Loop Setup ---

# Initial World and Mob Generation
WORLD_MAP, MOBS = generate_world() 

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

running = True
water_flow_timer = 0  # Timer to control water flow updates

# --- Main Game Loop ---
while running:
    
    # 1. EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if player.is_crafting:
                reset_crafting_grid(player) # Cleanup on Escape
                player.is_crafting = False
            else:
                running = False
        
        # Mouse Interaction (Mining/Placing/Attacking OR Crafting)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if player.is_crafting:
                handle_crafting_interaction(player, event)
            else:
                camera_x, camera_y = calculate_camera_offset(player.rect)
                handle_interaction(player, MOBS, event, camera_x, camera_y)

    # 2. INPUT PROCESSING
    keys = pygame.key.get_pressed()
    player.handle_input(keys)

    # 3. GAME LOGIC UPDATE
    if not player.is_crafting: 
        player.update()
        MOBS.update(player)
        
        # Sync player position with camel AFTER camel has moved
        if player.mounted_camel is not None and player.mounted_camel.alive():
            player.rect.centerx = player.mounted_camel.rect.centerx
            player.rect.bottom = player.mounted_camel.rect.top + player.mount_offset_y
    
    # Water flow update (every 10 frames to reduce lag)
    water_flow_timer += 1
    if water_flow_timer >= 10:
        update_water_flow()
        water_flow_timer = 0
    
    # Mob Attack/Damage Logic - check collision regardless of riding status
    for mob in MOBS:
        if player.rect.colliderect(mob.rect):
            if hasattr(mob, 'attack') and player.damage_flash_timer <= 0:
                mob.attack(player) 
    
    # Calculate camera offset 
    camera_x, camera_y = calculate_camera_offset(player.rect)

    # 4. DRAWING
    screen.fill(BLOCK_TYPES[0]["color"]) 
    
    draw_world(camera_x, camera_y)

    # Draw block highlight 
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

    # Draw Mobs
    for mob in MOBS:
        mob_screen_pos = (mob.rect.x - camera_x, mob.rect.y - camera_y)
        screen.blit(mob.image, mob_screen_pos)
        
        # Health Bar
        if mob.health < mob.max_health:
            bar_width = mob.rect.width
            bar_height = 5
            health_ratio = mob.health / mob.max_health
            pygame.draw.rect(screen, (50, 50, 50), (mob_screen_pos[0], mob_screen_pos[1] - 10, bar_width, bar_height))
            pygame.draw.rect(screen, (255, 0, 0), (mob_screen_pos[0], mob_screen_pos[1] - 10, bar_width * health_ratio, bar_height))
    
    # Draw the player 
    player_screen_pos = (player.rect.x - camera_x, player.rect.y - camera_y)
    screen.blit(player.get_image(), player_screen_pos)

    # Draw the HUD elements 
    draw_hud(player)
    
    # Draw Crafting Menu OVERLAY (if active)
    if player.is_crafting:
        draw_crafting_menu(player)

    # 5. UPDATE DISPLAY & CLOCK
    pygame.display.flip()
    clock.tick(FPS) 

# --- Cleanup ---
pygame.quit()
