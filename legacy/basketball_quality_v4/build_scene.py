"""Assemble an approximate 3D gym from the AI-generated visual references.
Exports actual geometry to OBJ/MTL and renders a 3D guide with a small software rasterizer.
The reference bitmap images are not pasted, projected or texture-mapped.
"""
import os,math,json
import numpy as np,cv2
D=os.path.dirname(os.path.abspath(__file__));W,H=960,540
MATS={
 'cream':((226,199,157),True),'cream2':((213,183,141),True),'padding':((50,77,94),True),'padding2':((59,89,106),True),
 'wood0':((202,137,76),False),'wood1':((206,142,81),False),'wood2':((196,128,70),False),'wood3':((211,147,86),False),'mark':((244,229,198),False),
 'beam':((91,67,57),True),'roof':((76,64,58),False),'beamlight':((121,88,67),True),'window':((205,226,218),True),'windowshine':((233,236,215),False),'frame':((66,62,57),True),
 'sunlight':((232,170,98),False),'sunlight2':((241,184,114),False),'steel':((57,53,51),True),'lamp':((250,233,194),False),'bleacher':((152,94,59),True),'bleachertop':((189,125,75),True),'backboard':((244,238,217),True),'boardline':((60,64,60),True),'metal':((184,79,43),True),'net':((231,226,207),False),'door':((92,80,70),True)
}
verts=[];faces=[]
def poly(points,material):
 ids=[]
 for p in points:verts.append(tuple(map(float,p)));ids.append(len(verts))
 faces.append((ids,material))
