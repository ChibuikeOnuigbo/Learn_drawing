"""Learn a sparse color-difference correction between old and new 3D guides.
It augments the older color network at render time, without loading either image.
"""
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
from PIL import Image
from train_drawing import feat,pred
from improve_training import update,optinit
D=os.path.dirname(os.path.abspath(__file__))
with np.load(os.path.join(D,'scene_color_v3.npz'),allow_pickle=False) as z:base={k:z[k].copy() for k in z.files}
w,h=384,216
old=np.asarray(Image.open(os.path.join(D,'baseline_v2','3d_guide.png')).convert('RGB').resize((w,h),Image.Resampling.BOX),dtype='float32').reshape(-1,3)/255
new=np.asarray(Image.open(os.path.join(D,'3d_guide_unmarked.png')).convert('RGB').resize((w,h),Image.Resampling.BOX),dtype='float32').reshape(-1,3)/255
target=new-old;xx,yy=np.meshgrid((np.arange(w)+.5)/w,(np.arange(h)+.5)/h);xy=np.stack([xx,yy],-1).reshape(-1,2).astype('float32');r=np.random.default_rng(563);freq=r.normal(0,11,(64,2)).astype('float32');x=feat(xy,freq);bx=feat(xy,base['frequencies']);original=np.concatenate([pred(v,base) for v in np.array_split(bx,8)]);change=(np.abs(target).max(1)>.03);perm=np.random.default_rng(759).permutation(len(x));cut=int(.75*len(x));tr,te=perm[:cut],perm[cut:];changed=tr[change[tr]];testchanged=te[change[te]]
print('changed training / validation',len(changed),len(testchanged),flush=True)
p={'w1':(r.normal(0,.07,(130,128))).astype('float32'),'b1':np.zeros(128,'float32'),'w2':(r.normal(0,.07,(128,128))).astype('float32'),'b2':np.zeros(128,'float32'),'w3':np.zeros((128,3),'float32'),'b3':np.zeros(3,'float32')};opt=optinit(p)
def predict(a,p):return np.tanh(np.tanh(a@p['w1']+p['b1'])@p['w2']+p['b2'])@p['w3']+p['b3']
def evaluate(p):
 result=[]
 for idx in [te,testchanged]:
  ae=0
  for ix in np.array_split(idx,8):ae+=float(np.abs(np.clip(original[ix]+predict(x[ix],p),0,1)-new[ix]).sum())
  result.append(ae/(len(idx)*3))
 return result
before=evaluate(p);best=before[1]*.8+before[0]*.2;bestp={k:v.copy() for k,v in p.items()};beststep=0
for step in range(1,50001):
 ix=np.concatenate([r.choice(changed,192,replace=True),r.choice(tr,192,replace=True)]);a=x[ix];b=target[ix];h1=np.tanh(a@p['w1']+p['b1']);h2=np.tanh(h1@p['w2']+p['b2']);v=h2@p['w3']+p['b3'];d=2*(v-b)/(len(ix)*3);g={'w3':h2.T@d,'b3':d.sum(0)};d=(d@p['w3'].T)*(1-h2*h2);g['w2']=h1.T@d;g['b2']=d.sum(0);d=(d@p['w2'].T)*(1-h1*h1);g['w1']=a.T@d;g['b1']=d.sum(0);update(p,opt,g,step,.0003 if step<30000 else .00012)
 if step%1000==0:
  total,roi=evaluate(p);score=.8*roi+.2*total
  if score<best:best=score;beststep=step;bestp={k:v.copy() for k,v in p.items()}
  if step%10000==0:print(step,'all',total,'changed',roi,'best',best,flush=True)
after=evaluate(bestp);bestp['frequencies']=freq;bestp['grid_w']=np.array(w);bestp['grid_h']=np.array(h);np.savez_compressed(os.path.join(D,'color_detail_v4.npz'),**bestp);res={'updates':50000,'best_step':beststep,'validation_all_before_mae':before[0],'validation_all_after_mae':after[0],'validation_changed_before_mae':before[1],'validation_changed_after_mae':after[1],'validation_changed_pixels':len(testchanged),'note':'changed pixels are automatically defined using both guides; validation is same image and was used to select checkpoints; not independent test'};json.dump(res,open(os.path.join(D,'color_detail_v4_results.json'),'w'),indent=2);print(res,flush=True)
