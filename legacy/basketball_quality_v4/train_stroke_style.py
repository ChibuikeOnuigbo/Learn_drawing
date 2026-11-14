"""Train a third, sunlight-edge ink label on the existing stroke features."""
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np,cv2
from train_drawing import outline_targets
from memory_draw import features
D=os.path.dirname(os.path.abspath(__file__));W,H=960,540
with np.load(os.path.join(D,'scene_strokes_v3.npz'),allow_pickle=False) as z:p={k:z[k].copy() for k in z.files}
y=outline_targets();im=cv2.cvtColor(cv2.imread(os.path.join(D,'3d_guide.png')),cv2.COLOR_BGR2RGB);mask=((im[:,:,0]>=230)&(im[:,:,0]<243)&(im[:,:,1]>=168)&(im[:,:,1]<192)&(im[:,:,2]>=95)&(im[:,:,2]<125)).astype('uint8');mask[:319]=0;mask=cv2.dilate(mask,np.ones((5,5),np.uint8));label=[]
for x1,y1,x2,y2 in y:
 xs=np.clip(np.rint(np.linspace(x1,x2,7)*W).astype(int),0,W-1);ys=np.clip(np.rint(np.linspace(y1,y2,7)*H).astype(int),0,H-1);label.append(float(mask[ys,xs].mean()>.5))
y=np.array(label,dtype='float32')[:,None];x=features(len(y));h=np.tanh(x@p['w1']+p['b1']);w=np.zeros((256,1),dtype='float32');b=np.array([-1.],dtype='float32');mw=np.zeros_like(w);vw=np.zeros_like(w);mb=np.zeros_like(b);vb=np.zeros_like(b)
for step in range(1,15001):
 z=h@w+b;pr=1/(1+np.exp(-np.clip(z,-20,20)));d=(pr-y)/len(y);gw=h.T@d;gb=d.sum(0);mw=.9*mw+.1*gw;vw=.999*vw+.001*gw*gw;mb=.9*mb+.1*gb;vb=.999*vb+.001*gb*gb;w-=.001*(mw/(1-.9**step))/(np.sqrt(vw/(1-.999**step))+1e-8);b-=.001*(mb/(1-.9**step))/(np.sqrt(vb/(1-.999**step))+1e-8)
p['w2']=np.concatenate([p['w2'],w],1);p['b2']=np.concatenate([p['b2'],b]);np.savez_compressed(os.path.join(D,'scene_strokes_style_v3.npz'),**p);acc=float(((h@w+b>0)==y).mean());res={'updates':15000,'sunlit_edge_labels':int(y.sum()),'in_sample_label_accuracy':acc,'note':'automatic same-scene labels; not new scene generalization'};json.dump(res,open(os.path.join(D,'stroke_style_results.json'),'w'),indent=2);print(res)
