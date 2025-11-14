from solid import text, linear_extrude

def scad_text(txt, size=30, height=1.5):
    # Returns a 3D extruded text object, centered
    # You may tweak font or alignment here
    return linear_extrude(height=height)(text(txt, size=size, halign="center", valign="center"))