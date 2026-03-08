# PyCraft Mod System

Place `.py` mod files in this folder. They are loaded automatically when the game starts.

## Mod Template

```python
MOD_NAME = "My Mod"
MOD_VERSION = "1.0"

def register(api):
    """Called by the game to register your mod content."""

    # Add a new block/item
    api.add_block(700, {
        "name": "Ruby",
        "color": (200, 0, 50),
        "mineable": False,
        "solid": False,
    })

    # Add a crafting recipe (ingredient_id: count pairs -> (result_id, result_count))
    # 3 Iron Ingots -> Ruby (example)
    api.add_recipe({108: 3}, (700, 1))

    # Add your new item to the creative inventory (category name, list of IDs)
    api.add_to_creative("Items", [700])
```

## API Reference

| Method | Description |
|---|---|
| `api.add_block(id, data_dict)` | Register a new block/item in BLOCK_TYPES |
| `api.add_recipe(ingredients, result)` | Add a crafting recipe. `ingredients` = `{item_id: count}`. `result` = `(item_id, count)` |
| `api.add_to_creative(category, id_list)` | Add items to a creative tab. Categories: `"Building Blocks"`, `"Items"`, `"Nature"`, `"Nether"`, `"Spawn Eggs"` |
| `api.BLOCK_TYPES` | Direct access to the game's block type dictionary |
| `api.CRAFTING_RECIPES` | Direct access to crafting recipes dictionary |
| `api.CREATIVE_CATEGORIES` | Direct access to creative inventory categories |

## Notes
- Use IDs 700+ to avoid conflicts with vanilla blocks (IDs below 700 are reserved)
- Mods are loaded after all vanilla content is defined
- Errors in a mod are caught and reported in the console; other mods still load
