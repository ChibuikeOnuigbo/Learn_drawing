"""Compose trained 2D ball on a denoised, neural-upscaled static gym at UHD 4K.
This reuses the prior drawing; it does not train a new artist model or infer detail.
"""
import os,math,subprocess,cv2,numpy as np
from PIL import Image
D=os.path.dirname(os.path.abspath(__file__));root=os.path.dirname(D);cv2.setNumThreads(2)
background=cv2.imread(os.path.join(D,'gym_fsrcnn_4k.png'));H,W=background.shape[:2];assert (W,H)==(3840,2160)
rgba=cv2.imread(os.path.join(root,'basketball_quality_v4','drawn_ball_from_memory.png'),cv2.IMREAD_UNCHANGED);assert rgba.shape[2]==4
sr=cv2.dnn_superres.DnnSuperResImpl_create();sr.readModel(os.path.join(D,'FSRCNN_x4.pb'));sr.setModel('fsrcnn',4);rgb=sr.upsample(rgba[:,:,:3]);alpha=cv2.resize(rgba[:,:,3],(rgb.shape[1],rgb.shape[0]),interpolation=cv2.INTER_LANCZOS4);ball=np.dstack([rgb,alpha]);del sr,rgba,rgb,alpha;import gc;gc.collect()
# Same camera as the 3D guide, 4x pixel coordinates for 4K output.
eye=np.array([0.,-8.5,5.25]);target=np.array([0.,15.,3.1]);up=np.array([0.,0.,1.]);f=target-eye;f/=np.linalg.norm(f);right=np.cross(f,up);right/=np.linalg.norm(right);cup=np.cross(right,f)
def project(p):
 q=np.asarray(p)-eye;z=q@f;return 4*(480+750*(q@right)/z),4*(270-750*(q@cup)/z),z
fps=30;nframes=180;radius=.15;g=9.81;restitution=.73;v=0.;height=2.0;X=-1.5;Y=3.9
ff=os.environ.get('FFMPEG_PATH','ffmpeg');dst=os.path.join(D,'basketball_4k.mp4');args=[ff,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','1','-preset','ultrafast','-tune','zerolatency','-x264-params','threads=1:sync-lookahead=0:rc-lookahead=0','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',dst];proc=subprocess.Popen(args,stdin=subprocess.PIPE)
for i in range(nframes):
 if i>0:
  for _ in range(8):
   dt=1/(fps*8);v-=g*dt;height+=v*dt
   if height<radius:
    height=radius+(radius-height);v=-v*restitution
    if abs(v)<.18:height=radius;v=0
 px,py,depth=project((X,Y,height));gx,gy,_=project((X,Y,.012));rad=3000*radius/depth
 frame=background.copy();rr=rad*(.9+min((height-radius)*.08,.35));x0=max(0,int(gx-rr-2));x1=min(W,int(gx+rr+3));y0=max(0,int(gy-rr*.21-2));y1=min(H,int(gy+rr*.21+3))
 if x1>x0 and y1>y0:
  mask=np.zeros((y1-y0,x1-x0),np.uint8);cv2.ellipse(mask,(round(gx)-x0,round(gy)-y0),(max(1,round(rr)),max(1,round(rr*.21))),0,0,360,255,-1,cv2.LINE_AA);a=mask.astype(np.float32)/255*(max(28,int(100-20*(height-radius)))/255);roi=frame[y0:y1,x0:x1];roi[:]=(roi*(1-a[:,:,None])+np.array([25,33,42])*a[:,:,None]).astype(np.uint8)
 size=max(1,round(rad*2*160/134));sprite=cv2.resize(ball,(size,size),interpolation=cv2.INTER_AREA if size<480 else cv2.INTER_CUBIC);center=(size/2,size/2);mat=cv2.getRotationMatrix2D(center,i*2.5,1.0);# pad sprite before rotation to avoid cropped corners
 diag=math.ceil(size*1.42);mat[0,2]+=(diag-size)/2;mat[1,2]+=(diag-size)/2;sprite=cv2.warpAffine(sprite,mat,(diag,diag),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0));left=round(px-diag/2);top=round(py-diag/2);lx=max(0,left);ly=max(0,top);rx=min(W,left+diag);ry=min(H,top+diag)
 if lx<rx and ly<ry:
  sp=sprite[ly-top:ry-top,lx-left:rx-left];a=sp[:,:,3:4].astype(np.float32)/255;region=frame[ly:ry,lx:rx];region[:]=(sp[:,:,:3]*a+region*(1-a)).astype(np.uint8)
 if i==0:cv2.imwrite(os.path.join(D,'first_frame_4k.png'),frame)
 try:proc.stdin.write(frame.tobytes())
 except BrokenPipeError:raise RuntimeError('ffmpeg closed early with status '+str(proc.wait()))
 if i%30==0:print('frame',i,flush=True)
proc.stdin.close();code=proc.wait()
if code:raise RuntimeError('ffmpeg failed: '+str(code))
print('done',dst,flush=True)
