from solid import *
from solid.utils import *
from textutils import scad_text

# Helper to create ball, star, bell or custom SVG (future) base

def base_shape(shape, size, thickness):
    if shape == "ball":
        return cylinder(d=size, h=thickness, center=True)
    elif shape == "star":
        return star_shape(size, thickness)
    elif shape == "bell":
        return bell_shape(size, thickness)
    else:
        raise ValueError("Unknown shape")

def star_shape(size, thickness):
    # Approximate a 5-point star with 2D polygon, then extrude
    import math
    r_outer = size / 2
    r_inner = r_outer * 0.4
    num_points = 5
    verts = []
    for i in range(2 * num_points):
        r = r_outer if i % 2 == 0 else r_inner
        angle = math.pi / num_points * i
        verts.append([r * math.cos(angle), r * math.sin(angle)])
    return linear_extrude(height=thickness)(polygon(verts))

def bell_shape(size, thickness):
    # Simplified bell: wide bottom, arch top, extrude
    h = size * 0.9
    w = size * 0.80
    path = [
        [-w / 2, 0], [w / 2, 0],
        [w / 2, h * 0.7], [0, h], [-w / 2, h * 0.7], [-w / 2, 0]
    ]
    return translate([0, -h / 2, 0])(linear_extrude(height=thickness)(polygon(path)))

def create_shape_with_text_and_morse(
    shape, name, morse, size, thickness, text_height,
    morse_height, morse_dot_size, morse_dash_length,
    color_split, add_loop
):
    scad_objs = []
    # Base shape
    scad_objs.append(base_shape(shape, size, thickness))
    z_base = thickness / 2

    # Optional filament color split: add 0.2mm disc before text/Morse
    if color_split:
        scad_objs.append(translate([0, 0, z_base])(base_shape(shape, size, 0.2)))

    # Name text, centered, raised
    text_obj = up(thickness)(scad_text(name, size=size * 0.4, height=text_height))
    scad_objs.append(text_obj)

    # Morse code as raised dots/dashes, centered below text
    morse_objs = []
    x_cursor = 0
    spacing = morse_dot_size * 2  # Space between elements
    dot_r = morse_dot_size / 2
    dash_len = morse_dash_length
    dash_ht = morse_dot_size
    # Calculate total length to center
    el_lengths = [(dash_len if c == "-" else morse_dot_size) for c in morse if c in ".-"]
    total_len = sum(el_lengths) + spacing * (len(el_lengths) - 1)
    x_start = -total_len / 2

    for c in morse:
        if c == ".":
            morse_objs.append(translate([x_start + x_cursor + dot_r, -size * 0.15, thickness])(cylinder(d=morse_dot_size, h=morse_height)))
            x_cursor += morse_dot_size + spacing
        elif c == "-":
            morse_objs.append(translate([x_start + x_cursor + dash_len / 2, -size * 0.15, thickness])(cube([dash_len, dash_ht, morse_height], center=True)))
            x_cursor += dash_len + spacing
        elif c == " ":
            x_cursor += spacing * 1.1  # Slightly bigger space between 'words'
    scad_objs += morse_objs

    # Add top loop if needed
    if add_loop:
        loop = translate([0, size / 2 + 4, thickness / 2])(cylinder(d=8, h=thickness))
        hole = translate([0, size / 2 + 4, thickness / 2])(cylinder(d=4, h=thickness + 1))
        scad_objs.append(loop - hole)

    # Final union
    return union()(scad_objs)

# --- Placeholder for text rendering (scad_text) for solidpython