# Model sheet renderer.
#
#   blender FILE.blend --background --python tools/modelsheet.py -- OUT NAME [--inspect]
#
# Renders a consistent set of passes per model. The whole point is that every model is
# framed identically regardless of real-world size, so a milk vat and a mobile crane read
# as part of one sheet rather than two unrelated images.
#
# Consistency comes from normalising to the bounding sphere: the camera sits at a fixed
# angle and backs off exactly far enough that the model's bounding sphere fills the same
# fraction of the frame every time. Nothing depends on the scene's own camera, its units,
# or how the model happens to be positioned.

import bpy
import sys
import math
from mathutils import Vector

# ---- args after the -- separator -------------------------------------------------
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
OUT = argv[0] if argv else "."
NAME = argv[1] if len(argv) > 1 else "model"
INSPECT = "--inspect" in argv
SWEEP = "--sweep" in argv          # render clay at 8 angles to choose from

# ---- framing constants, identical for every model --------------------------------
AZIMUTH   = math.radians(48)    # around Z, from +X
ELEVATION = math.radians(22)    # above horizon
FOV       = math.radians(32)    # a longer lens flattens perspective distortion
FILL      = 0.82                # fraction of frame the bounding sphere occupies
RES       = (1600, 1200)

scene = bpy.context.scene


def visible_meshes():
    out = []
    for ob in scene.objects:
        if ob.type != "MESH":
            continue
        if ob.hide_render or not ob.visible_get():
            continue
        # skip anything with no geometry
        if not ob.data or not len(ob.data.vertices):
            continue
        out.append(ob)
    return out


def world_bounds(objs):
    lo = Vector(( 1e18,  1e18,  1e18))
    hi = Vector((-1e18, -1e18, -1e18))
    for ob in objs:
        mw = ob.matrix_world
        for corner in ob.bound_box:
            p = mw @ Vector(corner)
            for i in range(3):
                lo[i] = min(lo[i], p[i])
                hi[i] = max(hi[i], p[i])
    return lo, hi


meshes = visible_meshes()
if not meshes:
    print("MODELSHEET: no visible mesh objects found")
    sys.exit(1)

lo, hi = world_bounds(meshes)
centre = (lo + hi) / 2.0
size = hi - lo
radius = size.length / 2.0

print("MODELSHEET: %d mesh objects" % len(meshes))
print("MODELSHEET: bbox size  %.3f x %.3f x %.3f" % (size.x, size.y, size.z))
print("MODELSHEET: radius     %.3f" % radius)
print("MODELSHEET: objects    " + ", ".join(sorted(o.name for o in meshes)[:25]))

if INSPECT:
    # look before rendering: a file may contain a whole environment rather than one asset
    sys.exit(0)

# ---- camera ----------------------------------------------------------------------
cam_data = bpy.data.cameras.new("sheet_cam")
cam_data.lens_unit = "FOV"
cam_data.angle = FOV
cam = bpy.data.objects.new("sheet_cam", cam_data)
scene.collection.objects.link(cam)

dist = (radius / FILL) / math.sin(FOV / 2.0)
cam.location = centre + Vector((
    math.cos(ELEVATION) * math.cos(AZIMUTH),
    math.cos(ELEVATION) * math.sin(AZIMUTH),
    math.sin(ELEVATION),
)) * dist

direction = (centre - cam.location).normalized()
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
cam_data.clip_start = max(dist * 0.001, 0.01)
cam_data.clip_end = dist * 10.0
scene.camera = cam

# ---- lighting --------------------------------------------------------------------
# The scene's own lights are built for the VR environment, not for a product shot, so
# they are switched off and replaced with a neutral rig. Same rig for every model.
for ob in list(scene.objects):
    if ob.type == "LIGHT":
        ob.hide_render = True

world = bpy.data.worlds.new("sheet_world")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.57, 0.60, 1.0)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
scene.world = world


def add_area(name, offset, energy, sz):
    d = bpy.data.lights.new(name, type="AREA")
    d.energy = energy * (radius ** 2)      # scale with the model so exposure matches
    d.size = sz * radius
    o = bpy.data.objects.new(name, d)
    scene.collection.objects.link(o)
    o.location = centre + Vector(offset) * dist
    o.rotation_euler = (centre - o.location).normalized().to_track_quat("-Z", "Y").to_euler()
    return o


add_area("key",  ( 0.7,  0.5, 0.9), 900, 1.6)   # high three-quarter key
add_area("fill", (-0.9,  0.3, 0.2), 260, 2.4)   # soft opposite fill
add_area("rim",  (-0.3, -1.0, 0.6), 500, 1.2)   # separation from behind

# ---- render settings --------------------------------------------------------------
scene.render.resolution_x, scene.render.resolution_y = RES
scene.render.resolution_percentage = 100
scene.render.film_transparent = True          # PNG with alpha, composite on anything
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "Standard"


def render_to(suffix):
    scene.render.filepath = "%s/%s_%s.png" % (OUT.rstrip("/"), NAME, suffix)
    bpy.ops.render.render(write_still=True)
    print("MODELSHEET: wrote %s_%s.png" % (NAME, suffix))


def set_engine(*names):
    # the EEVEE identifier moved between 4.x and 5.x, so try in order
    for n in names:
        try:
            scene.render.engine = n
            return n
        except TypeError:
            continue
    raise RuntimeError("no usable engine from %s" % (names,))


def shade(**kw):
    # workbench shading attribute names have drifted between versions
    sh = scene.display.shading
    for k, v in kw.items():
        try:
            setattr(sh, k, v)
        except (AttributeError, TypeError) as e:
            print("MODELSHEET: skipped shading.%s (%s)" % (k, e))


def aim(az_deg):
    a = math.radians(az_deg)
    cam.location = centre + Vector((
        math.cos(ELEVATION) * math.cos(a),
        math.cos(ELEVATION) * math.sin(a),
        math.sin(ELEVATION),
    )) * dist
    cam.rotation_euler = (centre - cam.location).normalized().to_track_quat("-Z", "Y").to_euler()


if SWEEP:
    # A fixed azimuth cannot suit every asset: the interesting face (ladders, doors,
    # valves) points a different way in each file. Render clay at 8 angles and pick.
    set_engine("BLENDER_WORKBENCH")
    shade(light="STUDIO", color_type="SINGLE", single_color=(0.62, 0.62, 0.63),
          show_shadows=True, show_cavity=True, cavity_type="BOTH", type="SOLID")
    for az in range(0, 360, 45):
        aim(az)
        render_to("az%03d" % az)
    print("MODELSHEET: sweep done")
    sys.exit(0)

# 1. beauty, the model's own materials
print("MODELSHEET: engine " + set_engine("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"))
render_to("beauty")

# 2. clay, geometry and form with no material distraction
set_engine("BLENDER_WORKBENCH")
shade(light="STUDIO", color_type="SINGLE", single_color=(0.62, 0.62, 0.63),
      show_shadows=True, show_cavity=True, cavity_type="BOTH", type="SOLID")
render_to("clay")

# 3. wireframe, proof the topology is real rather than scanned or bought
shade(type="WIREFRAME", wireframe_color_type="THEME",
      show_xray=True, xray_alpha_wireframe=1.0)
render_to("wire")

print("MODELSHEET: done %s" % NAME)
