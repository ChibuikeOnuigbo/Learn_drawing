#!/usr/bin/env python3
"""Author original, editable demonstration projects (not reference-film copies)."""
from __future__ import annotations
import json, math, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageSequence
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from animation_mcp.character import character_svg
from animation_mcp.render import draw_frame
from animation_mcp.scene import Scene

FPS=24;W=1280;H=720
OUT=ROOT/'examples';OUT.mkdir(exist_ok=True)
FONT=ROOT/'src/animation_mcp/assets/fonts/inter-400.ttf'
BOLD=ROOT/'src/animation_mcp/assets/fonts/space-grotesk-700.ttf'

def track(prop,keys):return {'property':prop,'keys':[{'frame':f,'value':v,'easing':e} for f,v,*rest in keys for e in [rest[0] if rest else 'smooth']]}
def layer(id,kind,**kw):return dict(id=id,kind=kind,**kw)
def save(name,scene):
    p=OUT/name;p.mkdir(parents=True,exist_ok=True);(p/'scene.json').write_text(Scene.model_validate(scene).model_dump_json(indent=2));return p

def soundtrack(path,duration,impacts=(),music=True):
    rate=44100;n=round(rate*duration);t=np.arange(n)/rate;rng=np.random.default_rng(14)
    mix=np.zeros(n)
    if music:
        envelope=np.minimum(t/1.5,1)*np.minimum((duration-t)/1.5,1)
        chord=[130.8128,164.8138,195.9977,246.9417]
        for i,f in enumerate(chord):mix+=.014*np.sin(2*np.pi*f*t+.2*np.sin(t*.3+i))*envelope
        notes=[523.25,659.25,783.99,987.77,783.99,659.25,587.33,659.25]
        step=.375
        for k in range(int(duration/step)):
            start=round(k*step*rate);tt=np.arange(min(round(rate*1.2),n-start))/rate
            f=notes[k%len(notes)];tone=(np.sin(2*np.pi*f*tt)+.23*np.sin(2*np.pi*f*2*tt))*np.exp(-tt*6)*np.minimum(tt/.006,1)
            mix[start:start+len(tt)]+=tone*.035
    for sec,kind in impacts:
        start=round(sec*rate);tt=np.arange(round(.5*rate))/rate
        if kind=='whoosh':
            noise=rng.normal(0,1,len(tt));noise=np.convolve(noise,np.ones(12)/12,'same')
            s=noise*np.sin(np.pi*np.minimum(tt/.5,1))**.8*.12
        elif kind=='chime':s=(np.sin(2*np.pi*880*tt)+.4*np.sin(2*np.pi*1320*tt))*np.exp(-tt*8)*.11
        else:s=(np.sin(2*np.pi*(100*tt-80*tt*tt))*np.exp(-tt*16)+rng.normal(0,.04,len(tt))*np.exp(-tt*35))*.24
        mix[start:start+len(s)]+=s[:max(0,n-start)]
    mix=np.tanh(mix*1.2)*.8
    stereo=np.column_stack([mix,np.roll(mix,130)*.96])
    with wave.open(str(path),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate);w.writeframes((stereo*32767).astype('<i2').tobytes())

def character_film():
    duration=10;frames=FPS*duration
    p=OUT/'01-2d-moonlight';p.mkdir(parents=True,exist_ok=True)
    (p/'audio.wav').unlink(missing_ok=True);soundtrack(p/'audio.wav',duration,[(2.2,'whoosh'),(3.1,'chime'),(6.1,'chime'),(7.2,'whoosh')])
    # Authored nested SVG rig rendered at real poses, with background and effects layers.
    (p/'character.svg').write_text(character_svg(0))
    import shutil
    shutil.copy2(ROOT/'src/animation_mcp/assets/art/observatory.jpg',p/'observatory.jpg')
    layers=[layer('background', 'image',asset='observatory.jpg',x=640,y=360,width=1320,height=743,
                  tracks=[track('scale',[(0,1.02),(72,1.06),(144,1.025),(239,1.07)]),track('x',[(0,640),(239,625)])])]
    # A proper shadow stays on the floor while the character acts above it.
    layers.append(layer('contact-shadow','ellipse',x=602,y=650,width=175,height=25,fill='#102c3c',opacity=.48,
                        tracks=[track('scale_x',[(0,.9),(52,1.05),(66,.85),(82,1),(190,.9)])]))
    layers.append(layer('performer','image',asset='character.svg',x=592,y=431,width=307,height=430,
                        tracks=[track('x',[(0,460),(40,570),(60,582),(100,592),(145,620),(190,620),(239,635)]),
                                track('rotation',[(0,-4),(40,0),(60,3),(82,0),(145,-3),(190,0)])]))
    # Magical orb has independent motion, halo, core and a multi-particle release.
    layers.append(layer('orb-halo','ellipse',x=725,y=333,width=105,height=105,fill='#eabb73',opacity=0,
                        tracks=[track('opacity',[(0,0),(58,0),(70,.18),(100,.1),(140,.2),(174,0)]),track('scale',[(58,.3),(75,1),(120,1.2),(160,1.8)])]))
    layers.append(layer('orb','ellipse',x=725,y=333,width=34,height=34,fill='#ffe3a1',stroke='#fff4d2',stroke_width=3,opacity=0,
                        tracks=[track('opacity',[(0,0),(58,0),(65,1),(135,1),(165,0)]),track('y',[(58,360),(78,322),(120,312),(155,220)]),track('x',[(58,712),(120,730),(155,800)])]))
    for i in range(26):
        angle=i*2.39996;radius=80+(i%6)*18;start=144+i%5
        layers.append(layer(f'spark-{i:02d}','ellipse',x=800,y=220,width=3+i%4,height=3+i%4,fill='#ffe0a0' if i%3 else '#bcebe2',opacity=0,
                            tracks=[track('opacity',[(0,0),(start,0),(start+3,.9),(start+38,0)]),
                                    track('x',[(start,800),(start+38,800+math.cos(angle)*radius)]),
                                    track('y',[(start,220),(start+38,220+math.sin(angle)*radius+25)])]))
    # Foreground silhouette creates a separate parallax plane, not a fake camera label.
    layers.append(layer('foreground','path',points=[(0,675),(80,686),(170,700),(350,714),(500,720),(0,720)],closed=True,fill='#0c2432',opacity=.75,
                        tracks=[track('x',[(0,0),(239,-45)])]))
    scene=dict(version=1,title='Moonlight — a small discovery',width=W,height=H,fps=FPS,frames=frames,background='#112b42',layers=layers,audio='audio.wav')
    # Rasterize the nested cut-out rig to a bounded image sequence, keeping SVG source.
    import resvg_py
    seq=p/'rig-frames';seq.mkdir(exist_ok=True)
    for f in range(frames):
        svg=character_svg(f,FPS)
        png=resvg_py.svg_to_bytes(svg_string=svg,font_files=[str(FONT)])
        (seq/f'{f:04d}.png').write_bytes(png)
    scene['layers'][2]['asset']='rig-frames/%04d.png'
    # The render API accepts frame-token image assets (expanded by render.py).
    save('01-2d-moonlight',scene)
    return scene

