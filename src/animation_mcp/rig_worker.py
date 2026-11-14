"""Trusted Blender humanoid rig builder, IK motion presets and actual-pose audit."""
import math
import bpy
from mathutils import Vector,Quaternion


def material(name,color,metal=.25):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=.38;p.inputs['Metallic'].default_value=metal
    return m


def build_rig(spec):
    data=bpy.data.armatures.new(spec['name']+'_skeleton')
    rig=bpy.data.objects.new(spec['name'],data);bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    definitions=[('root',(0,0,.95),(0,0,1.1),None),('spine',(0,0,1.05),(0,0,1.75),'root'),
                 ('head',(0,0,1.75),(0,-.22,2.04),'spine')]
    for side,sign in [('R',1),('L',-1)]:
        definitions.extend([
            ('upper_arm.'+side,(sign*.4,0,1.7),(sign*.7,0,1.35),'spine'),
            ('forearm.'+side,(sign*.7,0,1.35),(sign*.75,0,1.0),'upper_arm.'+side),
            ('hand.'+side,(sign*.75,0,1.0),(sign*.75,-.1,.85),'forearm.'+side),
            ('thigh.'+side,(sign*.19,0,1.0),(sign*.19,-.03,.55),'root'),
            ('shin.'+side,(sign*.19,-.03,.55),(sign*.19,0,.14),'thigh.'+side),
            ('foot.'+side,(sign*.19,0,.14),(sign*.19,-.2,.1),'shin.'+side)])
    for name,head,tail,parent in definitions:
        bone=data.edit_bones.new(name);bone.head=head;bone.tail=tail
        if parent:bone.parent=data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
    shell=material(spec['name']+'_shell',spec['color'])
    ivory=material(spec['name']+'_ivory',(.88,.91,.83))
    dark=material(spec['name']+'_visor',(.025,.09,.15),.5)
    copper=material(spec['name']+'_trim',(.92,.40,.12))
    parts=[]

    def part(name,bone,position,scale,mat,rotation=None):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=position)
        obj=bpy.context.object;obj.name=spec['name']+'_'+name;obj.scale=scale
        if rotation:obj.rotation_euler=rotation
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
        obj.data.materials.append(mat)
        for p in obj.data.polygons:p.use_smooth=True
        group=obj.vertex_groups.new(name=bone);group.add(list(range(len(obj.data.vertices))),1,'REPLACE')
        parts.append(obj)

    part('torso','spine',(0,0,1.4),(.36,.23,.43),shell)
    part('hip','root',(0,0,1.02),(.29,.21,.19),dark)
    part('helmet','head',(0,0,2.0),(.32,.29,.32),ivory)
    part('visor','head',(0,-.255,2.02),(.25,.065,.16),dark)
    part('eye_R','head',(.10,-.315,2.03),(.035,.013,.035),copper)
    part('eye_L','head',(-.10,-.315,2.03),(.035,.013,.035),copper)
    part('chest','spine',(0,-.22,1.43),(.19,.035,.13),ivory)
    for name,head,tail,parent in definitions:
        if name.startswith(('upper_arm','forearm','thigh','shin')):
            a,b=Vector(head),Vector(tail);delta=b-a
            radius=.085 if 'arm' in name else .10
            part(name,name,(a+b)/2,(radius,radius,delta.length*.56),shell,delta.to_track_quat('Z','Y').to_euler())
            part(name+'_joint',name,head,(radius*1.25,)*3,copper)
        if name.startswith('hand'):
            a,b=Vector(head),Vector(tail)
            part(name,name,(a+b)/2,(.095,.10,.12),ivory)
        if name.startswith('foot'):
            part(name,name,(head[0],-.08,.10),(.14,.23,.10),ivory)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts:obj.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
    skin=bpy.context.object;skin.name=spec['name']+'_weighted_mesh'
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    modifier=skin.modifiers.new('Skeleton deformation','ARMATURE');modifier.object=rig
    skin.parent=rig;skin.location=(0,0,0)
    rig.location=spec['position'];rig.show_in_front=True
    controls={}
    for side,sign in [('R',1),('L',-1)]:
        for limb,bone,position in [('hand','forearm.'+side,(sign*.75,0,1.0)),('foot','shin.'+side,(sign*.19,0,.14))]:
            obj=bpy.data.objects.new(spec['name']+'_'+limb+'.'+side+'_IK',None)
            bpy.context.collection.objects.link(obj);obj.empty_display_type='SPHERE';obj.empty_display_size=.08
            obj.location=Vector(spec['position'])+Vector(position)
            ik=rig.pose.bones[bone].constraints.new('IK');ik.target=obj;ik.chain_count=2;ik.use_stretch=False
            controls[limb+'.'+side]=obj
            if limb=='foot':
                obj.rotation_euler=rig.data.bones['foot.'+side].matrix_local.to_euler()
                lock=rig.pose.bones['foot.'+side].constraints.new('COPY_ROTATION');lock.target=obj
                lock.target_space='WORLD';lock.owner_space='WORLD'
    rig['skin']=skin.name
    for name,obj in controls.items():rig['control_'+name]=obj.name
    return rig


