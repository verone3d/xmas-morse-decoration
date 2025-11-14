from solid import *
from solid.utils import *
from textutils import scad_text

# Helper to create ball, star, bell or custom SVG (future) base
def base_shape(shape, size, thickness):
    if shape == "ball":
        return cylinder(d=size, h=thickness, center=False)
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
        angle = math.pi / num_points * i - math.pi/2
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
    # All primitives start at z = 0, base at z=0, everything else "stacked" upwards

    # Base shape (disc/whatever), bottom at z=0
    scad_objs.append(base_shape(shape, size, thickness))

    # Optional filament color split: add 0.2mm disc above base, for filament change
    z_base = thickness
    if color_split:
        scad_objs.append(translate([0, 0, thickness])(base_shape(shape, size, 0.2)))
        z_base += 0.2

    # Name text: centered horizontally, raised exactly above base ("face" of ornament: z=z_base)
    # Conservative size so it fits (0.33 of diameter)
    text_size = size * 0.33
    text_y = size * 0.09  # Slightly above center-mass, to allow Morse below
    scad_objs.append(
        translate([0, text_y, z_base])(
            scad_text(name, size=text_size, height=text_height)
        )
    )

    # Morse code: build elements in a row below text (below center), raised same as text
    morse_y = text_y - text_size * 0.55 - morse_dot_size * 0.5
    x_cursor = 0
    dot_r = morse_dot_size / 2
    dash_len = morse_dash_length
    dash_ht = morse_dot_size
    spacing = morse_dot_size * 1.7

    el_lengths = [(dash_len if c == "-" else morse_dot_size) for c in morse if c in ".-"]
    total_len = sum(el_lengths) + spacing * (len(el_lengths) - 1)
    x_start = -total_len / 2

    morse_objs = []
    for c in morse:
        if c == ".":
            morse_objs.append(
                translate([x_start + x_cursor + dot_r, morse_y, z_base])(
                    cylinder(d=morse_dot_size, h=morse_height)
                )
            )
            x_cursor += morse_dot_size + spacing
        elif c == "-":
            morse_objs.append(
                translate([x_start + x_cursor + dash_len / 2, morse_y, z_base])(
                    cube([dash_len, dash_ht, morse_height], center=True)
                )
            )
            x_cursor += dash_len + spacing
        elif c == " ":
            x_cursor += spacing * 1.5  # Bigger space between words
    scad_objs += morse_objs

    # Add top loop for string: at topmost position, centered, flush with top edge
    if add_loop:
        loop_center_y = size / 2 + 4  # 4mm above ornament edge
        loop_z = z_base / 2
        loop = translate([0, loop_center_y, loop_z])(
            cylinder(d=8, h=z_base)
        )
        hole = translate([0, loop_center_y, loop_z])(
            cylinder(d=4, h=z_base + 0.01)
        )
        scad_objs.append(loop - hole)

    return union()(scad_objs)
