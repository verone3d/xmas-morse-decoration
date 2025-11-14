from solid import *
from solid.utils import *
from textutils import scad_text

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

    # Base ornament
    scad_objs.append(base_shape(shape, size, thickness))
    z_base = thickness
    if color_split:
        scad_objs.append(translate([0, 0, z_base])(base_shape(shape, size, 0.2)))
        z_base += 0.2

    safe_edge = size * 0.09  # Keep text/Morse this far from the edge
    max_text_width = size * 0.70  # 70% of ball width max
    max_morse_width = size * 0.80

    # TEXT: auto-scale text size to fit width (crude, but practical)
    # Empirical: OpenSCAD's text string is about 0.6 * len(text) * fontsize wide for most fonts.
    text_size_guess = max_text_width / max(len(name), 1) / 0.6
    text_size = min(text_size_guess, size * 0.24)  # never exceed 24% of ball size as font height

    text_y = size / 2 - safe_edge - text_size/2  # Place lower than the top by safe_edge
    scad_objs.append(
        translate([0, text_y-size/2, z_base])(
            scad_text(name, size=text_size, height=text_height)
        )
    )

    # MORSE: scale so full string fits, is below text but inside the ball.
    num_morse = sum(1 for c in morse if c in ".-")
    dash_len = morse_dash_length
    dot_d = morse_dot_size
    spacing = dot_d * 1.4

    # Calculate total Morse width, scale so it fits
    morse_unit_widths = [(dash_len if c == "-" else dot_d) for c in morse if c in ".-"]
    morse_total_len = sum(morse_unit_widths) + spacing * (num_morse - 1 if num_morse > 0 else 0)

    # If Morse line too long, reduce dash/dot size
    if morse_total_len > max_morse_width:
        scale_factor = max_morse_width / morse_total_len
        dot_d *= scale_factor
        dash_len *= scale_factor
        spacing *= scale_factor
        morse_total_len = sum([(dash_len if c == "-" else dot_d) for c in morse if c in ".-"]) + spacing * (num_morse - 1 if num_morse > 0 else 0)

    morse_y = text_y - text_size / 2 - dot_d / 1.4  # Place Morse snugly below text
    x_cursor = 0
    dot_r = dot_d / 2
    dash_ht = dot_d

    el_lengths = [(dash_len if c == "-" else dot_d) for c in morse if c in ".-"]
    total_len = sum(el_lengths) + spacing * (len(el_lengths) - 1)
    x_start = -total_len / 2

    morse_objs = []
    for c in morse:
        if c == ".":
            morse_objs.append(
                translate([x_start + x_cursor + dot_r, morse_y-size/2, z_base])(
                    cylinder(d=dot_d, h=morse_height)
                )
            )
            x_cursor += dot_d + spacing
        elif c == "-":
            morse_objs.append(
                translate([x_start + x_cursor + dash_len / 2, morse_y-size/2, z_base])(
                    cube([dash_len, dash_ht, morse_height], center=True)
                )
            )
            x_cursor += dash_len + spacing
        elif c == " ":
            x_cursor += spacing * 2  # Bigger space between words

    scad_objs += morse_objs

    # Add top loop (ensure connection: bottom of loop at y=size/2, top edge of ball)
    if add_loop:
        loop_r = 4
        loop_d = 8
        loop_z = z_base / 2  # Match ornament height
        # Move it so bottom sits flush at y=size/2
        scad_objs.append(
            translate([0, size/2 - loop_r, loop_z])(
                cylinder(d=loop_d, h=z_base)
            )
            - translate([0, size/2 - loop_r, loop_z])(
                cylinder(d=loop_r, h=z_base + 0.1)
            )
        )

    return union()(scad_objs)