"""Original layered vector character: connected limbs, expressive face and poses.

Coordinates are authored at 400x560. The renderer uses true nested transforms;
this is an editable cut-out rig, not a flat image translated across a screen.
"""
from __future__ import annotations
import math
import xml.etree.ElementTree as ET

INK='#142536';SKIN='#f3c6a5';HAIR='#183b4b';COAT='#427c83';LIGHT='#75b7b4'

def ease(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)

def keyed(frame, keys):
    if frame<=keys[0][0]:return keys[0][1]
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if frame<b:return x+(y-x)*ease((frame-a)/(b-a))
    return keys[-1][1]

def path(g,d,fill,stroke=INK,width=3,**extra):
    return ET.SubElement(g,'path',d=d,fill=fill,stroke=stroke,**{'stroke-width':str(width),'stroke-linecap':'round','stroke-linejoin':'round',**{k.replace('_','-'):str(v) for k,v in extra.items()}})

def ellipse(g,cx,cy,rx,ry,fill,stroke='none',width=2):
    return ET.SubElement(g,'ellipse',cx=str(cx),cy=str(cy),rx=str(rx),ry=str(ry),fill=fill,stroke=stroke,**{'stroke-width':str(width)})

def limb(g,name,anchor,length1,length2,angle1,angle2,kind='arm'):
    root=ET.SubElement(g,'g',id=name,transform=f'translate({anchor[0]} {anchor[1]}) rotate({angle1})')
    w=19 if kind=='arm' else 23
    color=COAT if kind=='arm' else '#233849'
    path(root,f'M {-w} -8 Q 0 -19 {w} -8 L {w-2} {length1} Q 0 {length1+12} {-w+2} {length1} Z',color)
    path(root,f'M {-w+5} 8 L {-w+7} {length1-9}', 'none', LIGHT if kind=='arm' else '#456174',3)
    joint=ET.SubElement(root,'g',transform=f'translate(0 {length1}) rotate({angle2})',id=name+'-joint')
    ellipse(joint,0,0,w-2,w-2,color)
    path(joint,f'M {-w+2} -2 Q 0 -9 {w-2} -2 L {w-5} {length2} Q 0 {length2+8} {-w+5} {length2} Z',color)
    if kind=='arm':
        path(joint,f'M -15 {length2-13} L 15 {length2-13} L 14 {length2-2} L -14 {length2-2} Z','#d6e5dc',width=2)
        path(joint,f'M -12 {length2} Q -20 {length2+12} -12 {length2+24} Q -6 {length2+32} 2 {length2+27} L 12 {length2+20} Q 18 {length2+14} 12 {length2+10} L 7 {length2+14} L 10 {length2+2} Z',SKIN,width=2.5)
    else:
        path(joint,f'M -19 {length2-9} L 18 {length2-9} L 23 {length2+4} Q 42 {length2+7} 40 {length2+20} L -22 {length2+20} Q -28 {length2+8} -19 {length2-9} Z','#e7e6d7',width=3)
        path(joint,f'M -22 {length2+14} L 38 {length2+14}','none','#6b8c91',3)
    return root

