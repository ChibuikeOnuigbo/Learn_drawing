#!/usr/bin/env python3
"""Generate the procedural asset kit, a contact sheet and a layered demo composite.

Outputs bulky PNG sequences to gitignored data/assets; commits only the small
contact sheet, demo video, scene JSON and manifests under examples/10-procedural-assets.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from animation_mcp.procedural import generate, KINDS
from animation_mcp.planner import composite_scene
from animation_mcp.render import render

FONT=ROOT/'src/animation_mcp/assets/fonts/inter-400.ttf'

def main():
    kit=ROOT/'data/assets/kit'; kit.mkdir(parents=True,exist_ok=True)
    example=ROOT/'examples/10-procedural-assets'; example.mkdir(parents=True,exist_ok=True)
    manifests={}
    for kind in KINDS:
        frames=48 if KINDS[kind]=='loop' else 1
        m=generate(kind,kit/kind,seed=11,width=384,height=384,frames=frames,variant=0)
        manifests[kind]=m
        print('asset',kind,flush=True)
    # Contact sheet over a neutral dark background so alpha is visible.
    cols=5; tile=200; rows=(len(KINDS)+cols-1)//cols
    sheet=Image.new('RGB',(cols*tile,rows*(tile+26)+40),'#101827')
    draw=ImageDraw.Draw(sheet); font=ImageFont.truetype(str(FONT),14)
    draw.text((10,10),'Procedural asset kit — original code-generated PNG/loops (seed 11)',font=font,fill='white')
    for i,(kind,m) in enumerate(manifests.items()):
        path=kit/kind/m['files'][0]
        im=Image.open(path).convert('RGBA'); im.thumbnail((tile-12,tile-12))
        bg=Image.new('RGBA',(tile,tile),'#1e293b'); bg.paste(im,((tile-im.width)//2,(tile-im.height)//2),im)
        x=(i%cols)*tile; y=40+(i//cols)*(tile+26)
        sheet.paste(bg.convert('RGB'),(x,y))
        draw.text((x+8,y+tile+4),kind,font=font,fill='#dbeafe')
    sheet.save(example/'contact-sheet.jpg',quality=90)
    # Demo background gradient.
    w,h=960,540
    yy,xx=np.mgrid[0:h,0:w]
    t=yy/h
    bg=np.zeros((h,w,3),np.uint8)
    bg[:,:,0]=(18+30*t).astype(np.uint8); bg[:,:,1]=(24+36*t).astype(np.uint8); bg[:,:,2]=(40+50*t).astype(np.uint8)
    Image.fromarray(bg).save(kit/'background.png')
    # Longer overlay loops matching the demo timeline.
    generate('snow',kit/'snow-demo',seed=5,width=w,height=h,frames=144)
    generate('fog',kit/'fog-demo',seed=6,width=w,height=h,frames=144)
    generate('vignette',kit/'vignette-demo',seed=0,width=w,height=h)
    rel=lambda p: str(Path(p).resolve().relative_to(ROOT))
    layers=[
        {'id':'background','asset':rel(kit/'background.png'),'depth':0,'width':w,'height':h,'x':w/2,'y':h/2,'parallax':4},
        {'id':'clouds','asset':rel(kit/'cloud/cloud.png'),'depth':0.1,'width':500,'height':250,'x':700,'y':110,'opacity':0.5,'parallax':10},
        {'id':'pine-far','asset':rel(kit/'tree_pine/tree_pine.png'),'depth':0.2,'width':260,'height':260,'x':180,'y':330,'opacity':0.7,'parallax':12},
        {'id':'oak-mid','asset':rel(kit/'tree_oak/tree_oak.png'),'depth':0.45,'width':420,'height':420,'x':640,'y':300,'parallax':22},
        {'id':'rock','asset':rel(kit/'rock/rock.png'),'depth':0.6,'width':180,'height':180,'x':380,'y':450,'parallax':28},
        {'id':'grass','asset':rel(kit/'grass_clump/grass_clump.png'),'depth':0.75,'width':300,'height':300,'x':120,'y':470,'parallax':36},
        {'id':'snow','asset':rel(kit/'snow-demo/snow-%04d.png'),'depth':0.9,'width':w,'height':h,'x':w/2,'y':h/2,'opacity':0.85,'parallax':0},
        {'id':'fog','asset':rel(kit/'fog-demo/fog-%04d.png'),'depth':0.95,'width':w,'height':h,'x':w/2,'y':h/2,'opacity':0.5,'parallax':0},
        {'id':'vignette','asset':rel(kit/'vignette-demo/vignette.png'),'depth':1,'width':w,'height':h,'x':w/2,'y':h/2,'parallax':0},
    ]
    scene=composite_scene(layers,width=w,height=h,fps=24,frames=144,background='#101827',title='Procedural winter composite')
    scene_path=example/'scene.json'; scene_path.write_text(json.dumps(scene,indent=2)+'\n')
    qa=render(scene_path,example/'render',ROOT)
    (example/'manifest.json').write_text(json.dumps({'assets':manifests,'demo':{'scene':'scene.json','video':'render/video.mp4','qa':'render/inspection/qa.json'}},indent=2)+'\n')
    print(json.dumps({'technical_pass':qa['technical_pass'],'frames':qa['frames'],'contact_sheet':str(example/'contact-sheet.jpg')},indent=2))
if __name__=='__main__':main()
