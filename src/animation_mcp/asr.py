"""Local, checksum-pinned Whisper base.en transcription for supplied voiceovers."""
from functools import lru_cache
import json
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.request
import numpy as np
from .semantic import checksum,PACKAGE


def asr_cache():
    return Path(os.environ.get('ANIMATION_ASR_CACHE',str(Path(tempfile.gettempdir())/'animation-studio-whisper-base.en')))


def prepare_speech_model():
    root=asr_cache();root.mkdir(parents=True,exist_ok=True)
    result=[]
    for entry in json.loads((PACKAGE/'models/asr-manifest.json').read_text()):
        path=root/entry['file']
        if not path.exists():
            temp=path.with_suffix(path.suffix+'.part')
            with urllib.request.urlopen(entry['url'],timeout=180) as source,temp.open('wb') as target:
                while block:=source.read(1048576):target.write(block)
            if checksum(temp)!=entry['sha256']:
                temp.unlink();raise ValueError('Speech model checksum mismatch')
            temp.replace(path)
        if checksum(path)!=entry['sha256']:raise ValueError('Cached speech model checksum mismatch')
        result.append(dict(file=entry['file'],bytes=path.stat().st_size,verified=True))
    return dict(model='Whisper base.en converted by Systran; pretrained, not trained in this project',
                cache=str(root),files=result,language='English',license='MIT declared by upstream')


@lru_cache(maxsize=1)
def model(path):
    from faster_whisper import WhisperModel
    if not (Path(path)/'model.bin').exists():raise RuntimeError('Call prepare_voiceover_model first')
    prepare_speech_model()
    return WhisperModel(path,device='cpu',compute_type='int8',cpu_threads=2,num_workers=1,local_files_only=True)


def transcribe(audio: Path, folder: Path):
    decoded=subprocess.run(['ffmpeg','-v','error','-i',str(audio),'-t','601','-ac','1','-ar','16000',
                            '-f','f32le','pipe:1'],capture_output=True,check=True,timeout=120)
    samples=np.frombuffer(decoded.stdout,dtype='<f4')
    duration=len(samples)/16000
    if not 0<duration<=600:raise ValueError('Supply a voiceover between 0 and 600 seconds')
    if not np.isfinite(samples).all() or np.sqrt(np.mean(samples.astype(float)**2))<1e-4:
        raise ValueError('Audio is silent or invalid; no transcript generated')
    segments,info=model(str(asr_cache())).transcribe(samples,language='en',beam_size=5,
        word_timestamps=True,vad_filter=False,condition_on_previous_text=False)
    words=[];parts=[];cursor=0
    for segment in segments:
        for word in segment.words or []:
            token=word.word.strip()
            if not token:continue
            if parts:cursor+=1
            start=cursor;parts.append(token);cursor+=len(token)
            words.append(dict(text=token,char_start=start,char_end=cursor,start=max(0,min(duration,word.start)),
                              end=max(0,min(duration,word.end)),probability=float(word.probability)))
    if not words:raise ValueError('No speech was recognized')
    result=dict(audio=str(audio.resolve()),text=' '.join(parts),duration=duration,words=words,
                engine='pretrained Whisper base.en / faster-whisper CPU int8',
                timing='ASR-estimated word boundaries; verify uncertain or critical cues',
                review_required=any(w['probability']<.6 for w in words),language='en')
    folder.mkdir(parents=True,exist_ok=True)
    path=folder/'narration.json';path.write_text(json.dumps(result,indent=2)+'\n')
    result['narration_json']=str(path.resolve())
    return result
