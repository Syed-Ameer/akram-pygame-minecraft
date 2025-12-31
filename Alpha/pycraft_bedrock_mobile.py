"""
PyCraft Bedrock Edition - Mobile/Tablet Version
Optimized for touch controls and smaller screens
"""

import pygame
import random
import math
import json
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Get device screen info for adaptive sizing
info = pygame.display.Info()
DEVICE_WIDTH = info.current_w
DEVICE_HEIGHT = info.current_h

# Mobile/Tablet screen settings (adaptive)
SCREEN_WIDTH = min(1280, DEVICE_WIDTH)
SCREEN_HEIGHT = min(720, DEVICE_HEIGHT)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PyCraft Bedrock Edition - Mobile")

# Performance settings for mobile
FPS = 60  # Higher FPS for smoother gameplay
RENDER_DISTANCE = 30  # Better render distance

# Block settings (larger for touch)
BLOCK_SIZE = 48  # Larger blocks for mobile visibility
GRID_WIDTH = 400  # Larger world like Java edition
GRID_HEIGHT = 150  # Taller world for better caves

# Touch control settings
JOYSTICK_SIZE = 120
JOYSTICK_OUTER_RADIUS = 60
JOYSTICK_INNER_RADIUS = 25
BUTTON_SIZE = 60

# UI Colors
UI_BACKGROUND = (40, 40, 40, 180)
UI_BORDER = (100, 100, 100)
BUTTON_COLOR = (70, 70, 70, 200)
BUTTON_HOVER = (90, 90, 90, 200)

# Game constants - Block IDs
AIR_ID = 0
GRASS_ID = 1
DIRT_ID = 2
STONE_ID = 3
WOOD_ID = 4
LEAVES_ID = 5
WATER_ID = 6
SAND_ID = 7
COBBLESTONE_ID = 8
PLANKS_ID = 9
BEDROCK_ID = 10
COAL_ORE_ID = 11
IRON_ORE_ID = 12
GOLD_ORE_ID = 13
DIAMOND_ORE_ID = 14
EMERALD_ORE_ID = 15
GLASS_ID = 16
BRICK_ID = 17
TNT_ID = 18
LAVA_ID = 19
OBSIDIAN_ID = 20
CRAFTING_TABLE_ID = 21
FURNACE_ID = 22
CHEST_ID = 23
SNOW_ID = 24
ICE_ID = 25
CACTUS_ID = 26
BAMBOO_ID = 27
FIRE_ID = 28
REDSTONE_ORE_ID = 29
LAPIS_ORE_ID = 30
NETHER_PORTAL_ID = 31
ENCHANTING_TABLE_ID = 32
ANVIL_ID = 33
BOOKSHELF_ID = 34
TORCH_ID = 35
GLOWSTONE_ID = 36

# Item IDs (100+)
COAL_ITEM = 100
IRON_INGOT = 101
GOLD_INGOT = 102
DIAMOND = 103
EMERALD = 104
STICK = 105
WOODEN_PICKAXE = 106
STONE_PICKAXE = 107
IRON_PICKAXE = 108
DIAMOND_PICKAXE = 109
WOODEN_SWORD = 110
STONE_SWORD = 111
IRON_SWORD = 112
DIAMOND_SWORD = 113
WOODEN_AXE = 114
STONE_AXE = 115
IRON_AXE = 116
DIAMOND_AXE = 117
BREAD = 118
APPLE = 119
COOKED_BEEF = 120
RAW_BEEF = 121
ENDER_PEARL = 122
BOW = 123
ARROW = 124
SHIELD = 125
TRIDENT = 126
ELYTRA = 127
TOTEM = 128
EXP_BOTTLE = 129
REDSTONE = 130
LAPIS = 131
BOOK = 132
PAPER = 133

# Simple block colors for mobile (no textures for performance)
BLOCK_COLORS = {
    0: None,  # Air
    1: (34, 139, 34),  # Grass
    2: (139, 69, 19),  # Dirt
    3: (128, 128, 128),  # Stone
    4: (101, 67, 33),  # Wood
    5: (0, 128, 0),  # Leaves
    6: (30, 144, 255, 150),  # Water (semi-transparent)
    7: (238, 214, 175),  # Sand
    8: (105, 105, 105),  # Cobblestone
    9: (160, 120, 70),  # Planks
    10: (64, 64, 64),  # Bedrock
    11: (70, 70, 70),  # Coal Ore
    12: (180, 140, 100),  # Iron Ore
    13: (255, 215, 0),  # Gold Ore
    14: (0, 255, 255),  # Diamond Ore
    15: (0, 200, 0),  # Emerald Ore
    16: (200, 230, 255),  # Glass
    17: (150, 80, 60),  # Brick
    18: (200, 0, 0),  # TNT
    19: (255, 100, 0),  # Lava
    20: (40, 20, 60),  # Obsidian
    21: (120, 80, 40),  # Crafting Table
    22: (90, 90, 90),  # Furnace
    23: (120, 90, 50),  # Chest
    24: (240, 250, 255),  # Snow
    25: (180, 220, 255),  # Ice
    26: (50, 150, 50),  # Cactus
    27: (100, 180, 80),  # Bamboo
    28: (255, 150, 0),  # Fire
    29: (150, 50, 50),  # Redstone Ore
    30: (50, 80, 150),  # Lapis Ore
    31: (80, 0, 120),  # Nether Portal
    32: (100, 50, 100),  # Enchanting Table
    33: (140, 140, 140),  # Anvil
    34: (130, 90, 50),  # Bookshelf
    35: (255, 200, 100),  # Torch
    36: (255, 220, 150),  # Glowstone
    100: (50, 50, 50),  # Coal
    101: (200, 200, 200),  # Iron Ingot
    102: (255, 215, 0),  # Gold Ingot
    103: (0, 255, 255),  # Diamond
    104: (0, 200, 100),  # Emerald
    105: (120, 80, 40),  # Stick
    106: (120, 80, 40),  # Wooden Pickaxe
    107: (128, 128, 128),  # Stone Pickaxe
    108: (200, 200, 200),  # Iron Pickaxe
    109: (0, 255, 255),  # Diamond Pickaxe
    110: (120, 80, 40),  # Wooden Sword
    111: (128, 128, 128),  # Stone Sword
    112: (200, 200, 200),  # Iron Sword
    113: (0, 255, 255),  # Diamond Sword
    114: (120, 80, 40),  # Wooden Axe
    115: (128, 128, 128),  # Stone Axe
    116: (200, 200, 200),  # Iron Axe
    117: (0, 255, 255),  # Diamond Axe
    118: (200, 150, 100),  # Bread
    119: (200, 50, 50),  # Apple
    120: (150, 80, 60),  # Cooked Beef
    121: (180, 50, 50),  # Raw Beef
    122: (100, 200, 150),  # Ender Pearl
    123: (120, 80, 40),  # Bow
    124: (200, 200, 200),  # Arrow
    125: (100, 100, 150),  # Shield
    126: (100, 180, 200),  # Trident
    127: (150, 100, 200),  # Elytra
    128: (220, 180, 50),  # Totem
    129: (100, 255, 100),  # Exp Bottle
    130: (200, 0, 0),  # Redstone
    131: (50, 80, 200),  # Lapis
    132: (150, 100, 50),  # Book
    133: (240, 240, 220),  # Paper
}

BLOCK_NAMES = {
    0: "Air", 1: "Grass", 2: "Dirt", 3: "Stone", 4: "Wood", 5: "Leaves",
    6: "Water", 7: "Sand", 8: "Cobblestone", 9: "Planks", 10: "Bedrock",
    11: "Coal Ore", 12: "Iron Ore", 13: "Gold Ore", 14: "Diamond Ore", 15: "Emerald Ore",
    16: "Glass", 17: "Brick", 18: "TNT", 19: "Lava", 20: "Obsidian",
    21: "Crafting Table", 22: "Furnace", 23: "Chest", 24: "Snow", 25: "Ice",
    26: "Cactus", 27: "Bamboo", 28: "Fire", 29: "Redstone Ore", 30: "Lapis Ore",
    31: "Nether Portal", 32: "Enchanting Table", 33: "Anvil", 34: "Bookshelf", 35: "Torch", 36: "Glowstone",
    100: "Coal", 101: "Iron Ingot", 102: "Gold Ingot", 103: "Diamond", 104: "Emerald",
    105: "Stick", 106: "Wooden Pickaxe", 107: "Stone Pickaxe", 108: "Iron Pickaxe", 109: "Diamond Pickaxe",
    110: "Wooden Sword", 111: "Stone Sword", 112: "Iron Sword", 113: "Diamond Sword",
    114: "Wooden Axe", 115: "Stone Axe", 116: "Iron Axe", 117: "Diamond Axe",
    118: "Bread", 119: "Apple", 120: "Cooked Beef", 121: "Raw Beef",
    122: "Ender Pearl", 123: "Bow", 124: "Arrow", 125: "Shield", 126: "Trident",
    127: "Elytra", 128: "Totem of Undying", 129: "Bottle o' Enchanting", 130: "Redstone",
    131: "Lapis Lazuli", 132: "Book", 133: "Paper",
}

