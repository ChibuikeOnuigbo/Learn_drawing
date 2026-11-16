"""Reproduce model preparation without needing to connect an MCP host first."""
import json
import os
from pathlib import Path
from animation_mcp.semantic import prepare_models
from animation_mcp.asr import prepare_speech_model


def main():
    root=Path(__file__).resolve().parents[1];cache=root/'.work/models'
    os.environ.setdefault('ANIMATION_MODEL_CACHE',str(cache/'clip'))
    os.environ.setdefault('ANIMATION_ASR_CACHE',str(cache/'whisper-base.en'))
    result=dict(reference=prepare_models(),voiceover=prepare_speech_model())
    (root/'output').mkdir(exist_ok=True)
    (root/'output/model-readiness.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
