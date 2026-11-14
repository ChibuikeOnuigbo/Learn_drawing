"""Decode supplied Drive videos, make study boards and index sampled frames."""
import argparse
import io
import json
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw
from animation_mcp.semantic import encode_images,prepare_models


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--embed',action='store_true')
    args=parser.parse_args()
    root=Path('/workspace/drawing-data/new-drive');out=root/'analysis';out.mkdir(exist_ok=True)
    entries=json.loads((root/'downloads.json').read_text())+json.loads((root/'channel-downloads.json').read_text())
    entries=[e for e in entries if e.get('status')=='downloaded' and e['name'].endswith('.mp4')]
    catalog=[];index=[];embeddings=[];pending=[];direct_sheets=[]
    if args.embed:prepare_models()
    for n,e in enumerate(entries):
        path=root/e['path']
        raw=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],capture_output=True,check=True,text=True)
        meta=json.loads(raw.stdout);stream=next(s for s in meta['streams'] if s['codec_type']=='video')
        a,b=map(int,stream['avg_frame_rate'].split('/'));fps=a/b
        duration=float(meta['format']['duration']);frames=int(stream.get('nb_frames',round(duration*fps)))
        width,height=stream['width'],stream['height']
        times=sorted(set(min(duration-.05,x) for x in [0,.5,1.5,duration*.25,duration*.5,duration*.85] if x>=0))
        row=dict(name=e['name'],drive_id=e['id'],seconds=duration,fps=fps,frames=frames,width=width,height=height,sample_times=times,
                 sha256=e['sha256'],scope='6 sparse visual samples; not whole-video or audio analysis')
        board=Image.new('RGB',(1440,170),'#121a26');draw=ImageDraw.Draw(board)
        for j,t in enumerate(times):
            # System FFmpeg supports the AV1 clips that pip OpenCV cannot decode.
            decoded=subprocess.run(['ffmpeg','-v','error','-threads','2','-ss',str(t),'-i',str(path),
                                    '-frames:v','1','-vf','scale=960:-2','-f','image2pipe','-vcodec','png','pipe:1'],
                                   capture_output=True,check=True,timeout=90)
            image=Image.open(io.BytesIO(decoded.stdout)).convert('RGB');small=image.copy();small.thumbnail((240,135));board.paste(small,(j*240,0))
            draw.text((j*240+4,138),f'{t:.2f}s / {duration:.1f}s',fill='white')
            if args.embed:
                index.append(dict(name=e['name'],drive_id=e['id'],time_seconds=t,source_sha256=e['sha256'],
                                  source='user-supplied Drive reference',url='https://drive.google.com/file/d/'+e['id']+'/view'))
                pending.append(image)
                if len(pending)==8:embeddings.extend(encode_images(pending));pending=[]
        board.save(out/f'board-{n:03d}.jpg',quality=88)
        catalog.append(row)
        if '/' not in e['path']:direct_sheets.append((e['name'],board))
        print(n+1,e['name'],round(duration,2),flush=True)
    if args.embed:
        if pending:embeddings.extend(encode_images(pending))
        package=Path(__file__).resolve().parents[1]/'src/animation_mcp/models'
        np.savez_compressed(package/'reference-index.npz',embeddings=np.asarray(embeddings,dtype=np.float32))
        (package/'reference-index.json').write_text(json.dumps(index,indent=2)+'\n')
    for start in range(0,len(direct_sheets),4):
        subset=direct_sheets[start:start+4];sheet=Image.new('RGB',(1440,len(subset)*200),'#121a26');draw=ImageDraw.Draw(sheet)
        for i,(name,board) in enumerate(subset):
            draw.text((8,i*200+4),name,fill='#68dac9');sheet.paste(board,(0,i*200+24))
        sheet.save(out/f'direct-{start//4:02d}.jpg',quality=90)
    (out/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')


if __name__=='__main__':main()
