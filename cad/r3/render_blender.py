"""Render the one-controller Sofle RGB and Cirque 40-mm case with Blender 4.x.

Usage: blender -b --python render_blender.py
All dimensions are millimetres. Keycap volumes are illustrative.
"""
import bpy
import json
import math
import sys
from mathutils import Vector
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "layout_components.json").read_text())

BOARD_W = 143.4952
BOARD_H = 111.85
GAP = 17
SIDE = 10
END = 12
PAD_ZONE = 66
W = 2 * BOARD_W + GAP + PAD_ZONE + 2 * SIDE
H = BOARD_H + 2 * END
TOP = 17.5
RIGHT_X = SIDE + BOARD_W + GAP
PAD_X = RIGHT_X + BOARD_W + PAD_ZONE / 2
PAD_Y = H / 2 + 8
USB_X = PAD_X - 5
POWER_X = W - 16


def mat(name, color, roughness=0.45, metal=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metal
    return m


GRAPHITE = mat("Satin graphite aluminium-look polymer", (.095, .11, .14), .57, .24)
LOWER = mat("Satin graphite removable service cover", (.19, .22, .25), .62, .18)
KEY_IVORY = mat("Warm PBT ivory", (.76, .78, .74), .68)
KEY_DARK = mat("Muted accent keys", (.18, .23, .26), .62)
BLACK = mat("Trackpad black glass", (.018, .027, .040), .13, .12)
GUNMETAL = mat("Rotary knob", (.23, .25, .27), .42, .7)
EDGE = mat("Brushed port housing", (.29, .33, .37), .5, .65)
PLASTIC = mat("Dark USB port", (.008, .011, .015), .7)
BLUE = mat("Protected single LiPo, schematic", (.19, .39, .54), .7)
FOAM = mat("Mounting foam", (.27, .28, .30), .85)
GROUND = mat("Warm studio background", (.73, .76, .76), .77)


def add_bevel(obj, width=.45, segments=3):
    bevel = obj.modifiers.new("Soft machined edge", "BEVEL")
    bevel.width = width
    bevel.segments = segments
    if hasattr(bevel, "affect"):
        bevel.affect = "EDGES"
    obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")


def cube(name, location, size, material, bevel=0, angle=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if angle:
        o.rotation_euler.z = math.radians(angle)
    o.data.materials.append(material)
    if bevel:
        add_bevel(o, bevel)
    return o


def cylinder(name, location, radius, depth, material, bevel=.35):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius, depth=depth, location=location)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    if bevel:
        add_bevel(o, bevel)
    return o


def load_mesh(filename, name, material, z=0):
    filepath = str(HERE / filename)
    try:
        bpy.ops.wm.stl_import(filepath=filepath)
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=filepath)
    obj = bpy.context.object
    obj.name = name
    obj.location.z += z
    obj.data.materials.append(material)
    return obj


