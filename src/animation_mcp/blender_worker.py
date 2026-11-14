"""Trusted worker run inside Blender, not imported by the server."""
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector


def main():
    path, folder = map(Path, sys.argv[sys.argv.index("--")+1:])
    spec = json.loads(path.read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = spec["samples"]
    scene.cycles.use_denoising = False
    scene.render.resolution_x = spec["width"]
    scene.render.resolution_y = spec["height"]
    scene.render.resolution_percentage = 100
    scene.render.fps = spec["fps"]
    scene.frame_start,scene.frame_end = 0,spec["frames"]-1
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (.025,.04,.08,1)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = .35
    for item in spec["objects"]:
        kind = item["kind"]
        if kind == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16)
        else:
            {"cube":bpy.ops.mesh.primitive_cube_add,"cone":bpy.ops.mesh.primitive_cone_add,
             "cylinder":bpy.ops.mesh.primitive_cylinder_add,"torus":bpy.ops.mesh.primitive_torus_add}[kind]()
        obj = bpy.context.object
        obj.name = item["name"]
        obj.location,obj.scale = item["location"],item["scale"]
        mat = bpy.data.materials.new(item["name"]+"_material")
        mat.diffuse_color = (*item["color"],1)
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = (*item["color"],1)
        shader.inputs["Roughness"].default_value = .32
        shader.inputs["Metallic"].default_value = .25
        obj.data.materials.append(mat)
        if kind in {"sphere","torus"}:
            for poly in obj.data.polygons:
                poly.use_smooth = True
        bevel = obj.modifiers.new("Soft edges","BEVEL")
        bevel.width,bevel.segments = .055,3
        for pose in item["poses"]:
            obj.location,obj.rotation_euler,obj.scale = pose["location"],pose["rotation"],pose["scale"]
            for prop in ["location","rotation_euler","scale"]:
                obj.keyframe_insert(data_path=prop,frame=pose["frame"])
    bpy.ops.object.camera_add(location=spec["camera"])
    camera = bpy.context.object
    camera.rotation_euler = (Vector(spec["target"])-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.lens = 48
    scene.camera = camera
    for name,position,power,color,size in [
        ("Key",(2,-4,7),1300,(.68,.84,1),5),
        ("Rim",(-4,2,5),1600,(.2,.7,1),4),
        ("Warm",(4,4,3),1100,(1,.44,.2),3)]:
        bpy.ops.object.light_add(type="AREA",location=position)
        lamp = bpy.context.object
        lamp.name = name
        lamp.data.energy,lamp.data.color,lamp.data.shape,lamp.data.size = power,color,'DISK',size
        lamp.rotation_euler = (Vector(spec["target"])-lamp.location).to_track_quat('-Z','Y').to_euler()
    (folder/"frames").mkdir(exist_ok=True)
    scene.render.filepath = str(folder/"frames"/"")
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/"scene.blend"))
    for frame in range(spec["frames"]):
        scene.frame_set(frame)
        scene.render.filepath = str(folder/"frames"/f"{frame:04d}.png")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
