"""Fit a drawing memory to the improved 3D guide; not general art training or RL."""
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,cv2
from PIL import Image
from train_drawing import outline_targets,feat,pred
from memory_draw import features
from improve_training import update,optinit,segmetric
D=os.path.dirname(os.path.abspath(__file__));W,H=960,540

def lines():
 y=outline_targets();x=features(len(y));guide=cv2.cvtColor(cv2.imread(os.path.join(D,'3d_guide.png')),cv2.COLOR_BGR2RGB)
 mask=((guide[:,:,0]>232)&(guide[:,:,1]>215)&(guide[:,:,2]>185)).astype('uint8');mask[:320]=0;mask=cv2.dilate(mask,np.ones((5,5),np.uint8));labels=[]
 for x1,y1,x2,y2 in y:
  xs=np.clip(np.rint(np.linspace(x1,x2,7)*W).astype(int),0,W-1);ys=np.clip(np.rint(np.linspace(y1,y2,7)*H).astype(int),0,H-1);labels.append(float(mask[ys,xs].mean()>.5))
 label=np.array(labels,dtype='float32')[:,None]
 with np.load(os.path.join(D,'baseline_v2','scene_strokes.npz'),allow_pickle=False) as z:p={k:z[k].copy() for k in z.files}
 p['w2']=np.concatenate([p['w2'],np.zeros((256,1),dtype='float32')],axis=1);p['b2']=np.concatenate([p['b2'],np.array([-1.],dtype='float32')]);opt=optinit(p);r=np.random.default_rng(411)
 def evaluate(p):
  z=np.tanh(x@p['w1']+p['b1'])@p['w2']+p['b2'];coord=np.clip(z[:,:4],0,1);proba=1/(1+np.exp(-np.clip(z[:,4:],-20,20)));err=float(np.abs(coord-y).mean());accuracy=float(((proba>.5)==label).mean());return err,accuracy,coord
 before,acc0,c=evaluate(p);before_f=segmetric(y,c);best=before;bestp={k:v.copy() for k,v in p.items()};beststep=0
 for t in range(1,85001):
  ix=r.integers(0,len(y),384);a=x[ix];b=y[ix];lab=label[ix];h=np.tanh(a@p['w1']+p['b1']);z=h@p['w2']+p['b2'];pr=1/(1+np.exp(-np.clip(z[:,4:],-20,20)));delta=np.concatenate([2*(z[:,:4]-b)/(len(ix)*4),.15*(pr-lab)/len(ix)],axis=1);g={'w2':h.T@delta,'b2':delta.sum(0)};dh=(delta@p['w2'].T)*(1-h*h);g['w1']=a.T@dh;g['b1']=dh.sum(0);update(p,opt,g,t,.00025 if t<45000 else .00009)
  if t%1000==0:
   err,acc,_=evaluate(p)
   if err<best and acc>.98:best=err;beststep=t;bestp={k:v.copy() for k,v in p.items()}
   if t%10000==0:print('strokes',t,'error',err,'class accuracy',acc,'best',best,flush=True)
 np.savez_compressed(os.path.join(D,'scene_strokes_v3.npz'),**bestp);_,acc,c=evaluate(bestp)
 return {'updates':85000,'best_step':beststep,'segments':len(y),'teacher_white_segments':int(label.sum()),'before_in_sample_coordinate_mae':before,'after_in_sample_coordinate_mae':best,'before_in_sample_trace_f1_3px':before_f,'after_in_sample_trace_f1_3px':segmetric(y,c),'after_in_sample_stroke_color_accuracy':acc,'teacher':'automatically traced edges and automatic white-court-line labels from this guide'}

def color():
 with np.load(os.path.join(D,'baseline_v2','scene_color.npz'),allow_pickle=False) as z:p={k:z[k].copy() for k in z.files}
 w,h=int(p['grid_w']),int(p['grid_h']);im=Image.open(os.path.join(D,'3d_guide.png')).convert('RGB').resize((w,h),Image.Resampling.BOX);y=np.asarray(im).astype('float32').reshape(-1,3)/255;xx,yy=np.meshgrid((np.arange(w)+.5)/w,(np.arange(h)+.5)/h);xy=np.stack([xx,yy],-1).reshape(-1,2).astype('float32');x=feat(xy,p['frequencies']);order=np.random.default_rng(756).permutation(len(x));cut=int(.75*len(x));tr,te=order[:cut],order[cut:];r=np.random.default_rng(315);opt=optinit(p)
 def measure(p):return sum(float(np.abs(pred(x[i],p)-y[i]).sum()) for i in np.array_split(te,8))/(len(te)*3)
 before=measure(p);best=before;beststep=0;bestp={k:v.copy() for k,v in p.items()}
 for step in range(1,75001):
  ix=r.choice(tr,384,replace=True);a=x[ix];b=y[ix];h1=np.tanh(a@p['w1']+p['b1']);h2=np.tanh(h1@p['w2']+p['b2']);z=h2@p['w3']+p['b3'];v=1/(1+np.exp(-np.clip(z,-20,20)));d=(2/(len(ix)*3))*(v-b)*v*(1-v);g={'w3':h2.T@d,'b3':d.sum(0)};d=(d@p['w3'].T)*(1-h2*h2);g['w2']=h1.T@d;g['b2']=d.sum(0);d=(d@p['w2'].T)*(1-h1*h1);g['w1']=a.T@d;g['b1']=d.sum(0);update(p,opt,g,step,.0004 if step<45000 else .00015)
  if step%1000==0:
   err=measure(p)
   if err<best:best=err;beststep=step;bestp={k:v.copy() for k,v in p.items()}
   if step%10000==0:print('color',step,err,'best',best,flush=True)
 np.savez_compressed(os.path.join(D,'scene_color_v3.npz'),**bestp);return {'updates':75000,'best_step':beststep,'training_points':len(tr),'validation_points':len(te),'before_validation_mae':before,'after_validation_mae':best,'note':'positions from same guide, selected repeatedly to choose checkpoint; not unseen scenes'}
res={'strokes':lines(),'color':color()};json.dump(res,open(os.path.join(D,'v3_training_results.json'),'w'),indent=2);print(json.dumps(res,indent=2))