def setup_studio():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    world = bpy.context.scene.world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (.78, .82, .84, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = .55
    cube("Studio floor", (W/2, H/2, -5.5), (950, 780, 8), GROUND, 1.2)
    for name, location, power, size in [
        ("Softbox upper left", (30,-150,470), 21000, 390),
        ("Softbox upper right", (470,60,400), 13000, 330),
        ("Rim softbox", (200,270,380), 18000, 300),
    ]:
        bpy.ops.object.light_add(type="AREA", location=location)
        o = bpy.context.object
        o.name = name
        o.data.energy = power
        o.data.shape = "DISK"
        o.data.size = size
        rotate_towards(o, (W/2,H/2,0))


def rotate_towards(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_camera(location, target, scale):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.object
    rotate_towards(cam, target)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = scale
    bpy.context.scene.camera = cam
    return cam


def set_cam(cam, location, target, scale):
    cam.location = location
    rotate_towards(cam, target)
    cam.data.ortho_scale = scale


def render(name, cam, location, target, scale, width, height, samples=18):
    set_cam(cam, location, target, scale)
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(HERE / name)
    scene.cycles.samples = samples
    bpy.ops.render.render(write_still=True)
    print(f"RENDERED: {name}", flush=True)


def keyboard_appearance():
    keys = []
    for side in ("left", "right"):
        for idx, key in enumerate(DATA["keys"]):
            if side == "right":
                x, angle = RIGHT_X + key["x"], key["angle"]
            else:
                x, angle = SIDE + BOARD_W - key["x"], -key["angle"]
            y = END + key["y"]
            accent = idx in (0,5,18,22,23,24,25,26,27,28)
            cap = cube(f"{side} {key['ref']} cap", (x,y,TOP+6.6),
                       (17.45,17.45,7.0), KEY_DARK if accent else KEY_IVORY,
                       bevel=.95, angle=angle)
            keys.append(cap)
        for encoder in DATA["encoders"]:
            x = (RIGHT_X + encoder["x"]) if side == "right" else (SIDE+BOARD_W-encoder["x"])
            y = END + encoder["y"]
            cylinder(f"{side} encoder", (x,y,TOP+7.1), 6.45, 9.0, GUNMETAL, .35)
    # The exact purchased part has a 40-mm round adhesive overlay.
    cylinder("Cirque 40-mm SPI round touch surface", (PAD_X,PAD_Y,TOP-.01),
             19.9,.12,BLACK,.12)
    # This physical insert matches the modelled USB-C port cutout, which is
    # on the rear edge. The case CAD controls the actual manufacturing hole.
    cube("USB-C connector depth", (USB_X,H-2.8,8.8), (9.2,5.8,3.2), PLASTIC, .6)
    cube("USB-C silver rim", (USB_X,H+.04,8.8), (10.1,.34,4.1), EDGE, .65)
    cube("USB-C black aperture", (USB_X,H+.25,8.8), (7.5,.2,2.35), PLASTIC, .65)
    cube("Rear power switch", (POWER_X,H+.4,8.8), (8.4,1.3,2.8), BLACK, .6)
    cube("Rear power switch slider", (POWER_X+1.8,H+1.22,8.8),
         (2.1,.8,2.3), EDGE, .35)
    return keys


def exploded_components():
    retainer = load_mesh("TPS43_Retainer.stl", "Cirque circular four-screw retainer", GRAPHITE)
    retainer.location = (PAD_X,PAD_Y,9.9)
    battery = cube("One protected NOVA 603450 cell, indicative envelope",
                   (PAD_X,25,6.45), (54,38,8),BLUE,1.25)
    # Separate the bottom only, leaving the shell and trackpad in place.
    # Move only the battery and its service panel, to show their locations.
    retainer.hide_render = False
    return retainer,battery


def main():
    setup_studio()
    case = load_mesh("Unibody_Shell.stl", "One-piece upper shell", GRAPHITE)
    bottom = load_mesh("Service_Bottom.stl", "Removable lower cover", LOWER)
    keys = keyboard_appearance()
    cam = add_camera((W*1.20,-H*1.7,280),(W/2,H/2,13),495)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    # The distribution available on the build host omits OpenImageDenoise.
    scene.cycles.use_denoising = False
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"
    scene.camera.data.lens = 50

    if "--service-only" not in sys.argv:
        render("render_hero.png",cam,(W*.90,-H*1.35,285),
               (W/2,H/2,9),485,1650,840)
        render("render_top.png",cam,(W/2,H/2,540),
               (W/2,H/2,8),425,1600,650)
        render("render_rear_ports.png",cam,(W*.94,H+195,72),
               (W*.89,H,10),190,1400,680)

    # Hide decorative keys to reveal how the single battery and trackpad
    # retainer sit in the same shell; an exploded view is not assembly-ready.
    for key in keys:
        key.hide_render = True
    bpy.data.objects["Studio floor"].hide_render = True
    bottom.location = (0,-165,-34)
    retainer,battery = exploded_components()
    battery.location.z -= 16
    bpy.ops.object.light_add(type="AREA", location=(350,-230,-300))
    lamp = bpy.context.object
    lamp.name = "Underside service softbox"
    lamp.data.energy = 25000
    lamp.data.shape = "DISK"
    lamp.data.size = 360
    rotate_towards(lamp, (W/2,H/2,0))
    render("render_service.png",cam,(W*.90,-H*1.50,-265),
           (W/2,H/2-60,-8),600,1650,950)


if __name__ == "__main__":
    main()
