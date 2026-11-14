"""Small editable 3D production briefs, progressing from motion to humanoid IK."""
import math


def scene_preset(level='simple',width=640,height=360,samples=12):
    if level not in {'easy','simple','medium','hard'}:raise ValueError('Use easy, simple, medium or hard')
    frames={'easy':72,'simple':72,'medium':96,'hard':96}[level]
    scene=dict(width=width,height=height,fps=24,frames=frames,samples=samples,denoise=False,
               camera=[4.5,-7,3.1],target=[0,0,1.0],objects=[
                   dict(name='stage',kind='cylinder',location=[0,0,-.12],scale=[2.4,2.4,.12],color=[.045,.10,.16])])
    if level=='easy':
        poses=[];height_z=2.4;velocity=0
        for frame in range(frames):
            if frame:
                velocity-=9.81/24;height_z+=velocity/24
                if height_z<.32:height_z=.32;velocity=abs(velocity)*.72
            impact=max(0,1-(height_z-.32)/.14)
            poses.append(dict(frame=frame,location=[0,0,height_z],scale=[.32*(1+.18*impact),.32*(1+.18*impact),.32*(1-.18*impact)]))
        scene['objects'].append(dict(name='ball',kind='sphere',color=[.94,.44,.12],poses=poses))
    else:
        action={'simple':'wave','medium':'walk','hard':'pickup'}[level]
        scene['rigs']=[dict(name='Nova',action=action,color=[.055,.50,.56])]
        if level=='medium':
            scene['target']=[0,-.35,1]
            scene['camera_poses']=[dict(frame=0,location=[4.5,-7,3.1],target=[0,0,1]),
                                   dict(frame=frames,location=[4.0,-7.3,3.0],target=[0,-.8,1])]
        if level=='hard':
            scene['camera_poses']=[dict(frame=0,location=[4.5,-7,3.1],target=[0,0,1]),
                                   dict(frame=frames,location=[3.7,-6.2,2.8],target=[0,-.2,1.1])]
    return scene
