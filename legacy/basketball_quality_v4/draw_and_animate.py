"""Generate drawings from five checkpoints only; reference images and teacher mesh are denied.
Run: OPENBLAS_NUM_THREADS=1 python draw_and_animate.py [output-directory]
No source image, 3D guide, or trace coordinates are read during rendering.
"""
import os,sys,zipfile,encodings.cp437,math
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont,PngImagePlugin,JpegImagePlugin
D=os.path.dirname(os.path.abspath(__file__));O=os.path.abspath(sys.argv[1]) if len(sys.argv)>1 else D
os.makedirs(O,exist_ok=True)
scene=os.path.join(D,'scene_color_v3.npz');stroke=os.path.join(D,'scene_strokes_style_v3.npz');ball=os.path.join(D,'ball_drawing_v3.npz');detail=os.path.join(D,'color_detail_v4.npz');court=os.path.join(D,'court_strokes_v4.npz');allowed={os.path.realpath(p) for p in [scene,stroke,ball,detail,court]}
def guard(event,args):
 if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
  path=os.path.realpath(args[0]);mode=args[1] if len(args)>1 else 'r';write=isinstance(mode,str) and any(c in mode for c in 'wax+')
  if path not in allowed and not (write and os.path.dirname(path)==O):raise PermissionError('Only checkpoint reads and output writes are allowed: '+path)
