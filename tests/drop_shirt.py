import os
import airo_blender_toolkit as abt
import blenderproc as bproc
import bpy
import numpy as np
from cipc.simulator import SimulationCIPC
# from cloth_manipulation.cipc_sim import SimulationCIPC
from cipc.dirs import ensure_output_filepaths
from cipc.materials.penava import materials_by_name


bproc.init()
ground = bproc.object.create_primitive("PLANE", size=5.0)
ground.blender_obj.name = "Ground"

cloth_material = materials_by_name["cotton penava"]

shirt = abt.PolygonalShirt()
shirt_obj = shirt.blender_obj
abt.triangulate_blender_object(shirt_obj, minimum_triangle_density=100)
shirt_obj.location.z = 0.5  # ground offset + cloth offset
# shirt_obj.rotation_euler.z = np.deg2rad(10)
shirt.persist_transformation_into_mesh()

simulation_steps = 100
scene = bpy.context.scene
scene.frame_end = simulation_steps

print(f"Simulating {simulation_steps} steps.")

filepaths = ensure_output_filepaths()

# Running the simulation
simulation = SimulationCIPC(filepaths, 25)
simulation.add_cloth(shirt.blender_obj, cloth_material)
simulation.add_collider(ground.blender_obj, friction_coefficient=0.8)
simulation.initialize_cipc()

simulated_shirt = shirt.blender_obj

for frame in range(scene.frame_start, scene.frame_end):
    scene.frame_set(frame)
    action = {}
    if frame == 0:
        # Without this if statement, CIPC fails to converge :(
        action = {0: (0,0,0)}
    simulation.step(action)
    simulated_shirt = simulation.blender_objects_output[shirt_obj.name][frame + 1]
    scene.frame_set(frame + 1)


scene.frame_set(simulation_steps)
objects_to_hide = [ground.blender_obj, shirt.blender_obj]

for object in objects_to_hide:
    object.hide_viewport = True
    object.hide_render = True

bpy.ops.wm.save_as_mainfile(filepath=filepaths["blend"])

scene.cycles.adaptive_threshold = 0.1
scene.render.filepath = os.path.join(filepaths["run"], "result.png")
bpy.ops.render.render(write_still=True)
