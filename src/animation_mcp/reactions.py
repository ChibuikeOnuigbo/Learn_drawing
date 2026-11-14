"""Learned narration-intent retrieval plus explicit editorial and timing rules.

The classifier is deliberately small; asset taste and strong phrase anchoring
remain editorial choices. No hosted service, arbitrary pickle or account is used.
"""
from functools import lru_cache
import json
import math
from pathlib import Path
import re
import subprocess
import wave

import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps

from .render import confined,inspect,probe

PACKAGE=Path(__file__).resolve().parent
ASSETS={
    'disaster':('anime-disaster.png','anime','horrified disbelief at a disastrous plan'),
    'confusion':('anime-disaster.png','anime','a puzzled/horrified reaction; review intensity'),
    'disappointment':('anime-disaster.png','anime','facepalm reaction; may be too intense for quiet disappointment'),
    'brain_wipe':('brain-wipe.png','cartoon','clueless thinking: tiny sleeping brain / polishing its helmet'),
    'victory':('anime-victory.png','anime','celebratory comeback and raised fist')}
ANCHORS={
    'disaster':['messed up','mess','disaster','catastrophe','chaos','nightmare','cooked','exploded','fell apart','wrong'],
    'brain_wipe':['no brain','brain cell','zero common sense','brain has','stupid','dumb','idiotic','same trick'],
    'confusion':['what just happened','no idea','no sense','how does','confused','what am','understand','questions'],
    'victory':['won','did it','comeback','win','saved','victory','nailed','defeated','pulled it off','celebrate','worked'],
    'disappointment':['disappointing','nothing','let everyone down','expected','sad','heartbreaking','wasted','underwhelming','letdown']}


@lru_cache(maxsize=1)
def classifier():
    from sklearn.feature_extraction.text import TfidfVectorizer,TfidfTransformer
    meta=json.loads((PACKAGE/'models/reaction_classifier.json').read_text())
    vectorizers=[]
    for name,analyzer,ngram in [('word','word',(1,2)),('char','char_wb',(3,5))]:
        v=TfidfVectorizer(analyzer=analyzer,ngram_range=ngram,sublinear_tf=True,
                         vocabulary=meta[name+'_vocabulary'])
        v.vocabulary_=meta[name+'_vocabulary'];v.fixed_vocabulary_=True
        v._tfidf=TfidfTransformer(sublinear_tf=True)
        v._tfidf.idf_=np.asarray(meta[name+'_idf'])
        vectorizers.append(v)
    with np.load(PACKAGE/'models/reaction_classifier.npz',allow_pickle=False) as weights:
        coef=weights['coef'].copy();intercept=weights['intercept'].copy()
    return meta,vectorizers,coef,intercept


def classify(text: str) -> dict:
    from scipy.sparse import hstack
    if not text.strip() or len(text)>4000:raise ValueError('Provide 1–4000 characters')
    # Literal medical/scientific contexts are not a stupidity gag.
    if re.search(r'\b(neurons?|tumou?r|medical|anatomy|neuroscience|brain tissue|recovery simulation)\b',text,re.I):
        return dict(intent='none',confidence=1.0,reason='literal/scientific editorial guard; not classifier probability')
    if re.search(r'\bnot (?:a |an )?(?:dumb|stupid|disaster)\b',text,re.I):
        return dict(intent='none',confidence=1.0,reason='explicit negation guard; not classifier probability')
    meta,vs,coef,bias=classifier()
    x=hstack([v.transform([text]) for v in vs])
    score=np.asarray(x@coef.T+bias)[0]
    probability=np.exp(score-score.max());probability/=probability.sum()
    index=int(np.argmax(probability))
    return dict(intent=meta['classes'][index],confidence=float(probability[index]),
                reason='small supervised English intent classifier; confidence is not calibrated')


