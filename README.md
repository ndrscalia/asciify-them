<p align="center">
    <img src="https://raw.githubusercontent.com/ndrscalia/asciify-them/main/cover_photos/banner.png" alt="Cover photo" />
    <br/>
    <img src="https://api.visitorbadge.io/api/VisitorHit?user=ndrscalia&repo=github-visitors-badge&countColor=%237B1E7A" />
    <br/>
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg"
   />
    <img src="https://img.shields.io/github/license/ndrscalia/asciify-them" />
    <img src="https://img.shields.io/github/stars/ndrscalia/asciify-them?style=social" />
    <a href="https://asciify-them.readthedocs.io/en/latest/"><img src="https://img.shields.io/badge/docs-read%20the%20docs-blue" /></a>
  </p>

This package allows you to turn images (only `.jpg` and `.png` tested) into ASCII art drawings.<br/>
Inspired by [ascii-view](https://github.com/gouwsxander/ascii-view/tree/main).
# Documentation
Full documentation is available at:
**[asciify-them.readthedocs.io](https://asciify-them.readthedocs.io/en/latest/)**

# Features
- **CLI**: This software can be accessed both as a Python library and as a CLI;
- **Colored output**: ANSI color codes allow to print colors (requires a modern terminal);
- **Resizing flexibility**: Images are scaled to keep aspect ratio and fit the image to the terminal, but both options can be disabled;
- **Edge detection**: Sobel and Canny algorithm are used to highlight edges;
- **Output flexibility**: Resulting images can be saved in a file (both using the terminal to determine optimal size or providing custom height and/or width);
- **Custom charsets and presets**: You can now use different presets or provide a custom charset (any length is supported).

# Installation
The package can be installed through PyPi:<br/>
```
# using pip
pip install asciify-them

# or using uv
uv tool install asciify-them
```
But also from source:
```
git clone https://github.com/ndrscalia/asciify-them
cd <repo-dir>
python -m venv .venv
source .venv/bin/activate
pip install -e .
```
The software can also be used without installing it through uv:
```
uvx --from asciify-them asciify path/to/image [OPTIONS]
```
# Usage
This package requires a terminal emulator with true color support (e.g. kitty, alacritty, iTerm2).
## CLI
The only required argument is the path to the image:
```
asciify <path/to/image> [OPTIONS]
```
The following options are available:
- `-bw, --black_white`: Set the output to black&white.
- `-e, --edges`: Enable edge detection.
- `-w, --width`: Provide custom width. If not specified, terminal's size is going to determine this value. This value can be specified only when `f_type='wide'`.
- `-he, --height`: Provide custom height. If not specified, terminal's size is going to determine this value. This value can be specified only when `f_type='tall'`.
- `-ar, --no_aspect_ratio`: Disable original aspect ratio's protection.
- `-f, --factor_type`: Choose the downsampling factor type among the following values: `in_terminal`, `wide`, `tall`.
- `-b, --blur`: Provide a list with kernel size as a tuple, std for x axis, std for y axis. For more details refere to the docs for `cv2.GaussianBlur`. Changing the default values allow to tweak edge detection.
- `ct, --canny_threshold`: Provide edges detection threshold as a tuple. For more details refer to the docs for `cv2.Canny`.
- `-at, --angles_threshold`: Provide kernel size for angles calculation as an integer.
- `-o, --output`: Provide the output's path. If not specified, uses stdout (e.g.: terminal).
- `-A, --aspect_ratio_correction`: Provide the value by witch to divide the terminal's detected aspect ratio to account for line spacing.
- `-p, --preset`: Choose one of the installed preset: `classic`, `extended`, `unicode_blocks`, `braille`.
- `-c, --charset`: Provide a custom charset of any length (use quotes to include space as a character).

### Details
The different factors available are meant for different scenarios:
- `in_terminal` allows to keep the output inside the terminal keeping aspect ratio;
- `wide` is better suited for images which are wider than taller but the output does not stay in the terminal. This option is also optimal for conversion to `.png` through [ansee](https://github.com/codersauce/ansee), regardless of the relation between height and width;
- `tall` is better suited for images which are taller than wider but the output does not stay in the terminal;
If aspect ratio's protection is disabled, output will be squished by a factor to stay in the terminal.
## Python library
This package can also be used as a python library. Most of the API is exposed to the user, but a convenient wrapper is also available for simpler use cases.
```python
from asciify import asciify

# Minimal use
result = asciify("path/to/image")
print(result)

# More advanced use
result = asciify(
    "path/to/image",
    color_mode="bw",
    edges_detection=True,
    f_type="tall",
    aspect_ratio_correction=1.10,
    charset=["."]
)

with open("output.txt", "w") as f:
    f.write(result)
```

The `.txt` output can be used with [ansee](https://github.com/codersauce/ansee) to get a `.png` file out of it.<br/>
If needed, the core classes can be used as follows:

```python
from asciify import ImgProcessor, Renderer, DEFAULT_CHARSET

# Configs
IMAGE_PATH = "examples/images/girl.jpg"  # Change this to a real image path
ASPECT_RATIO_CORRECTION = 1.10

# Optional parameters (set to None to use terminal size)
height = None
width = None

# Processing options
# default values
keep_aspect_ratio = True
f_type = "in_terminal"  # Options: "in_terminal", "wide", "tall"
angles_thresh = 3
blur = [(9, 9), 1.5, 1.5]
canny_thresh = (200, 300)
color_mode = "color"  # Options: "color", "bw"
edges_detection = False

# Process the image
processor = ImgProcessor(IMAGE_PATH)

if not height and not width:
    term_height, term_width = processor.calculate_print_size()
else:
    term_height = height if height else 40
    term_width = width if width else 100

ds_f = processor.calculate_downsample_factor(
    term_height=term_height,
    term_width=term_width,
    keep_aspect_ratio=keep_aspect_ratio,
    f_type=f_type,
    aspect_ratio_correction=ASPECT_RATIO_CORRECTION
)

ds_img = processor.downsample_image(
    f=ds_f,
    keep_aspect_ratio=keep_aspect_ratio,
    aspect_ratio_correction=ASPECT_RATIO_CORRECTION
)

img_hsv = processor.convert_to_hsv(image=ds_img)

angles = processor.calculate_angles(
    image=ds_img,
    k_size=angles_thresh
)

edges = processor.detect_edges(
    image=ds_img,
    blur=blur,
    canny_thresh=canny_thresh
)

renderer = Renderer(
    color_mode=color_mode,
    charset=DEFAULT_CHARSET # or any custom charset
)                           # or any preset (see changelog
                            # at the bottom of this doc)
if edges_detection:
    result = renderer.draw_in_ascii_with_edges(img_hsv=img_hsv, angles=angles, edges=edges)
else:
    result = renderer.draw_in_ascii(img_hsv=img_hsv)

print(result)
```
# Examples
The following image compares the original input with the output you can get with the default options (except for `-f`, which was set to `tall`).
<p align="center">
    <img src="https://raw.githubusercontent.com/ndrscalia/asciify-them/main/cover_photos/side_by_side.jpg" alt="Example photo" />
    <br/>
    </p>

This is what you can get using, for example, the Unicode blocks preset:
```bash
# left image
asciify examples/images/girl.jpg --preset unicode_blocks

# right image (you will have to zoom out the terminal)
asciify examples/images/girl.jpg -f tall -p unicode blocks
```
<p align="center">
    <img src="https://raw.githubusercontent.com/ndrscalia/asciify-them/custom-charsets/cover_photos/side_by_side_unicode.jpg" alt="Example photo" />
    <br/>
    </p>

# Testing
To test the codebase check `tests/README.md`.

# Changelog
- 1.1.0
    - Custom charsets of any length can now be provided both in the cli and in the python library.
    - New presets have been added: `CLASSIC_GRADIENT`, `EXTENDED_SMOOTH_GRADIENT`, `BRAILLE_CHARSET`, `UNICODE_BLOCKS`.
- 1.0.4
    - Fix to get char's aspect ratio in the terminal in non-Unix systems.
- 1.0.3
    - Add aspect ratio correction flag to account for line spacing.
- 1.0.2
    - Windows fix to get terminal size even when stdout is not the terminal.
- 1.0.1
    - Improved width factor for better aspect-ratio's protection.
- 1.0.0
    - First working version.

# Future updates and possible contributions
- ~Allow custom charset with different number of characters~;
- Allow tuning brightness for better piping to ansee;
- Improve edges' detection.