def render_character_video():
    from animation_mcp.render import render
    p=OUT/'01-2d-moonlight'
    qa=render(p/'scene.json',p/'render',p)
    (p/'qa.json').write_text(json.dumps(qa,indent=2))
    print('2D moonlight render',qa['technical_pass'],flush=True)
    return qa


def render_reaction_examples():
    from animation_mcp.reactions import compose_reactions
    base=OUT/'02-semantic-reactions'
    for name,heading,theme in [('brain','The missing brain cell','cartoon'),
                               ('disaster','A very bad rescue','anime'),
                               ('victory','The comeback','anime')]:
        p=base/name
        qa=compose_reactions(p/'narration.json',p,p,theme=theme,heading=heading,width=960,height=540,fps=30)
        print('Reaction',name,qa['technical_pass'],flush=True)


def render_3d_examples(level=None):
    from animation_mcp.blender_scene import render_3d
    from animation_mcp.presets import scene_preset,LEVELS
    for level in ([level] if level else LEVELS):
        p=OUT/f'03-3d-{level}';p.mkdir(parents=True,exist_ok=True)
        spec=scene_preset(level,width=800,height=450,samples=12)
        print('Rendering 3D',level,spec['frames'],'frames',flush=True)
        qa=render_3d(spec,p)
        (p/'qa.json').write_text(json.dumps(qa,indent=2))
        print('3D',level,'technical_pass',qa['technical_pass'],'rig_pass',qa.get('rig_pass'),flush=True)


def asset_based_short():
    from animation_mcp.edit import edit_video
    p=OUT/'04-asset-based-short';p.mkdir(parents=True,exist_ok=True)
    duration=9.0
    soundtrack(p/'music.wav',duration,[(0.1,'whoosh'),(4.0,'impact'),(7.0,'chime')])
    spec=dict(width=1280,height=720,fps=24,clips=[
        dict(path='01-2d-moonlight/render/video.mp4',start=0,duration=4.0),
        dict(path='03-3d-hard/video.mp4',start=1.0,duration=3.0),
        dict(path='03-3d-simple/video.mp4',start=1.0,duration=2.0),
    ],captions=[
        dict(text='Original 2D cut-out rig + painted background',start=.3,end=3.7),
        dict(text='Editable Blender shot: modeled set, IK rig, camera move',start=4.2,end=6.8),
        dict(text='Same toolkit, different engine — source projects included',start=7.1,end=8.8),
    ],audio='04-asset-based-short/music.wav',caption_position=.88)
    qa=edit_video(spec,p,OUT)
    (p/'qa.json').write_text(json.dumps(qa,indent=2))
    print('Asset-based short',qa['technical_pass'],flush=True)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['author','2d','reactions','3d','edit','all'],default='all')
    ap.add_argument('--level',choices=['easy','simple','medium','hard'],help='Render only one 3D level');a=ap.parse_args()
    if a.stage in ('author','all'):
        character_film();print('Authored 2D moonlight project',flush=True)
    if a.stage in ('2d','all'):
        render_character_video()
    if a.stage in ('reactions','all'):
        render_reaction_examples()
    if a.stage in ('3d','all'):
        render_3d_examples(a.level)
    if a.stage in ('edit','all'):
        asset_based_short()
