"""Original editable chibi character with a hierarchical 2D rig and four beats."""
import json
import math
from pathlib import Path
import re
import textwrap
from animation_mcp.speech import synthesize
from animation_mcp.render import render


def main():
    root=Path(__file__).resolve().parents[1];folder=root/'exmapels/2d-character';folder.mkdir(parents=True,exist_ok=True)
    text=('First, make the pose readable. Give the motion a little anticipation. '
          'Add a surprise, then let the character settle. Keep the design consistent in every shot.')
    audio=synthesize(text,folder/'speech',150)
    fps=24;frames=math.ceil((audio['duration']+.65)*fps);q=frames//4
    layers=[]
    def track(prop,keys):return dict(property=prop,keys=[dict(frame=f,value=v,easing='smooth') for f,v in keys])
    def add(ident,kind,parent=None,**kwargs):
        value=dict(id=ident,kind=kind,**kwargs)
        if parent:value['parent']=parent
        layers.append(value);return value
    def path(ident,points,fill='none',stroke='#243147',parent=None,**kw):
        kw.setdefault('stroke_width',3)
        return add(ident,'path',parent,points=points,fill=fill,stroke=stroke,**kw)
    add('halo','ellipse',x=350,y=278,width=390,height=390,fill='#e0e8e0')
    add('ground','ellipse',x=350,y=455,width=210,height=22,fill='#c2ceca')
    add('title','text',x=480,y=54,text='A character is more than a moving picture.',font_size=30,fill='#243147')
    add('actor','group',x=350,y=365)
    for side,x in [('left',-24),('right',24)]:
        add('leg-'+side,'rect','actor',x=x,y=42,width=31,height=74,fill='#293544')
        add('shoe-'+side,'ellipse','actor',x=x,y=84,width=47,height=23,fill='#faf5e9',stroke='#243147',stroke_width=3)
    add('upper-body','group','actor',tracks=[track('y',[(0,0),(q,-3),(2*q,1),(3*q,-2),(frames-1,0)]),
          track('rotation',[(0,0),(q//2,-3),(q,1),(2*q,0),(3*q,3),(frames-1,0)])])
    # Back arm remains behind the torso.
    add('arm-left','group','upper-body',x=-49,y=-85,rotation=-12)
    add('sleeve-left','rect','arm-left',y=32,width=27,height=66,fill='#766994',stroke='#243147',stroke_width=3)
    add('hand-left','ellipse','arm-left',y=75,width=27,height=30,fill='#f6ceb2',stroke='#243147',stroke_width=3)
    path('jacket',[(-50,-100),(50,-100),(62,-29),(44,9),(-44,9),(-62,-29)],'#786a97',parent='upper-body',closed=True)
    path('jacket-shadow',[(28,-96),(50,-100),(62,-29),(44,9),(24,9)],'#5b5077',stroke='none',parent='upper-body',closed=True)
    path('zip',[(0,-74),(0,7)],stroke='#d7d3cf',parent='upper-body',stroke_width=4)
    add('badge','ellipse','upper-body',x=-24,y=-53,width=18,height=18,fill='#e9c16b',stroke='#243147',stroke_width=2)
    add('hood','ellipse','upper-body',y=-103,width=110,height=45,fill='#5d5279',stroke='#243147',stroke_width=3)
    add('head','group','upper-body',y=-160,tracks=[track('rotation',[(0,-3),(q,3),(2*q,-5),(3*q,5),(frames-1,-2)])])
    path('hair-back',[(-91,-31),(-69,-93),(-17,-115),(57,-101),(92,-46),(87,62),(58,92),(-75,68)],'#255561',parent='head',closed=True)
    for side,x in [('left',-72),('right',72)]:
        add('ear-'+side,'ellipse','head',x=x,y=13,width=26,height=37,fill='#f6ceb2',stroke='#243147',stroke_width=3)
    add('face','ellipse','head',y=3,width=147,height=155,fill='#f7d4ba',stroke='#243147',stroke_width=3)
    for side,x in [('left',-34),('right',34)]:
        blink=[(0,1),(24,1),(26,.05),(28,1),(2*q-3,1),(2*q,.06),(2*q+5,1),(3*q+12,1),(3*q+14,.05),(3*q+16,1),(frames-1,1)]
        add('eye-'+side,'group','head',x=x,y=9,tracks=[track('scale_y',blink)])
        add('white-'+side,'ellipse','eye-'+side,width=40,height=49,fill='#fff9ef',stroke='#243147',stroke_width=3)
        add('iris-'+side,'ellipse','eye-'+side,width=27,height=40,fill='#438b91',stroke='#243147',stroke_width=2)
        add('pupil-'+side,'ellipse','eye-'+side,width=13,height=31,fill='#1b2b3d')
        add('shine-'+side,'ellipse','eye-'+side,x=-6,y=-10,width=9,height=12,fill='#ffffff')
        add('blush-'+side,'ellipse','head',x=x*1.36,y=39,width=24,height=10,fill='#eeb4ad',opacity=.65)
        path('brow-'+side,[(-17,0),(0,-5),(17,-2)],parent='head',x=x,y=-26,
             tracks=[track('rotation',[(0,-4),(q,12 if x<0 else -12),(2*q,0),(3*q,8),(frames-1,0)])])
    path('hair-front',[(-87,-24),(-72,-79),(-16,-110),(54,-98),(91,-47),(75,20),(48,0),(28,-40),(9,-9),(-9,-30),(-39,8),(-61,-2),(-81,25)],'#347482',parent='head',closed=True)
    path('hair-shine',[(-60,-64),(-16,-94),(42,-85),(12,-78),(-30,-56)],'#5aa0a3',stroke='none',parent='head',closed=True)
    path('smile',[(-16,42),(-9,48),(0,50),(9,48),(16,42)],parent='head',start=0,end=q)
    add('surprise','ellipse','head',y=49,width=20,height=27,fill='#5a3347',start=q,end=2*q)
    path('stress',[(-17,49),(-7,45),(5,45),(17,49)],parent='head',start=2*q,end=3*q)
    path('happy',[(-20,39),(-11,49),(0,53),(12,49),(20,39)],'#ffffff',parent='head',closed=True,start=3*q)
    # Front arm: preparation -> raised wave -> recoil -> facepalm -> settle.
    add('arm-right','group','upper-body',x=49,y=-85,tracks=[track('rotation',[(0,12),(8,28),(q//2,-140),(q,-125),
        (q+12,10),(2*q-8,10),(2*q+14,150),(3*q,150),(3*q+18,-35),(frames-1,-25)])])
    add('sleeve-right','rect','arm-right',y=27,width=27,height=58,fill='#8879a9',stroke='#243147',stroke_width=3)
    add('forearm','group','arm-right',y=55,tracks=[track('rotation',[(0,0),(q//2,20),(q,2),(2*q,0),(2*q+14,30),(3*q,30),(frames-1,0)])])
    add('cuff','rect','forearm',y=17,width=27,height=36,fill='#c8bdce',stroke='#243147',stroke_width=3)
    add('hand-right','ellipse','forearm',y=45,width=30,height=33,fill='#f6ceb2',stroke='#243147',stroke_width=3)
    for i in range(3):path('finger'+str(i),[(-6+i*6,34),(-7+i*6,44)],stroke='#c88e80',parent='forearm',stroke_width=1.5)
    # Clean information column; no copied character or downloaded art is used.
    for i,(label,detail) in enumerate([('POSE','A clear silhouette'),('ANTICIPATE','Prepare the action'),('REACT','Commit to the expression'),('SETTLE','Let the viewer read it')]):
        start=i*q;end=(i+1)*q if i<3 else frames
        add('panel'+str(i),'group',start=start,end=end)
        add('panel-box'+str(i),'rect','panel'+str(i),x=745,y=275,width=290,height=220,fill='#e5dedf')
        add('panel-num'+str(i),'text','panel'+str(i),x=745,y=240,text=f'0{i+1}',font_size=54,fill='#347482')
        add('panel-title'+str(i),'text','panel'+str(i),x=745,y=292,text=label,font_size=28,fill='#243147')
        add('panel-copy'+str(i),'text','panel'+str(i),x=745,y=330,text=detail,font_size=19,fill='#5d5279')
    sentences=list(re.finditer(r'[^.!?]+[.!?]?',text))
    # Retiming the acting beats to actual speech avoids equal-quarter timing
    # drifting away from narration sentences of different lengths.
    starts=[round(next(w['start'] for w in audio['words'] if w['char_start']>=m.start())*fps) for m in sentences]
    old=[0,q,2*q,3*q,frames-1];new=[*starts,frames-1]
    def retime(frame):
        if frame>=frames-1:return frame
        for a,b,x,y in zip(old,old[1:],new,new[1:]):
            if a<=frame<b:return round(x+(frame-a)/(b-a)*(y-x))
        return frame
    for layer in layers:
        if 'start' in layer:layer['start']=retime(layer['start'])
        if 'end' in layer:layer['end']=retime(layer['end'])
        for tr in layer.get('tracks',[]):
            # Closely spaced keys may quantize to one frame; retain the final value.
            keys={retime(k['frame']):dict(k,frame=retime(k['frame'])) for k in tr['keys']}
            tr['keys']=[keys[f] for f in sorted(keys)]
    # Caption starts are grounded in the actual generated speech events.
    for i,m in enumerate(sentences):
        word=next(w for w in audio['words'] if w['char_start']>=m.start())
        next_start=audio['duration'] if i==len(sentences)-1 else next(w['start'] for w in audio['words'] if w['char_start']>=sentences[i+1].start())
        lines=textwrap.wrap(m.group().strip(),64)
        for j,line in enumerate(lines):
            add(f'caption-{i}-{j}','text',x=480,y=503+j*27,text=line,font_size=24,fill='#243147',start=round(word['start']*fps),end=min(frames,max(round(word['start']*fps)+1,round(next_start*fps))))
    spec=dict(title='Original chibi character acting study',width=960,height=540,fps=fps,frames=frames,
              background='#f8f3eb',layers=layers,audio=str((folder/'speech/narration.wav').relative_to(root)))
    path_json=folder/'scene.json';path_json.write_text(json.dumps(spec,indent=2)+'\n')
    result=render(path_json,folder,root)
    # Clean visual master for later editing: captions and narration stay separate.
    clean=dict(spec,layers=[l for l in layers if not l['id'].startswith('caption-')],audio=None)
    clean_path=folder/'scene-clean.json';clean_path.write_text(json.dumps(clean,indent=2)+'\n')
    render(clean_path,folder/'clean',root)
    print(json.dumps(dict(video=result['video'],technical_pass=result['technical_pass']),indent=2))


if __name__=='__main__':main()
