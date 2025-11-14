# Xmas Morse Ornament Generator

Generate a printable 3D Christmas ornament with a name and its Morse code underneath!

## Features
- Choose ornament shape: ball, star, bell (SVG import planned)
- Custom size, thickness, and raised text/Morse height (all CLI options)
- Raised morse dots/dashes for multicolor 3D printing (with optional separation layer)
- Top loop for hanging (customizable)
- CLI interface, modular Python code (expandable to web-GUI in future)

## Usage

### Command Line Example

```bash
python generator.py --shape ball --name Alex --size 80 --thickness 2 --text_height 1.5 --morse_height 1.5 --add_loop --output Alex_ornament.stl
```

All CLI options:
- `--shape` ("ball", "star", "bell")
- `--name` Name to print (Morse code generated automatically)
- `--size` Ornament size (mm)
- `--thickness` Ornament base thickness (mm)
- `--text_height` Height of raised text (mm)
- `--morse_height` Height of raised Morse (mm)
- `--morse_dot_size` Diameter of Morse dots (mm)
- `--morse_dash_length` Length of Morse dashes (mm)
- `--color_split` Add a filament transition wall/pause
- `--add_loop` Add top hanging loop
- `--output` Output STL filename

### Requirements

- Python 3.x
- [`solidpython`](https://github.com/SolidCode/SolidPython)
- (Optional, for visualization) [OpenSCAD](https://openscad.org/)

### Roadmap

- SVG import support for custom shapes
- Parameters for more detailed placement/layout
- Web front-end preview (Flask/FastAPI)