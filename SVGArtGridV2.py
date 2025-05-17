#!/usr/bin/env python3
"""
SVGArtGridV2.py - Generate artistic SVG grids based on design patterns or images

This script creates SVG art pieces with a grid of squares containing various designs.
Each square uses two colors from a selected color palette, with the possibility of
including one larger block as a focal point.

Added features from V1:
- Higher resolution support with increased row/column limits
- Image input with two modes:
  1. Color sample mode: Extract a color palette from an input image
  2. Composition mode: Use colors from regions of the image to determine colors for each grid square

Usage:
    python SVGArtGridV2.py [options]

Options:
    --rows ROWS                 Number of rows (default: random 8-16)
    --cols COLS                 Number of columns (default: random 8-16)
    --square-size SIZE          Size of each square in pixels (default: 100)
    --output FILE               Output file path (default: art_grid.svg)
    --seed SEED                 Random seed for reproducibility
    --palette-file FILE         Path to JSON file with color palettes (default: fetch from URL)
    --palette-index INDEX       Index of palette to use (default: random)
    --big-block                 Include a big block (default: True)
    --no-big-block              Do not include a big block
    --big-block-size {2,3}      Size multiplier for big block (default: random 2-3)
    --block-styles STYLES       Comma-separated list of block styles to include (default: all)
    --image FILE                Path to input image file
    --mode {palette,composition} Image processing mode
    --color-count COUNT         Number of colors to extract from image (default: 5)
    --blend-factor FACTOR       How closely to follow image colors (0-1, default: 0.7)
"""

import argparse
import random
import json
import svgwrite
import requests
from math import ceil
import colorsys
# New imports for image processing
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate an SVG art grid.')
    # Original command line parameters
    parser.add_argument('--rows', type=int, help='Number of rows (default: random 8-16)')
    parser.add_argument('--cols', type=int, help='Number of columns (default: random 8-16)')
    parser.add_argument('--square-size', type=int, default=100, help='Size of each square in pixels (default: 100)')
    parser.add_argument('--output', default='art_grid.svg', help='Output file path (default: art_grid.svg)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--palette-file', help='Path to JSON file with color palettes (default: fetch from URL)')
    parser.add_argument('--palette-index', type=int, help='Index of palette to use (default: random)')
    parser.add_argument('--big-block', action='store_true', default=True, help='Include a big block (default: True)')
    parser.add_argument('--no-big-block', action='store_false', dest='big_block', help='Do not include a big block')
    parser.add_argument('--big-block-size', type=int, choices=[2, 3], help='Size multiplier for big block (default: random 2-3)')
    parser.add_argument('--block-styles', help='Comma-separated list of block styles to include (default: all)')
    
    # New image-related parameters
    parser.add_argument('--image', help='Path to input image file')
    parser.add_argument('--mode', choices=['palette', 'composition'], 
                        help='Image processing mode: "palette" to extract colors or "composition" to follow image structure')
    parser.add_argument('--color-count', type=int, default=5, 
                        help='Number of colors to extract from image (default: 5)')
    parser.add_argument('--blend-factor', type=float, default=0.7, 
                        help='How closely to follow image colors in composition mode (0-1, default: 0.7)')
    
    return parser.parse_args()

def load_color_palettes(palette_file):
    """Load color palettes from a file or URL."""
    if palette_file:
        with open(palette_file, 'r') as f:
            return json.load(f)
    else:
        response = requests.get("https://unpkg.com/nice-color-palettes@3.0.0/100.json")
        return response.json()

