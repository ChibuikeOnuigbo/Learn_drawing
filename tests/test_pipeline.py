import asyncio
import json
import os
from pathlib import Path
import sys

import numpy as np
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import ValidationError

from animation_mcp.scene import Scene, Track, sample, reveal_points
from animation_mcp.render import draw_frame, confined, render, probe
from PIL import Image


def fixture_scene():
    return dict(width=160,height=96,frames=12,fps=12,background='#101820',layers=[
        dict(id='moving',kind='rect',x=30,y=48,width=20,height=24,fill='#ff9900',
             start=2,end=10,tracks=[dict(property='x',keys=[dict(frame=2,value=30),dict(frame=9,value=125)])])])


def test_half_open_intervals_and_real_motion(tmp_path):
    scene=Scene.model_validate(fixture_scene())
    frames=[np.array(draw_frame(scene,n,tmp_path)) for n in [1,2,9,10]]
    assert np.array_equal(frames[0],frames[3])
    assert not np.array_equal(frames[0],frames[1])
    assert not np.array_equal(frames[1],frames[2])


def test_stroke_reveal_uses_length():
    points=reveal_points([(0,0),(10,0),(10,30)],.5)
    assert points == [(0,0),(10,0),(10,10)]
    assert reveal_points([(0,0),(10,0)],0)==[]


def test_easing_and_endpoint():
    t=Track.model_validate(dict(property='x',keys=[dict(frame=0,value=0),dict(frame=10,value=100,easing='ease_out')]))
    assert sample(t,5)==87.5
    assert sample(t,10)==100


@pytest.mark.parametrize('mutation',[
    lambda s:s.update(width=161),
    lambda s:s['layers'].append(s['layers'][0].copy()),
    lambda s:s['layers'][0].update(end=20),
    lambda s:s['layers'][0].update(fill='url(file:///etc/passwd)'),
    lambda s:s['layers'][0].update(x=float('nan')),
])
def test_invalid_scene_rejected(mutation):
    data=fixture_scene()
    mutation(data)
    with pytest.raises(ValidationError): Scene.model_validate(data)


def test_workspace_escape_and_symlink_rejected(tmp_path):
    with pytest.raises(ValueError):confined(tmp_path,'../outside')
    (tmp_path/'escape').symlink_to('/etc')
    with pytest.raises(ValueError):confined(tmp_path,'escape/passwd')


def test_raster_asset_changes_invalidate_cache(tmp_path):
    asset=tmp_path/'asset.png'
    Image.new('RGB',(20,20),'red').save(asset)
    scene=Scene.model_validate(dict(width=160,height=96,frames=1,layers=[
        dict(id='plate',kind='image',asset='asset.png',x=80,y=48,width=160,height=96)]))
    before=np.array(draw_frame(scene,0,tmp_path))
    Image.new('RGB',(20,20),'blue').save(asset)
    after=np.array(draw_frame(scene,0,tmp_path))
    assert not np.array_equal(before,after)


def test_actual_encode_decode_and_scene_metadata(tmp_path):
    path=tmp_path/'scene.json'
    path.write_text(json.dumps(fixture_scene()))
    qa=render(path,tmp_path/'render',tmp_path)
    assert qa['technical_pass']
    assert qa['frames']==12 and qa['fps']==12
    assert qa['codec']=='h264'
    assert Path(qa['contact_sheet']).exists()


def test_stdio_mcp_client_render_and_error(tmp_path):
    async def run():
        params=StdioServerParameters(command=sys.executable,args=['-m','animation_mcp.server'],
                                    env={**os.environ,'ANIMATION_WORKSPACE':str(tmp_path)})
        async with stdio_client(params) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize()
                tools=await session.list_tools()
                assert 'render_scene' in {t.name for t in tools.tools}
                response=await session.call_tool('save_scene',{'scene':fixture_scene(),'path':'scene.json'})
                assert not response.isError
                response=await session.call_tool('render_scene',{'scene_path':'scene.json'})
                assert not response.isError
                payload=response.structuredContent or json.loads(response.content[0].text)
                assert payload['technical_pass'] and payload['frames']==12
                response=await session.call_tool('preview_frame',{'scene_path':'../outside','frame':0})
                assert response.isError
    asyncio.run(run())
