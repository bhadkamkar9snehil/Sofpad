"""Render the Sofpad R3 case from STLs exported by Sofpad_R3_Alice.scad.

Usage: blender -b --python render_case.py   (STLs expected in ./build)
Writes render_*.png next to this script. Millimetres.
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
OUT = HERE.parent.parent / "docs" / "images"


def mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


M = {
    "shell": mat("shell", (.075, .078, .085), .55, .1),
    "bottom": mat("bottom", (.16, .17, .19), .6),
    "retainer": mat("retainer", (.2, .21, .23), .6),
    "keys": mat("keys", (.62, .60, .55), .7),
    "pcbs": mat("pcbs", (.05, .32, .24), .5),
    "knobs": mat("knobs", (.3, .31, .33), .35, .8),
    "battery": mat("battery", (.19, .39, .54), .7),
    "carrier": mat("carrier", (.04, .28, .2), .5),
    "padface": mat("padface", (.01, .015, .02), .12, .1),
}


def load(name):
    p = str(BUILD / f"{name}.stl")
    try:
        bpy.ops.wm.stl_import(filepath=p)
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=p)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(M[name])
    return o


def look(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def setup(parts):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for p in parts:
        load(p)
    w = bpy.context.scene.world
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (.75, .78, .8, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = .7
    bpy.ops.mesh.primitive_plane_add(size=1200, location=(0, 60, -3))
    bpy.context.object.data.materials.append(mat("floor", (.72, .72, .7), .8))
    for loc, power in [((-200, -250, 450), 30000), ((350, -100, 400), 18000), ((0, 300, 350), 12000)]:
        bpy.ops.object.light_add(type="AREA", location=loc)
        l = bpy.context.object
        l.data.energy, l.data.size = power, 350
        look(l, (0, 60, 0))
    bpy.ops.object.camera_add()
    return bpy.context.object


def shot(cam, name, loc, target, scale, w=1800, h=1000):
    cam.location = loc
    look(cam, target)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = scale
    s = bpy.context.scene
    s.camera = cam
    s.render.engine = "CYCLES"
    s.cycles.samples = 24
    s.render.resolution_x, s.render.resolution_y = w, h
    s.render.filepath = str(OUT / name)
    bpy.ops.render.render(write_still=True)
    print("RENDERED", name, flush=True)


cam = setup(["shell", "bottom", "keys", "knobs", "padface"])
shot(cam, "sofpad-r3-hero.png", (-300, -420, 420), (0, 60, 0), 520)
shot(cam, "sofpad-r3-top.png", (0, 60, 700), (0, 60, 0), 470)
# internals: remove shell and keys to show PCBs, battery, carrier on the plate
cam = setup(["bottom", "pcbs", "battery", "carrier", "retainer"])
shot(cam, "sofpad-r3-internals.png", (0, 60, 700), (0, 60, 0), 470)
cam = setup(["shell", "bottom"])
shot(cam, "sofpad-r3-rear.png", (30, 520, 120), (30, 100, 8), 300)
