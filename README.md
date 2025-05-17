# SVG_ArtGrid
![example](https://raw.githubusercontent.com/MushroomFleet/SVG_ArtGrid/refs/heads/main/images/art_grid.png?raw=true)

A Python CLI tool for generating artistic SVG grids inspired by modernist design patterns. This tool creates beautiful, generative art pieces featuring various geometric designs arranged in a grid pattern, with a cohesive color palette.

## Features

- Generates a grid of squares, each with a different design pattern
- Uses color palettes from a collection of popular design palettes
- Creates a subtle background gradient that complements the design
- Optionally adds a larger focal block for visual interest
- Fully customizable via command line arguments
- Reproducible designs with seed support
- Support for generating grids based on input images

## Installation

### Quick Installation (Windows)

1. Clone this repository or download the files
2. Run the installation batch file:
```
SVG_ArtGrid\install-artgrid-env.bat
```
This will:
- Create a Python virtual environment named "artgrid-env" in the SVG_ArtGrid directory
- Install all required dependencies with compatible versions
- Provide instructions for activating the environment

### Manual Installation

1. Clone this repository or download the files
2. Navigate to the SVG_ArtGrid directory and create a virtual environment:
```
cd SVG_ArtGrid
python -m venv artgrid-env
```
3. Activate the virtual environment:
   - Windows: `artgrid-env\Scripts\activate`
   - Linux/Mac: `source artgrid-env/bin/activate`
4. Install required dependencies:
```
pip install -r requirements.txt
```

### Linux/Mac Installation

1. Clone this repository or download the files
2. Navigate to the SVG_ArtGrid directory and create a virtual environment:
```
cd SVG_ArtGrid
python -m venv artgrid-env
```
3. Activate the virtual environment:
```
source artgrid-env/bin/activate
```
4. Install required dependencies:
```
pip install -r requirements.txt
```

## Usage

Before running the script, ensure you have activated the virtual environment:

- Windows: `SVG_ArtGrid\artgrid-env\Scripts\activate`
- Linux/Mac: `source SVG_ArtGrid/artgrid-env/bin/activate`

Basic usage:
```
python SVG_ArtGrid\SVG_ArtGrid.py
```

Or for the enhanced version (V2) with image input support:
```
python SVG_ArtGrid\SVGArtGridV2.py
```

This will generate a randomized art grid and save it as `art_grid.svg` in the current directory.

### Command Line Options (SVGArtGridV2.py)

```
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
```

### Examples

Generate a 6×6 grid:
```
python SVG_ArtGrid\SVGArtGridV2.py --rows 6 --cols 6
```

Use a specific seed for reproducibility:
```
python SVG_ArtGrid\SVGArtGridV2.py --seed 42
```

Use only specific block styles:
```
python SVG_ArtGrid\SVGArtGridV2.py --block-styles circle,cross,letter_block
```

Generate art based on an image (palette mode):
```
python SVG_ArtGrid\SVGArtGridV2.py --image your_image.png --mode palette
```

Generate art based on an image (composition mode):
```
python SVG_ArtGrid\SVGArtGridV2.py --image your_image.png --mode composition
```

Disable the big block:
```
python SVG_ArtGrid\SVGArtGridV2.py --no-big-block
```

Custom output file:
```
python SVG_ArtGrid\SVGArtGridV2.py --output my_masterpiece.svg
```

Use a custom color palette file:
```
python SVG_ArtGrid\SVGArtGridV2.py --palette-file my_palettes.json
```

## Supported Block Styles

The tool includes several block styles:

- `circle` - A circle centered in the square
- `opposite_circles` - Two circles positioned in opposite corners
- `cross` - A plus (+) or times (×) symbol
- `half_square` - Half of the square filled in a random direction
- `diagonal_square` - A triangle filling half the square diagonally
- `quarter_circle` - A quarter circle in one of the corners
- `dots` - A grid of dots (2×2, 3×3, or 4×4)
- `letter_block` - A random letter or symbol

## Custom Color Palettes

You can create your own color palette JSON file. The format should be an array of arrays, where each inner array contains 5 hex color codes:

```json
[
  ["#69d2e7","#a7dbd8","#e0e4cc","#f38630","#fa6900"],
  ["#fe4365","#fc9d9a","#f9cdad","#c8c8a9","#83af9b"],
  ...
]
```

## Troubleshooting

### Dependency Issues

If you encounter errors related to NumPy, SciPy, or scikit-learn compatibility issues (such as `RuntimeError: module compiled against API version 0xf but this version of numpy is 0xe`), use the virtual environment installation method described above.

The virtual environment approach ensures all packages are installed with compatible versions, avoiding conflicts between NumPy, SciPy, and scikit-learn.

## Credits

This tool was inspired by an [article](https://frontend.horse/articles/generative-grids/) on generative art techniques and modernist design principles written in javascript from 2022.

## License

MIT
