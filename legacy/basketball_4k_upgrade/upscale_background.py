"""Denoise then apply pretrained FSRCNN x4 once to the static 960p scene."""
import os,cv2,numpy as np
cv2.setNumThreads(2)
D=os.path.dirname(os.path.abspath(__file__));src=os.path.join(os.path.dirname(D),'basketball_quality_v4','drawn_gym_from_memory.png')
im=cv2.imread(src);assert im is not None and im.shape[:2]==(540,960)
clean=cv2.fastNlMeansDenoisingColored(im,None,8,8,7,21);cv2.imwrite(os.path.join(D,'clean_960.png'),clean)
sr=cv2.dnn_superres.DnnSuperResImpl_create();sr.readModel(os.path.join(D,'FSRCNN_x4.pb'));sr.setModel('fsrcnn',4)
h,w=clean.shape[:2];dst=np.zeros((h*4,w*4,3),dtype=np.uint8);step=160;pad=16
for y in range(0,h,step):
 for x in range(0,w,step):
  y1=min(y+step,h);x1=min(x+step,w);a=max(0,y-pad);b=min(h,y1+pad);c=max(0,x-pad);d=min(w,x1+pad)
  tile=sr.upsample(clean[a:b,c:d]);dst[y*4:y1*4,x*4:x1*4]=tile[(y-a)*4:(y1-a)*4,(x-c)*4:(x1-c)*4]
 print('processed to row',y1,flush=True)
cv2.imwrite(os.path.join(D,'gym_fsrcnn_4k.png'),dst);print('saved',dst.shape,flush=True)
