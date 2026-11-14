"""Continue ball RGBA memory using the depth-correct 3D render as teacher."""
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
from PIL import Image
from train_drawing import feat,pred
from improve_training import update,optinit
D=os.path.dirname(os.path.abspath(__file__))
with np.load(os.path.join(D,'ball_drawing.npz'),allow_pickle=False) as z:p={k:z[k].copy() for k in z.files}
w,h=int(p['grid_w']),int(p['grid_h']);im=Image.open(os.path.join(D,'3d_ball_guide_v3.png')).convert('RGBA').resize((w,h),Image.Resampling.LANCZOS);y=np.asarray(im).astype('float32').reshape(-1,4)/255;xx,yy=np.meshgrid((np.arange(w)+.5)/w,(np.arange(h)+.5)/h);x=feat(np.stack([xx,yy],-1).reshape(-1,2).astype('float32'),p['frequencies']);o=np.random.default_rng(554).permutation(len(x));n=int(len(x)*.75);tr,te=o[:n],o[n:];r=np.random.default_rng(333);opt=optinit(p)
def measure(p):return float(np.abs(pred(x[te],p)-y[te]).mean())
before=measure(p);best=before;beststep=0;bestp={k:v.copy() for k,v in p.items()}
for t in range(1,45001):
 ix=r.choice(tr,384,replace=True);a=x[ix];b=y[ix];h1=np.tanh(a@p['w1']+p['b1']);h2=np.tanh(h1@p['w2']+p['b2']);z=h2@p['w3']+p['b3'];v=1/(1+np.exp(-np.clip(z,-20,20)));d=(2/(len(ix)*4))*(v-b)*v*(1-v);g={'w3':h2.T@d,'b3':d.sum(0)};d=(d@p['w3'].T)*(1-h2*h2);g['w2']=h1.T@d;g['b2']=d.sum(0);d=(d@p['w2'].T)*(1-h1*h1);g['w1']=a.T@d;g['b1']=d.sum(0);update(p,opt,g,t,.00035 if t<28000 else .00015)
 if t%1000==0:
  err=measure(p)
  if err<best:best=err;beststep=t;bestp={k:v.copy() for k,v in p.items()}
  if t%10000==0:print(t,err,best,flush=True)
np.savez_compressed(os.path.join(D,'ball_drawing_v3.npz'),**bestp);res={'additional_updates':45000,'best_step':beststep,'validation_points':len(te),'before_mae':before,'after_mae':best,'note':'same-image held-out coordinates, used to select checkpoint, not new ball views'};json.dump(res,open(os.path.join(D,'ball_v3_results.json'),'w'),indent=2);print(res,flush=True)