def plan_cues(narration: dict, fps=30, threshold=.40, theme='anime') -> dict:
    text=narration['text'];duration=float(narration['duration']);words=narration['words']
    if not math.isfinite(duration) or not 0<duration<=600 or not 1<=fps<=60:
        raise ValueError('Invalid duration or frame rate')
    if not 0<=threshold<=1:raise ValueError('Threshold must be in [0,1]')
    last=-1
    for word in words:
        if not (math.isfinite(word['start']) and 0<=word['start']<=duration) or word['start']<last:
            raise ValueError('Word times must be finite, ordered and inside the audio')
        if not 0<=word['char_start']<word['char_end']<=len(text):
            raise ValueError('Invalid word character span')
        last=word['start']
    cues=[];decisions=[]
    for match in re.finditer(r'[^.!?]+[.!?]?',text):
        sentence=match.group().strip()
        if not sentence:continue
        prediction=classify(sentence)
        decisions.append(dict(text=sentence,**prediction))
        intent=prediction['intent']
        if intent=='none' or prediction['confidence']<threshold:continue
        matches=[(sentence.lower().find(a),a) for a in ANCHORS[intent] if a in sentence.lower()]
        if not matches:
            # Avoid filling every narrative sentence with an unrelated reaction.
            continue
        offset,phrase=min(matches,key=lambda pair:pair[0])
        sentence_start=match.start()+len(match.group())-len(match.group().lstrip())
        anchor=sentence_start+offset
        candidates=[w for w in words if w['char_end']>anchor and w['char_start']<match.end()]
        if not candidates:continue
        word=candidates[0];frame=round(word['start']*fps)
        if cues and frame < cues[-1]['frame_start']+round(fps*.8):continue
        name,style,meaning=ASSETS[intent]
        cues.append(dict(intent=intent,phrase=phrase,word=word['text'],word_time=word['start'],
                         frame_start=frame,frame_end=frame+round(1.9*fps),asset=name,style=style,
                         transcript_word_confidence=word.get('probability'),
                         confidence=prediction['confidence'],editorial_reason=meaning,
                         theme_note=f'Semantic match uses {style} art; requested theme is {theme}. Review or override the asset.' if style!=theme else 'Theme match'))
    frames=math.ceil((duration+1)*fps)
    for i,cue in enumerate(cues):
        cue['frame_end']=min(cue['frame_end'],cues[i+1]['frame_start'] if i+1<len(cues) else frames)
        cue['timing_error_seconds']=cue['frame_start']/fps-cue['word_time']
    return dict(fps=fps,frames=frames,cues=cues,decisions=decisions,
                timing_source=narration.get('timing','caller-supplied word timestamps'),
                alignment_review_required='ASR' in narration.get('timing',''),
                transcript_review_required=narration.get('review_required',False),
                evaluation='Technical timing can be measured; whether this is the best meme needs viewer review')


def _caption(draw,text,font,max_width):
    lines=[];line=''
    for word in text.split():
        candidate=(line+' '+word).strip()
        if draw.textlength(candidate,font=font)>max_width and line:
            lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    return '\n'.join(lines)


def _asset_frames(path: Path, folder: Path):
    if path.suffix.lower() in {'.png','.jpg','.jpeg'}:
        return [Image.open(path).convert('RGB')],1
    folder.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(path),'-t','6','-vf',
                    'fps=15,scale=960:540:force_original_aspect_ratio=decrease',
                    '-frames:v','90',str(folder/'asset-%03d.png')],check=True,timeout=120)
    frames=[Image.open(p).convert('RGB') for p in sorted(folder.glob('asset-*.png'))]
    if not frames:raise ValueError('Reaction asset has no decodable frames')
    return frames,15


