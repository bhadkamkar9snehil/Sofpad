"""True-to-scale render of the whole Sofpad R3: shell, keys, screen, trackpad, PCBs, battery, cables.

Everything comes from the same CAD numbers as Sofpad_R3_Alice.scad (STLs in ./build) plus the routed
carrier board exported from KiCad (build/carrier.glb, optional). Run:
  blender -b --python render_full.py
Writes docs/images/sofpad-r3-*.png. Millimetres, world frame = the SCAD frame (x right, y rear, z up).
"""
import math
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
OUT = HERE.parent.parent / "docs" / "images"

# ---- numbers shared with Sofpad_R3_Alice.scad ----
ANG, G = 12.0, 92.0
BOARD_H = 111.85
HY = BOARD_H * math.cos(math.radians(ANG))
Y_REAR = HY + 8 + 11
CAR_W, CAR_L, CAR_Z, CAR_T = 62.0, 28.0, 3.0, 1.0
CAR_Y = Y_REAR - 3.2 - 1.2 - CAR_L / 2
ADP_X, ADP_Y, ADP_L = 17.75, 94.7, 40.0
PCB_TOP = 10.6
UNDER_TOP = PCB_TOP + 5.0
TOP_Z = UNDER_TOP + 1.5
SCR_CY, SCR_T = 88.0, 4.0
PAD_CY = 26.0


