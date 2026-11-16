"""Local clip assembly, portrait/landscape fitting, narration and timed captions."""
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont
from pydantic import Field, model_validator
from .scene import Strict
from .render import confined, probe, inspect


class Clip(Strict):
    path: str
    start: float = Field(default=0,ge=0)
    duration: float = Field(gt=0,le=600)
    hold_last: bool = False


class Caption(Strict):
    text: str = Field(min_length=1,max_length=240)
    start: float = Field(ge=0)
    end: float = Field(gt=0)


class Edit(Strict):
    width: int = Field(default=1280,ge=160,le=1920)
    height: int = Field(default=720,ge=96,le=1920)
    fps: int = Field(default=30,ge=1,le=60)
    clips: list[Clip] = Field(min_length=1,max_length=40)
    captions: list[Caption] = Field(default_factory=list,max_length=40)
    audio: str | None = None
    caption_position: float = Field(default=.8,ge=.15,le=.95)

    @model_validator(mode='after')
    def timeline(self):
        if self.width%2 or self.height%2:
            raise ValueError('Dimensions must be even')
        duration=sum(round(c.duration*self.fps) for c in self.clips)/self.fps
        if any(round(c.duration*self.fps)<1 for c in self.clips):
            raise ValueError('Every clip must occupy at least one output frame')
        if self.width*self.height*duration*self.fps > 2_000_000_000:
            raise ValueError('Edit exceeds preview render budget')
        if any(c.end<=c.start or c.end>duration for c in self.captions):
            raise ValueError('Caption interval outside timeline')
        return self


def edit_video(spec: dict, folder: Path, root: Path):
    edit=Edit.model_validate(spec)
    folder.mkdir(parents=True,exist_ok=True)
    total=0
    for i,clip in enumerate(edit.clips):
        source=confined(root,clip.path,True)
        metadata=probe(source)
        source_duration=float(metadata['format']['duration'])
        if clip.start>=source_duration:raise ValueError(f'Clip {i} starts after its source ends')
        if not clip.hold_last and clip.start+clip.duration > source_duration+1/edit.fps:
            raise ValueError(f'Clip {i} exceeds its source duration')
        frames=round(clip.duration*edit.fps)
        total+=frames
        filters=(f'scale={edit.width}:{edit.height}:force_original_aspect_ratio=decrease,'
                 f'pad={edit.width}:{edit.height}:(ow-iw)/2:(oh-ih)/2:color=0x101820,'
                 f'setsar=1,fps={edit.fps},tpad=stop_mode=clone:stop_duration={clip.duration if clip.hold_last else 1}')
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(clip.start),'-i',str(source),'-an',
                        '-vf',filters,'-frames:v',str(frames),'-c:v','libx264','-threads','2',
                        '-pix_fmt','yuv420p',str(folder/f'clip-{i:03d}.mp4')],check=True,timeout=180)
    # Generated relative paths avoid concat path quoting and external protocols.
    (folder/'concat.txt').write_text(''.join(f"file 'clip-{i:03d}.mp4'\n" for i in range(len(edit.clips))))
    subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','1','-i',str(folder/'concat.txt'),
                    '-c','copy',str(folder/'assembled.mp4')],check=True,timeout=120)
    args=['ffmpeg','-y','-v','error','-i',str(folder/'assembled.mp4')]
    # Captions are drawn to PNGs; arbitrary user text never becomes FFmpeg filter syntax.
    for i,caption in enumerate(edit.captions):
        im=Image.new('RGBA',(edit.width,edit.height),(0,0,0,0))
        draw=ImageDraw.Draw(im)
        font=ImageFont.truetype(str(Path(__file__).parent/'assets/fonts/inter-400.ttf'),max(14,round(edit.width/30)))
        lines=[]
        line=''
        for word in caption.text.split():
            candidate=(line+' '+word).strip()
            if draw.textbbox((0,0),candidate,font=font)[2] > edit.width*.86:
                if not line:raise ValueError('Caption word exceeds safe width')
                lines.append(line);line=word
            else:line=candidate
        lines.append(line)
        if len(lines)>4:raise ValueError('Caption too long; split it into shorter cues')
        text='\n'.join(lines)
        box=draw.multiline_textbbox((0,0),text,font=font,align='center')
        w,h=box[2]-box[0],box[3]-box[1]
        x,y=(edit.width-w)/2,edit.height*edit.caption_position-h
        draw.rounded_rectangle((x-14,y-10,x+w+14,y+h+14),radius=8,fill=(5,12,22,220))
        draw.multiline_text((x,y-box[1]),text,font=font,align='center',fill='white')
        png=folder/f'caption-{i:03d}.png';im.save(png)
        args+=['-loop','1','-i',str(png)]
    if edit.audio:
        audio=confined(root,edit.audio,True)
        if float(probe(audio)['format']['duration'])>total/edit.fps+1/edit.fps:
            raise ValueError('Voiceover exceeds edit duration')
        args+=['-i',str(audio)]
    if edit.captions:
        filters=[]
        prev='0:v'
        for i,c in enumerate(edit.captions):
            out=f'cap{i}'
            filters.append(f'[{prev}][{i+1}:v]overlay=0:0:enable=\'gte(t,{c.start})*lt(t,{c.end})\'[{out}]')
            prev=out
        args+=['-filter_complex',';'.join(filters),'-map',f'[{prev}]']
    else:args+=['-map','0:v']
    if edit.audio:
        args+=['-map',f'{len(edit.captions)+1}:a','-af','apad','-c:a','aac']
    args+=['-c:v','libx264','-threads','2','-r',str(edit.fps),'-frames:v',str(total),
           '-t',str(total/edit.fps),'-pix_fmt','yuv420p','-movflags','+faststart',str(folder/'video.mp4')]
    subprocess.run(args,check=True,timeout=300)
    (folder/'edit.json').write_text(edit.model_dump_json(indent=2))
    qa=inspect(folder/'video.mp4',folder/'inspection')
    qa['technical_pass']=qa['technical_pass'] and qa['frames']==total and qa['fps']==edit.fps
    qa['source_audio']='Source-clip audio is intentionally dropped; provide an audio track to include narration.'
    (folder/'inspection/qa.json').write_text(json.dumps(qa,indent=2)+'\n')
    return qa
