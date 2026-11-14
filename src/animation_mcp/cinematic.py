"""Authored Blender art direction: materials, modeled sets and character finish.

These are original procedural assets. Reference films inform shot grammar, not
copied characters, frames or claimed reconstruction of their source projects.
"""
from __future__ import annotations
import math, random
import bpy
from mathutils import Vector

PALETTE={
 'ink':(.018,.035,.055,1),'steel':(.075,.16,.20,1),'teal':(.035,.38,.40,1),
 'ivory':(.77,.82,.75,1),'gold':(.75,.43,.13,1),'orange':(.98,.22,.055,1),
 'mint':(.12,.85,.68,1),'floor':(.065,.105,.13,1),'blue':(.08,.22,.38,1)}

def mat(name,color=None,metal=0,rough=.4,emission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    c=color or PALETTE.get(name,PALETTE['teal'])
    p.inputs['Base Color'].default_value=c if len(c)==4 else (*c,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    if emission:
        p.inputs['Emission Color'].default_value=c if len(c)==4 else (*c,1)
        p.inputs['Emission Strength'].default_value=emission
    return m

def assign(obj,material):
    obj.data.materials.append(material)
    return obj

def cube(name,location,scale,material,bevel=.06):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location);o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    assign(o,material)
    if bevel:
        b=o.modifiers.new('Machined edge radius','BEVEL');b.width=bevel;b.segments=3
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o

def sphere(name,location,scale,material,segments=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=16,location=location)
    o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in o.data.polygons:p.use_smooth=True
    return assign(o,material)

def cylinder(name,location,radius,depth,material,vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=location)
    o=bpy.context.object;o.name=name;assign(o,material)
    b=o.modifiers.new('Edge glints','BEVEL');b.width=.025;b.segments=3
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def ring(name,location,major,minor,material,rotation=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=80,minor_segments=12,location=location,rotation=rotation)
    o=bpy.context.object;o.name=name;assign(o,material)
    for p in o.data.polygons:p.use_smooth=True
    return o

def line(name,points,material,radius=.025):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=radius;curve.bevel_resolution=3
    s=curve.splines.new('POLY');s.points.add(len(points)-1)
    for p,co in zip(s.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(o);assign(o,material);return o

def area(name,location,target,power,color,size):
    bpy.ops.object.light_add(type='AREA',location=location);o=bpy.context.object;o.name=name
    o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

def light_scene(world=.22):
    s=bpy.context.scene;s.world=bpy.data.worlds.new('Blue hour atmosphere');s.world.use_nodes=True
    s.world.node_tree.nodes['Background'].inputs[0].default_value=(.075,.13,.21,1)
    s.world.node_tree.nodes['Background'].inputs[1].default_value=world
    area('Key • warm softbox',(1.5,-4,7),(0,0,1),1050,(1,.82,.64),5)
    area('Rim • glacier',(-4,2,4),(0,0,1),1350,(.24,.73,1),3)
    area('Fill • frontal bounce',(4,-1,3),(0,0,1),420,(.55,.82,1),4)
    s.view_settings.view_transform='AgX'
    s.view_settings.look='AgX - Medium High Contrast'
    s.render.image_settings.color_mode='RGB'
    s.render.film_transparent=False
    s.use_nodes=True
    tree=s.node_tree;tree.nodes.clear()
    source=tree.nodes.new('CompositorNodeRLayers');glow=tree.nodes.new('CompositorNodeGlare')
    glow.glare_type='FOG_GLOW';glow.quality='HIGH';glow.inputs['Threshold'].default_value=1.5;glow.inputs['Strength'].default_value=.08
    output=tree.nodes.new('CompositorNodeComposite');tree.links.new(source.outputs['Image'],glow.inputs['Image']);tree.links.new(glow.outputs['Image'],output.inputs['Image'])


def stage(name='Moonstone dais',radius=2.65):
    floor=mat('Stage floor',PALETTE['floor'],.35,.32)
    # Noise gives restrained micro-roughness, not a flat plastic checkerboard.
    tree=floor.node_tree;p=tree.nodes.get('Principled BSDF');noise=tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=38
    ramp=tree.nodes.new('ShaderNodeMapRange');ramp.inputs['To Min'].default_value=.27;ramp.inputs['To Max'].default_value=.42
    tree.links.new(noise.outputs['Fac'],ramp.inputs['Value']);tree.links.new(ramp.outputs['Result'],p.inputs['Roughness'])
    cylinder('Foundation',(0,0,-.20),radius,.35,mat('Basalt',(.025,.05,.07),.4,.3))
    cylinder(name,(0,0,-.015),radius-.08,.08,floor)
    glow=mat('Inlaid luminous brass',(.55,.31,.09),.65,.3,.45)
    for r in [radius-.22,radius-.34,1.05]:ring('Concentric inlay',(0,0,.032),r,.012,glow)
    for i in range(24):
        a=i*math.tau/24;r=radius-.48
        o=cube(f'Radial index {i:02}',(r*math.cos(a),r*math.sin(a),.035),(.13,.025,.009),glow,.003);o.rotation_euler.z=a
    return floor


def finish_rig(rig):
    """Replace the engineering preset's simple shells with art-directed armor."""
    skin=bpy.data.objects[rig['skin']]
    # Materials were appended in build_rig order. Keep weights/modifier untouched.
    name=rig.name
    shell=mat(name+' • enamel',(.035,.30,.33),.58,.27)
    ivory=mat(name+' • ceramic',(.78,.83,.77),.22,.26)
    dark=mat(name+' • carbon',(.012,.032,.047),.55,.28)
    copper=mat(name+' • brushed brass',(.68,.34,.095),.72,.26)
    for i,m in enumerate([shell,ivory,dark,copper]):
        if len(skin.data.materials)>i:skin.data.materials[i]=m
    # Add chest reactor and helmet hardware as rigid children of the head/spine.
    def attach(bone,obj):
        bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
        world=obj.matrix_world.copy();obj.parent=rig;obj.parent_type='BONE';obj.parent_bone=bone
        bpy.context.view_layer.update();obj.matrix_world=world
    origin=Vector(rig.location)
    reactor=ring(name+' reactor rim',origin+Vector((0,-.267,1.46)),.087,.016,copper,(math.pi/2,0,0));attach('spine',reactor)
    core=sphere(name+' reactor core',origin+Vector((0,-.275,1.46)),(.065,.025,.065),mat(name+' core light',(.1,.75,.76),.25,.2,3));attach('spine',core)
    for sign in [-1,1]:
        o=cube(name+' temple plate',origin+Vector((sign*.285,-.05,2.04)),(.06,.20,.14),copper,.025);attach('head',o)
    if 'payload' in rig:
        prop=bpy.data.objects[rig['payload']]
        prop.data.materials.clear();prop.data.materials.append(copper)
    return skin


def bounce_scene(frames,fps):
    stage(radius=2.35)
    orange=mat('Lacquered vermilion',(.82,.12,.035),.35,.23)
    ball=sphere('BALL • hero',(0,0,2.5),(.38,.38,.38),orange,48)
    seam=mat('Ball seam',(.025,.04,.045),.15,.45)
    for rot in [(0,0,0),(math.pi/2,0,0),(0,math.pi/2,0)]:
        r=ring('Inset basketball seam',(0,0,0),.381,.012,seam,rot);r.parent=ball;r.location=(0,0,0)
    # Low surrounding light bars give scale and reflected highlights.
    glow=mat('Warm floor strips',(.95,.43,.10),.3,.3,1.6)
    for i in range(8):
        a=i*math.tau/8;o=cube('Perimeter marker',(2.05*math.cos(a),2.05*math.sin(a),.10),(.25,.07,.10),glow,.02);o.rotation_euler.z=a
    for f in range(frames):
        t=f/fps;period=1.15;u=(t%period)/period
        z=.40+1.95*4*u*(1-u)
        impact=max(0,1-(z-.4)/.16)
        ball.location=(.4*math.sin(t*.9),0,z)
        ball.scale=(1+.18*impact,1+.18*impact,1-.25*impact)
        ball.rotation_euler=(t*.4,t*.7,t*.2)
        for p in ['location','scale','rotation_euler']:ball.keyframe_insert(data_path=p,frame=f)


def walk_set(frames,fps):
    m=mat('Runway terrazzo',(.11,.18,.21),.22,.4)
    cube('Endless runway',(0,-1,.0), (2.5,9,.16),m,.08)
    trim=mat('Runway edge light',(.08,.55,.56),.4,.3,.8)
    for x in [-1.14,1.14]:cube('Continuous edge strip',(x,-1,.10),(.028,8.6,.015),trim,.006)
    for i in range(16):cube('Runway joint',(0,3-i*.5,.087),(2.2,.009,.006),mat('Joint'+str(i),(.035,.07,.085),0,.6),0)
    # Architectural rhythm and receding light portals, rather than empty gray void.
    for i,y in enumerate([2.3,.5,-1.3,-3.1]):
        for sign in [-1,1]:
            cube('Portal column',(sign*1.7,y,1.35),(.16,.20,2.7),mat('Portal structure'+str(i)+str(sign),(.055,.12,.16),.5,.32),.035)
            cube('Portal practical',(sign*1.60,y-.12,1.4),(.025,.035,2.2),trim,.005)
        cube('Portal lintel',(0,y,2.72),(3.55,.20,.16),mat('Lintel'+str(i),(.08,.17,.21),.5,.3),.035)


def pickup_set(frames,fps):
    stage(radius=2.6)
    gold=mat('Payload brushed gold',(.68,.35,.075),.7,.24)
    dark=mat('Pedestal graphite',(.025,.06,.08),.5,.28)
    cylinder('Payload plinth',(.60,-.42,.35),.30,.70,dark)
    ring('Plinth rim',(.60,-.42,.71),.28,.018,mat('Plinth glow',(.08,.7,.62),.4,.3,1))
    # Floating geometric archive with real beveled casing and inset panels.
    for sign in [-1,1]:cube('Archive wall',(sign*2.3,1.5,1.5),(.16,.2,3),dark,.03)
    cube('Archive crown',(0,1.5,3.02),(4.8,.22,.16),dark,.03)
    for i in range(7):
        cube('Archive index',(-1.8+i*.6,1.36,2.65),(.26,.03,.035),mat('Archive index glow'+str(i),(.10,.55,.51),.3,.4,1),.004)


def corridor_scene(frames,fps):
    """Original sci-fi retrieval shot: articulated hero, opening iris, drone and light sweep."""
    floor=mat('Corridor floor',(.035,.07,.09),.55,.28)
    cube('Deck',(0,-1,-.13),(7,12,.2),floor,.03)
    wall=mat('Corridor walls',(.04,.095,.13),.55,.34)
    glow=mat('Corridor mint phosphor',(.045,.75,.56),.3,.28,2)
    amber=mat('Corridor amber',(.95,.24,.045),.3,.3,2)
    for i,y in enumerate([-5,-3,-1,1,3]):
        for sign in [-1,1]:
            cube('Structural rib',(sign*3.25,y,1.65),(.23,.23,3.4),wall,.04)
            cube('Rib light',(sign*3.10,y-.14,1.7),(.04,.035,2.65),glow,.008)
            pane=cube('Recessed wall panel',(sign*3.4,y+.75,1.4),(.10,1.25,2.3),wall,.035)
            for j in range(4):cube('Panel vent',(sign*3.32,y+.35+j*.23,1.9),(.035,.11,.04),glow,.004)
        cube('Overhead rib',(0,y,3.35),(6.7,.24,.20),wall,.035)
        cube('Ceiling light',(0,y-.02,3.22),(2.2,.08,.035),glow,.008)
    for x in [-1.5,1.5]:cube('Floor guide',(x,-1,.005),(.025,11,.012),amber,.003)
    for i in range(18):cube('Deck seam',(0,-5+i*.55,.006),(5.2,.014,.01),mat('Seam'+str(i),(.01,.02,.025),0,.5),0)
    # Bulkhead and segmented iris door. The opening is animated geometry.
    cube('Bulkhead header',(0,2.65,3.0),(5.4,.4,.6),wall,.05)
    for sign in [-1,1]:cube('Bulkhead jamb',(sign*2.05,2.65,1.4),(.9,.4,2.8),wall,.05)
    ring('Iris surround',(0,2.48,1.43),1.25,.10,mat('Iris rim',(.19,.29,.31),.8,.24),(math.pi/2,0,0))
    ring('Iris illumination',(0,2.35,1.43),1.14,.022,amber,(math.pi/2,0,0))
    doors=[]
    for sign in [-1,1]:
        door=cube('Iris half',(sign*.53,2.52,1.43),(1.04,.16,2.12),mat('Iris armor'+str(sign),(.06,.14,.18),.65,.28),.10);doors.append((sign,door))
        for f,amount in [(0,0),(28,0),(48,1),(frames-1,1)]:
            t=amount*amount*(3-2*amount);door.location.x=sign*(.53+.99*t);door.keyframe_insert(data_path='location',frame=f)
    # Drone is separate from the hero, with moving shell, eye and stabilizer rings.
    drone=sphere('DRONE • shell',(-.95,.25,1.85),(.28,.24,.22),mat('Drone ceramic',(.68,.75,.70),.45,.25))
    eye=sphere('DRONE • optic',(-.95,.025,1.85),(.115,.04,.11),amber);eye.parent=drone;eye.location=(0,-.225,0)
    for sign in [-1,1]:
        r=ring('Drone stabilizer',(-.95+sign*.34,.25,1.85),.18,.027,glow,(math.pi/2,0,0));r.parent=drone;r.location=(sign*.34,0,0)
    for f in range(frames):
        t=f/fps;u=f/max(1,frames-1)
        drone.location=(-.95+1.55*u,.25-.9*u,1.85+.10*math.sin(t*3)-.45*max(0,(u-.55)/.45))
        drone.rotation_euler.z=.12*math.sin(t*2);drone.keyframe_insert(data_path='location',frame=f);drone.keyframe_insert(data_path='rotation_euler',frame=f)
    # A small archive core floats beyond the opening door.
    core=sphere('Archive energy',(0,2.8,1.45),(.22,.22,.22),mat('Archive core',(.95,.30,.05),.2,.22,4))
    for r in [.36,.48]:ring('Archive gyro',(0,2.8,1.45),r,.018,amber,(math.pi/3,r*3,0))
    area('Door backlight',(0,3.3,1.7),(0,0,1.2),650,(1,.21,.04),2)
