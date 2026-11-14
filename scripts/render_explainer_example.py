"""A complete original narration-led short using the produced animation assets."""
from pathlib import Path
import json
import math
import re
from animation_mcp.speech import synthesize
from animation_mcp.edit import edit_video


def main():
    root=Path(__file__).resolve().parents[1];folder=root/'exmapels/youtube-explainer'
    text=('A good animation starts with a clear pose. Timing gives a simple shape weight. '
          'A rig lets the character wave. Inverse kinematics keeps the feet on the ground. '
          'Finally, coordinate the hands, the prop, and the camera. Every shot should help tell the story.')
    audio=synthesize(text,folder/'speech',135);fps=30
    sentences=list(re.finditer(r'[^.!?]+[.!?]?',text))
    starts=[round(next(w['start'] for w in audio['words'] if w['char_start']>=m.start())*fps) for m in sentences]
    starts.append(math.ceil(audio['duration']*fps)+8)
    sources=['exmapels/2d-character/clean/video.mp4','exmapels/3d/easy/video.mp4','exmapels/3d/simple/video.mp4',
             'exmapels/3d/medium/video.mp4','exmapels/3d/hard/video.mp4','exmapels/2d-character/clean/video.mp4']
    clips=[];captions=[]
    for i,(m,path) in enumerate(zip(sentences,sources)):
        clips.append(dict(path=path,start=8.5 if i==5 else 0,duration=(starts[i+1]-starts[i])/fps,hold_last=True))
        captions.append(dict(text=m.group().strip(),start=starts[i]/fps,end=starts[i+1]/fps))
    spec=dict(width=960,height=540,fps=fps,clips=clips,captions=captions,audio=audio['audio'],caption_position=.94)
    qa=edit_video(spec,folder,root)
    print(json.dumps(dict(video=qa['video'],technical_pass=qa['technical_pass'],frames=qa['frames']),indent=2))


if __name__=='__main__':main()
