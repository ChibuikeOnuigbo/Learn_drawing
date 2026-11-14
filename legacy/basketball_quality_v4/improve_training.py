"""Continue training the existing gym stroke/color and ball checkpoints.
Same teachers, same 75/25 pixel split; no reinforcement learning or new art training data.
Retain the best measured checkpoint. The line metric is in-sample.
"""
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,cv2
from PIL import Image,ImageDraw
from train_drawing import outline_targets,feat,pred
from memory_draw import features
D=os.path.dirname(os.path.abspath(__file__)); W,H=960,540

def load(n):
 with np.load(os.path.join(D,'previous_version',n),allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
def optinit(p):return {k:[np.zeros_like(v),np.zeros_like(v)] for k,v in p.items() if k[0] in 'wb'}
def update(p,o,g,t,lr):
 for k in g:
  m,v=o[k];m[:]=.9*m+.1*g[k];v[:]=.999*v+.001*g[k]*g[k];p[k]-=lr*(m/(1-.9**t))/(np.sqrt(v/(1-.999**t))+1e-8)
def segpred(x,p):return np.clip(np.tanh(x@p['w1']+p['b1'])@p['w2']+p['b2'],0,1)
def segmetric(y,p):
 def paint(lines):
  im=Image.new('L',(W,H));d=ImageDraw.Draw(im)
  for x1,y1,x2,y2 in lines:d.line((float(x1*W),float(y1*H),float(x2*W),float(y2*H)),fill=255,width=1)
  return np.asarray(im)>0
 a=paint(y);b=paint(p);k=np.ones((7,7),np.uint8);pr=float((b&(cv2.dilate(a.astype('uint8'),k)>0)).sum()/max(1,b.sum()));rec=float((a&(cv2.dilate(b.astype('uint8'),k)>0)).sum()/max(1,a.sum()));return 2*pr*rec/(pr+rec+1e-12)
def train_lines():
 y=outline_targets();x=features(len(y));p=load('scene_strokes.npz');o=optinit(p);r=np.random.default_rng(720);before=segpred(x,p);before_err=float(np.abs(before-y).mean());before_f=segmetric(y,before);best=before_err;bestp={k:v.copy() for k,v in p.items()};beststep=0
 for t in range(1,65001):
  ix=r.integers(0,len(y),384);a=x[ix];b=y[ix];h=np.tanh(a@p['w1']+p['b1']);z=h@p['w2']+p['b2'];delta=2*(z-b)/(len(ix)*4);g={'w2':h.T@delta,'b2':delta.sum(0)};d=(delta@p['w2'].T)*(1-h*h);g['w1']=a.T@d;g['b1']=d.sum(0);lr=.00022 if t<=35000 else .00010;update(p,o,g,t,lr)
  if t%1000==0:
   pp=segpred(x,p);err=float(np.abs(pp-y).mean())
   if err<best:best=err;beststep=t;bestp={k:v.copy() for k,v in p.items()}
   if t%10000==0:print('lines',t,'mae',err,'best',best,flush=True)
 np.savez_compressed(os.path.join(D,'scene_strokes.npz'),**bestp);after=segpred(x,bestp);return {'updates_additional':65000,'best_continuation_step':beststep,'in_sample_coordinate_mae_before':before_err,'in_sample_coordinate_mae_after':best,'in_sample_3px_f1_before':before_f,'in_sample_3px_f1_after':segmetric(y,after),'same_automatically_traced_lines':True}

def train_rgba(filename,teacher,seed,steps):
 p=load(filename);gw,gh=int(p['grid_w']),int(p['grid_h']);im=Image.open(os.path.join(D,teacher)).convert('RGBA' if filename=='ball_drawing.npz' else 'RGB').resize((gw,gh),Image.Resampling.LANCZOS if filename=='ball_drawing.npz' else Image.Resampling.BOX);y=np.asarray(im).astype('float32').reshape(-1,len(im.getbands()))/255;xx,yy=np.meshgrid((np.arange(gw)+.5)/gw,(np.arange(gh)+.5)/gh);xy=np.stack([xx,yy],-1).reshape(-1,2).astype('float32');x=feat(xy,p['frequencies']);r=np.random.default_rng(seed)
 # The exact prior split for each model, not a fresh test split.
 if filename=='scene_color.npz':perm=np.random.default_rng(932).permutation(len(x))
 else:perm=np.random.default_rng(124).permutation(len(x))
 cut=int(.75*len(x));tr,te=perm[:cut],perm[cut:];o=optinit(p);before=float(np.abs(pred(x[te],p)-y[te]).mean());best=before;bestp={k:v.copy() for k,v in p.items()};beststep=0
 for t in range(1,steps+1):
  ix=r.choice(tr,384,replace=True);a=x[ix];b=y[ix];h1=np.tanh(a@p['w1']+p['b1']);h2=np.tanh(h1@p['w2']+p['b2']);z=h2@p['w3']+p['b3'];v=1/(1+np.exp(-np.clip(z,-20,20)));delta=(2/(len(ix)*b.shape[1]))*(v-b)*v*(1-v);g={'w3':h2.T@delta,'b3':delta.sum(0)};d=(delta@p['w3'].T)*(1-h2*h2);g['w2']=h1.T@d;g['b2']=d.sum(0);d=(d@p['w2'].T)*(1-h1*h1);g['w1']=a.T@d;g['b1']=d.sum(0);lr=.00035 if t<=steps*.6 else .00015;update(p,o,g,t,lr)
  if t%1000==0:
   err=float(np.abs(pred(x[te],p)-y[te]).mean())
   if err<best:best=err;beststep=t;bestp={k:v.copy() for k,v in p.items()}
   if t%10000==0:print(filename,t,'excluded MAE',err,'best',best,flush=True)
 np.savez_compressed(os.path.join(D,filename),**bestp);return {'updates_additional':steps,'best_continuation_step':beststep,'before_excluded_same_image_mae':before,'after_excluded_same_image_mae':best,'held_out_positions':len(te),'note':'same image, random spatial split; repeated checkpoint selection used these positions; not a new-image test'}
def main():
 result={'lines':train_lines(),'gym_color':train_rgba('scene_color.npz','3d_guide.png',48,50000),'ball_color':train_rgba('ball_drawing.npz','3d_ball_guide.png',19,40000)}
 json.dump(result,open(os.path.join(D,'quality_training_results.json'),'w'),indent=2);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
