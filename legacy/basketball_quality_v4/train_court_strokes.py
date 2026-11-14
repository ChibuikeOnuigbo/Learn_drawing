"""Learn projected 3D court marking centerline strokes, not doubled edge traces."""
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,cv2
from PIL import Image,ImageDraw
import build_scene as s
from memory_draw import features
from improve_training import update,optinit
D=os.path.dirname(os.path.abspath(__file__));W,H=960,540
s.build();targets=[]
# Render actual room-depth buffer without court marks. This is used only to
# build the training target: hidden floor markings are not visible strokes.
zbuf=np.full((H,W),np.inf,dtype='float32')
for ids,mat in s.faces:
 if mat=='mark':continue
 xyz=np.array([s.verts[i-1] for i in ids]);pts,depth=s.project(xyz)
 if np.any(depth<=.3):continue
 for k in range(1,len(ids)-1):
  tri=pts[[0,k,k+1]];dep=depth[[0,k,k+1]];x0=max(0,int(np.floor(tri[:,0].min())));x1=min(W-1,int(np.ceil(tri[:,0].max())));y0=max(0,int(np.floor(tri[:,1].min())));y1=min(H-1,int(np.ceil(tri[:,1].max())))
  if x1<x0 or y1<y0:continue
  xg=np.arange(x0,x1+1,dtype=np.float32)[None,:]+.5;yg=np.arange(y0,y1+1,dtype=np.float32)[:,None]+.5;ax,ay=tri[0];bx,by=tri[1];cx,cy=tri[2];den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
  if abs(den)<1e-8:continue
  w0=((by-cy)*(xg-cx)+(cx-bx)*(yg-cy))/den;w1=((cy-ay)*(xg-cx)+(ax-cx)*(yg-cy))/den;w2=1-w0-w1;dd=1/np.maximum(w0/dep[0]+w1/dep[1]+w2/dep[2],1e-8);view=zbuf[y0:y1+1,x0:x1+1];ok=(w0>=-1e-5)&(w1>=-1e-5)&(w2>=-1e-5)&(dd<view);view[ok]=dd[ok]
for ids,mat in s.faces:
 if mat!='mark':continue
 p=np.array([s.verts[i-1] for i in ids]);aa=(p[0]+p[3])/2;bb=(p[1]+p[2])/2;xy,z=s.project([aa,bb]);quad,_=s.project(p)
 if min(z)<=0:continue
 width=(np.linalg.norm(quad[0]-quad[3])+np.linalg.norm(quad[1]-quad[2]))/2
 # Sample along each 3D line for reliable room/bench occlusion and viewport clipping.
 count=max(2,int(np.linalg.norm(xy[0]-xy[1])*1.2)+1);ts=np.linspace(0,1,count);world=aa[None,:]*(1-ts[:,None])+bb[None,:]*ts[:,None];screen,depth=s.project(world);xi=np.rint(screen[:,0]).astype(int);yi=np.rint(screen[:,1]).astype(int);inside=(xi>=0)&(xi<W)&(yi>=0)&(yi<H)&(world[:,1]>=0)&(world[:,1]<=25)&(world[:,0]>=-8)&(world[:,0]<=8);visible=np.zeros(count,dtype=bool);ii=np.flatnonzero(inside);visible[ii]=depth[ii]<=zbuf[yi[ii],xi[ii]]+.06
 runs=np.diff(np.r_[False,visible,False].astype(int));starts=np.flatnonzero(runs==1);ends=np.flatnonzero(runs==-1)-1
 for first,last in zip(starts,ends):
  if last<=first:continue
  a=screen[first];b=screen[last];targets.append([a[0]/W,a[1]/H,b[0]/W,b[1]/H,np.clip(width,0.5,8)/8])
y=np.array(targets,dtype='float32');n=len(y);x=features(n);r=np.random.default_rng(915);p={'w1':(r.normal(0,.06,(193,256))).astype('float32'),'b1':np.zeros(256,'float32'),'w2':(r.normal(0,.05,(256,5))).astype('float32'),'b2':np.array([.5,.5,.5,.5,.3],dtype='float32')};opt=optinit(p)
def out(p):return np.clip(np.tanh(x@p['w1']+p['b1'])@p['w2']+p['b2'],0,1)
def paint(lines):
 im=Image.new('L',(W,H),0);d=ImageDraw.Draw(im)
 for x1,y1,x2,y2,w in lines:d.line((float(x1*W),float(y1*H),float(x2*W),float(y2*H)),fill=255,width=max(1,round(float(w*8))))
 return np.array(im)>0
before=out(p);best=1e9;beststep=0
for t in range(1,65001):
 ix=r.integers(0,n,256);a=x[ix];b=y[ix];h=np.tanh(a@p['w1']+p['b1']);z=h@p['w2']+p['b2'];delta=2*(z-b)/(len(ix)*5);g={'w2':h.T@delta,'b2':delta.sum(0)};dh=(delta@p['w2'].T)*(1-h*h);g['w1']=a.T@dh;g['b1']=dh.sum(0);update(p,opt,g,t,.00022 if t<35000 else .00008)
 if t%500==0:
  err=float(np.abs(out(p)-y).mean())
  if err<best:best=err;beststep=t;bestp={k:v.copy() for k,v in p.items()}
  if t%10000==0:print('step',t,'err',err,'best',best,flush=True)
bestp['n']=np.array(n);bestp['width']=np.array(W);bestp['height']=np.array(H);np.savez_compressed(os.path.join(D,'court_strokes_v4.npz'),**bestp)
truth=paint(y);pred=paint(out(bestp));k=np.ones((7,7),np.uint8);prec=float((pred&(cv2.dilate(truth.astype('uint8'),k)>0)).sum()/max(pred.sum(),1));rec=float((truth&(cv2.dilate(pred.astype('uint8'),k)>0)).sum()/max(truth.sum(),1));Image.fromarray(np.uint8(255-255*truth)).save(os.path.join(D,'court_visible_3d_trace.png'));Image.fromarray(np.uint8(255-255*pred)).save(os.path.join(D,'court_learned_strokes.png'));res={'steps':65000,'best_step':beststep,'segments':n,'mean_absolute_coordinate_and_width_error':best,'same_teacher_3px_f1':2*prec*rec/(prec+rec+1e-12),'note':'in-sample 3D-projected paths, not a test on a new court'};json.dump(res,open(os.path.join(D,'court_training_results.json'),'w'),indent=2);print(res)
# Separate 3D guide with painted court stripes removed; color only. The other geometry and lights remain.
s.faces[:]=[f for f in s.faces if f[1]!='mark'];cv2.imwrite(os.path.join(D,'3d_guide_unmarked.png'),s.render())
