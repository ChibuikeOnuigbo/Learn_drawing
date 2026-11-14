"""Generate original, editable example scenes without downloaded artwork."""
import json
import math
from pathlib import Path
import random

ROOT=Path(__file__).resolve().parents[1]
layers=[]


def add(ident,kind,**kwargs):
    layer=dict(id=ident,kind=kind,**kwargs)
    layers.append(layer)
    return layer


def track(prop,*keys):
    return dict(property=prop,keys=[dict(frame=f,value=v,easing='smooth') for f,v in keys])


def main():
    rng=random.Random(41)
    for i in range(45):
        x,y=rng.randrange(1280),rng.randrange(70,590)
        add(f'star{i}','ellipse',x=x,y=y,width=2,height=2,fill='#637c9a',
            tracks=[track('x',(0,x),(179,x-12))])
    add('moon','ellipse',x=1000,y=180,width=160,height=160,fill='#1d415a')
    add('moon-core','ellipse',x=1015,y=163,width=105,height=105,fill='#295a6e')
    add('back-ridge','path',fill='#132e43',closed=True,
        points=[(0,480),(155,350),(280,440),(490,320),(680,470),(880,345),(1080,450),(1280,360),(1320,720),(-20,720)],
        tracks=[track('x',(0,0),(179,-25))])
    add('near-ridge','path',fill='#1b4352',closed=True,
        points=[(-50,650),(130,550),(330,600),(510,490),(760,610),(970,545),(1320,610),(1320,780),(-50,780)],
        tracks=[track('x',(0,0),(179,-70))])
    add('ground','path',fill='#0d202e',closed=True,points=[(-60,675),(260,600),(600,690),(920,645),(1320,660),(1320,750),(-60,750)])
    add('label','text',x=122,y=66,text='FIELD NOTES / 001',font_size=16,fill='#65dace')
    add('title','text',x=640,y=130,text='Small steps. New worlds.',font_size=46,fill='#f0f5f0',
        tracks=[track('opacity',(0,0),(22,1)),track('y',(0,148),(22,130))])
    # Original helmeted explorer, built from editable vector components.
    add('shadow','ellipse',x=370,y=632,width=200,height=25,fill='#070f19')
    add('left-boot','rect',x=330,y=606,width=52,height=70,fill='#9cb5bb')
    add('right-boot','rect',x=404,y=606,width=52,height=70,fill='#bdd0cb')
    add('pack','rect',x=310,y=490,width=80,height=132,fill='#173e4e')
    add('body','path',fill='#dae4d6',closed=True,points=[(318,453),(414,453),(441,572),(307,572)])
    add('arm-left','path',stroke='#dae4d6',stroke_width=28,points=[(321,471),(287,511),(298,546)])
    add('arm-right','path',stroke='#dae4d6',stroke_width=28,points=[(413,474),(457,497),(489,465)])
    add('cuff','ellipse',x=491,y=461,width=29,height=28,fill='#63d8cb')
    add('helmet','ellipse',x=367,y=400,width=137,height=137,fill='#e9ece0',stroke='#87a8ac',stroke_width=4,
        tracks=[track('y',(0,400),(65,394),(120,400),(179,396))])
    add('visor','ellipse',x=377,y=401,width=104,height=87,fill='#0e293b',stroke='#56c7ca',stroke_width=3,
        tracks=[track('y',(0,401),(65,395),(120,401),(179,397))])
    add('visor-shine','path',stroke='#b9f1df',stroke_width=5,points=[(355,376),(381,370),(400,374)])
    add('chest-panel','rect',x=365,y=505,width=48,height=45,fill='#173f50')
    for i in range(3):
        add(f'panel-light{i}','ellipse',x=351+14*i,y=502,width=6,height=6,fill='#65dace')
    # Draw a scientific orbit diagram on the right, not a fade of finished art.
    for i,radius in enumerate([90,135]):
        points=[(830+radius*math.cos(j*math.tau/100),395+radius*.56*math.sin(j*math.tau/100)) for j in range(101)]
        add(f'orbit{i}','path',stroke='#4c8793',stroke_width=2,points=points,
            tracks=[track('reveal',(28+i*8,0),(82+i*8,1))])
    add('planet','ellipse',x=830,y=395,width=70,height=70,fill='#f3b46d',
        tracks=[track('scale',(24,.01),(45,1.12),(55,1))])
    points=[(690,515),(725,488),(752,511),(779,451),(810,477),(844,430),(881,459),(918,405),(963,429)]
    add('signal','path',points=points,stroke='#70e2cf',stroke_width=4,
        tracks=[track('reveal',(75,0),(128,1))])
    add('diagram-label','text',x=830,y=577,text='OBSERVE  /  CONNECT  /  CREATE',font_size=18,fill='#8eb6bd',
        tracks=[track('opacity',(90,0),(115,1))])
    add('footer','text',x=640,y=695,text='ORIGINAL VECTOR ART  •  EDITABLE LAYERS  •  FRAME-ACCURATE MOTION',font_size=14,fill='#72a1ab')
    scene=dict(version=1,title='Field notes: an original layered explorer scene',width=1280,height=720,fps=30,frames=180,background='#0b192a',layers=layers)
    (ROOT/'examples/explorer.json').write_text(json.dumps(scene,indent=2)+'\n')
    objects=[dict(name='stage',kind='cylinder',color=[.025,.09,.14],location=[0,0,-.15],scale=[3.1,3.1,.15]),
             dict(name='core',kind='sphere',color=[.05,.65,.67],location=[0,0,1.55],scale=[.75,.75,.75]),
             dict(name='ring',kind='torus',color=[.85,.47,.17],location=[0,0,1.55],scale=[1.25,1.25,.18],
                  poses=[dict(frame=0,location=[0,0,1.55],rotation=[.35,.4,0]),
                         dict(frame=48,location=[0,0,1.55],rotation=[.35,.4,math.tau])])]
    for i in range(6):
        angle=i*math.tau/6
        pos=[2*math.cos(angle),2*math.sin(angle),.25]
        objects.append(dict(name=f'node{i}',kind='cube',color=[.15,.3,.4],location=pos,scale=[.25,.25,.25]))
    spec=dict(width=640,height=360,fps=24,frames=48,samples=48,camera=[6,-9,6],target=[0,0,.8],objects=objects)
    (ROOT/'examples/orbital-3d.json').write_text(json.dumps(spec,indent=2)+'\n')


if __name__=='__main__':
    main()