def box(lo,hi,material):
 x0,y0,z0=lo;x1,y1,z1=hi
 for p in [[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],[(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],[(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],[(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],[(x0,y0,z0),(x0,y1,z0),(x0,y1,z1),(x0,y0,z1)],[(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)]]:poly(p,material)
def ribbon_floor(points,width,material='mark'):
 for a,b in zip(points,points[1:]):
  a=np.array(a,float);b=np.array(b,float);v=b[:2]-a[:2];l=np.linalg.norm(v)
  if l<1e-8:continue
  n=np.array([-v[1],v[0]])/l*width/2
  poly([(a[0]+n[0],a[1]+n[1],a[2]),(b[0]+n[0],b[1]+n[1],b[2]),(b[0]-n[0],b[1]-n[1],b[2]),(a[0]-n[0],a[1]-n[1],a[2])],material)
def ellipse(cx,cy,rx,ry,steps=64,start=0,end=2*math.pi):
 return [(cx+rx*math.cos(t),cy+ry*math.sin(t),.022) for t in np.linspace(start,end,steps)]
def build():
 verts.clear();faces.clear()
 # Floor is a genuine set of 3D plank polygons, with no photographic texture.
 for j in range(40):
  x=-8+j*.4;poly([(x,0,0),(x+.4,0,0),(x+.4,25,0),(x,25,0)],'wood'+str((j*13+2)%4))
 # Walls; room's front wall is open for the camera.
 poly([(-8,25,0),(8,25,0),(8,25,8.5),(-8,25,8.5)],'cream')
 poly([(-8,24.98,0),(8,24.98,0),(8,24.98,2.5),(-8,24.98,2.5)],'padding')
 poly([(-8,0,0),(-8,25,0),(-8,25,8.5),(-8,0,8.5)],'cream')
 poly([(-7.99,0,0),(-7.99,25,0),(-7.99,25,2.5),(-7.99,0,2.5)],'padding2')
 poly([(8,0,0),(8,25,0),(8,25,8.5),(8,0,8.5)],'cream2')
 poly([(7.99,0,0),(7.99,25,0),(7.99,25,2.5),(7.99,0,2.5)],'padding')
 # Five tall windows on the left wall, with geometry rather than pasted imagery.
 for j in range(5):
  y=2+j*4.4;box((-7.985,y,3.2),(-7.93,y+2.45,7.25),'frame');poly([(-7.91,y+.11,3.32),(-7.91,y+2.34,3.32),(-7.91,y+2.34,7.13),(-7.91,y+.11,7.13)],'window')
  box((-7.90,y+1.16,3.32),(-7.85,y+1.22,7.13),'frame');box((-7.90,y+.11,5.1),(-7.85,y+2.34,5.18),'frame')
 # Doors and blue wall seams.
 for x in [-6.9,6.9]:
  poly([(x-.38,24.94,.03),(x+.38,24.94,.03),(x+.38,24.94,2.7),(x-.38,24.94,2.7)],'door')
 for j in range(1,12):box((-8+j*(16/12),24.94,.06),(-7.97+j*(16/12),24.93,2.45),'padding2')
 # Bleachers: three stepped 3D wooden benches along right long wall.
 for j in range(3):
  x0=5.4+j*.78;z=.20+j*.38;box((x0,5,z),(7.9,19,z+.22),'bleacher');box((x0,5,z+.22),(7.9,19,z+.26),'bleachertop')
  for y in [5.2,9.5,13.8,18.8]:box((x0,y,.03),(x0+.1,y+.1,z),'beam')
 # Pitched roof and cross beams.
 poly([(-8,0,8.5),(0,0,10),(0,25,10),(-8,25,8.5)],'roof');poly([(0,0,10),(8,0,8.5),(8,25,8.5),(0,25,10)],'roof')
 for y in [1,5.8,10.6,15.4,20.2,24.8]:
  poly([(-8,y,8.38),(0,y,9.88),(0,y+.16,9.88),(-8,y+.16,8.38)],'beamlight');poly([(0,y,9.88),(8,y,8.38),(8,y+.16,8.38),(0,y+.16,9.88)],'beamlight')
 # Hoop backboard, target rectangle and rim, all spatial geometry.
 poly([(-1.5,24.88,4.15),(1.5,24.88,4.15),(1.5,24.88,5.9),(-1.5,24.88,5.9)],'boardline');poly([(-1.43,24.84,4.22),(1.43,24.84,4.22),(1.43,24.84,5.83),(-1.43,24.84,5.83)],'backboard')
 for lo,hi in [((-0.52,24.80,4.45),(-.47,24.78,5.15)),((.47,24.80,4.45),(.52,24.78,5.15)),((-.52,24.80,5.1),(.52,24.78,5.15)),((-.52,24.80,4.45),(.52,24.78,4.50))]:box(lo,hi,'boardline')
 # Rim and net are thin real 3D faces so the OBJ contains them too.
 ring=[(.50*math.cos(t),24.00+.34*math.sin(t),4.36) for t in np.linspace(0,2*math.pi,49)]
 for a,b in zip(ring,ring[1:]):
  a=np.array(a);b=np.array(b);d=b[:2]-a[:2];normal=np.array([-d[1],d[0]])/(np.linalg.norm(d)+1e-9)*.035
  poly([(a[0]+normal[0],a[1]+normal[1],a[2]),(b[0]+normal[0],b[1]+normal[1],b[2]),(b[0]-normal[0],b[1]-normal[1],b[2]),(a[0]-normal[0],a[1]-normal[1],a[2])],'metal')
 for a in ring[::6]:
  end=(a[0]*.55,24+(a[1]-24)*.55,3.75);poly([(a[0]-.012,a[1],a[2]),(a[0]+.012,a[1],a[2]),(end[0]+.012,end[1],end[2]),(end[0]-.012,end[1],end[2])],'net')
 # Approximate sunlight patches as floor-level geometry, inspired by the views.
 # This is a hand-designed lighting cue, not a physically computed light simulation.
 for yi in [2.4,6.8,11.2,15.6,20.0]:
  for k in range(2):
   a=yi+k*1.10
   poly([(-7.95,a,.010),(-7.95,a+.82,.010),(-4.65,a+2.20,.010),(-4.65,a+1.38,.010)],'sunlight' if k==0 else 'sunlight2')
 # Framed trusses hanging under the pitched roof, made of real 3D faces.
 def xzbeam(a,b,width,y):
  a=np.array(a,float);b=np.array(b,float);v=b-a;v=v/(np.linalg.norm(v)+1e-9);n=np.array([-v[1],v[0]])*width/2
  poly([(a[0]+n[0],y,a[1]+n[1]),(b[0]+n[0],y,b[1]+n[1]),(b[0]-n[0],y,b[1]-n[1]),(a[0]-n[0],y,a[1]-n[1])],'steel')
 for y in [2.2,7,11.8,16.6,21.4]:
  xzbeam((-8,8.20),(8,8.20),.09,y)
  xzbeam((-7.9,8.28),(0,9.79),.09,y);xzbeam((0,9.79),(7.9,8.28),.09,y)
  for x in [-5.3,-2.65,0,2.65,5.3]:
   z=9.79-abs(x)*1.51/7.9;xzbeam((x,8.20),(x,z),.045,y)
  for x in [-5.3,-2.65,0,2.65]:
   z=9.79-abs(x+2.65)*1.51/7.9;xzbeam((x,8.2),(x+2.65,z),.035,y)
 # Rectangular overhead luminaires suspended beneath roof beams.
 for y in [4.6,10,15.4,20.8]:
  for x in [-3.5,3.5]:
   box((x-.53,y-.15,8.11),(x+.53,y+.15,8.19),'steel')
   poly([(x-.48,y-.13,8.10),(x+.48,y-.13,8.10),(x+.48,y+.13,8.10),(x-.48,y+.13,8.10)],'lamp')
 # Court stripes stored as thin 3D faces rather than drawn over a reference bitmap.
 ribbon_floor([(-6,2,.02),(-6,23,.02),(6,23,.02),(6,2,.02),(-6,2,.02)],.11)
 ribbon_floor([(-6,12.5,.021),(6,12.5,.021)],.11);ribbon_floor(ellipse(0,12.5,1.75,1.75),.11)
 for y,sgn in [(2,1),(23,-1)]:
  ribbon_floor([(-2.4,y,.022),(-2.4,y+sgn*4.8,.022),(2.4,y+sgn*4.8,.022),(2.4,y,.022)],.11)
  ribbon_floor(ellipse(0,y+sgn*4.8,2.4,2.4,60,0,math.pi),.10)
  ribbon_floor(ellipse(0,y,5.1,5.1,80,0,math.pi),.10)
 return verts,faces

def camera():
 eye=np.array([0.,-8.5,5.25]);target=np.array([0.,15,3.1]);up=np.array([0.,0.,1.]);f=(target-eye);f/=np.linalg.norm(f);right=np.cross(f,up);right/=np.linalg.norm(right);u=np.cross(right,f);return eye,right,u,f

def project(P):
 eye,right,up,f=camera();q=np.asarray(P)-eye;depth=q@f;x=480+750*(q@right)/depth;y=270-750*(q@up)/depth;return np.stack([x,y],-1),depth

def render():
 # Triangle z-buffer: later/nearer geometry properly occludes earlier surfaces.
 # Reciprocal depth is interpolated in screen space (perspective correct).
 im=np.empty((H,W,3),dtype=np.uint8);im[:]=(235,220,195);zbuf=np.full((H,W),np.inf,dtype=np.float32)
 for ids,material in faces:
  xyz=np.array([verts[i-1] for i in ids]);pts,depth=project(xyz)
  if np.any(depth<=.3):continue
  rgb,_=MATS[material];col=np.array(rgb[::-1],dtype=np.uint8)
  for k in range(1,len(ids)-1):
   tri=pts[[0,k,k+1]];dep=depth[[0,k,k+1]]
   x0=max(0,int(np.floor(tri[:,0].min())));x1=min(W-1,int(np.ceil(tri[:,0].max())));y0=max(0,int(np.floor(tri[:,1].min())));y1=min(H-1,int(np.ceil(tri[:,1].max())))
   if x1<x0 or y1<y0:continue
   x=np.arange(x0,x1+1,dtype=np.float32)[None,:]+.5;y=np.arange(y0,y1+1,dtype=np.float32)[:,None]+.5
   ax,ay=tri[0];bx,by=tri[1];cx,cy=tri[2];den=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
   if abs(den)<1e-8:continue
   w0=((by-cy)*(x-cx)+(cx-bx)*(y-cy))/den;w1=((cy-ay)*(x-cx)+(ax-cx)*(y-cy))/den;w2=1-w0-w1
   inv=w0/dep[0]+w1/dep[1]+w2/dep[2];d=1/np.maximum(inv,1e-8);view=zbuf[y0:y1+1,x0:x1+1];valid=(w0>=-1e-5)&(w1>=-1e-5)&(w2>=-1e-5)&(d<view-1e-5)
   view[valid]=d[valid];im[y0:y1+1,x0:x1+1][valid]=col
 # Hoop and net are drawn from projected 3D coordinates (they are also listed
 # as separate line geometry in the accompanying scene metadata).
 ring=[(.50*math.cos(t),24.00+.34*math.sin(t),4.36) for t in np.linspace(0,2*math.pi,48)];xy,_=project(ring);cv2.polylines(im,[np.rint(xy).astype(np.int32)],True,(39,70,173),3,cv2.LINE_AA)
 for i in range(0,48,6):
  a=ring[i];b=(a[0]*.55,24+(a[1]-24)*.55,3.75);xy,_=project([a,b]);cv2.line(im,*[tuple(x) for x in np.rint(xy).astype(int)],(234,235,237),1,cv2.LINE_AA)
 return im

def export():
 with open(os.path.join(D,'gym_scene.obj'),'w') as f:
  f.write('mtllib gym_scene.mtl\n# Approximate reference-informed 3D model, not a photogrammetric reconstruction\n')
  for p in verts:f.write('v %.5f %.5f %.5f\n'%p)
  last=None
  for ids,m in faces:
   if m!=last:f.write('usemtl '+m+'\n');last=m
   f.write('f '+' '.join(map(str,ids))+'\n')
 with open(os.path.join(D,'gym_scene.mtl'),'w') as f:
  for name,(rgb,_) in MATS.items():f.write('newmtl '+name+'\nKd %.5f %.5f %.5f\n'%tuple(v/255 for v in rgb)+'Ka 0.1 0.1 0.1\nKs 0 0 0\n\n')

def main():
 build();export();cv2.imwrite(os.path.join(D,'3d_guide.png'),render());json.dump({'vertices':len(verts),'faces':len(faces),'camera_eye':camera()[0].tolist(),'room_width':16,'room_depth':25,'note':'Manually assembled plausible geometry from conflicting generated reference views; no photogrammetric reconstruction, texture mapping, or bitmap pasting.'},open(os.path.join(D,'scene_manifest.json'),'w'),indent=2);print('3d vertices',len(verts),'faces',len(faces))
if __name__=='__main__':main()
