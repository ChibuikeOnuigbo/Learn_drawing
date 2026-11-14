"""Render the 3D ball mesh using triangle depth; replaces the former painter-sort guide."""
import os,math
import numpy as np
from PIL import Image
from build_ball import mesh,vs,faces
D=os.path.dirname(os.path.abspath(__file__));mesh();v=np.array(vs);theta=.55;view=np.column_stack([v[:,0]*np.cos(theta)-v[:,1]*np.sin(theta),v[:,0]*np.sin(theta)+v[:,1]*np.cos(theta),v[:,2]])
scale=3;N=160*scale;canvas=np.zeros((N,N,4),dtype='uint8');depth=np.full((N,N),np.inf,dtype='float32')
for ids,mat in faces:
 p=view[np.array(ids)-1];q=np.stack([(80+p[:,0]*67)*scale,(80-p[:,2]*67)*scale],axis=1)
 if mat=='seam':col=(52,32,23,255)
 else:
  center=np.mean(v[np.array(ids)-1],axis=0);light=max(0,np.dot(center,np.array([-.3,-.75,.58])));col=(int(190+48*light),int(70+43*light),int(16+18*light),255)
 for k in range(1,len(ids)-1):
  tri=q[[0,k,k+1]];z=p[[0,k,k+1],1];x0=max(0,int(np.floor(tri[:,0].min())));x1=min(N-1,int(np.ceil(tri[:,0].max())));y0=max(0,int(np.floor(tri[:,1].min())));y1=min(N-1,int(np.ceil(tri[:,1].max())))
  if x1<x0 or y1<y0:continue
  x=np.arange(x0,x1+1)[None,:]+.5;y=np.arange(y0,y1+1)[:,None]+.5;ax,ay=tri[0];bx,by=tri[1];cx,cy=tri[2];den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
  if abs(den)<1e-8:continue
  w0=((by-cy)*(x-cx)+(cx-bx)*(y-cy))/den;w1=((cy-ay)*(x-cx)+(ax-cx)*(y-cy))/den;w2=1-w0-w1;zz=w0*z[0]+w1*z[1]+w2*z[2];buf=depth[y0:y1+1,x0:x1+1];ok=(w0>=0)&(w1>=0)&(w2>=0)&(zz<buf);buf[ok]=zz[ok];canvas[y0:y1+1,x0:x1+1][ok]=col
Image.fromarray(canvas,'RGBA').resize((160,160),Image.Resampling.LANCZOS).save(os.path.join(D,'3d_ball_guide_v3.png'))
