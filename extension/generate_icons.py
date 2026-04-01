#!/usr/bin/env python3
"""Generate icon images for the extension"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create images directory
os.makedirs('images', exist_ok=True)

# Icon sizes
sizes = [16, 48, 128]
colors = {
    'bg': '#1a1a2e',      # Dark blue background
    'circle': '#e94560',  # Red/pink accent
    'text': '#ffffff'     # White text
}

for size in sizes:
    # Create a new image with dark background
    img = Image.new('RGB', (size, size), colors['bg'])
    draw = ImageDraw.Draw(img)
    
    # Draw a circle (representing a scan/detection)
    margin = size // 8
    bbox = [margin, margin, size - margin, size - margin]
    draw.ellipse(bbox, outline=colors['circle'], width=max(1, size // 16))
    
    # Draw a checkmark style line for detection
    if size >= 16:
        line_width = max(1, size // 16)
        # Diagonal line for checkmark
        draw.line([(size // 4, size // 2), (size // 2.5, size * 0.65), 
                   (size * 0.7, size // 3)], fill=colors['circle'], width=line_width)
    
    # Save the icon
    img.save(f'images/icon-{size}.png')
    print(f'✓ Created images/icon-{size}.png')

print('\n✅ All icons created successfully!')