def right_frame(x, y):
    a = math.radians(ANG)
    return (G / 2 + x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


def half_world(side, x, y):
    wx, wy = right_frame(x, y)
    return (-wx if side == "left" else wx, wy)


def mat(name, color, rough=0.5, metal=0.0, spec=0.5, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = spec
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = 1.0
    return m


M = {
    "shell": mat("shell", (.04, .042, .046), .5, 0.0, .6),
    "bottom": mat("bottom", (.09, .095, .10), .6),
    "retainer_view": mat("retainer", (.12, .125, .13), .6),
    "keys": mat("keys", (.70, .68, .62), .62),
    "switches": mat("switches", (.02, .02, .022), .4),
    "knobs": mat("knobs", (.55, .56, .58), .28, 1.0),
    "pcbs": mat("pcbs", (.02, .20, .11), .35),
    "adapters": mat("adapters", (.05, .22, .12), .35),
    "adapter_conns": mat("adapter_conns", (.86, .83, .74), .5),
    "battery": mat("battery", (.10, .30, .62), .35, .2),
    "carrier": mat("carrier", (.02, .20, .11), .35),
    "padface": mat("padface", (.01, .012, .015), .2),
    "padbody": mat("padbody", (.03, .03, .035), .4),
    "screen": mat("screen", (.01, .01, .012), .3),
}
CREAM = mat("ffc", (.86, .80, .62), .55)
RED = mat("red", (.7, .05, .04), .5)
BLACKW = mat("black wire", (.02, .02, .02), .5)


def load(name, parent_mat=None, alpha=None):
    p = BUILD / f"{name}.stl"
    if not p.exists():
        return None
    try:
        bpy.ops.wm.stl_import(filepath=str(p))
    except AttributeError:
        bpy.ops.import_mesh.stl(filepath=str(p))
    o = bpy.context.object
    o.name = name
    o.data.materials.append(parent_mat or M[name])
    return o


def look(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def ribbon(name, pts, width, thick, material):
    """Flat cable along a Bezier through pts (list of xyz)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = Vector(p)
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    prof = bpy.data.curves.new(name + "_prof", "CURVE")
    prof.dimensions = "2D"
    ps = prof.splines.new("POLY")
    ps.points.add(3)
    for pt, (x, y) in zip(ps.points, [(-width / 2, -thick / 2), (width / 2, -thick / 2), (width / 2, thick / 2), (-width / 2, thick / 2)]):
        pt.co = (x, y, 0, 1)
    ps.use_cyclic_u = True
    po = bpy.data.objects.new(name + "_prof", prof)
    bpy.context.collection.objects.link(po)
    po.hide_render = True
    cu.bevel_mode = "OBJECT"
    cu.bevel_object = po
    cu.resolution_u = 24
    o = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    return o


def tube(name, pts, radius, material):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = Vector(p)
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    cu.bevel_depth = radius
    cu.resolution_u = 16
    o = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    return o


def build_scene(ghost=False, show=("shell", "keys")):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for n in ("bottom", "retainer_view", "battery", "switches", "knobs", "pcbs", "adapters", "adapter_conns", "padbody"):
        load(n)
    for n in show:
        o = load(n)
        if n == "shell" and o and ghost:
            nt = M["shell"].node_tree
            out = nt.nodes["Material Output"]
            bsdf = nt.nodes["Principled BSDF"]
            tr = nt.nodes.new("ShaderNodeBsdfTransparent")
            mix = nt.nodes.new("ShaderNodeMixShader")
            mix.inputs[0].default_value = 0.88
            nt.links.new(tr.outputs[0], mix.inputs[1])
            nt.links.new(bsdf.outputs[0], mix.inputs[2])
            nt.links.new(mix.outputs[0], out.inputs["Surface"])
    # screen module, glass with the UI picture
    load("screen")
    ui = BUILD / "screen_ui.png"
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, SCR_CY + 2, TOP_Z - 0.25))
    g = bpy.context.object
    g.scale = (30.6, 40.8, 1)
    gm = bpy.data.materials.new("screen glass")
    gm.use_nodes = True
    b = gm.node_tree.nodes["Principled BSDF"]
    if ui.exists():
        tex = gm.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(str(ui))
        gm.node_tree.links.new(tex.outputs[0], b.inputs["Base Color"])
        gm.node_tree.links.new(tex.outputs[0], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = 1.2
    b.inputs["Roughness"].default_value = 0.08
    g.data.materials.append(gm)
    # carrier PCB (routed KiCad board) or an envelope
    glb = BUILD / "carrier.glb"
    if glb.exists():
        bpy.ops.import_scene.gltf(filepath=str(glb))
        objs = [o for o in bpy.context.selected_objects]
        place_carrier(objs)
    else:
        load("carrier")
    # cables
    mats = {"red": RED, "black": BLACKW}
    for side in ("left", "right"):
        cx, cy = half_world(side, ADP_X, ADP_Y + ADP_L / 2 - 4.3)
        dx, dy = half_world(side, 0, 1)
        dx, dy = (dx - (-G / 2 if side == "left" else G / 2)), dy  # direction only
        a = math.radians(ANG)
        d = (math.sin(-a) * (1 if side == "right" else -1) * -1, math.cos(a))
        start = (cx + d[0] * 4.2, cy + d[1] * 4.2, PCB_TOP + 0.5 + 1.0 + 1.0)
        sx = -1 if side == "left" else 1
        end = (sx * (CAR_W / 2 - 4.4 + 4.6) - 0 + 0, CAR_Y, CAR_Z + CAR_T + 1.0)
        end = (sx * 31.0, CAR_Y, CAR_Z + CAR_T + 1.0)
        ribbon(f"ffc_{side}", [end, (sx * 34.0, CAR_Y + 4, 7.5), (start[0] * 0.97, start[1] - 3, 12.5), start], 8.5, 0.3, CREAM)
    # battery leads to J2 (front-right of the carrier)
    j2 = (39.5 - 31.0, CAR_Y + (14 - 23.4), CAR_Z + CAR_T + 2.0)
    tube("bat_red", [(0.5, 59.0 + 36, 7.0), (4.0, 98.0, 8.0), j2], 0.45, RED)
    tube("bat_black", [(-1.0, 59.0 + 36, 7.0), (2.5, 98.5, 7.6), (j2[0] + 1.2, j2[1], j2[2])], 0.45, BLACKW)
    # trackpad flex and cable: from the pad rear edge to the carrier front
    ribbon("pad_flex", [(0, PAD_CY + 24.5, TOP_Z - 2.5), (-4, PAD_CY + 34, 9.0), (6, 60.0, 8.0), (19.5, CAR_Y + (14 - 24.0), 6.0)], 6.0, 0.15, CREAM)
    # screen cable (8 colours)
    cols = [(.8, .1, .1), (.05, .05, .05), (.9, .9, .1), (.1, .6, .2), (.9, .45, .1), (.15, .3, .85), (.6, .2, .7), (.9, .9, .9)]
    for i, c in enumerate(cols):
        off = (i - 3.5) * 0.9
        tube(f"scr_wire{i}", [(off - 4, CAR_Y + (14 - 23.6), CAR_Z + CAR_T + 2.0), (off - 3, 98.0, 9.5), (off, SCR_CY - 22, 10.8)], 0.3, mat(f"w{i}", c, .5))
    # studio
    w = bpy.context.scene.world
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (.80, .82, .84, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = .8
    bpy.ops.mesh.primitive_plane_add(size=1400, location=(0, 70, -3))
    bpy.context.object.data.materials.append(mat("floor", (.55, .54, .52), .75))
    for loc, power in [((-250, -300, 520), 36000), ((380, -120, 420), 22000), ((0, 330, 380), 14000)]:
        bpy.ops.object.light_add(type="AREA", location=loc)
        l = bpy.context.object
        l.data.energy, l.data.size = power, 380
        look(l, (0, 70, 0))
    bpy.ops.object.camera_add()
    return bpy.context.object


def place_carrier(objs):
    """Put the KiCad GLB where the CAD carrier is: board centre at (0, CAR_Y), underside at CAR_Z."""
    root = bpy.data.objects.new("carrier_root", None)
    bpy.context.collection.objects.link(root)
    for o in objs:
        if o.parent is None:
            o.parent = root
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    if not pts:
        return
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    ext = mx - mn
    # glTF is y-up: the board plane is x/z. Rotate so the board lies in x/y with top side up.
    root.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    scale = CAR_W / max(mx.x - mn.x, mx.y - mn.y)
    root.scale = (scale, scale, scale)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs if o.type == "MESH" for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    root.location += Vector((-(mn.x + mx.x) / 2, CAR_Y - (mn.y + mx.y) / 2, CAR_Z - CAR_T / 2 * 0 - mn.z))


def shot(cam, name, loc, target, scale, w=2000, h=1100, persp=False, lens=60, samples=36):
    cam.location = loc
    look(cam, target)
    if persp:
        cam.data.type = "PERSP"
        cam.data.lens = lens
    else:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = scale
    s = bpy.context.scene
    s.camera = cam
    s.render.engine = "CYCLES"
    s.cycles.samples = samples
    s.render.resolution_x, s.render.resolution_y = w, h
    s.render.filepath = str(OUT / name)
    bpy.ops.render.render(write_still=True)
    print("RENDERED", name, flush=True)


if __name__ == "__main__":
    cam = build_scene(ghost=False)
    shot(cam, "sofpad-r3-hero.png", (-330, -400, 330), (0, 62, 8), 0, persp=True, lens=48)
    shot(cam, "sofpad-r3-top.png", (0, 62, 760), (0, 62, 0), 430)
    cam = build_scene(show=())
    shot(cam, "sofpad-r3-internals.png", (0, 62, 760), (0, 62, 0), 430)
    shot(cam, "sofpad-r3-internals-3q.png", (-260, -300, 380), (0, 80, 8), 0, persp=True, lens=52)
    shot(cam, "sofpad-r3-bay.png", (0, 62, 330), (0, 104, 6), 0, persp=True, lens=70)
