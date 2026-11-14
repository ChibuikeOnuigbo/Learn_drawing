"""Verify current exports and write a compact example index; never invent art scores."""
import json
from pathlib import Path
from animation_mcp.render import probe
from animation_mcp.reactions import plan_cues


def main():
    root=Path(__file__).resolve().parents[1];folder=root/'exmapels'
    projects=['reaction-story','reaction-from-audio','2d-character','youtube-explainer',
              '3d/easy','3d/simple','3d/medium','3d/hard']
    results=[]
    for name in projects:
        project=folder/name;qa=json.loads((project/'inspection/qa.json').read_text())
        info=probe(project/'video.mp4');v=next(s for s in info['streams'] if s['codec_type']=='video')
        assert int(v['nb_read_frames'])==qa['frames']
        audio=any(s['codec_type']=='audio' for s in info['streams'])
        assert audio==(not name.startswith('3d/'))
        if (project/'rig-qa.json').exists():
            rigs=json.loads((project/'rig-qa.json').read_text());assert all(r['geometry_pass'] for r in rigs)
        results.append(dict(project=name,video=str((project/'video.mp4').relative_to(root)),
                            width=qa['width'],height=qa['height'],frames=qa['frames'],fps=qa['fps'],
                            seconds=qa['duration'],audio=audio,technical_pass=qa['technical_pass'],
                            visual_review='Sampled contact sheets inspected; full playback/humor acceptance remains viewer review'))
    truth=json.loads((folder/'reaction-story/speech/narration.json').read_text())
    transcript=json.loads((folder/'reaction-story/asr-base/narration.json').read_text())
    a={c['intent']:c for c in plan_cues(truth)['cues']};b={c['intent']:c for c in plan_cues(transcript)['cues']}
    sync=[dict(intent=k,tts_word_onset=a[k]['word_time'],asr_word_onset=b[k]['word_time'],
               offset_seconds=b[k]['word_time']-a[k]['word_time']) for k in a if k in b]
    (root/'reports/voiceover-sync.json').write_text(json.dumps(dict(comparisons=sync,
        maximum_absolute_offset_seconds=max(abs(x['offset_seconds']) for x in sync),
        scope='One synthetic narration, compared against engine word events; not a general ASR benchmark'),indent=2)+'\n')
    (folder/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
