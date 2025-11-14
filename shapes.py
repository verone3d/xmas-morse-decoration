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
    import math
    scad_objs = []

    # Base ornament
    scad_objs.append(base_shape(shape, size, thickness))
    z_base = thickness
    if color_split:
        scad_objs.append(translate([0, 0, z_base])(base_shape(shape, size, 0.2)))
        z_base += 0.2

    # For ball shape, calculate safe area considering circular boundary
    # Keep content within a safe inscribed area to ensure visibility
    radius = size / 2
    safe_margin = size * 0.12  # 12% margin from edge
    safe_radius = radius - safe_margin
    
    # Maximum safe dimensions for content (using inscribed rectangle in circle)
    # For a circle, the inscribed rectangle has max area when it's a square
    # But we want max width and some height, so use ~65% of diameter for width
    max_content_width = size * 0.60  # Conservative to ensure nothing touches edges
    
    # Reserve space for loop at top if present
    loop_reserve = size * 0.15 if add_loop else 0
    max_content_height = size * 0.60 - loop_reserve  # Safe vertical space
    
    # TEXT: Calculate initial text size to fit width
    # Empirical: OpenSCAD's text is roughly 0.6 * len(text) * fontsize wide
    text_size_from_width = max_content_width / max(len(name), 1) / 0.6
    text_size = min(text_size_from_width, size * 0.18)  # Cap at 18% of ball size
    
    # MORSE: Calculate Morse dimensions
    num_morse = sum(1 for c in morse if c in ".-")
    num_spaces = morse.count(" ")
    dash_len = morse_dash_length
    dot_d = morse_dot_size
    
    # Calculate total Morse width, accounting for word spacing
    morse_unit_widths = [(dash_len if c == "-" else dot_d) for c in morse if c in ".-"]
    spacing = dot_d * 1.4
    num_normal_gaps = num_morse - 1 - num_spaces
    morse_total_len = sum(morse_unit_widths) + spacing * num_normal_gaps + spacing * 3 * num_spaces
    
    # Scale down Morse if too wide
    if morse_total_len > max_content_width:
        scale_factor = max_content_width / morse_total_len
        dot_d *= scale_factor
        dash_len *= scale_factor
        spacing = dot_d * 1.4  # Recalculate spacing based on new dot_d
        morse_total_len = max_content_width
    
    # Calculate total stack height (text + gap + morse)
    vertical_gap = text_size * 0.3  # Gap between text and Morse
    morse_visual_height = dot_d  # Visual height of Morse line
    total_stack_height = text_size + vertical_gap + morse_visual_height
    
    # Scale down the entire stack if it exceeds available height
    if total_stack_height > max_content_height:
        scale_factor = max_content_height / total_stack_height
        text_size *= scale_factor
        vertical_gap *= scale_factor
        morse_visual_height *= scale_factor
        dot_d *= scale_factor
        dash_len *= scale_factor
        spacing = dot_d * 1.4  # Recalculate spacing based on new dot_d
        # Recalculate morse width with scaled dimensions
        morse_unit_widths = [(dash_len if c == "-" else dot_d) for c in morse if c in ".-"]
        morse_total_len = sum(morse_unit_widths) + spacing * num_normal_gaps + spacing * 3 * num_spaces
        total_stack_height = max_content_height
    
    # Vertically center the text + Morse stack within safe area
    # Account for loop reserve at top
    available_center_y = -(loop_reserve / 2)  # Offset center down by half the loop reserve
    stack_top_y = available_center_y + total_stack_height / 2
    
    # Position text at top of stack
    text_center_y = stack_top_y - text_size / 2
    scad_objs.append(
        translate([0, text_center_y, z_base])(
            scad_text(name, size=text_size, height=text_height)
        )
    )
    
    # Position Morse below text
    morse_center_y = text_center_y - text_size / 2 - vertical_gap - morse_visual_height / 2
    
    # For circular ball, calculate available width at morse_center_y position
    # Using circle equation: x^2 + y^2 = r^2, so max_x = sqrt(r^2 - y^2)
    available_width_at_morse_y = 2 * math.sqrt(max(0, safe_radius**2 - morse_center_y**2))
    
    # If morse is too wide for its Y position, scale it down further
    # Need to account for element sizes: the total span includes center positions + half-elements on each end
    # Total span = morse_total_len (center to center) + dash_len/2 (half of largest element on each side)
    max_morse_element_width = max(dash_len, dot_d)
    total_morse_span = morse_total_len + max_morse_element_width
    
    if total_morse_span > available_width_at_morse_y:
        scale_factor = available_width_at_morse_y / total_morse_span
        dot_d *= scale_factor
        dash_len *= scale_factor
        spacing = dot_d * 1.4  # Recalculate spacing based on new dot_d
        morse_total_len *= scale_factor
    
    # Build Morse code elements
    dot_r = dot_d / 2
    dash_ht = dot_d
    
    # Calculate total width more accurately, accounting for spaces
    el_lengths = [(dash_len if c == "-" else dot_d) for c in morse if c in ".-"]
    num_spaces = morse.count(" ")
    num_normal_gaps = len(el_lengths) - 1 - num_spaces
    total_len = sum(el_lengths) + spacing * num_normal_gaps + spacing * 3 * num_spaces
    x_start = -total_len / 2
    x_cursor = 0
    
    morse_objs = []
    for c in morse:
        if c == ".":
            morse_objs.append(
                translate([x_start + x_cursor + dot_r, morse_center_y, z_base])(
                    cylinder(d=dot_d, h=morse_height)
                )
            )
            x_cursor += dot_d + spacing
        elif c == "-":
            morse_objs.append(
                translate([x_start + x_cursor + dash_len / 2, morse_center_y, z_base])(
                    cube([dash_len, dash_ht, morse_height], center=True)
                )
            )
            x_cursor += dash_len + spacing
        elif c == " ":
            x_cursor += spacing * 2  # Bigger space between words (total 3x spacing)
    
    scad_objs += morse_objs
    
    # Add top loop - position it outside and flush with top of ornament
    if add_loop:
        loop_outer_r = 4  # Inner hole radius
        loop_thickness = 2  # Wall thickness of loop
        loop_d = (loop_outer_r + loop_thickness) * 2  # Outer diameter
        loop_z = z_base / 2  # Center the loop vertically on ornament thickness
        
        # Position loop so its bottom is flush with top edge of ball at y=radius
        # The loop extends upward from there
        loop_center_y = radius + loop_outer_r
        
        scad_objs.append(
            difference()(
                translate([0, loop_center_y, loop_z])(
                    cylinder(d=loop_d, h=z_base)
                ),
                translate([0, loop_center_y, loop_z - 0.05])(
                    cylinder(d=loop_outer_r * 2, h=z_base + 0.1)
                )
            )
        )
    
    return union()(scad_objs)