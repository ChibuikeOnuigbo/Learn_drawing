#!/usr/bin/env python3
"""Build per-frame trace records from authorized local Drive videos.

Never downloads from YouTube. Input files must already be present locally
(e.g. restored through the Drive connector). Outputs go to data/traces by default.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from animation_mcp.tracing import trace_video, library_root

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('videos',nargs='+',type=Path)
    p.add_argument('--output',type=Path,default=None)
    p.add_argument('--annotations',type=Path,default=None)
    p.add_argument('--analysis-width',type=int,default=480)
    p.add_argument('--max-tracks',type=int,default=192)
    p.add_argument('--drive-id',default=None)
    p.add_argument('--youtube-url',default=None)
    p.add_argument('--video-id',default=None)
    a=p.parse_args()
    out=a.output or library_root(ROOT)
    results=[]
    for video in a.videos:
        vid=a.video_id if len(a.videos)==1 and a.video_id else video.stem
        target=out/vid
        print(f'TRACE {video.name} -> {target}',flush=True)
        def progress(done,total): print(f'  {done}/{total or "?"}',flush=True)
        m=trace_video(video,target,video_id=vid,drive_id=a.drive_id,youtube_url=a.youtube_url,
                      analysis_width=a.analysis_width,max_tracks=a.max_tracks,annotations=a.annotations,progress=progress)
        print(json.dumps({'video_id':vid,**m['coverage']},indent=2),flush=True)
        results.append(m)
    print(f'COMPLETE {len(results)} videos',flush=True)
if __name__=='__main__':main()