# Block properties
BLOCK_TYPES = {
    1: {"mineable": True, "drops": 1, "hardness": 0.6, "tool": "shovel"},
    2: {"mineable": True, "drops": 2, "hardness": 0.5, "tool": "shovel"},
    3: {"mineable": True, "drops": 8, "hardness": 1.5, "tool": "pickaxe", "min_level": 0},
    4: {"mineable": True, "drops": 4, "hardness": 2.0, "tool": "axe"},
    5: {"mineable": True, "drops": 0, "hardness": 0.2, "tool": "shears"},
    7: {"mineable": True, "drops": 7, "hardness": 0.5, "tool": "shovel"},
    8: {"mineable": True, "drops": 8, "hardness": 2.0, "tool": "pickaxe", "min_level": 0},
    9: {"mineable": True, "drops": 9, "hardness": 2.0, "tool": "axe"},
    11: {"mineable": True, "drops": 100, "hardness": 3.0, "tool": "pickaxe", "min_level": 0},
    12: {"mineable": True, "drops": 12, "hardness": 3.0, "tool": "pickaxe", "min_level": 1},
    13: {"mineable": True, "drops": 13, "hardness": 3.0, "tool": "pickaxe", "min_level": 2},
    14: {"mineable": True, "drops": 103, "hardness": 3.0, "tool": "pickaxe", "min_level": 2},
    15: {"mineable": True, "drops": 104, "hardness": 3.0, "tool": "pickaxe", "min_level": 2},
    16: {"mineable": True, "drops": 16, "hardness": 0.3, "tool": "any"},
    20: {"mineable": True, "drops": 20, "hardness": 50.0, "tool": "pickaxe", "min_level": 3},
    21: {"mineable": True, "drops": 21, "hardness": 2.5, "tool": "axe"},
    22: {"mineable": True, "drops": 22, "hardness": 3.5, "tool": "pickaxe"},
}

# Tool properties
TOOL_PROPERTIES = {
    106: {"type": "pickaxe", "level": 0, "speed": 2.0, "damage": 2},  # Wooden Pickaxe
    107: {"type": "pickaxe", "level": 1, "speed": 4.0, "damage": 3},  # Stone Pickaxe
    108: {"type": "pickaxe", "level": 2, "speed": 6.0, "damage": 4},  # Iron Pickaxe
    109: {"type": "pickaxe", "level": 3, "speed": 8.0, "damage": 5},  # Diamond Pickaxe
    110: {"type": "sword", "level": 0, "speed": 1.0, "damage": 4},  # Wooden Sword
    111: {"type": "sword", "level": 1, "speed": 1.0, "damage": 5},  # Stone Sword
    112: {"type": "sword", "level": 2, "speed": 1.0, "damage": 6},  # Iron Sword
    113: {"type": "sword", "level": 3, "speed": 1.0, "damage": 7},  # Diamond Sword
    114: {"type": "axe", "level": 0, "speed": 2.0, "damage": 3},  # Wooden Axe
    115: {"type": "axe", "level": 1, "speed": 4.0, "damage": 4},  # Stone Axe
    116: {"type": "axe", "level": 2, "speed": 6.0, "damage": 5},  # Iron Axe
    117: {"type": "axe", "level": 3, "speed": 8.0, "damage": 6},  # Diamond Axe
}

# Food items
FOOD_ITEMS = {
    118: 5,  # Bread: +5 hunger
    119: 4,  # Apple: +4 hunger
    120: 8,  # Cooked Beef: +8 hunger
    121: 3,  # Raw Beef: +3 hunger
}

# Crafting recipes
RECIPES = {
    "planks": {"input": [(4, 1)], "output": (9, 4)},
    "stick": {"input": [(9, 2)], "output": (105, 4)},
    "crafting_table": {"input": [(9, 4)], "output": (21, 1)},
    "wooden_pickaxe": {"input": [(9, 3), (105, 2)], "output": (106, 1)},
    "wooden_sword": {"input": [(9, 2), (105, 1)], "output": (110, 1)},
    "wooden_axe": {"input": [(9, 3), (105, 2)], "output": (114, 1)},
    "stone_pickaxe": {"input": [(8, 3), (105, 2)], "output": (107, 1)},
    "stone_sword": {"input": [(8, 2), (105, 1)], "output": (111, 1)},
    "stone_axe": {"input": [(8, 3), (105, 2)], "output": (115, 1)},
    "iron_pickaxe": {"input": [(101, 3), (105, 2)], "output": (108, 1)},
    "iron_sword": {"input": [(101, 2), (105, 1)], "output": (112, 1)},
    "iron_axe": {"input": [(101, 3), (105, 2)], "output": (116, 1)},
    "diamond_pickaxe": {"input": [(103, 3), (105, 2)], "output": (109, 1)},
    "diamond_sword": {"input": [(103, 2), (105, 1)], "output": (113, 1)},
    "diamond_axe": {"input": [(103, 3), (105, 2)], "output": (117, 1)},
    "furnace": {"input": [(8, 8)], "output": (22, 1)},
    "chest": {"input": [(9, 8)], "output": (23, 1)},
    "tnt": {"input": [(7, 4), (100, 5)], "output": (18, 1)},
    "glass": {"input": [(7, 1)], "output": (16, 1), "smelt": True},
    "iron_ingot": {"input": [(12, 1)], "output": (101, 1), "smelt": True},
    "gold_ingot": {"input": [(13, 1)], "output": (102, 1), "smelt": True},
    "cooked_beef": {"input": [(121, 1)], "output": (120, 1), "smelt": True},
    "bread": {"input": [(1, 3)], "output": (118, 1)},  # Using grass as wheat substitute
    "bow": {"input": [(105, 3), (5, 3)], "output": (123, 1)},
    "arrow": {"input": [(105, 1), (28, 1), (5, 1)], "output": (124, 4)},
    "shield": {"input": [(9, 6), (101, 1)], "output": (125, 1)},
    "enchanting_table": {"input": [(132, 1), (103, 2), (20, 4)], "output": (32, 1)},
    "anvil": {"input": [(101, 31)], "output": (33, 1)},
    "bookshelf": {"input": [(9, 6), (132, 3)], "output": (34, 1)},
    "book": {"input": [(133, 3)], "output": (132, 1)},
    "paper": {"input": [(27, 3)], "output": (133, 3)},  # Bamboo to paper
    "torch": {"input": [(105, 1), (100, 1)], "output": (35, 4)},
    "redstone": {"input": [(29, 1)], "output": (130, 4), "smelt": False},
    "lapis": {"input": [(30, 1)], "output": (131, 4), "smelt": False},
}

# Biome constants
PLAINS_BIOME = 0
DESERT_BIOME = 1
SNOW_BIOME = 2
JUNGLE_BIOME = 3

# Time constants
DAY_LENGTH = 600
EVENING_LENGTH = 150
NIGHT_LENGTH = 600
MORNING_LENGTH = 150
TOTAL_CYCLE_LENGTH = DAY_LENGTH + EVENING_LENGTH + NIGHT_LENGTH + MORNING_LENGTH

DAY_PHASE = 0
EVENING_PHASE = 1
NIGHT_PHASE = 2
MORNING_PHASE = 3

# Achievements
ACHIEVEMENTS = {
    "getting_wood": {"name": "Getting Wood", "desc": "Mine a wood block", "unlocked": False},
    "getting_upgrade": {"name": "Getting an Upgrade", "desc": "Craft a pickaxe", "unlocked": False},
    "diamonds": {"name": "Diamonds!", "desc": "Mine diamond ore", "unlocked": False},
    "enchanter": {"name": "Enchanter", "desc": "Build an enchanting table", "unlocked": False},
    "monster_hunter": {"name": "Monster Hunter", "desc": "Kill 10 hostile mobs", "unlocked": False, "progress": 0},
    "adventuring_time": {"name": "Adventuring Time", "desc": "Visit all biomes", "unlocked": False, "biomes": set()},
    "iron_man": {"name": "Iron Man", "desc": "Smelt iron ore", "unlocked": False},
}

# Font
FONT = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)
FONT_LARGE = pygame.font.Font(None, 48)

clock = pygame.time.Clock()


class TouchButton:
    """Touch-friendly button"""
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.pressed = False
        self.color = BUTTON_COLOR
        
    def draw(self, surface):
        # Draw button with rounded corners
        color = BUTTON_HOVER if self.pressed else self.color
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, color, (0, 0, self.rect.width, self.rect.height), border_radius=10)
        surface.blit(s, self.rect)
        
        # Draw border
        pygame.draw.rect(surface, UI_BORDER, self.rect, 2, border_radius=10)
        
        # Draw text
        text_surf = FONT_SMALL.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_touch(self, pos):
        return self.rect.collidepoint(pos)