def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)


def bake_motion(rig,spec,frames,fps):
    origin=Vector(spec['position']);controls={n:bpy.data.objects[rig['control_'+n]] for n in ['hand.R','hand.L','foot.R','foot.L']}
    for f in range(frames):
        u=f/max(1,frames-1);t=f/fps
        root=origin.copy()
        targets={'hand.R':Vector((.75,0,1.0)),'hand.L':Vector((-.75,0,1.0)),
                 'foot.R':Vector((.19,0,.14)),'foot.L':Vector((-.19,0,.14))}
        if spec['action']=='wave':
            blend=smooth(u/.22)
            targets['hand.R']=Vector((.75-.08*blend+.14*math.sin(t*7)*blend,-.10*blend,1.0+1.12*blend))
        elif spec['action']=='walk':
            root.y-=.28*t;root.z+=.012*math.cos(t*math.tau*2)
            for side,phase in [('R',0),('L',.5)]:
                absolute=t+phase;cycle=math.floor(absolute);p=absolute-cycle
                swing=smooth((p-.6)/.4)
                y=-.28*(cycle+swing)+phase*.28
                lift=.15*math.sin(math.pi*max(0,(p-.6)/.4)) if p>=.6 else 0
                targets['foot.'+side]=Vector(((1 if side=='R' else -1)*.19,y,.14+lift))
                targets['hand.'+side].y=-.28*t+.18*math.sin(absolute*math.tau)
        elif spec['action']=='pickup':
            reach=smooth((u-.15)/.25);stand=smooth((u-.44)/.3)
            root.z-=.28*reach*(1-stand)
            targets['hand.R']=Vector((.75-.15*reach,-.42*reach+.12*stand,1.0+.43*stand))
        elif spec['action']=='reach':
            # Anticipation, approach, contact, lift and settle. Targets stay inside
            # the limb reach envelope and translate with the body so IK does not stretch.
            approach=smooth((t-.65)/.85);lift=smooth((t-2.6)/1.15)
            root.y=.30*approach
            root.z=-.045*math.sin(math.pi*approach)
            targets['hand.R']=Vector((.75-.15*approach,root.y-.25*approach-.10*lift,1.0+.55*lift))
            targets['hand.L']=Vector((-.75,root.y-.10*approach,1.0+.08*lift))
            targets['foot.R'].y=root.y;targets['foot.L'].y=root.y
        rig.location=root;rig.keyframe_insert(data_path='location',frame=f)
        for name,obj in controls.items():
            local=targets[name]
            keys=sorted([k for k in spec.get('target_keys',[]) if k['control']==name],key=lambda k:k['frame'])
            if keys:
                local=Vector(keys[0]['location'])
                for a,b in zip(keys,keys[1:]):
                    if a['frame']<=f<b['frame']:
                        local=Vector(a['location']).lerp(Vector(b['location']),smooth((f-a['frame'])/(b['frame']-a['frame'])));break
                else:
                    if f>=keys[-1]['frame']:local=Vector(keys[-1]['location'])
            obj.location=origin+local;obj.keyframe_insert(data_path='location',frame=f)
        head=rig.pose.bones['head'];head.rotation_mode='XYZ'
        head.rotation_euler[1]=.04*math.sin(t*2);head.keyframe_insert(data_path='rotation_euler',frame=f)
    if spec['action'] in ('pickup','reach'):
        grasp=round((frames-1)*.40) if spec['action']=='pickup' else round(2.55*fps)
        bpy.context.scene.frame_set(grasp);bpy.context.view_layer.update()
        hold=rig.matrix_world@rig.pose.bones['hand.R'].tail+Vector((0,-.05,.08))
        bpy.ops.mesh.primitive_cube_add(size=.28,location=hold)
        prop=bpy.context.object;prop.name=spec['name']+'_payload';prop.data.materials.append(material('Payload',(.85,.26,.56)))
        bevel=prop.modifiers.new('Rounded corners','BEVEL');bevel.width=.035;bevel.segments=3
        initial=hold.copy()
        for f in range(frames):
            bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
            prop.location=initial if f<grasp else rig.matrix_world@rig.pose.bones['hand.R'].tail+Vector((0,-.05,.08))
            prop.keyframe_insert(data_path='location',frame=f)
        if spec['action'] in ('pickup','reach'):
            radius=.23 if spec['action']=='pickup' else .20
            bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=max(.1,initial.z-.14),
                                               location=(initial.x,initial.y,(initial.z-.14)/2))
            bpy.context.object.name=spec['name']+'_pedestal';bpy.context.object.data.materials.append(material('Pedestal',(.05,.13,.2)))
        rig['payload']=prop.name;rig['grasp_frame']=grasp
    for obj in [rig,*controls.values()]:
        if obj.animation_data and obj.animation_data.action:
            for curve in obj.animation_data.action.fcurves:
                for k in curve.keyframe_points:k.interpolation='LINEAR'