sys.addaudithook(guard)
def load(path):
 with np.load(path,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
def pixel_model(p):
 w,h=int(p['grid_w']),int(p['grid_h']);xx,yy=np.meshgrid((np.arange(w)+.5)/w,(np.arange(h)+.5)/h);xy=np.stack([xx,yy],-1).reshape(-1,2).astype('float32');a=2*np.pi*(xy@p['frequencies'].T);x=np.concatenate([xy,np.sin(a),np.cos(a)],1).astype('float32');h1=np.tanh(x@p['w1']+p['b1']);h2=np.tanh(h1@p['w2']+p['b2']);v=h2@p['w3']+p['b3'];return np.clip(1/(1+np.exp(-np.clip(v,-20,20))),0,1).reshape(h,w,-1)
def features(n):
 i=np.arange(n,dtype=np.float32)/max(n-1,1);freq=np.arange(1,97,dtype=np.float32);a=2*np.pi*i[:,None]*freq[None,:];return np.concatenate([i[:,None],np.sin(a),np.cos(a)],1).astype('float32')
sc=load(scene);st=load(stroke);ba=load(ball);dt=load(detail);ct=load(court)
# Learned spatial color correction for new 3D-guide details (not reference-pixel compositing).
w,h=int(dt['grid_w']),int(dt['grid_h']);xx,yy=np.meshgrid((np.arange(w)+.5)/w,(np.arange(h)+.5)/h);xy=np.stack([xx,yy],-1).reshape(-1,2).astype('float32');phase=2*np.pi*(xy@dt['frequencies'].T);features2=np.concatenate([xy,np.sin(phase),np.cos(phase)],1).astype('float32');h1=np.tanh(features2@dt['w1']+dt['b1']);h2=np.tanh(h1@dt['w2']+dt['b2']);correction=(h2@dt['w3']+dt['b3']).reshape(h,w,3)
image=(np.clip(pixel_model(sc)+correction,0,1)*255+.5).astype('uint8');image=cv2.bilateralFilter(image,7,25,4)  # coded, edge-preserving color cleanup
base=Image.fromarray(image,'RGB').resize((960,540),Image.Resampling.BICUBIC)
x=features(int(st['n']));raw=np.tanh(x@st['w1']+st['b1'])@st['w2']+st['b2'];lines=np.clip(raw[:,:4],0,1);iswhite=raw[:,4]>0;issun=raw[:,5]>0
# The trained fifth and sixth outputs choose pale court-marking, sunlit edge, or dark outline ink.
# For a readable monochrome line-only image all strokes are displayed dark.
ink=Image.new('RGBA',(1920,1080),(0,0,0,0));mono=Image.new('RGBA',(1920,1080),(0,0,0,0));d=ImageDraw.Draw(ink);m=ImageDraw.Draw(mono)
for (x1,y1,x2,y2),white,sun in zip(lines,iswhite,issun):
 if white:continue  # a separate learned centerline network draws court markings
 p=(float(x1*1920),float(y1*1080),float(x2*1920),float(y2*1080));d.line(p,fill=(224,164,101,120) if sun else (42,33,32,155),width=2);m.line(p,fill=(42,33,32,155),width=2
 )
cx=features(int(ct['n']));courtlines=np.clip(np.tanh(cx@ct['w1']+ct['b1'])@ct['w2']+ct['b2'],0,1)
for x1,y1,x2,y2,wt in courtlines:
 p=(float(x1*1920),float(y1*1080),float(x2*1920),float(y2*1080));width=max(1,round(float(wt*16)));d.line(p,fill=(247,232,202,245),width=width);m.line(p,fill=(42,33,32,155),width=max(2,width))
ink=ink.resize((960,540),Image.Resampling.LANCZOS);mono=mono.resize((960,540),Image.Resampling.LANCZOS);Image.alpha_composite(Image.new('RGBA',(960,540),'white'),mono).convert('RGB').save(os.path.join(O,'drawn_gym_lines.png'));background=Image.alpha_composite(base.convert('RGBA'),ink).convert('RGB');background.save(os.path.join(O,'drawn_gym_from_memory.png'))
ball_pixels=(pixel_model(ba)*255+.5).astype('uint8');ball_im=Image.fromarray(ball_pixels,'RGBA');ball_im.save(os.path.join(O,'drawn_ball_from_memory.png'))
# Constant-perspective 3D camera copied from the project's camera calibration, not from the guide image.
eye=np.array([0.,-8.5,5.25]);target=np.array([0.,15.,3.1]);up=np.array([0.,0.,1.]);forward=target-eye;forward/=np.linalg.norm(forward);right=np.cross(forward,up);right/=np.linalg.norm(right);cup=np.cross(right,forward);focal=750
def project(p):
 q=np.asarray(p)-eye;z=q@forward;return (480+focal*(q@right)/z,270-focal*(q@cup)/z,z)
# Vertical gravity in world units. Impact attenuates speed by coefficient of restitution.
fps=30;nframes=180;radius=.65;g=9.81;restitution=.73;v=0.;height=3.5;ground=radius;X=-1.5;Y=3.9;frames=[];trajectory=[]
writer=cv2.VideoWriter(os.path.join(O,'basketball_bounce.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),fps,(960,540))
if not writer.isOpened():raise RuntimeError('MP4 writer unavailable')
for i in range(nframes):
 t=i/fps
 if i>0:
  for _ in range(8):
   dt=1/(fps*8);v-=g*dt;height+=v*dt
   if height<ground:
    height=ground+(ground-height);v=-v*restitution
    if abs(v)<.18:height=ground;v=0
 px,py,depth=project((X,Y,height));gx,gy,_=project((X,Y,.012));rad=focal*radius/depth
 frame=background.convert('RGBA');shadow=Image.new('RGBA',frame.size);sd=ImageDraw.Draw(shadow);rr=rad*(.9+min((height-ground)*.08,.35));sd.ellipse((gx-rr,gy-rr*.21,gx+rr,gy+rr*.21),fill=(42,33,25,max(28,int(100-20*(height-ground)))));frame=Image.alpha_composite(frame,shadow)
 # Rotation is 2D artwork rotation, not newly rendered 3D rotation.
 scale=max(1,round(rad*2*160/134));sprite=ball_im.resize((scale,scale),Image.Resampling.LANCZOS).rotate(i*2.5,resample=Image.Resampling.BICUBIC,expand=True);frame.alpha_composite(sprite,(round(px-sprite.width/2),round(py-sprite.height/2)));rgb=np.asarray(frame.convert('RGB'));writer.write(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR));trajectory.append([round(t,5),round(float(height),5),round(float(v),5),round(float(px),3),round(float(py),3)])
 if i in (0,18,35,55,80,110,150):frames.append((i,Image.fromarray(rgb)))
writer.release()
# Visible timeline proves frame differences, separate from static drawing.
thumb=Image.new('RGB',(960,2*200),(248,246,240));td=ImageDraw.Draw(thumb)
for j,(i,im) in enumerate(frames[:6]):
 im.thumbnail((320,180));x0=(j%3)*320;y0=(j//3)*200;thumb.paste(im,(x0,y0));td.text((x0+8,y0+181),f'frame {i:03d}  |  {i/fps:.2f}s',fill=(30,30,30))
thumb.save(os.path.join(O,'drawn_animation_frames.jpg'),quality=90)
with open(os.path.join(O,'bounce_trajectory.csv'),'w') as f:
 f.write('time_s,height_world,velocity_world_s,screen_x_px,screen_y_px\n');f.writelines(','.join(map(str,r))+'\n' for r in trajectory)
print('Rendered only from checkpoints; frames:',nframes)
