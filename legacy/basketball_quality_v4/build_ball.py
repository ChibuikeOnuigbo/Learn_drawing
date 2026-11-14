"""Export a genuine 3D ball mesh with raised seam ribbons in local coordinates."""
import math,os
import numpy as np
D=os.path.dirname(os.path.abspath(__file__));vs=[];faces=[]
def mesh():
 for i in range(25):
  phi=math.pi*i/24
  for j in range(48):
   a=2*math.pi*j/48;vs.append((math.sin(phi)*math.cos(a),math.sin(phi)*math.sin(a),math.cos(phi)))
 for i in range(24):
  for j in range(48):
   a=i*48+j+1;b=i*48+(j+1)%48+1;faces.append(([a,b,b+48,a+48],'ball'))
 # Three great circles, represented as thin ribbons a little above the sphere.
 for k in range(3):
  start=len(vs)
  for i in range(97):
   a=2*math.pi*i/96;c=math.cos(a);s=math.sin(a);eps=.018
   if k==0:p=np.array([0.,c,s]);n=np.array([1.,0.,0.])
   elif k==1:p=np.array([c,0.,s]);n=np.array([0.,1.,0.])
   else:p=np.array([c,s,0.]);n=np.array([0.,0.,1.])
   for sign in [-1,1]:vs.append(tuple(p*1.003+n*eps*sign))
  for i in range(96):q=start+2*i+1;faces.append(([q,q+1,q+3,q+2],'seam'))

def main():
 mesh()
 with open(os.path.join(D,'basketball_3d.obj'),'w') as f:
  f.write('mtllib basketball_3d.mtl\n# unit-radius 3D sphere with 3D seam ribbons\n')
  for p in vs:f.write('v %.6f %.6f %.6f\n'%p)
  mat=''
  for ids,m in faces:
   if m!=mat:f.write('usemtl '+m+'\n');mat=m
   f.write('f '+' '.join(map(str,ids))+'\n')
 with open(os.path.join(D,'basketball_3d.mtl'),'w') as f:f.write('newmtl ball\nKd 0.90 0.36 0.09\nKs 0.0 0.0 0.0\n\nnewmtl seam\nKd 0.12 0.08 0.06\nKs 0.0 0.0 0.0\n')
 print('ball vertices',len(vs),'faces',len(faces))
if __name__=='__main__':main()
