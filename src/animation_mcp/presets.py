"""Editable 3D briefs progressing from weight/spacing to a staged retrieval shot.

Difficulty describes these exercises, not equivalence to professional reference
films. Every preset saves its actual armature, materials, lighting and camera.
"""
import math

LEVELS=('easy','simple','medium','hard')

def scene_preset(level='simple',width=960,height=540,samples=24):
    if level not in LEVELS:raise ValueError('Use easy, simple, medium or hard')
    frames={'easy':96,'simple':96,'medium':120,'hard':120}[level]
    scene=dict(width=width,height=height,fps=24,frames=frames,samples=samples,denoise=True,
               art_direction=level,camera=[4.5,-7,3.1],target=[0,0,1.0],objects=[])
    if level=='easy':
        scene.update(camera=[4.2,-7.4,3.4],target=[0,0,1.1],
                     camera_poses=[dict(frame=0,location=[4.2,-7.4,3.4],target=[0,0,1.1]),
                                   dict(frame=frames-1,location=[3.4,-7.1,3.0],target=[0,0,1.1])])
    elif level=='simple':
        scene.update(rigs=[dict(name='Nova',action='wave',color=[.055,.50,.56])],camera=[3.0,-6.8,2.7],target=[0,0,1.18],
                     camera_poses=[dict(frame=0,location=[3.0,-6.8,2.7],target=[0,0,1.18]),
                                   dict(frame=frames-1,location=[2.1,-6.2,2.5],target=[0,0,1.22])])
    elif level=='medium':
        scene.update(rigs=[dict(name='Nova',action='walk',color=[.055,.50,.56])],camera=[1.25,-6.2,2.5],target=[0,-.45,1.15],
                     camera_poses=[dict(frame=0,location=[1.25,-6.2,2.5],target=[0,0,1.15]),
                                   dict(frame=frames-1,location=[1.0,-7.7,2.35],target=[0,-1.35,1.15])])
    else:
        scene.update(rigs=[dict(name='Nova',action='reach',color=[.055,.50,.56])],camera=[1.35,-7.2,2.8],target=[0,.4,1.35],
                     camera_poses=[dict(frame=0,location=[1.35,-7.2,2.8],target=[0,.4,1.35]),
                                   dict(frame=55,location=[1.1,-6.7,2.6],target=[0,.55,1.35]),
                                   dict(frame=100,location=[.8,-6.2,2.4],target=[0,.25,1.4]),
                                   dict(frame=frames-1,location=[.6,-5.8,2.3],target=[0,.1,1.4])])
    return scene