def extract_palette_from_image(image_path, color_count=5):
    """
    Extract a color palette from an image using k-means clustering.
    
    Args:
        image_path (str): Path to the input image
        color_count (int): Number of colors to extract
        
    Returns:
        list: List of hex color codes
    """
    # Open and resize image (for faster processing)
    img = Image.open(image_path)
    img = img.resize((150, 150))  # Smaller size for faster processing
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Get pixel data as numpy array and reshape for k-means
    pixels = np.array(img)
    pixels = pixels.reshape(-1, 3)
    
    # Apply k-means clustering to find dominant colors
    kmeans = KMeans(n_clusters=color_count, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Get the colors
    colors = kmeans.cluster_centers_
    
    # Convert to hex format
    hex_colors = []
    for color in colors:
        # Convert to integers
        r, g, b = [int(c) for c in color]
        # Convert to hex
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        hex_colors.append(hex_color)
    
    return hex_colors

def sample_image_region(image, x, y, width, height, sample_count=2):
    """
    Sample predominant colors from a region of an image.
    
    Args:
        image: PIL Image object
        x, y: Top-left coordinates of the region
        width, height: Dimensions of the region
        sample_count: Number of colors to extract
        
    Returns:
        dict: Dict with "foreground" and "background" color values
    """
    # Crop the region from the image
    region = image.crop((x, y, x + width, y + height))
    
    # Resize for faster processing
    region = region.resize((50, 50))
    
    # Convert to RGB if needed
    if region.mode != 'RGB':
        region = region.convert('RGB')
    
    # Get pixel data as numpy array
    pixels = np.array(region)
    pixels = pixels.reshape(-1, 3)
    
    # Use k-means to find dominant colors
    kmeans = KMeans(n_clusters=sample_count, random_state=42, n_init=10)
    kmeans.fit(pixels)
    
    # Get the colors
    colors = kmeans.cluster_centers_
    
    # Convert to hex format
    hex_colors = []
    for color in colors:
        r, g, b = [int(c) for c in color]
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        hex_colors.append(hex_color)
    
    # Calculate brightness for each color to determine foreground/background
    brightness = []
    for color in colors:
        # Simple brightness formula: 0.299*R + 0.587*G + 0.114*B
        bright = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        brightness.append(bright)
    
    # Sort colors by brightness
    sorted_colors = [x for _, x in sorted(zip(brightness, hex_colors))]
    
    # Return darkest as foreground, lightest as background (or vice versa)
    # This creates better contrast in the blocks
    return {
        "foreground": sorted_colors[0],  # Darkest color
        "background": sorted_colors[-1]  # Lightest color
    }

def create_background_colors(color_palette):
    """Create background colors by mixing colors from the palette."""
    # Mix the first two colors of the palette
    color1 = color_palette[0].lstrip('#')
    color2 = color_palette[1].lstrip('#')
    
    # Convert hex to RGB
    r1, g1, b1 = tuple(int(color1[i:i+2], 16) for i in (0, 2, 4))
    r2, g2, b2 = tuple(int(color2[i:i+2], 16) for i in (0, 2, 4))
    
    # Mix colors (50% blend)
    r = (r1 + r2) // 2
    g = (g1 + g2) // 2
    b = (b1 + b2) // 2
    
    # Desaturate (convert to HSL, reduce saturation, convert back)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    s = max(0, s - 0.1)  # Desaturate by 10%
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    r, g, b = int(r*255), int(g*255), int(b*255)
    
    # Create hex color
    bg = f"#{r:02x}{g:02x}{b:02x}"
    
    # Create lighter and darker versions
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    
    # Lighter (increase lightness)
    l_light = min(1, l + 0.1)
    r_light, g_light, b_light = colorsys.hls_to_rgb(h, l_light, s)
    r_light, g_light, b_light = int(r_light*255), int(g_light*255), int(b_light*255)
    bg_inner = f"#{r_light:02x}{g_light:02x}{b_light:02x}"
    
    # Darker (decrease lightness)
    l_dark = max(0, l - 0.1)
    r_dark, g_dark, b_dark = colorsys.hls_to_rgb(h, l_dark, s)
    r_dark, g_dark, b_dark = int(r_dark*255), int(g_dark*255), int(b_dark*255)
    bg_outer = f"#{r_dark:02x}{g_dark:02x}{b_dark:02x}"
    
    return {"bg_inner": bg_inner, "bg_outer": bg_outer}

def get_two_colors(color_palette):
    """Get two different colors from the palette."""
    color_list = color_palette.copy()
    # Get random index for this array of colors
    color_index = random.randint(0, len(color_list) - 1)
    # Set the background to the color at that array
    background = color_list[color_index]
    # Remove that color from the options
    color_list.pop(color_index)
    # Set the foreground to any other color in the array
    foreground = random.choice(color_list)
    
    return {"foreground": foreground, "background": background}

def draw_circle(dwg, x, y, square_size, foreground, background):
    """Draw a circle block."""
    # Create group
    group = dwg.g(class_="draw-circle")
    
    # Draw background
    group.add(dwg.rect((x, y), (square_size, square_size), fill=background))
    
    # Draw foreground circle
    group.add(dwg.circle(center=(x + square_size/2, y + square_size/2), 
                         r=square_size/2, fill=foreground))
    
    # Add variation: sometimes add an inner circle
    if random.random() < 0.3:
        group.add(dwg.circle(center=(x + square_size/2, y + square_size/2),
                             r=square_size/4, fill=background))
    
    dwg.add(group)

def draw_opposite_circles(dwg, x, y, square_size, foreground, background):
    """Draw opposite circles block."""
    group = dwg.g(class_="opposite-circles")
    circle_group = dwg.g()
    
    # Draw background
    group.add(dwg.rect((x, y), (square_size, square_size), fill=background))
    
    # Create mask
    mask_id = f"mask-{x}-{y}"
    mask = dwg.mask(id=mask_id)
    mask.add(dwg.rect((x, y), (square_size, square_size), fill="white"))
    dwg.defs.add(mask)
    
    # Choose one of these options for circle positions
    options = [
        # top left + bottom right
        [0, 0, square_size, square_size],
        # top right + bottom left
        [square_size, 0, 0, square_size]
    ]
    offset = random.choice(options)
    
    # Draw circles
    circle1 = dwg.circle(center=(x + offset[0], y + offset[1]), 
                        r=square_size/2, fill=foreground)
    circle2 = dwg.circle(center=(x + offset[2], y + offset[3]), 
                        r=square_size/2, fill=foreground)
    
    circle_group.add(circle1)
    circle_group.add(circle2)
    
    # Apply mask to circle group
    circle_group['mask'] = f"url(#{mask_id})"
    
    group.add(circle_group)
    dwg.add(group)

def draw_cross(dwg, x, y, square_size, foreground, background):
    """Draw a cross or X block."""
    group = dwg.g(class_="draw-cross")
    
    # Draw background
    group.add(dwg.rect((x, y), (square_size, square_size), fill=background))
    
    # Determine if it's a + or ×
    is_plus = random.random() < 0.5
    
    if is_plus:
        # Horizontal line
        group.add(dwg.rect(
            (x, y + square_size/3),
            (square_size, square_size/3),
            fill=foreground
        ))
        
        # Vertical line
        group.add(dwg.rect(
            (x + square_size/3, y),
            (square_size/3, square_size),
            fill=foreground
        ))
    else:
        # For the X, we use a polygon with two triangles
        # First diagonal line (top-left to bottom-right)
        width = square_size / 6  # Width of the line
        
        # Calculate points for diagonal line
        x1, y1 = x, y
        x2, y2 = x + square_size, y + square_size
        
        # Calculate points for the polygon (a thick line)
        dx = x2 - x1
        dy = y2 - y1
        length = (dx**2 + dy**2)**0.5
        
        # Normalize and rotate to get perpendicular vector
        nx, ny = -dy/length, dx/length
        
        # Calculate corners of the polygon
        p1 = (x1 + nx*width/2, y1 + ny*width/2)
        p2 = (x2 + nx*width/2, y2 + ny*width/2)
        p3 = (x2 - nx*width/2, y2 - ny*width/2)
        p4 = (x1 - nx*width/2, y1 - ny*width/2)
        
        group.add(dwg.polygon([p1, p2, p3, p4], fill=foreground))
        
        # Second diagonal line (top-right to bottom-left)
        x1, y1 = x + square_size, y
        x2, y2 = x, y + square_size
        
        # Calculate points for the polygon (a thick line)
        dx = x2 - x1
        dy = y2 - y1
        length = (dx**2 + dy**2)**0.5
        
        # Normalize and rotate to get perpendicular vector
        nx, ny = -dy/length, dx/length
        
        # Calculate corners of the polygon
        p1 = (x1 + nx*width/2, y1 + ny*width/2)
        p2 = (x2 + nx*width/2, y2 + ny*width/2)
        p3 = (x2 - nx*width/2, y2 - ny*width/2)
        p4 = (x1 - nx*width/2, y1 - ny*width/2)
        
        group.add(dwg.polygon([p1, p2, p3, p4], fill=foreground))
    
    dwg.add(group)

def draw_half_square(dwg, x, y, square_size, foreground, background):
    """Draw a half square block."""
    group = dwg.g(class_="draw-half-square")
    
    # Draw background
    group.add(dwg.rect((x, y), (square_size, square_size), fill=background))
    
    # Determine which half to fill
    direction = random.choice(['top', 'right', 'bottom', 'left'])
    
    if direction == 'top':
        points = [(x, y), (x + square_size, y), (x + square_size, y + square_size/2), (x, y + square_size/2)]
    elif direction == 'right':
        points = [(x + square_size/2, y), (x + square_size, y), (x + square_size, y + square_size), (x + square_size/2, y + square_size)]
    elif direction == 'bottom':
        points = [(x, y + square_size/2), (x + square_size, y + square_size/2), (x + square_size, y + square_size), (x, y + square_size)]
    else:  # left
        points = [(x, y), (x + square_size/2, y), (x + square_size/2, y + square_size), (x, y + square_size)]
    
    group.add(dwg.polygon(points, fill=foreground))
    
    dwg.add(group)

def draw_diagonal_square(dwg, x, y, square_size, foreground, background):
    """Draw a diagonal square block."""
    group = dwg.g(class_="draw-diagonal-square")
    
    # Draw background
    group.add(dwg.rect((x, y), (square_size, square_size), fill=background))
    
    # Determine which diagonal to fill
    is_top_left_to_bottom_right = random.random() < 0.5
    
    if is_top_left_to_bottom_right:
        points = [(x, y), (x + square_size, y + square_size), (x, y + square_size)]
    else:
        points = [(x + square_size, y), (x + square_size, y + square_size), (x, y)]
    
    group.add(dwg.polygon(points, fill=foreground))
    
    dwg.add(group)

def draw_quarter_circle(dwg, x, y, square_size, foreground, background):
    """Draw a quarter circle block."""
    group = dwg.g(class_="draw-quarter-circle")
    
    # Draw background
    group.add(dwg.rect((x, y), (square_size, square_size), fill=background))
    
    # Determine which corner to place the quarter circle
    corner = random.choice(['top-left', 'top-right', 'bottom-right', 'bottom-left'])
    
    # Create a path for the quarter circle
    path = dwg.path(fill=foreground)
    
    if corner == 'top-left':
        path.push(f"M {x} {y}")
        path.push(f"A {square_size} {square_size} 0 0 1 {x + square_size} {y}")
        path.push(f"L {x} {y}")
    elif corner == 'top-right':
        path.push(f"M {x + square_size} {y}")
        path.push(f"A {square_size} {square_size} 0 0 1 {x + square_size} {y + square_size}")
        path.push(f"L {x + square_size} {y}")
    elif corner == 'bottom-right':
        path.push(f"M {x + square_size} {y + square_size}")
        path.push(f"A {square_size} {square_size} 0 0 1 {x} {y + square_size}")
        path.push(f"L {x + square_size} {y + square_size}")
    else:  # bottom-left
        path.push(f"M {x} {y + square_size}")
        path.push(f"A {square_size} {square_size} 0 0 1 {x} {y}")
        path.push(f"L {x} {y + square_size}")
    
    group.add(path)
    
    dwg.add(group)

def draw_dots(dwg, x, y, square_size, foreground, background):
    """Draw a dots block."""
    group = dwg.g(class_="draw-dots")
    
    # Draw background
    group.add(dwg.rect((x, y), (square_size, square_size), fill=background))
    
    # Determine number of dots (4, 9, or 16)
    num_dots = random.choice([4, 9, 16])
    
    if num_dots == 4:
        rows, cols = 2, 2
    elif num_dots == 9:
        rows, cols = 3, 3
    else:  # 16
        rows, cols = 4, 4
    
    cell_size = square_size / rows
    dot_radius = cell_size * 0.3
    
    for i in range(rows):
        for j in range(cols):
            center_x = x + (i + 0.5) * cell_size
            center_y = y + (j + 0.5) * cell_size
            
            group.add(dwg.circle(center=(center_x, center_y), r=dot_radius, fill=foreground))
    
    dwg.add(group)

def draw_letter_block(dwg, x, y, square_size, foreground, background):
    """Draw a letter block."""
    group = dwg.g(class_="draw-letter-block")
    
    # Draw background
    group.add(dwg.rect((x, y), (square_size, square_size), fill=background))
    
    # Select a random character
    # Using a limited set that would look good in a monospace font
    characters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
                 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                 '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                 '+', '-', '*', '/', '=', '#', '@', '&', '%', '$']
    
    character = random.choice(characters)
    
    # Add text element
    text = dwg.text(character, insert=(x + square_size/2, y + square_size/2 + square_size*0.3), 
                    font_family="monospace", font_size=square_size*0.8, 
                    font_weight="bold", fill=foreground,
                    text_anchor="middle")
    
    group.add(text)
    
    dwg.add(group)

def generate_little_block(dwg, i, j, square_size, color_palette, block_styles):
    """Generate a single block in the grid."""
    colors = get_two_colors(color_palette)
    
    # Convert block_styles to function map if they are strings
    style_map = {
        'circle': draw_circle,
        'opposite_circles': draw_opposite_circles,
        'cross': draw_cross,
        'half_square': draw_half_square,
        'diagonal_square': draw_diagonal_square,
        'quarter_circle': draw_quarter_circle,
        'dots': draw_dots,
        'letter_block': draw_letter_block
    }
    
    # Filter available styles based on user selection
    available_styles = [style for style in block_styles if style in style_map]
    if not available_styles:
        available_styles = list(style_map.keys())
    
    # Select a random style
    style_name = random.choice(available_styles)
    style_func = style_map[style_name]
    
    x_pos = i * square_size
    y_pos = j * square_size
    
    # Call the appropriate drawing function
    style_func(dwg, x_pos, y_pos, square_size, colors["foreground"], colors["background"])

def generate_grid(dwg, num_rows, num_cols, square_size, color_palette, block_styles):
    """Generate the grid of blocks."""
    for i in range(num_rows):
        for j in range(num_cols):
            generate_little_block(dwg, i, j, square_size, color_palette, block_styles)

def generate_composition_grid(dwg, image_path, num_rows, num_cols, square_size, block_styles):
    """
    Generate a grid based on image composition.
    
    Args:
        dwg: SVG drawing object
        image_path: Path to the input image
        num_rows, num_cols: Grid dimensions
        square_size: Size of each square
        block_styles: List of available block styles
    """
    # Open and resize image to match the grid dimensions
    img = Image.open(image_path)
    img = img.resize((num_rows * square_size, num_cols * square_size))
    
    # For each grid position, sample colors and create a block
    for i in range(num_rows):
        for j in range(num_cols):
            # Calculate the region coordinates
            x_pos = i * square_size
            y_pos = j * square_size
            
            # Sample colors from this region of the image
            colors = sample_image_region(img, x_pos, y_pos, square_size, square_size)
            
            # Convert block_styles to function map
            style_map = {
                'circle': draw_circle,
                'opposite_circles': draw_opposite_circles,
                'cross': draw_cross,
                'half_square': draw_half_square,
                'diagonal_square': draw_diagonal_square,
                'quarter_circle': draw_quarter_circle,
                'dots': draw_dots,
                'letter_block': draw_letter_block
            }
            
            # Filter available styles based on user selection
            available_styles = [style for style in block_styles if style in style_map]
            if not available_styles:
                available_styles = list(style_map.keys())
            
            # Select a random style
            style_name = random.choice(available_styles)
            style_func = style_map[style_name]
            
            # Call the appropriate drawing function
            style_func(dwg, x_pos, y_pos, square_size, colors["foreground"], colors["background"])

def generate_big_block(dwg, num_rows, num_cols, square_size, color_palette, block_styles, multiplier):
    """Generate a big block."""
    colors = get_two_colors(color_palette)
    
    # Convert block_styles to function map
    style_map = {
        'circle': draw_circle,
        'opposite_circles': draw_opposite_circles,
        'cross': draw_cross,
        'half_square': draw_half_square,
        'diagonal_square': draw_diagonal_square,
        'quarter_circle': draw_quarter_circle,
        # 'dots' is excluded for big blocks as mentioned in the article
        'letter_block': draw_letter_block
    }
    
    # Filter available styles based on user selection
    available_styles = [style for style in block_styles if style in style_map and style != 'dots']
    if not available_styles:
        available_styles = list(style_map.keys())
        if 'dots' in available_styles:
            available_styles.remove('dots')
    
    # Random position that doesn't overflow
    x_pos = random.randint(0, num_rows - multiplier) * square_size
    y_pos = random.randint(0, num_cols - multiplier) * square_size
    
    # Calculate the big square size
    big_square_size = multiplier * square_size
    
    # Select a random style
    style_name = random.choice(available_styles)
    style_func = style_map[style_name]
    
    # Call the appropriate drawing function with the bigger size
    style_func(dwg, x_pos, y_pos, big_square_size, colors["foreground"], colors["background"])

def main():
    """Main function to run the SVG art grid generator."""
    args = parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
    
    # Determine rows and columns - now with higher limits
    num_rows = args.rows if args.rows is not None else random.randint(8, 16)
    num_cols = args.cols if args.cols is not None else random.randint(8, 16)
    square_size = args.square_size
    
    # Load color palettes based on input mode
    if args.image and args.mode == 'palette':
        # Get palette from image
        color_palette = extract_palette_from_image(args.image, args.color_count)
        print(f"Extracted {len(color_palette)} colors from image: {color_palette}")
    else:
        # Use traditional palette from JSON
        palettes = load_color_palettes(args.palette_file)
        palette_idx = args.palette_index if args.palette_index is not None else random.randint(0, len(palettes) - 1)
        color_palette = palettes[palette_idx]
    
    # Determine which block styles to use
    all_styles = ['circle', 'opposite_circles', 'cross', 'half_square', 'diagonal_square', 'quarter_circle', 'dots', 'letter_block']
    if args.block_styles:
        block_styles = args.block_styles.split(',')
    else:
        block_styles = all_styles
        
    # Create SVG
    svg_width = num_rows * square_size
    svg_height = num_cols * square_size
    dwg = svgwrite.Drawing(args.output, size=(f"{svg_width}px", f"{svg_height}px"), profile='full')
    
    # Add CSS for shape rendering
    dwg.defs.add(dwg.style("svg * { shape-rendering: crispEdges; }"))
    
    # Add background
    bg_colors = create_background_colors(color_palette)
    
    # Create a gradient for the background
    gradient = dwg.defs.add(dwg.radialGradient(id="background_gradient"))
    gradient.add_stop_color(0, bg_colors["bg_inner"])
    gradient.add_stop_color(1, bg_colors["bg_outer"])
    
    # Add a background rectangle with the gradient
    dwg.add(dwg.rect((0, 0), (svg_width, svg_height), fill="url(#background_gradient)"))
    
    # Generate grid based on mode
    if args.image and args.mode == 'composition':
        # Generate grid based on image composition
        generate_composition_grid(dwg, args.image, num_rows, num_cols, square_size, block_styles)
        print(f"Generated a {num_rows}x{num_cols} grid based on image composition")
    else:
        # Generate traditional grid
        generate_grid(dwg, num_rows, num_cols, square_size, color_palette, block_styles)
        print(f"Generated a {num_rows}x{num_cols} grid with square size {square_size}px")
        print(f"Used color palette: {color_palette}")
    
    # Add big block if enabled (only for non-composition mode)
    if args.big_block and not (args.image and args.mode == 'composition'):
        big_block_size = args.big_block_size if args.big_block_size is not None else random.choice([2, 3])
        generate_big_block(dwg, num_rows, num_cols, square_size, color_palette, block_styles, big_block_size)
        print(f"Added a big block with multiplier {big_block_size}")
    
    # Save SVG
    dwg.save()
    print(f"SVG saved to {args.output}")

if __name__ == "__main__":
    main()
