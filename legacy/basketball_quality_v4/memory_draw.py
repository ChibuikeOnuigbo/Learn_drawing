"""Reference-free drawing worker: accepts weights and output path only."""
import os,sys,zipfile,encodings.cp437
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import numpy as np
from PIL import Image,ImageDraw,PngImagePlugin

def features(n):
 i=np.arange(n,dtype=np.float32)/(max(n-1,1)); freq=np.arange(1,97,dtype=np.float32)
 a=2*np.pi*i[:,None]*freq[None,:]
 return np.concatenate([i[:,None],np.sin(a),np.cos(a)],axis=1).astype('float32')

def draw(weight_path,output):
 # After imports, only the checkpoint may be opened for reading and the image for writing.
 # This denies access to reference images, teacher SVGs, and cached stroke files.
 allowed={os.path.realpath(weight_path),os.path.realpath(output)}
 def check(event,args):
  if event=='open' and args and isinstance(args[0],(str,bytes,os.PathLike)):
   if os.path.realpath(args[0]) not in allowed: raise PermissionError('memory drawing denied file access: '+str(args[0]))
 sys.addaudithook(check)
 with np.load(weight_path,allow_pickle=False) as z:
  assert set(z.files)=={'w1','b1','w2','b2','n','width','height'}
  p={k:z[k].copy() for k in z.files}
 n=int(p['n']); w=int(p['width']); h=int(p['height']); x=features(n)
 y=np.tanh(x@p['w1']+p['b1'])@p['w2']+p['b2'];y=np.clip(y,0,1)
 # White canvas and independently predicted straight strokes, no source image loaded.
 im=Image.new('RGB',(w*2,h*2),'white');painter=ImageDraw.Draw(im)
 for x1,y1,x2,y2 in y:
  painter.line((float(x1*w*2),float(y1*h*2),float(x2*w*2),float(y2*h*2)),fill=(25,24,30),width=2)
 im.save(output)
if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('usage: python memory_draw.py WEIGHTS.npz OUTPUT.png')
 draw(sys.argv[1],sys.argv[2])
