import argparse
from shapes import create_shape_with_text_and_morse
from morse import text_to_morse
from solid import scad_render_to_file

def parse_args():
    parser = argparse.ArgumentParser(description="Generate a 3D printable Christmas ornament with a name and its Morse code.")
    parser.add_argument("--shape", choices=["ball", "star", "bell"], required=True, help="Shape of the ornament.")
    parser.add_argument("--name", required=True, help="Name to place on ornament.")
    parser.add_argument("--size", type=float, default=80.0, help="Ornament diameter/width in mm (default: 80mm).")
    parser.add_argument("--thickness", type=float, default=2.0, help="Base thickness in mm (default: 2mm).")
    parser.add_argument("--text_height", type=float, default=1.5, help="Raised text height in mm (default: 1.5mm).")
    parser.add_argument("--morse_height", type=float, default=1.5, help="Raised Morse code height in mm (default: 1.5mm).")
    parser.add_argument("--morse_dot_size", type=float, default=2.5, help="Diameter of Morse dots in mm (default: 2.5mm).")
    parser.add_argument("--morse_dash_length", type=float, default=7.0, help="Length of Morse dashes in mm (default: 7mm).")
    parser.add_argument("--color_split", action="store_true", help="Include a thin separation layer under text/Morse for multicolor prints.")
    parser.add_argument("--add_loop", action="store_true", default=True, help="Add top attachment loop.")
    parser.add_argument("--output", default="ornament.stl", help="Output filename, default 'ornament.stl'.")
    return parser.parse_args()

def main():
    args = parse_args()
    morse = text_to_morse(args.name)
    print(f"Generating {args.shape} ornament with name '{args.name}' and Morse '{morse}'...")
    model = create_shape_with_text_and_morse(
        shape=args.shape,
        name=args.name,
        morse=morse,
        size=args.size,
        thickness=args.thickness,
        text_height=args.text_height,
        morse_height=args.morse_height,
        morse_dot_size=args.morse_dot_size,
        morse_dash_length=args.morse_dash_length,
        color_split=args.color_split,
        add_loop=args.add_loop
    )
    scad_filename = args.output.replace('.stl', '.scad')
    scad_render_to_file(model, scad_filename)
    print(f"Saved SCAD file as {scad_filename}")
    print("Open this file in OpenSCAD and export as STL after rendering.")

if __name__ == "__main__":
    main()