def audit_rig(rig,spec,frames,fps):
    skin=bpy.data.objects[rig['skin']]
    foot_indices={}
    for side in ['R','L']:
        group=skin.vertex_groups.get('foot.'+side)
        foot_indices[side]=[v.index for v in skin.data.vertices if any(g.group==group.index for g in v.groups)]
    trace=[];minimum=float('inf');hold_errors=[];ik_errors=[]
    control_bones={'hand.R':'forearm.R','hand.L':'forearm.L','foot.R':'shin.R','foot.L':'shin.L'}
    for f in range(frames):
        bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
        positions={name:list(rig.matrix_world@rig.pose.bones[name].tail) for name in ['hand.R','hand.L','foot.R','foot.L']}
        for control,bone in control_bones.items():
            obj=bpy.data.objects.get(rig.get('control_'+control,''))
            if obj:ik_errors.append((obj.location-(rig.matrix_world@rig.pose.bones[bone].tail)).length)
        row=dict(frame=f,joints=positions)
        evaluated=skin.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        for side,indices in foot_indices.items():
            low=min((evaluated.matrix_world@mesh.vertices[i].co).z for i in indices)
            minimum=min(minimum,low)
        evaluated.to_mesh_clear()
        if 'payload' in rig and f>=rig['grasp_frame']:
            actual=bpy.data.objects[rig['payload']].location
            target=rig.matrix_world@rig.pose.bones['hand.R'].tail+Vector((0,-.05,.08))
            hold_errors.append((actual-target).length)
        trace.append(row)
    return dict(rig=rig.name,action=spec['action'],bones=len(rig.data.bones),
                weighted_vertices=len(skin.data.vertices),vertex_groups=len(skin.vertex_groups),
                armature_modifier=any(m.type=='ARMATURE' and m.object==rig for m in skin.modifiers),
                ik_chains=sum(c.type=='IK' for p in rig.pose.bones for c in p.constraints),
                minimum_foot_vertex_z=minimum,max_payload_hold_error=max(hold_errors,default=0),
                max_ik_target_error=max(ik_errors,default=0),
                geometry_pass=minimum>=-.025 and max(hold_errors,default=0)<.001 and max(ik_errors,default=0)<.03,
                trace=trace,limits='Procedural stylized humanoid rig. Preset/baked motion, not learned acting or universal auto-rigging.')
