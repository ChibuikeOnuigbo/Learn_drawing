#!/usr/bin/env python3
"""Decode the user's already-downloaded Drive videos; never contacts YouTube.

Dense timestamped visual sampling, plus every-adjacent-frame change measurements
for short files. Produces review boards outside Git and an honest provenance
catalog. Cut candidates are image-delta events, not semantic shot labels.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, math
from pathlib import Path
import av
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
FONT=str(ROOT/'src/animation_mcp/assets/fonts/inter-400.ttf')

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def analyze(path:Path, out:Path, count=48, full_decode_max=150.):
    out.mkdir(parents=True,exist_ok=True)
    existing=out/(path.stem+'.json')
    if existing.exists():
        prior=json.loads(existing.read_text())
        if len(prior.get('samples',[]))>=count and prior.get('decoded_frames',0)>0:return prior
    container=av.open(str(path));stream=container.streams.video[0]
    stream.thread_type='AUTO'
    fps=float(stream.average_rate);duration=float(stream.duration*stream.time_base)
    n=round(duration*fps);w=stream.codec_context.width;h=stream.codec_context.height
    if not fps or not n:raise RuntimeError(f'Cannot decode {path}')
    # Always include the opening; distribute remaining samples across entire file.
    times=sorted(set([0.,.5,1.5]+[duration*(i+.5)/count for i in range(count)]))
    tiles=[];samples=[]
    font=ImageFont.truetype(FONT,13)
    for t in times:
        target=min(n-1,round(t*fps))
        container.seek(round(t*av.time_base),backward=True)
        rgb=None
        for frame in container.decode(stream):
            if frame.pts is not None and round(float(frame.pts*stream.time_base)*fps)>=target:
                rgb=frame.to_ndarray(format='rgb24');actual=round(float(frame.pts*stream.time_base)*fps);break
        if rgb is None:continue
        im=Image.fromarray(rgb);im.thumbnail((256,144))
        tile=Image.new('RGB',(256,166),'#101827');tile.paste(im,((256-im.width)//2,0))
        ImageDraw.Draw(tile).text((6,146),f'{actual/fps:07.2f}s  f{int(actual)}',font=font,fill='#dbeafe')
        tiles.append(tile)
        small=np.asarray(Image.fromarray(rgb).resize((64,36)),dtype=float)
        samples.append(dict(frame=int(actual),time=actual/fps,luma=float(small.mean()),std=float(small.std())))
    # Full adjacent-frame measurements only for short films; long tutorials use
    # explicitly labelled sparse samples. Never present sample gaps as cut counts.
    full=duration<=full_decode_max
    container.seek(0,backward=True);prev=None;changes=[];motion=[];idx=0
    if full:
        for frame in container.decode(stream):
            small=np.asarray(frame.to_image().resize((96,54)),dtype=np.float32)
            if prev is not None:
                diff=float(np.mean(np.abs(small-prev)))
                motion.append(diff)
                if diff>24:changes.append(dict(frame=idx,time=idx/fps,mean_absolute_delta=diff))
            prev=small;idx+=1
    container.close()
    cols=6;rows=math.ceil(len(tiles)/cols)
    sheet=Image.new('RGB',(cols*256,rows*166+44),'#101827');draw=ImageDraw.Draw(sheet)
    draw.text((10,10),path.name[:112],font=ImageFont.truetype(FONT,17),fill='white')
    for i,tile in enumerate(tiles):sheet.paste(tile,((i%cols)*256,44+(i//cols)*166))
    board=out/(path.stem+'.jpg');sheet.save(board,quality=87)
    result=dict(name=path.name,bytes=path.stat().st_size,sha256=sha256(path),frames=n,fps=fps,duration=duration,width=w,height=h,
                decoded_frames=idx,samples=samples,visual_board=str(board.resolve().relative_to(ROOT)),
                full_adjacent_decode=full,cut_candidates=changes,
                adjacent_delta_median=float(np.median(motion)) if motion else None,
                scope=('Every adjacent frame decoded at 96x54; cuts are candidates, not semantic labels.' if full else
                       f'{len(samples)} timestamped visual samples; no exhaustive cut count or claim of full viewing.')+' Artistic techniques require review.')
    (out/(path.stem+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=ROOT/'google_drive');p.add_argument('--output',type=Path,default=ROOT/'.work/reference-study');p.add_argument('--workers',type=int,default=3);p.add_argument('--samples',type=int,default=48);p.add_argument('--full-decode-max',type=float,default=150.);a=p.parse_args()
    files=sorted(a.input.glob('*.mp4'));a.output.mkdir(parents=True,exist_ok=True)
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures={pool.submit(analyze,f,a.output,a.samples,a.full_decode_max):f for f in files}
        for fut in concurrent.futures.as_completed(futures):
            try:r=fut.result();results.append(r);print(r['name'],r['decoded_frames'],len(r['cut_candidates']),flush=True)
            except Exception as e:print('ERROR',futures[fut],repr(e),flush=True)
    results.sort(key=lambda r:r['name'])
    (a.output/'catalog.json').write_text(json.dumps(results,indent=2)+'\n')
    print('COMPLETE',len(results),'/',len(files),flush=True)
if __name__=='__main__':main()
