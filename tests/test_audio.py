import json
import subprocess
from pathlib import Path
import pytest
from animation_mcp.render import render, probe
from animation_mcp.server import plan_narration


def test_voiceover_mux_and_no_silent_truncation(tmp_path):
    audio=tmp_path/'narration.wav'
    subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','sine=frequency=330:duration=0.5',str(audio)],check=True)
    spec=dict(width=160,height=96,frames=12,fps=12,audio='narration.wav',layers=[])
    path=tmp_path/'scene.json'
    path.write_text(json.dumps(spec))
    qa=render(path,tmp_path/'audio-render',tmp_path)
    assert qa['technical_pass']
    assert any(s['codec_type']=='audio' for s in probe(tmp_path/'audio-render/video.mp4')['streams'])
    spec['frames']=1
    path.write_text(json.dumps(spec))
    with pytest.raises(ValueError,match='exceeds timeline'):render(path,tmp_path/'bad',tmp_path)


def test_estimated_narration_partition():
    result=plan_narration('Hello world. This is an original scene! Last sentence.',5,30)
    shots=result['shots']
    assert shots[0]['start']==0 and shots[-1]['end']==150
    assert all(a['end']==b['start'] for a,b in zip(shots,shots[1:]))
    assert all(a['end']>a['start'] for a in shots)
