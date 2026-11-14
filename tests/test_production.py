import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import wave
import numpy as np
import pytest
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import ValidationError
from animation_mcp.scene import Scene
from animation_mcp.render import draw_frame,probe
from animation_mcp.reactions import classify,plan_cues,compose_reactions
from animation_mcp.speech import synthesize
from animation_mcp.blender_scene import Scene3D,render_3d
from animation_mcp.presets import scene_preset
from animation_mcp.doctor import resolve_command


@pytest.mark.parametrize('text,intent',[
    ('This is absolutely messed up.','disaster'),('No brains at all.','brain_wipe'),
    ('They actually won!','victory'),('The medical student studies brain anatomy.','none'),
    ('This is not a dumb plan; the experiment is deliberate.','none')])
def test_editorial_reaction_selection(text,intent):
    assert classify(text)['intent']==intent


def test_group_transform_and_inherited_visibility(tmp_path):
    scene=Scene.model_validate(dict(width=160,height=96,frames=4,layers=[
        dict(id='root',kind='group',x=40,y=40,start=2),
        dict(id='child',kind='rect',parent='root',x=20,width=12,height=12,fill='#ff0000')]))
    hidden=np.array(draw_frame(scene,0,tmp_path));visible=np.array(draw_frame(scene,2,tmp_path))
    assert visible[40,60,0]>240 and visible[40,60,1]<10
    assert not np.array_equal(hidden[40,60],visible[40,60])


def test_parent_cycles_and_forward_references_rejected():
    with pytest.raises(ValidationError):Scene.model_validate(dict(layers=[dict(id='child',kind='group',parent='later'),dict(id='later',kind='group')]))


def test_actual_speech_and_reaction_video(tmp_path):
    narration=synthesize('This is absolutely messed up. No brains at all.',tmp_path/'speech')
    assert narration['duration']>2
    with wave.open(narration['audio'],'rb') as w:
        values=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
    assert np.max(np.abs(values.astype(float)))>1000
    plan=plan_cues(narration)
    assert [c['intent'] for c in plan['cues']]==['disaster','brain_wipe']
    assert all(abs(c['timing_error_seconds'])<=1/60+1e-9 for c in plan['cues'])
    qa=compose_reactions(tmp_path/'speech/narration.json',tmp_path/'render',tmp_path,width=480,height=270)
    assert qa['technical_pass'] and qa['timing_pass']
    assert any(s['codec_type']=='audio' for s in probe(tmp_path/'render/video.mp4')['streams'])
    # Samples at each cue onset must contain the selected reaction, changing pixels.
    assert max(s['stddev'] for s in qa['samples'])>min(s['stddev'] for s in qa['samples'])+5


def test_bad_word_timing_is_rejected():
    with pytest.raises(ValueError):
        plan_cues(dict(text='Hello',duration=1,words=[dict(text='Hello',char_start=0,char_end=5,start=float('nan'),end=1)]))


@pytest.mark.skipif(not resolve_command('blender'),reason='Optional Blender executable is not installed')
def test_real_armature_skin_and_ik_render(tmp_path):
    spec=scene_preset('simple',96,96,1);spec.update(frames=4,fps=4,camera_poses=[])
    qa=render_3d(spec,tmp_path/'blender')
    rig=json.loads((tmp_path/'blender/rig-qa.json').read_text())[0]
    assert qa['technical_pass'] and qa['rig_pass']
    assert rig['armature_modifier'] and rig['bones']==15 and rig['weighted_vertices']>5000
    assert rig['ik_chains']==4 and rig['minimum_foot_vertex_z']>=-.025


def test_character_rig_is_layered_and_posed():
    from animation_mcp.character import character_svg
    a=character_svg(0);b=character_svg(65)
    assert a!=b
    for token in ['id="body-pivot"','id="head-pivot"','id="arm-right"','id="eye-left"']:
        assert token in a
    assert 'transform="translate(0 ' in b


def test_mcp_production_tools_and_prompt(tmp_path):
    async def run():
        params=StdioServerParameters(command=sys.executable,args=['-m','animation_mcp.server'],env={**os.environ,'ANIMATION_WORKSPACE':str(tmp_path)})
        async with stdio_client(params) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize()
                names={t.name for t in (await session.list_tools()).tools}
                assert {'synthesize_narration','select_reaction','render_reaction_video','transcribe_voiceover','search_reference_library','render_3d_exercise'}<=names
                result=await session.call_tool('select_reaction',{'text':'No brains at all.'})
                assert not result.isError
                payload=result.structuredContent or json.loads(result.content[0].text)
                assert payload['intent']=='brain_wipe'
                prompts=await session.list_prompts();assert 'produce_video' in {p.name for p in prompts.prompts}
                resources=await session.list_resources();assert {'studio://workflow','studio://skills'} <= {str(r.uri) for r in resources.resources}
                templates=await session.list_resource_templates()
                assert any(t.uriTemplate=='studio://skills/{name}' for t in templates.resourceTemplates)
                guide=await session.read_resource('studio://skills/drawing')
                assert 'name: drawing' in guide.contents[0].text
                skill=await session.call_tool('get_skill',{'name':'3d-animation'})
                assert not skill.isError
                payload=skill.structuredContent or json.loads(skill.content[0].text)
                assert 'name: 3d-animation' in payload['content']
                bad=await session.call_tool('get_skill',{'name':'../server'})
                assert bad.isError
                health=await session.call_tool('check_environment',{})
                assert not health.isError
                payload=health.structuredContent or json.loads(health.content[0].text)
                assert payload['workspace']==str(tmp_path) and 'scope' in payload
                schema=await session.call_tool('get_scene_schema',{'kind':'3d'})
                assert not schema.isError
                data=schema.structuredContent or json.loads(schema.content[0].text)
                assert 'rigs' in data['properties']
                catalog=await session.call_tool('get_model_catalog',{})
                assert not catalog.isError
                prompt=await session.get_prompt('produce_video',arguments={'brief':'Make a timed reaction clip.'})
                assert prompt.messages
    asyncio.run(run())
