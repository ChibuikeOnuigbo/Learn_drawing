from pathlib import Path
import json
from animation_mcp.speech import synthesize
from animation_mcp.reactions import compose_reactions


def main():
    root=Path(__file__).resolve().parents[1]
    folder=root/'exmapels/reaction-story'
    text=('The anime hero had a perfect plan. He tried a shortcut. '
          'This is absolutely messed up. He walked into the trap again. No brains at all. '
          'Then the team changed its approach. They actually won!')
    synthesize(text,folder/'speech',150)
    qa=compose_reactions(folder/'speech/narration.json',folder,root,heading='THE WORST BATTLE PLAN')
    print(json.dumps(dict(video=qa['video'],technical_pass=qa['technical_pass'],cues=qa['cues']),indent=2))


if __name__=='__main__':main()
