"""Optional real-model integration; CI skips models that have not been fetched."""
import json
import re
from pathlib import Path
import wave
import numpy as np
import pytest
from animation_mcp.asr import asr_cache,transcribe
from animation_mcp.semantic import model_cache,search_references
from animation_mcp.speech import synthesize
from animation_mcp.reactions import plan_cues


def test_silent_audio_does_not_hallucinate_transcript(tmp_path):
    audio=tmp_path/'silence.wav'
    with wave.open(str(audio),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(bytes(32000))
    with pytest.raises(ValueError,match='silent'):transcribe(audio,tmp_path/'output')


@pytest.mark.skipif(not (asr_cache()/'model.bin').exists(),reason='Whisper model not fetched')
def test_real_voiceover_transcription_drives_meme_selection(tmp_path):
    truth=synthesize('This is absolutely messed up. No brains at all.',tmp_path/'speech',speed=135)
    result=transcribe(tmp_path/'speech/narration.wav',tmp_path/'asr')
    assert 'messed up' in result['text'].lower()
    # The observed ASR may drop the plural s. Test the required semantic cue,
    # retaining a real timing check rather than requiring exact transcription.
    assert re.search(r'no brains? at all',result['text'].lower())
    cues=plan_cues(result)['cues']
    assert {'disaster','brain_wipe'}<={x['intent'] for x in cues}
    true_times={x['intent']:x['word_time'] for x in plan_cues(truth)['cues']}
    assert all(abs(c['word_time']-true_times[c['intent']])<.4 for c in cues)


@pytest.mark.skipif(not (model_cache()/'text/model.onnx').exists(),reason='CLIP model not fetched')
def test_real_text_to_reference_retrieval():
    result=search_references('a three dimensional animated character in a scene',5)
    assert len(result['results'])==5
    assert len({r['source_sha256'] for r in result['results']})==5
    assert any('hCnsaahr2cc' in r['name'] or 'BAYQ2W_v08s' in r['name'] for r in result['results'])
    assert all(np.isfinite(r['cosine_similarity']) for r in result['results'])