class VirtualJoystick:
    """Virtual joystick for movement"""
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.outer_radius = JOYSTICK_OUTER_RADIUS
        self.inner_radius = JOYSTICK_INNER_RADIUS
        self.touch_pos = None
        self.active = False
        
    def update(self, touch_pos):
        if touch_pos:
            self.active = True
            dx = touch_pos[0] - self.center_x
            dy = touch_pos[1] - self.center_y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > self.outer_radius:
                # Clamp to outer radius
                angle = math.atan2(dy, dx)
                self.touch_pos = (
                    self.center_x + math.cos(angle) * self.outer_radius,
                    self.center_y + math.sin(angle) * self.outer_radius
                )
            else:
                self.touch_pos = touch_pos
        else:
            self.active = False
            self.touch_pos = None
    
    def get_direction(self):
        """Returns normalized direction vector"""
        if not self.active or not self.touch_pos:
            return (0, 0)
        
        dx = self.touch_pos[0] - self.center_x
        dy = self.touch_pos[1] - self.center_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 10:  # Dead zone
            return (0, 0)
        
        return (dx / self.outer_radius, dy / self.outer_radius)
    
    def draw(self, surface):
        # Draw outer circle (semi-transparent)
        s = pygame.Surface((self.outer_radius * 2, self.outer_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (100, 100, 100, 100), (self.outer_radius, self.outer_radius), self.outer_radius)
        surface.blit(s, (self.center_x - self.outer_radius, self.center_y - self.outer_radius))
        
        # Draw inner circle
        if self.active and self.touch_pos:
            pygame.draw.circle(surface, (150, 150, 150, 200), (int(self.touch_pos[0]), int(self.touch_pos[1])), self.inner_radius)
        else:
            pygame.draw.circle(surface, (120, 120, 120, 150), (self.center_x, self.center_y), self.inner_radius)


class Mob:
    """Base mob class"""
    def __init__(self, x, y, width, height, health, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 0.8
        self.on_ground = False
        self.health = health
        self.max_health = health
        self.color = color
        self.direction = 1
        self.move_timer = 0
        self.attack_cooldown = 0
        self.hostile = False
        
    def update(self, world_map, player):
        # AI movement
        self.move_timer += 1
        if self.move_timer > 60:
            self.move_timer = 0
            if self.hostile:
                # Move toward player
                if abs(player.rect.centerx - self.rect.centerx) < BLOCK_SIZE * 10:
                    if player.rect.centerx < self.rect.centerx:
                        self.vel_x = -2
                    else:
                        self.vel_x = 2
                else:
                    self.vel_x = random.choice([-1, 0, 1])
            else:
                self.vel_x = random.choice([-1, 0, 1])
        
        # Gravity
        self.vel_y += self.gravity
        if self.vel_y > 15:
            self.vel_y = 15
        
        # Apply movement
        self.rect.x += self.vel_x
        self.check_collision_x(world_map)
        
        self.rect.y += self.vel_y
        self.check_collision_y(world_map)
        
        # Attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    
    def check_collision_x(self, world_map):
        col1 = int(self.rect.left // BLOCK_SIZE)
        col2 = int(self.rect.right // BLOCK_SIZE)
        row1 = int(self.rect.top // BLOCK_SIZE)
        row2 = int(self.rect.bottom // BLOCK_SIZE)
        
        for row in range(row1, row2 + 1):
            for col in [col1, col2]:
                if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                    if world_map[row][col] not in [AIR_ID, WATER_ID]:
                        block_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                        if self.rect.colliderect(block_rect):
                            if self.vel_x > 0:
                                self.rect.right = block_rect.left
                            elif self.vel_x < 0:
                                self.rect.left = block_rect.right
                            self.vel_x = 0
    
    def check_collision_y(self, world_map):
        col1 = int(self.rect.left // BLOCK_SIZE)
        col2 = int(self.rect.right // BLOCK_SIZE)
        row1 = int(self.rect.top // BLOCK_SIZE)
        row2 = int(self.rect.bottom // BLOCK_SIZE)
        
        self.on_ground = False
        
        for row in [row1, row2]:
            for col in range(col1, col2 + 1):
                if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                    if world_map[row][col] not in [AIR_ID, WATER_ID]:
                        block_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                        if self.rect.colliderect(block_rect):
                            if self.vel_y > 0:
                                self.rect.bottom = block_rect.top
                                self.on_ground = True
                            elif self.vel_y < 0:
                                self.rect.top = block_rect.bottom
                            self.vel_y = 0
    
    def draw(self, surface, camera_x, camera_y):
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        pygame.draw.rect(surface, self.color, (screen_x, screen_y, self.rect.width, self.rect.height))
        
        # Health bar
        if self.health < self.max_health:
            bar_width = self.rect.width
            bar_height = 4
            health_ratio = self.health / self.max_health
            pygame.draw.rect(surface, (50, 50, 50), (screen_x, screen_y - 8, bar_width, bar_height))
            pygame.draw.rect(surface, (255, 0, 0), (screen_x, screen_y - 8, bar_width * health_ratio, bar_height))
    
    def attack(self, player, damage):
        if self.attack_cooldown == 0 and self.rect.colliderect(player.rect):
            player.take_damage(damage)
            self.attack_cooldown = 30


class Zombie(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 2, 20, (0, 100, 0))
        self.hostile = True


class Skeleton(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 2, 20, (220, 220, 220))
        self.hostile = True


class Creeper(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 2, 20, (0, 150, 0))
        self.hostile = True
        self.explode_timer = 0
    
    def update(self, world_map, player):
        super().update(world_map, player)
        # Explode near player
        if abs(player.rect.centerx - self.rect.centerx) < BLOCK_SIZE * 2:
            self.explode_timer += 1
            if self.explode_timer > 60:
                player.take_damage(10)
                self.health = 0


class Pig(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, 10, (255, 150, 150))
        self.hostile = False


class Cow(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, 10, (100, 70, 50))
        self.hostile = False


class Sheep(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE, 8, (240, 240, 240))
        self.hostile = False


class Spider(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 1.5, BLOCK_SIZE, 16, (50, 50, 50))
        self.hostile = True


class Enderman(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 3, 40, (20, 20, 20))
        self.hostile = True
        self.teleport_timer = 0
    
    def update(self, world_map, player):
        super().update(world_map, player)
        # Teleport randomly
        self.teleport_timer += 1
        if self.teleport_timer > 120 and random.random() < 0.1:
            self.rect.x += random.randint(-5, 5) * BLOCK_SIZE
            self.rect.y += random.randint(-3, 3) * BLOCK_SIZE
            self.teleport_timer = 0


class Witch(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE, BLOCK_SIZE * 2, 26, (100, 50, 150))
        self.hostile = True


class IronGolem(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLOCK_SIZE * 1.5, BLOCK_SIZE * 3, 100, (200, 200, 200))
        self.hostile = False  # Protects player
        self.attack_range = BLOCK_SIZE * 3
    
    def update(self, world_map, player):
        super().update(world_map, player)
        # Attack nearby hostile mobs (not implemented fully for performance)


class Particle:
    """Visual particle effect"""
    def __init__(self, x, y, color, vel_x, vel_y, lifetime=30):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.3  # Gravity
        self.lifetime -= 1
    
    def draw(self, surface, camera_x, camera_y):
        if self.lifetime > 0:
            alpha = int((self.lifetime / self.max_lifetime) * 255)
            size = max(2, int((self.lifetime / self.max_lifetime) * 6))
            screen_x = int(self.x - camera_x)
            screen_y = int(self.y - camera_y)
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((*self.color, alpha))
            surface.blit(s, (screen_x, screen_y))


class DroppedItem:
    """Dropped item entity"""
    def __init__(self, x, y, item_id, count):
        self.rect = pygame.Rect(x, y, BLOCK_SIZE // 2, BLOCK_SIZE // 2)
        self.item_id = item_id
        self.count = count
        self.vel_y = 0
        self.gravity = 0.5
        self.lifetime = 0
        self.bob_offset = 0
        self.bob_speed = 0.1
        
    def update(self, world_map):
        self.lifetime += 1
        
        # Bobbing animation
        self.bob_offset += self.bob_speed
        
        # Gravity
        self.vel_y += self.gravity
        if self.vel_y > 10:
            self.vel_y = 10
        
        self.rect.y += self.vel_y
        
        # Collision with ground
        col = int(self.rect.centerx // BLOCK_SIZE)
        row = int(self.rect.bottom // BLOCK_SIZE)
        
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            if world_map[row][col] not in [AIR_ID, WATER_ID]:
                block_top = row * BLOCK_SIZE
                self.rect.bottom = block_top
                self.vel_y = 0
    
    def draw(self, surface, camera_x, camera_y):
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y + math.sin(self.bob_offset) * 3  # Bobbing
        
        if self.item_id in BLOCK_COLORS:
            color = BLOCK_COLORS[self.item_id]
            if color:
                # Draw with glow effect
                if isinstance(color, tuple) and len(color) >= 3:
                    glow_size = self.rect.width + 4
                    glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                    glow_color = (*color[:3], 50)
                    pygame.draw.rect(glow_surf, glow_color, (0, 0, glow_size, glow_size))
                    surface.blit(glow_surf, (screen_x - 2, screen_y - 2))
                pygame.draw.rect(surface, color[:3] if isinstance(color, tuple) and len(color) > 3 else color, 
                               (screen_x, screen_y, self.rect.width, self.rect.height))


class Player:
    """Enhanced player for mobile"""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE * 2)
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 4
        self.jump_power = 12
        self.gravity = 0.8
        self.on_ground = False
        self.health = 20
        self.max_health = 20
        self.hunger = 20
        self.max_hunger = 20
        self.oxygen = 10
        self.max_oxygen = 10
        
        # Inventory
        self.hotbar = [(0, 0) for _ in range(9)]
        self.inventory = [(0, 0) for _ in range(27)]
        self.selected_slot = 0
        self.inventory_open = False
        
        # Modes
        self.creative_mode = False
        self.survival_mode = True
        
        # Mining
        self.mining_progress = 0
        self.mining_target = None
        self.mining_speed = 1.0
        
        # Combat
        self.attack_cooldown = 0
        self.damage_cooldown = 0
        
        # Experience
        self.xp = 0
        self.level = 0
        
        # Effects
        self.regeneration = 0
        self.speed_boost = 0
        self.is_underwater = False
        
    def take_damage(self, amount):
        if self.damage_cooldown == 0 and not self.creative_mode:
            self.health -= amount
            self.damage_cooldown = 30
            if self.health < 0:
                self.health = 0
        
    def update(self, world_map, joystick_dir):
        # Movement from joystick
        self.vel_x = joystick_dir[0] * self.speed
        
        # Gravity
        self.vel_y += self.gravity
        if self.vel_y > 15:
            self.vel_y = 15
        
        # Apply horizontal velocity
        self.rect.x += self.vel_x
        self.check_collision_x(world_map)
        
        # Apply vertical velocity
        self.rect.y += self.vel_y
        self.check_collision_y(world_map)
        
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        
        # Hunger depletion in survival
        if self.survival_mode:
            if random.random() < 0.001:  # Slowly lose hunger
                self.hunger = max(0, self.hunger - 1)
            if self.hunger == 0:
                self.take_damage(1)  # Starve
        
        # Regeneration when fed
        if self.hunger >= 18 and self.health < self.max_health:
            if random.random() < 0.01:
                self.health = min(self.max_health, self.health + 1)
        
        # Status effects
        if self.regeneration > 0:
            self.regeneration -= 1
            if random.random() < 0.1:
                self.health = min(self.max_health, self.health + 1)
        
        if self.speed_boost > 0:
            self.speed_boost -= 1
            self.speed = 6
        else:
            self.speed = 4
    
    def mine_block(self, world_map, target_row, target_col):
        """Progressive mining system"""
        block_id = world_map[target_row][target_col]
        
        if block_id == AIR_ID or block_id == BEDROCK_ID:
            return False
        
        # Get block properties
        block_data = BLOCK_TYPES.get(block_id, {"hardness": 1.0, "drops": block_id})
        hardness = block_data.get("hardness", 1.0)
        
        # Get tool bonus
        held_item_id, _ = self.get_held_item()
        tool_speed = 1.0
        
        if held_item_id in TOOL_PROPERTIES:
            tool_data = TOOL_PROPERTIES[held_item_id]
            tool_speed = tool_data["speed"]
        
        # Check if same target
        if self.mining_target != (target_row, target_col):
            self.mining_progress = 0
            self.mining_target = (target_row, target_col)
        
        # Add mining progress
        self.mining_progress += tool_speed
        
        # Check if block is broken
        if self.mining_progress >= hardness * 10:
            world_map[target_row][target_col] = AIR_ID
            drops = block_data.get("drops", block_id)
            if drops != 0:
                self.add_to_inventory(drops, 1)
            self.mining_progress = 0
            self.mining_target = None
            return True
        
        return False
    
    def check_collision_x(self, world_map):
        col1 = int(self.rect.left // BLOCK_SIZE)
        col2 = int(self.rect.right // BLOCK_SIZE)
        row1 = int(self.rect.top // BLOCK_SIZE)
        row2 = int(self.rect.bottom // BLOCK_SIZE)
        
        for row in range(row1, row2 + 1):
            for col in [col1, col2]:
                if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                    if world_map[row][col] != AIR_ID and world_map[row][col] != WATER_ID:
                        block_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                        if self.rect.colliderect(block_rect):
                            if self.vel_x > 0:
                                self.rect.right = block_rect.left
                            elif self.vel_x < 0:
                                self.rect.left = block_rect.right
                            self.vel_x = 0
    
    def check_collision_y(self, world_map):
        col1 = int(self.rect.left // BLOCK_SIZE)
        col2 = int(self.rect.right // BLOCK_SIZE)
        row1 = int(self.rect.top // BLOCK_SIZE)
        row2 = int(self.rect.bottom // BLOCK_SIZE)
        
        self.on_ground = False
        
        for row in [row1, row2]:
            for col in range(col1, col2 + 1):
                if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                    if world_map[row][col] != AIR_ID and world_map[row][col] != WATER_ID:
                        block_rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                        if self.rect.colliderect(block_rect):
                            if self.vel_y > 0:
                                self.rect.bottom = block_rect.top
                                self.on_ground = True
                            elif self.vel_y < 0:
                                self.rect.top = block_rect.bottom
                            self.vel_y = 0
    
    def jump(self):
        if self.on_ground:
            self.vel_y = -self.jump_power
    
    def add_to_inventory(self, item_id, count=1):
        if item_id == 0:
            return
            
        # Try hotbar first
        for i in range(9):
            slot_id, slot_count = self.hotbar[i]
            if slot_id == item_id and slot_count < 64:
                self.hotbar[i] = (item_id, min(64, slot_count + count))
                return
        
        # Try inventory
        for i in range(27):
            slot_id, slot_count = self.inventory[i]
            if slot_id == item_id and slot_count < 64:
                self.inventory[i] = (item_id, min(64, slot_count + count))
                return
        
        # Find empty slot in hotbar
        for i in range(9):
            if self.hotbar[i][0] == 0:
                self.hotbar[i] = (item_id, count)
                return
        
        # Find empty slot in inventory
        for i in range(27):
            if self.inventory[i][0] == 0:
                self.inventory[i] = (item_id, count)
                return
    
    def remove_from_inventory(self, item_id, count=1):
        """Remove items from inventory"""
        remaining = count
        
        # Check hotbar
        for i in range(9):
            if remaining <= 0:
                break
            slot_id, slot_count = self.hotbar[i]
            if slot_id == item_id:
                if slot_count >= remaining:
                    self.hotbar[i] = (item_id, slot_count - remaining)
                    if slot_count - remaining == 0:
                        self.hotbar[i] = (0, 0)
                    remaining = 0
                else:
                    remaining -= slot_count
                    self.hotbar[i] = (0, 0)
        
        # Check inventory
        for i in range(27):
            if remaining <= 0:
                break
            slot_id, slot_count = self.inventory[i]
            if slot_id == item_id:
                if slot_count >= remaining:
                    self.inventory[i] = (item_id, slot_count - remaining)
                    if slot_count - remaining == 0:
                        self.inventory[i] = (0, 0)
                    remaining = 0
                else:
                    remaining -= slot_count
                    self.inventory[i] = (0, 0)
        
        return remaining == 0
    
    def count_items(self, item_id):
        """Count total of an item in inventory"""
        total = 0
        for slot_id, count in self.hotbar:
            if slot_id == item_id:
                total += count
        for slot_id, count in self.inventory:
            if slot_id == item_id:
                total += count
        return total
    
    def eat_food(self, item_id):
        """Eat food item"""
        if item_id in FOOD_ITEMS:
            hunger_restore = FOOD_ITEMS[item_id]
            self.hunger = min(self.max_hunger, self.hunger + hunger_restore)
            self.remove_from_inventory(item_id, 1)
            return True
        return False
    
    def attack_mob(self, mobs):
        """Attack nearby mob"""
        if self.attack_cooldown > 0:
            return
        
        # Get weapon damage
        held_item_id, _ = self.get_held_item()
        damage = 1
        
        if held_item_id in TOOL_PROPERTIES:
            tool_data = TOOL_PROPERTIES[held_item_id]
            if tool_data["type"] == "sword":
                damage = tool_data["damage"]
        
        # Check for mob collision
        attack_range = BLOCK_SIZE * 1.5
        attack_rect = pygame.Rect(
            self.rect.centerx - attack_range,
            self.rect.centery - attack_range,
            attack_range * 2,
            attack_range * 2
        )
        
        for mob in mobs:
            if attack_rect.colliderect(mob.rect):
                mob.health -= damage
                self.attack_cooldown = 10
                
                # Drop loot if killed
                if mob.health <= 0:
                    if isinstance(mob, (Pig, Cow, Sheep)):
                        # Drop raw beef
                        return DroppedItem(mob.rect.centerx, mob.rect.centery, RAW_BEEF, 1)
        
        return None
    
    def get_held_item(self):
        return self.hotbar[self.selected_slot]
    
    def draw(self, surface, camera_x, camera_y):
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        
        # Draw simple player sprite (blue square with face)
        pygame.draw.rect(surface, (50, 150, 255), (screen_x, screen_y, self.rect.width, self.rect.height))
        
        # Draw eyes
        eye_size = 6
        eye_offset = 8
        pygame.draw.circle(surface, (255, 255, 255), (int(screen_x + self.rect.width//2 - eye_offset), int(screen_y + self.rect.height//4)), eye_size)
        pygame.draw.circle(surface, (255, 255, 255), (int(screen_x + self.rect.width//2 + eye_offset), int(screen_y + self.rect.height//4)), eye_size)
        pygame.draw.circle(surface, (0, 0, 0), (int(screen_x + self.rect.width//2 - eye_offset), int(screen_y + self.rect.height//4)), 3)
        pygame.draw.circle(surface, (0, 0, 0), (int(screen_x + self.rect.width//2 + eye_offset), int(screen_y + self.rect.height//4)), 3)


def generate_simple_world():
    """Generate enhanced world with biomes, ores, and caves"""
    world = [[AIR_ID for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    biomes = []
    
    # Bedrock layer
    for col in range(GRID_WIDTH):
        world[GRID_HEIGHT - 1][col] = BEDROCK_ID
    
    # Generate biomes
    for col in range(GRID_WIDTH):
        if col % 50 < 20:
            biomes.append(DESERT_BIOME)
        elif col % 50 < 30:
            biomes.append(SNOW_BIOME)
        elif col % 50 < 40:
            biomes.append(JUNGLE_BIOME)
        else:
            biomes.append(PLAINS_BIOME)
    
    # Terrain generation with biomes
    for col in range(GRID_WIDTH):
        biome = biomes[col]
        
        # Varying terrain height
        height = int(GRID_HEIGHT * 0.55 + math.sin(col * 0.03) * 12 + math.cos(col * 0.07) * 8)
        
        # Biome-specific terrain
        for row in range(height, GRID_HEIGHT - 1):
            if row == height:
                if biome == DESERT_BIOME:
                    world[row][col] = SAND_ID
                elif biome == SNOW_BIOME:
                    world[row][col] = SNOW_ID
                else:
                    world[row][col] = GRASS_ID
            elif row < height + 3:
                if biome == DESERT_BIOME:
                    world[row][col] = SAND_ID
                else:
                    world[row][col] = DIRT_ID
            elif row < height + 10:
                world[row][col] = STONE_ID
            else:
                world[row][col] = STONE_ID
        
        # Trees based on biome
        if biome == PLAINS_BIOME and random.random() < 0.06 and col > 5 and col < GRID_WIDTH - 5:
            tree_height = random.randint(4, 6)
            for i in range(tree_height):
                if height - i - 1 >= 0:
                    world[height - i - 1][col] = WOOD_ID
            
            leaf_row = height - tree_height - 1
            if leaf_row >= 0:
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        leaf_r = leaf_row + dr
                        leaf_c = col + dc
                        if 0 <= leaf_r < GRID_HEIGHT and 0 <= leaf_c < GRID_WIDTH:
                            if abs(dr) + abs(dc) <= 3 and world[leaf_r][leaf_c] == AIR_ID:
                                world[leaf_r][leaf_c] = LEAVES_ID
        
        elif biome == JUNGLE_BIOME and random.random() < 0.08:
            # Taller jungle trees
            tree_height = random.randint(6, 9)
            for i in range(tree_height):
                if height - i - 1 >= 0:
                    world[height - i - 1][col] = WOOD_ID
            
            # Add bamboo
            if random.random() < 0.5 and col + 1 < GRID_WIDTH:
                for i in range(random.randint(3, 5)):
                    if height - i - 1 >= 0:
                        world[height - i - 1][col + 1] = BAMBOO_ID
        
        elif biome == DESERT_BIOME and random.random() < 0.02:
            # Cactus
            for i in range(random.randint(2, 4)):
                if height - i - 1 >= 0:
                    world[height - i - 1][col] = CACTUS_ID
    
    # Generate ores underground with realistic distribution
    for _ in range(GRID_WIDTH * 3):  # Coal (common, higher up)
        ore_col = random.randint(0, GRID_WIDTH - 1)
        ore_row = random.randint(int(GRID_HEIGHT * 0.5), GRID_HEIGHT - 10)
        if world[ore_row][ore_col] == STONE_ID:
            # Create vein
            vein_size = random.randint(3, 6)
            for _ in range(vein_size):
                dr = random.randint(-2, 2)
                dc = random.randint(-2, 2)
                r, c = ore_row + dr, ore_col + dc
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    if world[r][c] == STONE_ID:
                        world[r][c] = COAL_ORE_ID
    
    for _ in range(GRID_WIDTH * 2):  # Iron (medium depth)
        ore_col = random.randint(0, GRID_WIDTH - 1)
        ore_row = random.randint(int(GRID_HEIGHT * 0.6), GRID_HEIGHT - 10)
        if world[ore_row][ore_col] == STONE_ID:
            vein_size = random.randint(2, 5)
            for _ in range(vein_size):
                dr = random.randint(-1, 1)
                dc = random.randint(-1, 1)
                r, c = ore_row + dr, ore_col + dc
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    if world[r][c] == STONE_ID:
                        world[r][c] = IRON_ORE_ID
    
    for _ in range(GRID_WIDTH):  # Gold (deeper)
        ore_col = random.randint(0, GRID_WIDTH - 1)
        ore_row = random.randint(int(GRID_HEIGHT * 0.7), GRID_HEIGHT - 10)
        if world[ore_row][ore_col] == STONE_ID:
            vein_size = random.randint(2, 4)
            for _ in range(vein_size):
                dr = random.randint(-1, 1)
                dc = random.randint(-1, 1)
                r, c = ore_row + dr, ore_col + dc
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    if world[r][c] == STONE_ID:
                        world[r][c] = GOLD_ORE_ID
    
    for _ in range(GRID_WIDTH // 2):  # Redstone (deep)
        ore_col = random.randint(0, GRID_WIDTH - 1)
        ore_row = random.randint(int(GRID_HEIGHT * 0.75), GRID_HEIGHT - 8)
        if world[ore_row][ore_col] == STONE_ID:
            vein_size = random.randint(3, 6)
            for _ in range(vein_size):
                dr = random.randint(-1, 1)
                dc = random.randint(-1, 1)
                r, c = ore_row + dr, ore_col + dc
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    if world[r][c] == STONE_ID:
                        world[r][c] = REDSTONE_ORE_ID
    
    for _ in range(GRID_WIDTH // 3):  # Lapis (medium-deep)
        ore_col = random.randint(0, GRID_WIDTH - 1)
        ore_row = random.randint(int(GRID_HEIGHT * 0.65), GRID_HEIGHT - 12)
        if world[ore_row][ore_col] == STONE_ID:
            vein_size = random.randint(2, 5)
            for _ in range(vein_size):
                dr = random.randint(-1, 1)
                dc = random.randint(-1, 1)
                r, c = ore_row + dr, ore_col + dc
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    if world[r][c] == STONE_ID:
                        world[r][c] = LAPIS_ORE_ID
    
    for _ in range(GRID_WIDTH // 4):  # Diamond (very deep, rare)
        ore_col = random.randint(0, GRID_WIDTH - 1)
        ore_row = random.randint(int(GRID_HEIGHT * 0.85), GRID_HEIGHT - 5)
        if world[ore_row][ore_col] == STONE_ID:
            vein_size = random.randint(1, 3)
            for _ in range(vein_size):
                dr = random.randint(-1, 1)
                dc = random.randint(-1, 1)
                r, c = ore_row + dr, ore_col + dc
                if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                    if world[r][c] == STONE_ID:
                        world[r][c] = DIAMOND_ORE_ID
    
    for _ in range(GRID_WIDTH // 6):  # Emerald (rare)
        ore_col = random.randint(0, GRID_WIDTH - 1)
        ore_row = random.randint(int(GRID_HEIGHT * 0.7), GRID_HEIGHT - 10)
        if world[ore_row][ore_col] == STONE_ID:
            world[ore_row][ore_col] = EMERALD_ORE_ID
    
    # Generate caves
    for _ in range(GRID_WIDTH // 3):
        cave_x = random.randint(10, GRID_WIDTH - 10)
        cave_y = random.randint(int(GRID_HEIGHT * 0.5), GRID_HEIGHT - 20)
        cave_length = random.randint(20, 40)
        
        for i in range(cave_length):
            cave_x += random.randint(-2, 2)
            cave_y += random.randint(-1, 1)
            
            if 0 <= cave_x < GRID_WIDTH and 0 <= cave_y < GRID_HEIGHT:
                radius = random.randint(2, 4)
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        if dr*dr + dc*dc <= radius*radius:
                            r, c = cave_y + dr, cave_x + dc
                            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                                if world[r][c] != BEDROCK_ID:
                                    world[r][c] = AIR_ID
    
    # Add some water lakes
    for _ in range(5):
        lake_col = random.randint(10, GRID_WIDTH - 10)
        for row in range(GRID_HEIGHT):
            if world[row][lake_col] in [GRASS_ID, DIRT_ID]:
                # Create lake
                lake_width = random.randint(3, 8)
                lake_depth = random.randint(2, 4)
                for dr in range(lake_depth):
                    for dc in range(-lake_width, lake_width + 1):
                        r, c = row + dr, lake_col + dc
                        if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                            if world[r][c] in [GRASS_ID, DIRT_ID, STONE_ID]:
                                world[r][c] = WATER_ID
                            # Sand around water
                            if dr == 0 and abs(dc) == lake_width:
                                world[r][c] = SAND_ID
                break
    
    # Add lava pools deep underground
    for _ in range(3):
        lava_col = random.randint(10, GRID_WIDTH - 10)
        lava_row = random.randint(int(GRID_HEIGHT * 0.85), GRID_HEIGHT - 5)
        if world[lava_row][lava_col] == AIR_ID:
            for dc in range(-2, 3):
                c = lava_col + dc
                if 0 <= c < GRID_WIDTH:
                    world[lava_row][c] = LAVA_ID
    
    return world, biomes


def calculate_camera(player_rect):
    """Calculate camera position centered on player"""
    camera_x = player_rect.centerx - SCREEN_WIDTH // 2
    camera_y = player_rect.centery - SCREEN_HEIGHT // 2
    
    # Clamp camera to world bounds
    camera_x = max(0, min(camera_x, GRID_WIDTH * BLOCK_SIZE - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, GRID_HEIGHT * BLOCK_SIZE - SCREEN_HEIGHT))
    
    return camera_x, camera_y


def calculate_lighting(world_map, player_pos, time_phase):
    """Calculate lighting for darkness in caves and night"""
    light_level = 1.0  # Full brightness
    
    if time_phase == NIGHT_PHASE:
        light_level = 0.3  # Dark at night
    elif time_phase == EVENING_PHASE:
        light_level = 0.6
    elif time_phase == MORNING_PHASE:
        light_level = 0.8
    
    # Check if player is underground (cave darkness)
    player_col = int(player_pos[0] // BLOCK_SIZE)
    player_row = int(player_pos[1] // BLOCK_SIZE)
    
    if 0 <= player_col < GRID_WIDTH and 0 <= player_row < GRID_HEIGHT:
        # Check if there's sky above
        has_sky = False
        for check_row in range(player_row):
            if world_map[check_row][player_col] == AIR_ID:
                has_sky = True
                break
        
        if not has_sky:
            light_level *= 0.2  # Very dark underground
    
    return light_level


def draw_world(surface, world_map, camera_x, camera_y, light_level=1.0):
    """Draw visible world blocks with lighting"""
    # Calculate visible range
    start_col = max(0, int(camera_x // BLOCK_SIZE) - 1)
    end_col = min(GRID_WIDTH, int((camera_x + SCREEN_WIDTH) // BLOCK_SIZE) + 2)
    start_row = max(0, int(camera_y // BLOCK_SIZE) - 1)
    end_row = min(GRID_HEIGHT, int((camera_y + SCREEN_HEIGHT) // BLOCK_SIZE) + 2)
    
    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            block_id = world_map[row][col]
            if block_id != AIR_ID and block_id in BLOCK_COLORS:
                color = BLOCK_COLORS[block_id]
                if color:
                    x = col * BLOCK_SIZE - camera_x
                    y = row * BLOCK_SIZE - camera_y
                    
                    # Apply lighting (except for light-emitting blocks)
                    if block_id in [TORCH_ID, GLOWSTONE_ID, LAVA_ID, FIRE_ID]:
                        # Light sources glow
                        lit_color = color
                    else:
                        # Apply darkness
                        if isinstance(color, tuple) and len(color) >= 3:
                            lit_color = tuple(int(c * light_level) for c in color[:3])
                            if len(color) == 4:  # Has alpha
                                lit_color = (*lit_color, color[3])
                        else:
                            lit_color = color
                    
                    # Handle transparency for water
                    if block_id == WATER_ID:
                        s = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                        s.fill(lit_color)
                        surface.blit(s, (x, y))
                    else:
                        pygame.draw.rect(surface, lit_color, (x, y, BLOCK_SIZE, BLOCK_SIZE))
                    
                    # Draw grid (subtle)
                    grid_color = tuple(int(c * 0.7) for c in lit_color[:3]) if isinstance(lit_color, tuple) else (0, 0, 0)
                    pygame.draw.rect(surface, grid_color, (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)


def get_sky_color(time_of_day, time_phase):
    """Get sky color based on time"""
    if time_phase == DAY_PHASE:
        return (135, 206, 235)  # Sky blue
    elif time_phase == EVENING_PHASE:
        return (255, 140, 80)  # Orange/red
    elif time_phase == NIGHT_PHASE:
        return (25, 25, 50)  # Dark blue
    elif time_phase == MORNING_PHASE:
        return (150, 180, 220)  # Light blue
    return (135, 206, 235)


def update_time(time_of_day):
    """Update time of day"""
    time_of_day += 1
    if time_of_day >= TOTAL_CYCLE_LENGTH:
        time_of_day = 0
    
    # Determine phase
    if time_of_day < DAY_LENGTH:
        phase = DAY_PHASE
    elif time_of_day < DAY_LENGTH + EVENING_LENGTH:
        phase = EVENING_PHASE
    elif time_of_day < DAY_LENGTH + EVENING_LENGTH + NIGHT_LENGTH:
        phase = NIGHT_PHASE
    else:
        phase = MORNING_PHASE
    
    return time_of_day, phase


class Weather:
    """Weather system with rain and snow"""
    def __init__(self):
        self.is_raining = False
        self.is_snowing = False
        self.weather_timer = 0
        self.weather_duration = 0
        self.rain_particles = []
        self.snow_particles = []
    
    def update(self, biome_type):
        self.weather_timer += 1
        
        # Random weather changes
        if self.weather_timer >= self.weather_duration:
            if random.random() < 0.05:  # 5% chance to start weather
                if biome_type == SNOW_BIOME:
                    self.is_snowing = True
                    self.is_raining = False
                elif biome_type in [PLAINS_BIOME, JUNGLE_BIOME]:
                    self.is_raining = True
                    self.is_snowing = False
                else:
                    self.is_raining = False
                    self.is_snowing = False
                
                self.weather_duration = random.randint(200, 600)
                self.weather_timer = 0
            else:
                self.is_raining = False
                self.is_snowing = False
                self.weather_duration = random.randint(400, 1000)
                self.weather_timer = 0
        
        # Update particles
        if self.is_raining:
            if len(self.rain_particles) < 100:
                for _ in range(5):
                    self.rain_particles.append({
                        'x': random.randint(0, SCREEN_WIDTH),
                        'y': -10,
                        'speed': random.randint(10, 15)
                    })
            
            for particle in self.rain_particles:
                particle['y'] += particle['speed']
            
            self.rain_particles = [p for p in self.rain_particles if p['y'] < SCREEN_HEIGHT]
        
        if self.is_snowing:
            if len(self.snow_particles) < 80:
                for _ in range(3):
                    self.snow_particles.append({
                        'x': random.randint(0, SCREEN_WIDTH),
                        'y': -10,
                        'speed': random.randint(2, 4),
                        'sway': random.uniform(-1, 1)
                    })
            
            for particle in self.snow_particles:
                particle['y'] += particle['speed']
                particle['x'] += particle['sway']
            
            self.snow_particles = [p for p in self.snow_particles if p['y'] < SCREEN_HEIGHT]
    
    def draw(self, surface):
        if self.is_raining:
            for particle in self.rain_particles:
                pygame.draw.line(surface, (150, 180, 255), 
                               (particle['x'], particle['y']),
                               (particle['x'], particle['y'] + 10), 2)
        
        if self.is_snowing:
            for particle in self.snow_particles:
                pygame.draw.circle(surface, (255, 255, 255), 
                                 (int(particle['x']), int(particle['y'])), 3)


def spawn_mobs_near_player(player, world_map, mobs, biomes):
    """Spawn mobs near player"""
    if len(mobs) > 50:  # Mob cap for performance
        return
    
    # Spawn location 20-30 blocks away from player
    distance = random.randint(20, 30) * BLOCK_SIZE
    angle = random.random() * 2 * math.pi
    spawn_x = int(player.rect.centerx + math.cos(angle) * distance)
    spawn_y = int(player.rect.centery + math.sin(angle) * distance)
    
    # Find ground
    spawn_col = spawn_x // BLOCK_SIZE
    if 0 <= spawn_col < GRID_WIDTH:
        for row in range(GRID_HEIGHT):
            if world_map[row][spawn_col] not in [AIR_ID, WATER_ID]:
                spawn_y = (row - 2) * BLOCK_SIZE
                break
        
        # Spawn mob based on biome and time
        biome = biomes[spawn_col] if spawn_col < len(biomes) else PLAINS_BIOME
        
        r = random.random()
        if r < 0.25:
            mobs.append(Zombie(spawn_x, spawn_y))
        elif r < 0.45:
            mobs.append(Skeleton(spawn_x, spawn_y))
        elif r < 0.6:
            mobs.append(Creeper(spawn_x, spawn_y))
        elif r < 0.7:
            mobs.append(Spider(spawn_x, spawn_y))
        elif r < 0.75:
            mobs.append(Enderman(spawn_x, spawn_y))
        elif r < 0.8:
            mobs.append(Witch(spawn_x, spawn_y))
        elif r < 0.85:
            mobs.append(Pig(spawn_x, spawn_y))
        elif r < 0.92:
            mobs.append(Cow(spawn_x, spawn_y))
        elif r < 0.97:
            mobs.append(Sheep(spawn_x, spawn_y))
        else:
            mobs.append(IronGolem(spawn_x, spawn_y))


def draw_crafting_menu(surface, player, recipes):
    """Draw simple crafting menu"""
    menu_width = SCREEN_WIDTH * 0.85
    menu_height = SCREEN_HEIGHT * 0.7
    menu_x = (SCREEN_WIDTH - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    
    # Background
    s = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
    pygame.draw.rect(s, UI_BACKGROUND, (0, 0, menu_width, menu_height), border_radius=15)
    surface.blit(s, (menu_x, menu_y))
    
    # Title
    title = FONT_LARGE.render("Crafting", True, (255, 255, 255))
    surface.blit(title, (menu_x + 20, menu_y + 20))
    
    # List available recipes
    y_offset = 80
    recipe_buttons = []
    
    for recipe_name, recipe_data in list(recipes.items())[:10]:  # Show first 10 recipes
        # Check if player has materials
        can_craft = True
        for item_id, count in recipe_data["input"]:
            if player.count_items(item_id) < count:
                can_craft = False
                break
        
        # Draw recipe button
        button_color = (50, 150, 50) if can_craft else (100, 50, 50)
        button_rect = pygame.Rect(menu_x + 20, menu_y + y_offset, menu_width - 40, 50)
        pygame.draw.rect(surface, button_color, button_rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 200), button_rect, 2, border_radius=8)
        
        # Recipe text
        output_id, output_count = recipe_data["output"]
        output_name = BLOCK_NAMES.get(output_id, f"Item {output_id}")
        recipe_text = FONT_SMALL.render(f"{output_name} x{output_count}", True, (255, 255, 255))
        surface.blit(recipe_text, (button_rect.x + 10, button_rect.y + 15))
        
        recipe_buttons.append((recipe_name, button_rect, can_craft))
        y_offset += 60
    
    return recipe_buttons


def craft_item(player, recipe_name, recipes):
    """Craft an item"""
    if recipe_name not in recipes:
        return False
    
    recipe = recipes[recipe_name]
    
    # Check materials
    for item_id, count in recipe["input"]:
        if player.count_items(item_id) < count:
            return False
    
    # Remove materials
    for item_id, count in recipe["input"]:
        player.remove_from_inventory(item_id, count)
    
    # Add result
    output_id, output_count = recipe["output"]
    player.add_to_inventory(output_id, output_count)
    
    return True


def draw_hotbar(surface, player):
    """Draw mobile-friendly hotbar"""
    hotbar_width = SCREEN_WIDTH * 0.8
    hotbar_height = 70
    hotbar_x = (SCREEN_WIDTH - hotbar_width) // 2
    hotbar_y = SCREEN_HEIGHT - hotbar_height - 10
    
    slot_size = hotbar_width // 9
    
    for i in range(9):
        slot_x = hotbar_x + i * slot_size
        
        # Draw slot background
        color = (100, 100, 100) if i == player.selected_slot else (60, 60, 60)
        pygame.draw.rect(surface, color, (slot_x, hotbar_y, slot_size, hotbar_height))
        pygame.draw.rect(surface, (200, 200, 200), (slot_x, hotbar_y, slot_size, hotbar_height), 2)
        
        # Draw item
        item_id, count = player.hotbar[i]
        if item_id != AIR_ID and item_id in BLOCK_COLORS:
            color = BLOCK_COLORS[item_id]
            if color:
                item_size = slot_size - 20
                item_x = slot_x + 10
                item_y = hotbar_y + 10
                
                # Handle transparency
                if isinstance(color, tuple) and len(color) == 4:
                    s = pygame.Surface((item_size, item_size), pygame.SRCALPHA)
                    s.fill(color)
                    surface.blit(s, (item_x, item_y))
                else:
                    pygame.draw.rect(surface, color, (item_x, item_y, item_size, item_size))
                
                # Draw count
                if count > 1:
                    count_text = FONT_SMALL.render(str(count), True, (255, 255, 255))
                    surface.blit(count_text, (item_x + item_size - 20, item_y + item_size - 20))


def draw_inventory(surface, player):
    """Draw mobile-friendly inventory"""
    inv_width = SCREEN_WIDTH * 0.9
    inv_height = SCREEN_HEIGHT * 0.8
    inv_x = (SCREEN_WIDTH - inv_width) // 2
    inv_y = (SCREEN_HEIGHT - inv_height) // 2
    
    # Background
    s = pygame.Surface((inv_width, inv_height), pygame.SRCALPHA)
    pygame.draw.rect(s, UI_BACKGROUND, (0, 0, inv_width, inv_height), border_radius=15)
    surface.blit(s, (inv_x, inv_y))
    
    # Title
    title = FONT_LARGE.render("Inventory", True, (255, 255, 255))
    surface.blit(title, (inv_x + 20, inv_y + 20))
    
    # Draw inventory grid (3x9)
    slot_size = 60
    grid_start_x = inv_x + 20
    grid_start_y = inv_y + 80
    
    for i in range(27):
        row = i // 9
        col = i % 9
        slot_x = grid_start_x + col * (slot_size + 5)
        slot_y = grid_start_y + row * (slot_size + 5)
        
        # Draw slot
        pygame.draw.rect(surface, (40, 40, 40), (slot_x, slot_y, slot_size, slot_size))
        pygame.draw.rect(surface, (100, 100, 100), (slot_x, slot_y, slot_size, slot_size), 2)
        
        # Draw item
        item_id, count = player.inventory[i]
        if item_id != AIR_ID and item_id in BLOCK_COLORS:
            color = BLOCK_COLORS[item_id]
            if color:
                pygame.draw.rect(surface, color, (slot_x + 10, slot_y + 10, slot_size - 20, slot_size - 20))
                if count > 1:
                    count_text = FONT_SMALL.render(str(count), True, (255, 255, 255))
                    surface.blit(count_text, (slot_x + slot_size - 25, slot_y + slot_size - 25))
    
    # Draw hotbar
    hotbar_start_y = grid_start_y + 3 * (slot_size + 5) + 20
    for i in range(9):
        slot_x = grid_start_x + i * (slot_size + 5)
        slot_y = hotbar_start_y
        
        color = (60, 100, 60) if i == player.selected_slot else (40, 40, 40)
        pygame.draw.rect(surface, color, (slot_x, slot_y, slot_size, slot_size))
        pygame.draw.rect(surface, (100, 100, 100), (slot_x, slot_y, slot_size, slot_size), 2)
        
        item_id, count = player.hotbar[i]
        if item_id != AIR_ID and item_id in BLOCK_COLORS:
            color = BLOCK_COLORS[item_id]
            if color:
                pygame.draw.rect(surface, color, (slot_x + 10, slot_y + 10, slot_size - 20, slot_size - 20))
                if count > 1:
                    count_text = FONT_SMALL.render(str(count), True, (255, 255, 255))
                    surface.blit(count_text, (slot_x + slot_size - 25, slot_y + slot_size - 25))


def draw_hud(surface, player, achievements, show_achievement=None):
    """Draw enhanced mobile HUD"""
    # Health bar
    bar_width = 200
    bar_height = 20
    bar_x = 10
    bar_y = 10
    
    pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    health_width = int((player.health / player.max_health) * bar_width)
    pygame.draw.rect(surface, (255, 50, 50), (bar_x, bar_y, health_width, bar_height))
    pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
    
    health_text = FONT_SMALL.render(f"HP: {player.health}/{player.max_health}", True, (255, 255, 255))
    surface.blit(health_text, (bar_x + 5, bar_y + 2))
    
    # Hunger bar
    bar_y = 35
    pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    hunger_width = int((player.hunger / player.max_hunger) * bar_width)
    pygame.draw.rect(surface, (255, 150, 50), (bar_x, bar_y, hunger_width, bar_height))
    pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
    
    hunger_text = FONT_SMALL.render(f"Hunger: {player.hunger}/{player.max_hunger}", True, (255, 255, 255))
    surface.blit(hunger_text, (bar_x + 5, bar_y + 2))
    
    # XP bar
    bar_y = 60
    xp_for_next = (player.level + 1) * 10
    pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, 15))
    xp_width = int((player.xp / xp_for_next) * bar_width)
    pygame.draw.rect(surface, (100, 255, 100), (bar_x, bar_y, xp_width, 15))
    pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, 15), 2)
    
    xp_text = FONT_SMALL.render(f"Level {player.level} | XP: {player.xp}/{xp_for_next}", True, (255, 255, 255))
    surface.blit(xp_text, (bar_x + 5, bar_y))
    
    # FPS counter (top right)
    fps = int(clock.get_fps())
    fps_color = (100, 255, 100) if fps >= 50 else (255, 255, 100) if fps >= 30 else (255, 100, 100)
    fps_text = FONT_SMALL.render(f"FPS: {fps}", True, fps_color)
    surface.blit(fps_text, (SCREEN_WIDTH - 100, 10))
    
    # Achievement popup
    if show_achievement:
        popup_width = 300
        popup_height = 80
        popup_x = (SCREEN_WIDTH - popup_width) // 2
        popup_y = 100
        
        # Background with glow
        s = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 215, 0, 200), (0, 0, popup_width, popup_height), border_radius=10)
        surface.blit(s, (popup_x, popup_y))
        pygame.draw.rect(surface, (255, 255, 255), (popup_x, popup_y, popup_width, popup_height), 3, border_radius=10)
        
        # Text
        title = FONT.render("Achievement Get!", True, (0, 0, 0))
        surface.blit(title, (popup_x + 10, popup_y + 10))
        
        ach_text = FONT_SMALL.render(show_achievement['name'], True, (0, 0, 0))
        surface.blit(ach_text, (popup_x + 10, popup_y + 40))


def main():
    """Main game loop for Bedrock Mobile"""
    global screen
    
    # Generate world
    print("🌍 Generating Bedrock Edition world...")
    world_map, biomes = generate_simple_world()
    
    # Create player at spawn
    spawn_x = GRID_WIDTH // 2 * BLOCK_SIZE
    spawn_y = GRID_HEIGHT // 3 * BLOCK_SIZE
    player = Player(spawn_x, spawn_y)
    
    # Game mode selection
    player.survival_mode = True
    player.creative_mode = False
    
    # Give player starting items (survival)
    if player.creative_mode:
        player.hotbar[0] = (GRASS_ID, 64)
        player.hotbar[1] = (DIRT_ID, 64)
        player.hotbar[2] = (STONE_ID, 64)
        player.hotbar[3] = (WOOD_ID, 64)
        player.hotbar[4] = (PLANKS_ID, 64)
        player.hotbar[5] = (COBBLESTONE_ID, 64)
    
    # Mobs and items
    mobs = []
    dropped_items = []
    particles = []
    
    # Time system
    time_of_day = 0
    time_phase = DAY_PHASE
    spawn_timer = 0
    
    # Weather
    weather = Weather()
    
    # Achievements
    achievements = ACHIEVEMENTS.copy()
    achievement_display_timer = 0
    current_achievement = None
    
    # Touch controls
    joystick = VirtualJoystick(JOYSTICK_SIZE, SCREEN_HEIGHT - JOYSTICK_SIZE)
    
    # Action buttons
    jump_btn = TouchButton(SCREEN_WIDTH - BUTTON_SIZE - 20, SCREEN_HEIGHT - BUTTON_SIZE * 3 - 100, BUTTON_SIZE, BUTTON_SIZE, "Jump", "jump")
    inventory_btn = TouchButton(SCREEN_WIDTH - BUTTON_SIZE - 20, SCREEN_HEIGHT - BUTTON_SIZE * 2 - 50, BUTTON_SIZE, BUTTON_SIZE, "Inv", "inventory")
    mine_btn = TouchButton(SCREEN_WIDTH - BUTTON_SIZE * 2 - 30, SCREEN_HEIGHT - BUTTON_SIZE - 20, BUTTON_SIZE, BUTTON_SIZE, "Mine", "mine")
    place_btn = TouchButton(SCREEN_WIDTH - BUTTON_SIZE - 20, SCREEN_HEIGHT - BUTTON_SIZE - 20, BUTTON_SIZE, BUTTON_SIZE, "Place", "place")
    craft_btn = TouchButton(20, SCREEN_HEIGHT - BUTTON_SIZE - 100, BUTTON_SIZE, BUTTON_SIZE, "Craft", "craft")
    attack_btn = TouchButton(20, SCREEN_HEIGHT - BUTTON_SIZE * 2 - 110, BUTTON_SIZE, BUTTON_SIZE, "⚔", "attack")
    eat_btn = TouchButton(20, SCREEN_HEIGHT - BUTTON_SIZE * 3 - 120, BUTTON_SIZE, BUTTON_SIZE, "🍖", "eat")
    
    buttons = [jump_btn, inventory_btn, mine_btn, place_btn, craft_btn, attack_btn, eat_btn]
    
    # UI states
    crafting_open = False
    mining_continuous = False
    
    # Touch state
    touches = {}  # finger_id -> pos
    joystick_finger = None
    
    running = True
    
    print("✅ PyCraft Bedrock Edition Mobile Ready!")
    print("📱 Touch controls enabled!")
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Touch events
            elif event.type == pygame.FINGERDOWN:
                finger_id = event.finger_id
                touch_x = int(event.x * SCREEN_WIDTH)
                touch_y = int(event.y * SCREEN_HEIGHT)
                touches[finger_id] = (touch_x, touch_y)
                
                # Check if touching joystick area
                joy_dist = math.sqrt((touch_x - joystick.center_x)**2 + (touch_y - joystick.center_y)**2)
                if joy_dist < JOYSTICK_SIZE:
                    joystick_finger = finger_id
                
                # Check button presses
                for btn in buttons:
                    if btn.check_touch((touch_x, touch_y)):
                        btn.pressed = True
                        if btn.action == "jump":
                            player.jump()
                        elif btn.action == "inventory":
                            player.inventory_open = not player.inventory_open
                            crafting_open = False
                        elif btn.action == "mine":
                            mining_continuous = True
                        elif btn.action == "craft":
                            crafting_open = not crafting_open
                            player.inventory_open = False
                        elif btn.action == "attack":
                            dropped = player.attack_mob(mobs)
                            if dropped:
                                dropped_items.append(dropped)
                        elif btn.action == "eat":
                            held_item_id, _ = player.get_held_item()
                            player.eat_food(held_item_id)
                        elif btn.action == "place":
                            # Place block at center of screen
                            held_item = player.get_held_item()
                            if held_item[0] != AIR_ID and held_item[1] > 0:
                                camera_x, camera_y = calculate_camera(player.rect)
                                target_col = (SCREEN_WIDTH // 2 + camera_x) // BLOCK_SIZE
                                target_row = (SCREEN_HEIGHT // 2 + camera_y) // BLOCK_SIZE
                                if 0 <= target_row < GRID_HEIGHT and 0 <= target_col < GRID_WIDTH:
                                    if world_map[target_row][target_col] == AIR_ID:
                                        world_map[target_row][target_col] = held_item[0]
                                        # Remove from inventory
                                        player.hotbar[player.selected_slot] = (held_item[0], held_item[1] - 1)
            
            elif event.type == pygame.FINGERUP:
                finger_id = event.finger_id
                if finger_id in touches:
                    del touches[finger_id]
                if finger_id == joystick_finger:
                    joystick_finger = None
                
                # Release buttons
                for btn in buttons:
                    if btn.action == "mine":
                        mining_continuous = False
                    btn.pressed = False
            
            elif event.type == pygame.FINGERMOTION:
                finger_id = event.finger_id
                touch_x = int(event.x * SCREEN_WIDTH)
                touch_y = int(event.y * SCREEN_HEIGHT)
                touches[finger_id] = (touch_x, touch_y)
            
            # Keyboard fallback for PC testing
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key == pygame.K_e:
                    player.inventory_open = not player.inventory_open
                elif event.key == pygame.K_c:
                    crafting_open = not crafting_open
                elif event.key == pygame.K_f:
                    held_item_id, _ = player.get_held_item()
                    player.eat_food(held_item_id)
                elif event.key == pygame.K_1:
                    player.selected_slot = 0
                elif event.key == pygame.K_2:
                    player.selected_slot = 1
                elif event.key == pygame.K_3:
                    player.selected_slot = 2
                elif event.key == pygame.K_4:
                    player.selected_slot = 3
                elif event.key == pygame.K_5:
                    player.selected_slot = 4
                elif event.key == pygame.K_6:
                    player.selected_slot = 5
                elif event.key == pygame.K_7:
                    player.selected_slot = 6
                elif event.key == pygame.K_8:
                    player.selected_slot = 7
                elif event.key == pygame.K_9:
                    player.selected_slot = 8
            
            # Handle crafting clicks
            elif event.type == pygame.MOUSEBUTTONDOWN and crafting_open:
                mouse_pos = pygame.mouse.get_pos()
                recipe_buttons = draw_crafting_menu(screen, player, RECIPES)
                for recipe_name, button_rect, can_craft in recipe_buttons:
                    if button_rect.collidepoint(mouse_pos) and can_craft:
                        craft_item(player, recipe_name, RECIPES)
        
        # Update joystick
        if joystick_finger and joystick_finger in touches:
            joystick.update(touches[joystick_finger])
        else:
            joystick.update(None)
        
        # Update player
        joystick_dir = joystick.get_direction()
        player.update(world_map, joystick_dir)
        
        # Mining (continuous while button held)
        if mining_continuous:
            camera_x, camera_y = calculate_camera(player.rect)
            target_col = (SCREEN_WIDTH // 2 + camera_x) // BLOCK_SIZE
            target_row = (SCREEN_HEIGHT // 2 + camera_y) // BLOCK_SIZE
            if 0 <= target_row < GRID_HEIGHT and 0 <= target_col < GRID_WIDTH:
                player.mine_block(world_map, target_row, target_col)
        else:
            player.mining_progress = 0
            player.mining_target = None
        
        # Update time
        time_of_day, time_phase = update_time(time_of_day)
        
        # Update weather
        player_col = int(player.rect.centerx // BLOCK_SIZE)
        current_biome = biomes[player_col] if player_col < len(biomes) else PLAINS_BIOME
        weather.update(current_biome)
        
        # Track biomes visited for achievement
        if 'adventuring_time' in achievements:
            achievements['adventuring_time']['biomes'].add(current_biome)
            if len(achievements['adventuring_time']['biomes']) >= 4:
                if not achievements['adventuring_time']['unlocked']:
                    achievements['adventuring_time']['unlocked'] = True
                    current_achievement = achievements['adventuring_time']
                    achievement_display_timer = 180
        
        # Spawn mobs
        spawn_timer += 1
        if spawn_timer >= 180:  # Every 6 seconds
            spawn_timer = 0
            if time_phase in [NIGHT_PHASE, EVENING_PHASE]:
                spawn_mobs_near_player(player, world_map, mobs, biomes)
        
        # Update mobs
        for mob in mobs[:]:
            mob.update(world_map, player)
            
            # Attack player if hostile
            if mob.hostile:
                mob.attack(player, 2)
            
            # Remove dead mobs
            if mob.health <= 0:
                # Drop loot and XP
                if isinstance(mob, (Pig, Cow, Sheep)):
                    dropped_items.append(DroppedItem(mob.rect.centerx, mob.rect.centery, RAW_BEEF, 1))
                    player.xp += 1
                elif mob.hostile:
                    player.xp += 5
                    # Achievement progress
                    if 'monster_hunter' in achievements:
                        achievements['monster_hunter']['progress'] += 1
                        if achievements['monster_hunter']['progress'] >= 10:
                            if not achievements['monster_hunter']['unlocked']:
                                achievements['monster_hunter']['unlocked'] = True
                                current_achievement = achievements['monster_hunter']
                                achievement_display_timer = 180
                
                # Particles on death
                for _ in range(10):
                    particles.append(Particle(
                        mob.rect.centerx + random.randint(-20, 20),
                        mob.rect.centery + random.randint(-20, 20),
                        mob.color,
                        random.uniform(-2, 2),
                        random.uniform(-3, -1),
                        30
                    ))
                
                mobs.remove(mob)
        
        # Level up check
        xp_for_next = (player.level + 1) * 10
        if player.xp >= xp_for_next:
            player.level += 1
            player.xp -= xp_for_next
            # Particle effect
            for _ in range(20):
                particles.append(Particle(
                    player.rect.centerx + random.randint(-30, 30),
                    player.rect.centery + random.randint(-30, 30),
                    (255, 215, 0),
                    random.uniform(-2, 2),
                    random.uniform(-4, -2),
                    60
                ))
        
        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                particles.remove(particle)
        
        # Update dropped items
        for item in dropped_items[:]:
            item.update(world_map)
            
            # Collect items
            if player.rect.colliderect(item.rect):
                player.add_to_inventory(item.item_id, item.count)
                dropped_items.remove(item)
            
            # Despawn old items
            if item.lifetime > 600:  # 20 seconds
                dropped_items.remove(item)
        
        # Check player death
        if player.health <= 0:
            print("💀 You died!")
            player.health = player.max_health
            player.hunger = player.max_hunger
            # Respawn at spawn
            player.rect.x = GRID_WIDTH // 2 * BLOCK_SIZE
            player.rect.y = GRID_HEIGHT // 3 * BLOCK_SIZE
        
        # Calculate camera
        camera_x, camera_y = calculate_camera(player.rect)
        
        # Calculate lighting
        light_level = calculate_lighting(world_map, (player.rect.centerx, player.rect.centery), time_phase)
        
        # Achievement timer
        if achievement_display_timer > 0:
            achievement_display_timer -= 1
            if achievement_display_timer == 0:
                current_achievement = None
        
        # Draw everything
        screen.fill(get_sky_color(time_of_day, time_phase))
        
        # Draw world with lighting
        draw_world(screen, world_map, camera_x, camera_y, light_level)
        
        # Draw particles
        for particle in particles:
            particle.draw(screen, camera_x, camera_y)
        
        # Draw dropped items
        for item in dropped_items:
            item.draw(screen, camera_x, camera_y)
        
        # Draw mobs
        for mob in mobs:
            mob.draw(screen, camera_x, camera_y)
        
        # Draw crosshair (center of screen)
        crosshair_size = 20
        pygame.draw.line(screen, (255, 255, 255), 
                        (SCREEN_WIDTH // 2 - crosshair_size, SCREEN_HEIGHT // 2),
                        (SCREEN_WIDTH // 2 + crosshair_size, SCREEN_HEIGHT // 2), 2)
        pygame.draw.line(screen, (255, 255, 255),
                        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - crosshair_size),
                        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + crosshair_size), 2)
        
        # Draw mining progress
        if player.mining_target:
            progress = min(1.0, player.mining_progress / 10)
            bar_width = 100
            bar_height = 10
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            bar_y = SCREEN_HEIGHT // 2 + 40
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (100, 200, 100), (bar_x, bar_y, int(bar_width * progress), bar_height))
        
        # Draw player
        player.draw(screen, camera_x, camera_y)
        
        # Draw weather effects
        weather.draw(screen)
        
        # Draw HUD
        draw_hud(screen, player, achievements, current_achievement if achievement_display_timer > 0 else None)
        draw_hotbar(screen, player)
        
        # Draw time and biome indicator
        time_text = FONT_SMALL.render(f"Time: {['Day', 'Evening', 'Night', 'Morning'][time_phase]}", True, (255, 255, 255))
        screen.blit(time_text, (SCREEN_WIDTH - 150, 60))
        
        biome_names = {0: "Plains", 1: "Desert", 2: "Snow", 3: "Jungle"}
        biome_text = FONT_SMALL.render(f"Biome: {biome_names.get(current_biome, 'Unknown')}", True, (255, 255, 255))
        screen.blit(biome_text, (SCREEN_WIDTH - 150, 85))
        
        # Draw mob count
        mob_text = FONT_SMALL.render(f"Mobs: {len(mobs)}", True, (255, 255, 255))
        screen.blit(mob_text, (SCREEN_WIDTH - 150, 110))
        
        # Draw touch controls (if not in menus)
        if not player.inventory_open and not crafting_open:
            joystick.draw(screen)
            for btn in buttons:
                btn.draw(screen)
        
        # Draw inventory overlay
        if player.inventory_open:
            draw_inventory(screen, player)
        
        # Draw crafting overlay
        if crafting_open:
            draw_crafting_menu(screen, player, RECIPES)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    print("🎮 PyCraft Bedrock Edition - Mobile/Tablet Version")
    print("📱 Optimized for touch controls and smaller screens")
    print("=" * 60)
    main()