def character_svg(frame:int,fps:int=24,expression:str='auto') -> str:
    """Return a standalone SVG master, with named pivot groups and face layers."""
    t=frame/fps
    root=ET.Element('svg',xmlns='http://www.w3.org/2000/svg',width='400',height='560',viewBox='0 0 400 560')
    defs=ET.SubElement(root,'defs')
    grad=ET.SubElement(defs,'linearGradient',id='coat',x1='0',y1='0',x2='1',y2='1')
    ET.SubElement(grad,'stop',offset='0%',stop_color='#639b9e');ET.SubElement(grad,'stop',offset='100%',stop_color='#2d5967')
    bob=keyed(frame,[(0,0),(20,-3),(40,0),(52,8),(66,-5),(82,0),(110,-2),(135,0),(160,-4),(185,0)])
    body=ET.SubElement(root,'g',id='body-pivot',transform=f'translate(0 {bob}) rotate({keyed(frame,[(0,0),(40,-3),(62,6),(85,-2),(120,0),(160,-4),(190,0)])} 200 365)')
    # Far limbs are behind torso; shoulder/elbow pivots remain anatomically connected.
    arm_l=keyed(frame,[(0,12),(35,20),(55,35),(75,15),(110,18),(148,-45),(170,-62),(190,-50)])
    arm_r=keyed(frame,[(0,-12),(35,-25),(55,-42),(75,-18),(110,-20),(148,-115),(170,-145),(190,-125)])
    limb(body,'arm-left',(143,246),65,61,arm_l,18+arm_l*.25)
    leg_angle=keyed(frame,[(0,0),(35,3),(55,10),(75,0),(190,0)])
    limb(body,'leg-left',(174,365),76,72,4+leg_angle,-leg_angle,'leg')
    limb(body,'leg-right',(225,365),76,72,-4-leg_angle,leg_angle,'leg')
    # Tailoring: actual silhouette, lapels, seam, belt and hanging pockets.
    path(body,'M 151 231 Q 177 218 201 226 Q 226 219 250 235 L 263 355 Q 245 383 204 380 Q 164 383 141 355 Z','url(#coat)',width=4)
    path(body,'M 184 226 L 202 241 L 220 226 L 231 285 L 201 300 L 173 282 Z','#e7e5d6',width=2)
    path(body,'M 178 228 L 161 250 L 178 267 L 168 280 L 197 308 L 187 247 Z','#8bbab6',width=2)
    path(body,'M 224 228 L 242 250 L 226 267 L 237 281 L 204 308 L 217 247 Z','#315c6b',width=2)
    path(body,'M 201 302 L 201 374','none','#a0c6be',2)
    path(body,'M 150 331 Q 199 342 257 331 L 258 345 Q 201 355 148 345 Z','#213d4d',width=2)
    ET.SubElement(body,'rect',x='192',y='335',width='20',height='15',rx='3',fill='#d5ad66',stroke=INK,stroke_width='2')
    path(body,'M 158 306 L 181 310 L 179 326 L 157 323 Z','#386773',width=2)
    path(body,'M 224 310 L 247 306 L 248 323 L 226 326 Z','#386773',width=2)
    ellipse(body,216,270,6,6,'#e7bc72',INK,1.5)
    limb(body,'arm-right',(253,246),65,61,arm_r,-18+arm_r*.12)
    # Neck and head rotate as a unit. Hair mass is not pasted over the eyes.
    head=ET.SubElement(body,'g',id='head-pivot',transform=f'translate(0 {keyed(frame,[(0,0),(45,-2),(65,5),(90,0),(145,-4),(175,0)])}) rotate({keyed(frame,[(0,-4),(40,-7),(62,8),(90,0),(135,-7),(165,3),(190,0)])} 202 214)')
    path(head,'M 185 203 L 184 230 Q 201 246 218 230 L 216 202 Z',SKIN,width=2)
    path(head,'M 133 139 Q 128 80 177 61 Q 235 35 268 92 Q 286 134 264 191 L 245 216 L 153 207 Z',HAIR,width=4)
    ellipse(head,143,166,13,20,SKIN,INK,2);ellipse(head,257,166,13,20,SKIN,INK,2)
    path(head,'M 148 126 Q 164 93 205 94 Q 244 95 253 131 L 251 174 Q 247 205 202 221 Q 159 208 150 180 Z',SKIN,width=3)
    path(head,'M 149 158 Q 159 191 178 199 Q 161 190 158 168 Z','#dda78f','none',0)
    # Fringe has separate locks and a restrained reflected-light shape.
    path(head,'M 137 141 Q 132 91 173 70 Q 230 43 263 94 L 265 143 L 247 158 L 237 113 L 218 147 L 202 112 L 180 148 L 171 116 L 150 157 Z',HAIR,width=3)
    path(head,'M 151 103 Q 174 73 208 73 Q 229 73 246 91 L 213 85 L 184 101 L 164 121 Z','#316476','none',0)
    path(head,'M 161 94 Q 181 76 201 78','none','#5a8b94',3)
    blink=(frame%89 in (43,44)) or (frame%113 in (91,92))
    mood=expression if expression!='auto' else ('shock' if 45<=frame<82 else ('happy' if frame>=137 else 'focus'))
    for side,cx in [('left',178),('right',225)]:
        eye=ET.SubElement(head,'g',id='eye-'+side)
        brow_y=145 if mood!='shock' else 138
        path(eye,f'M {cx-13} {brow_y} Q {cx} {brow_y-5 if mood=="happy" else brow_y+2} {cx+12} {brow_y-1}','none',HAIR,4)
        if blink:
            path(eye,f'M {cx-12} 165 Q {cx} 171 {cx+12} 164','none',INK,3)
        else:
            h=16 if mood=='shock' else 12
            path(eye,f'M {cx-14} 164 Q {cx} {164-h} {cx+14} 163 Q {cx+11} {164+h} {cx-1} {164+h} Q {cx-12} {164+h-2} {cx-14} 164 Z','#fff9ec',INK,2)
            ellipse(eye,cx+2,165,7,h-2,'#5b999e');ellipse(eye,cx+3,165,3.5,h-4,INK);ellipse(eye,cx+5,160,2.5,3,'#ffffff')
    path(head,'M 201 168 L 197 181 L 203 182','none','#bc826e',1.7)
    ellipse(head,163,183,9,3,'#e9a99b');ellipse(head,239,183,9,3,'#e9a99b')
    if mood=='shock':ellipse(head,202,197,7,9,INK)
    elif mood=='happy':
        path(head,'M 188 191 Q 202 199 217 190 Q 213 207 202 207 Q 192 204 188 191 Z','#fff9ec',INK,2)
    else:path(head,'M 192 197 Q 203 201 213 195','none',INK,2)
    # Small brass star pin and earring establish continuity across shots.
    ellipse(head,258,183,4,6,'#e8bd72',INK,1.5)
    return ET.tostring(root,encoding='unicode')
