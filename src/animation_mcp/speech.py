"""Offline eSpeak NG narration and engine-provided word onset timestamps.

The C synthesizer runs in a separate process so concurrent MCP calls cannot
share its global state. Timestamps are synthesis events, not ASR estimates.
"""
from __future__ import annotations
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys
import wave


def synthesize(text: str, folder: Path, speed: int = 155, voice: str = 'en-us') -> dict:
    if not text.strip() or len(text)>12000:
        raise ValueError('Provide 1–12000 characters of narration')
    if not 90<=speed<=250 or voice not in {'en','en-us','en-gb'}:
        raise ValueError('Use speed 90–250 and voice en, en-us or en-gb')
    folder.mkdir(parents=True,exist_ok=True)
    spec=folder/'speech-input.json'
    spec.write_text(json.dumps(dict(text=text,speed=speed,voice=voice)))
    subprocess.run([sys.executable,'-m','animation_mcp.speech',str(spec.resolve()),
                    str(folder.resolve())],capture_output=True,text=True,check=True,timeout=120)
    return json.loads((folder/'narration.json').read_text())


def worker(spec: dict, folder: Path):
    import espeakng_loader

    class Identifier(C.Union):
        _fields_=[('number',C.c_int),('name',C.c_char_p),('string',C.c_char*8)]

    class Event(C.Structure):
        _fields_=[('type',C.c_int),('unique_identifier',C.c_uint),('text_position',C.c_int),
                  ('length',C.c_int),('audio_position',C.c_int),('sample',C.c_int),
                  ('user_data',C.c_void_p),('id',Identifier)]

    lib=C.CDLL(espeakng_loader.get_library_path())
    lib.espeak_Initialize.argtypes=[C.c_int,C.c_int,C.c_char_p,C.c_int]
    lib.espeak_Initialize.restype=C.c_int
    rate=lib.espeak_Initialize(2,0,espeakng_loader.get_data_path().encode(),0)
    if rate<=0:raise RuntimeError('eSpeak initialization failed')
    chunks=[];words=[]
    text=spec['text']
    callback_type=C.CFUNCTYPE(C.c_int,C.POINTER(C.c_short),C.c_int,C.POINTER(Event))

    def callback(samples,count,events):
        if samples and count:chunks.append(C.string_at(samples,count*2))
        i=0
        while events and events[i].type!=0:
            event=events[i]
            if event.type==1:
                start=max(0,event.text_position-1)
                words.append(dict(text=text[start:start+event.length],char_start=start,
                                  char_end=start+event.length,start=event.audio_position/1000))
            i+=1
        return 0

    callback_ref=callback_type(callback)
    lib.espeak_SetSynthCallback.argtypes=[callback_type]
    lib.espeak_SetSynthCallback(callback_ref)
    lib.espeak_SetVoiceByName.argtypes=[C.c_char_p]
    if lib.espeak_SetVoiceByName(spec['voice'].encode())!=0:
        raise RuntimeError('Requested speech voice unavailable')
    lib.espeak_SetParameter(1,int(spec['speed']),0)
    lib.espeak_Synth.argtypes=[C.c_void_p,C.c_size_t,C.c_uint,C.c_int,C.c_uint,
                               C.c_uint,C.POINTER(C.c_uint),C.c_void_p]
    buf=C.create_string_buffer(text.encode('utf-8'))
    status=lib.espeak_Synth(buf,len(buf),0,1,0,1,None,None)
    if status!=0:raise RuntimeError(f'Speech synthesis failed: {status}')
    lib.espeak_Synchronize()
    data=b''.join(chunks)
    if not data or not words:raise RuntimeError('No speech samples or word events produced')
    path=folder/'narration.wav'
    with wave.open(str(path),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(data)
    duration=len(data)/(2*rate)
    for i,word in enumerate(words):
        word['end']=words[i+1]['start'] if i+1<len(words) else duration
    result=dict(audio=str(path.resolve()),text=text,duration=duration,sample_rate=rate,
                words=words,voice=spec['voice'],engine='eSpeak NG via espeakng-loader 0.2.4',
                timing='word starts from synthesis engine; ends are next-word start or audio end',
                voice_quality='offline synthetic demo voice; replace with supplied voiceover for production')
    (folder/'narration.json').write_text(json.dumps(result,indent=2)+'\n')
    lib.espeak_Terminate()


if __name__=='__main__':
    worker(json.loads(Path(sys.argv[1]).read_text()),Path(sys.argv[2]))
