import json
from pathlib import Path
import numpy as np
import pytest
from PIL import Image
from animation_mcp.edit import edit_video
from animation_mcp.render import render
from animation_mcp.server import curve_points


def test_clip_assembly_caption_and_portrait_fit(tmp_path):
    path=tmp_path/'source.json'
    path.write_text(json.dumps(dict(width=160,height=96,frames=12,fps=12,
        background='#ff8800',layers=[])))
    render(path,tmp_path/'source',tmp_path)
    result=edit_video(dict(width=160,height=240,fps=12,clips=[
        dict(path='source/video.mp4',start=0,duration=.5),
        dict(path='source/video.mp4',start=.5,duration=.5)],
        captions=[dict(text='Hello drawing',start=.25,end=.75)]),tmp_path/'edit',tmp_path)
    assert result['technical_pass'] and result['frames']==12
    assert result['height']==240
    # Decode includes a caption-free first frame and captioned middle frame.
    samples=sorted((tmp_path/'edit/inspection').glob('sample-*.png'))
    assert not np.array_equal(np.array(Image.open(samples[0])),np.array(Image.open(samples[2])))


def test_exact_bezier_endpoints():
    controls=[[.1,.2],[.3,.9],[.7,.1],[.9,.8]]
    result=curve_points(controls,17)
    assert result['points'][0]==controls[0]
    assert result['points'][-1]==controls[-1]


def test_explicit_final_frame_hold_preserves_longer_narration_slot(tmp_path):
    path=tmp_path/'source.json'
    source_scene={"width":160,"height":96,"frames":6,"fps":12,"layers":[
        {"id":"ball","kind":"ellipse","width":20,"height":20,"y":48,"fill":"#ff9900",
         "tracks":[{"property":"x","keys":[{"frame":0,"value":20},{"frame":5,"value":130}]}]}]}
    path.write_text(json.dumps(source_scene))
    render(path,tmp_path/'source',tmp_path)
    result=edit_video(dict(width=160,height=96,fps=12,clips=[
        dict(path='source/video.mp4',duration=1,hold_last=True)]),tmp_path/'held',tmp_path)
    assert result['technical_pass'] and result['frames']==12
    samples=sorted((tmp_path/'held/inspection').glob('sample-*.png'))
    first=np.array(Image.open(samples[0])).astype(float)
    late=np.array(Image.open(samples[-1])).astype(float)
    assert np.abs(first-late).mean()>1
    with pytest.raises(ValueError,match='starts after'):
        edit_video(dict(width=160,height=96,fps=12,clips=[dict(path='source/video.mp4',start=1,duration=1,hold_last=True)]),tmp_path/'bad',tmp_path)
