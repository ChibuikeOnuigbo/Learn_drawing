import json
from pathlib import Path
import numpy as np
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


def test_saved_neural_curve_can_be_used_by_tool():
    controls=[[.15,.25],[.25,.8],[.65,.2],[.85,.75]]
    learned=curve_points(controls,17,learned=True)
    exact=curve_points(controls,17)
    values=np.asarray(learned['points'])
    assert values.shape==(17,2) and np.isfinite(values).all()
    assert np.abs(values-np.asarray(exact['points'])).mean()<.04
