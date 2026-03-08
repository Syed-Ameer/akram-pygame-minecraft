# Example mod: adds a Ruby gem item
MOD_NAME = "Example Ruby Mod"
MOD_VERSION = "1.0"

def register(api):
    """Register this mod's content with the game."""

    # Add Ruby item (ID 700)
    api.add_block(700, {
        "name": "Ruby",
        "color": (220, 20, 60),
        "mineable": False,
        "solid": False,
    })

    # Ruby Sword (ID 701): crafted from 2 Rubies + 1 Stick
    api.add_block(701, {
        "name": "Ruby Sword",
        "color": (255, 50, 80),
        "mineable": False,
        "solid": False,
        "tool_level": 5,
        "durability": 1000,
        "damage_bonus": 15,
        "attack_cooldown": 10,
    })

    # 2 Ruby + 1 Stick -> Ruby Sword
    api.add_recipe({700: 2, 10: 1}, (701, 1))

    # Add to creative inventory
    api.add_to_creative("Items", [700, 701])
