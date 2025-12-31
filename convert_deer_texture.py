from PIL import Image, ImageEnhance
import os

# Load the deer texture
input_path = r"d:\Python\PyGame\Textures\Deer_Texture_.webp"
output_path = r"d:\Python\PyGame\Textures\deer_texture_brown.png"

# Open the image
img = Image.open(input_path)

# Convert to RGBA if not already
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# Make it blockier by reducing resolution then scaling back up
original_size = img.size
# Reduce to 1/4 size to get blocky effect
blocky_size = (original_size[0] // 4, original_size[1] // 4)
img_small = img.resize(blocky_size, Image.NEAREST)
img_blocky = img_small.resize(original_size, Image.NEAREST)

# Make it brown by adjusting color channels
pixels = img_blocky.load()
width, height = img_blocky.size

for y in range(height):
    for x in range(width):
        r, g, b, a = pixels[x, y]
        
        # Skip transparent pixels
        if a == 0:
            continue
        
        # Convert to brown tones
        # Increase red, moderate green, decrease blue
        new_r = min(255, int(r * 1.3 + 40))
        new_g = min(255, int(g * 0.8 + 20))
        new_b = min(255, int(b * 0.5))
        
        pixels[x, y] = (new_r, new_g, new_b, a)

# Save the result
img_blocky.save(output_path)
print(f"Brown and blocky deer texture saved to: {output_path}")
print(f"Original size: {original_size}")