def compose_reactions(narration_path: Path, folder: Path, root: Path, theme='anime',
                      overrides: dict | None=None, width=960, height=540, fps=30,
                      heading='The story takes a turn') -> dict:
    if width%2 or height%2 or not 320<=width<=1920 or not 180<=height<=1080:
        raise ValueError('Use even dimensions within 320×180 and 1920×1080')
    if not heading.strip() or len(heading)>60:raise ValueError('Heading must be 1–60 characters')
    narration=json.loads(narration_path.read_text())
    plan=plan_cues(narration,fps,theme=theme)
    if width*height*plan['frames']>2_000_000_000:raise ValueError('Render exceeds preview budget')
    folder.mkdir(parents=True,exist_ok=True)
    audio=confined(root,narration['audio'],True)
    with wave.open(str(audio),'rb') as wav:
        if wav.getsampwidth()!=2 or wav.getnchannels()!=1:
            raise ValueError('Narration must be mono 16-bit PCM WAV')
        rate=wav.getframerate();voice=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype(float)/32768
    if abs(len(voice)/rate-narration['duration'])>1/fps:raise ValueError('Audio and narration timing disagree')
    mix=np.zeros(math.ceil(plan['frames']/fps*rate));mix[:len(voice)]=voice
    for cue in plan['cues']:
        start=round(cue['frame_start']/fps*rate)
        t=np.arange(round(.16*rate))/rate
        sfx=.12*np.sin(2*np.pi*(180*t-240*t*t))*np.exp(-25*t)
        mix[start:start+len(sfx)]+=sfx[:max(0,len(mix)-start)]
    peak=float(np.max(np.abs(mix)))
    if peak>.94:mix*=.94/peak
    mixed=folder/'mixed.wav'
    with wave.open(str(mixed),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes((mix*32767).astype('<i2').tobytes())
    assets={}
    for cue in plan['cues']:
        custom=(overrides or {}).get(cue['intent'])
        cue['asset_origin']='caller-supplied local asset' if custom else 'original AI-generated reaction illustration bundled with toolkit'
        if cue['intent'] in assets:continue
        path=confined(root,custom,True) if custom else PACKAGE/'assets/reactions'/cue['asset']
        assets[cue['intent']]=_asset_frames(path,folder/('asset-'+cue['intent']))
    scale=width/960
    font=ImageFont.truetype('DejaVuSans.ttf',round(29*scale))
    small=ImageFont.truetype('DejaVuSans.ttf',round(15*scale))
    title=ImageFont.truetype('DejaVuSans-Bold.ttf',round(30*scale))
    while title.getlength(heading)>width*.9 and title.size>12:
        title=ImageFont.truetype('DejaVuSans-Bold.ttf',title.size-1)
    video=folder/'video.mp4'
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}',
         '-r',str(fps),'-i','pipe:0','-i',str(mixed),'-c:v','libx264','-threads','2','-crf','18',
         '-c:a','aac','-b:a','192k','-pix_fmt','yuv420p','-t',str(plan['frames']/fps),'-movflags','+faststart',str(video)]
    with (folder/'ffmpeg.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for frame in range(plan['frames']):
                seconds=frame/fps
                im=Image.new('RGB',(width,height),'#0b1326');d=ImageDraw.Draw(im)
                d.text((width*.5,height*.065),heading,font=title,fill='#eaf3f6',anchor='mm')
                cue=next((c for c in plan['cues'] if c['frame_start']<=frame<c['frame_end']),None)
                box=(round(width*.12),round(height*.15),round(width*.88),round(height*.77))
                if cue:
                    sequence,asset_fps=assets[cue['intent']]
                    image=sequence[int((frame-cue['frame_start'])/fps*asset_fps)%len(sequence)]
                    # Contain the source; important faces are never auto-cropped.
                    card=ImageOps.contain(image,(box[2]-box[0],box[3]-box[1]))
                    im.paste(card,((width-card.width)//2,(box[1]+box[3]-card.height)//2))
                    d.rounded_rectangle(box,radius=12,outline='#5fdcca',width=max(1,round(2*scale)))
                else:
                    d.rounded_rectangle(box,radius=12,fill='#13253b',outline='#284560',width=2)
                    cx,cy=width*.5,height*.44
                    r=height*.14
                    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill='#e3e8d8',outline='#62d8cb',width=4)
                    d.ellipse((cx-r*.72,cy-r*.55,cx+r*.72,cy+r*.55),fill='#11263b')
                    for dx in [-1,1]:
                        ex=cx+dx*r*.28
                        d.ellipse((ex-4*scale,cy-4*scale,ex+4*scale,cy+4*scale),fill='#63ddcf')
                    energy=float(np.abs(voice[int(seconds*rate):min(len(voice),int((seconds+.025)*rate))]).mean()) if seconds<narration['duration'] else 0
                    d.rectangle((cx-10*scale,cy+18*scale,cx+10*scale,cy+(22+min(energy*200,12))*scale),fill='#63ddcf')
                active=[w for w in narration['words'] if w['start']<=seconds<w['end']]
                # Use punctuation-delimited sentence text, not a full-page caption.
                if active:
                    pos=active[-1]['char_start']
                    sentence=next((m.group().strip() for m in re.finditer(r'[^.!?]+[.!?]?',narration['text']) if m.start()<=pos<m.end()),'')
                    text=_caption(d,sentence,font,width*.87)
                    d.multiline_text((width/2,height*.85),text,font=font,fill='#ffffff',anchor='mm',align='center',stroke_width=1,stroke_fill='#000000')
                d.rectangle((width*.08,height*.96,width*.92,height*.967),fill='#233e55')
                d.rectangle((width*.08,height*.96,width*(.08+.84*min(seconds/narration['duration'],1)),height*.967),fill='#62d8cb')
                proc.stdin.write(im.tobytes())
            proc.stdin.close()
            if proc.wait(timeout=120):raise RuntimeError((folder/'ffmpeg.log').read_text()[-2000:])
        except BaseException:
            proc.kill();proc.wait();raise
    (folder/'cue-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    sample_frames=[f for c in plan['cues'] for f in [c['frame_start']-1,c['frame_start'],(c['frame_start']+c['frame_end'])//2,c['frame_end']]]
    qa=inspect(video,folder/'inspection',frames=sample_frames)
    qa['timing_pass']=all(abs(c['timing_error_seconds'])<=.5/fps+1e-9 for c in plan['cues'])
    qa['timing_scope']='Cue frame rounding relative to supplied word times; ASR word times themselves are estimates'
    qa['audio_sync_review_required']='ASR' in narration.get('timing','') or narration.get('review_required',False)
    qa['audio_peak']=float(np.abs(mix).max())
    qa['cues']=plan['cues']
    qa['artistic_review']='pending: inspect timing, thematic fit, caption readability and humor; classifier is not a taste judge'
    audio_present=any(s['codec_type']=='audio' for s in probe(video)['streams'])
    qa['audio_present']=audio_present
    qa['technical_pass']=qa['technical_pass'] and qa['frames']==plan['frames'] and qa['timing_pass'] and audio_present and qa['fps']==fps and (qa['width'],qa['height'])==(width,height)
    (folder/'inspection/qa.json').write_text(json.dumps(qa,indent=2)+'\n')
    return qa
