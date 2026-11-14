"""Train per-scene color and stroke memories on the 3D guide (not on generated reference images)."""
import os,json,sys
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,cv2
from PIL import Image,ImageDraw
D=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.dirname(D);W,H=960,540
sys.path.insert(0,D);import memory_draw

def outline_targets():
 im=cv2.imread(os.path.join(D,'3d_guide.png'));gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY);edge=cv2.Canny(gray,50,110);contours,_=cv2.findContours(edge,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE);segs=[]
 for c in contours:
  p=cv2.approxPolyDP(c,1.0,False).reshape(-1,2)
  for a,b in zip(p,p[1:]):
   n=float(np.linalg.norm(a-b))
   if n>=1.5:segs.append((a,b,n))
 segs=sorted(segs,key=lambda r:r[2],reverse=True)[:1024];segs.sort(key=lambda r:((r[0][1]+r[1][1])/2,(r[0][0]+r[1][0])/2));return np.array([[a[0]/W,a[1]/H,b[0]/W,b[1]/H] for a,b,_ in segs],dtype='float32')
def outline():
 target=outline_targets();n=len(target);x=memory_draw.features(n);r=np.random.default_rng(840);p={'w1':(r.normal(0,.06,(193,256))).astype('float32'),'b1':np.zeros(256,'float32'),'w2':(r.normal(0,.05,(256,4))).astype('float32'),'b2':np.full(4,.5,'float32')};opt={k:[np.zeros_like(v),np.zeros_like(v)] for k,v in p.items()};best=None;loss=1e9;beststep=0
 for step in range(1,26001):
  ix=r.integers(0,n,192);a=x[ix];y=target[ix];h=np.tanh(a@p['w1']+p['b1']);z=h@p['w2']+p['b2'];delta=2*(z-y)/(192*4);g={'w2':h.T@delta,'b2':delta.sum(0)};dh=(delta@p['w2'].T)*(1-h*h);g['w1']=a.T@dh;g['b1']=dh.sum(0)
  for k in p:
   m,v=opt[k];m[:]=.9*m+.1*g[k];v[:]=.999*v+.001*g[k]*g[k];p[k]-=.00065*(m/(1-.9**step))/(np.sqrt(v/(1-.999**step))+1e-8)
  if step%500==0:
   pred=np.clip(np.tanh(x@p['w1']+p['b1'])@p['w2']+p['b2'],0,1);err=float(np.abs(pred-target).mean())
   if err<loss:loss=err;best={k:v.copy() for k,v in p.items()};beststep=step
   if step%6500==0:print('outline',step,err,'best',loss,flush=True)
 p=best;pred=np.clip(np.tanh(x@p['w1']+p['b1'])@p['w2']+p['b2'],0,1);np.savez_compressed(os.path.join(D,'scene_strokes.npz'),**p,n=np.array(n),width=np.array(W),height=np.array(H))
 def paint(a):
  im=Image.new('L',(W,H),255);d=ImageDraw.Draw(im)
  for x1,y1,x2,y2 in a:d.line((float(x1*W),float(y1*H),float(x2*W),float(y2*H)),fill=0,width=1)
  return np.asarray(im)<128
 a=paint(target);b=paint(pred);k=np.ones((7,7),np.uint8);prec=(b&(cv2.dilate(a.astype('uint8'),k)>0)).sum()/max(1,b.sum());rec=(a&(cv2.dilate(b.astype('uint8'),k)>0)).sum()/max(1,a.sum());f=float(2*prec*rec/(prec+rec+1e-12));return {'segments':n,'updates':26000,'best_training_step':beststep,'mean_coordinate_error_normalized':loss,'teacher_trace_f1_3px':f,'split':'in-sample lines against the auto-derived training trace'}

def feat(x,f):
 a=2*np.pi*(x@f.T);return np.concatenate([x,np.sin(a),np.cos(a)],1).astype('float32')
def pred(x,p):
 h=np.tanh(x@p['w1']+p['b1']);b=np.tanh(h@p['w2']+p['b2']);v=b@p['w3']+p['b3'];return 1/(1+np.exp(-np.clip(v,-20,20)))
def colors():
 gw,gh=192,108;img=cv2.imread(os.path.join(D,'3d_guide.png'));im=cv2.cvtColor(cv2.resize(img,(gw,gh),interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2RGB).astype('float32')/255;y=im.reshape(-1,3)
 xx,yy=np.meshgrid((np.arange(gw)+.5)/gw,(np.arange(gh)+.5)/gh);xy=np.stack([xx,yy],-1).reshape(-1,2).astype('float32');f=np.random.default_rng(202).normal(0,6,(64,2)).astype('float32');x=feat(xy,f);perm=np.random.default_rng(932).permutation(len(x));cut=int(.75*len(x));tr,te=perm[:cut],perm[cut:];r=np.random.default_rng(843)
 p={'w1':(r.normal(0,.09,(130,128))).astype('float32'),'b1':np.zeros(128,'float32'),'w2':(r.normal(0,.08,(128,128))).astype('float32'),'b2':np.zeros(128,'float32'),'w3':(r.normal(0,.08,(128,3))).astype('float32'),'b3':np.zeros(3,'float32')};opt={k:[np.zeros_like(v),np.zeros_like(v)] for k,v in p.items()}
 initial=float(np.abs(pred(x[te],p)-y[te]).mean())
 for step in range(1,20001):
  ix=r.choice(tr,256,replace=True);a=x[ix];b=y[ix];h1=np.tanh(a@p['w1']+p['b1']);h2=np.tanh(h1@p['w2']+p['b2']);z=h2@p['w3']+p['b3'];v=1/(1+np.exp(-np.clip(z,-20,20)));delta=(2/(len(ix)*3))*(v-b)*v*(1-v);g={'w3':h2.T@delta,'b3':delta.sum(0)};d=(delta@p['w3'].T)*(1-h2*h2);g['w2']=h1.T@d;g['b2']=d.sum(0);d=(d@p['w2'].T)*(1-h1*h1);g['w1']=a.T@d;g['b1']=d.sum(0)
  for k in p:
   m,vv=opt[k];m[:]=.9*m+.1*g[k];vv[:]=.999*vv+.001*g[k]*g[k];p[k]-=.0008*(m/(1-.9**step))/(np.sqrt(vv/(1-.999**step))+1e-8)
  if step%5000==0:print('color',step,'excluded_position_mae',float(np.abs(pred(x[te],p)-y[te]).mean()),flush=True)
 np.savez_compressed(os.path.join(D,'scene_color.npz'),**p,frequencies=f,grid_w=np.array(gw),grid_h=np.array(gh));return {'updates':20000,'training_positions':len(tr),'excluded_positions':len(te),'excluded_same_scene_color_mae_untrained':initial,'excluded_same_scene_color_mae_trained':float(np.abs(pred(x[te],p)-y[te]).mean()),'split':'random interspersed points in one 3D guide, not unseen scenes'}
def main():
 out={'outline':outline(),'color':colors()};json.dump(out,open(os.path.join(D,'drawing_training_results.json'),'w'),indent=2);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
