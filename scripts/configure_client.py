"""Write a concrete stdio MCP client entry for this interpreter and checkout."""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workspace',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,default=Path('output/mcp-client.json'))
    args=parser.parse_args();root=args.workspace.resolve()
    cache=root/'.work/models'
    config={'mcpServers':{'animation-studio':{'command':sys.executable,'args':['-m','animation_mcp.server'],
        'env':{'ANIMATION_WORKSPACE':str(root),'ANIMATION_MODEL_CACHE':str(cache/'clip'),
               'ANIMATION_ASR_CACHE':str(cache/'whisper-base.en')}}}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(config,indent=2)+'\n')
    print('MCP client configuration:',args.output.resolve())


if __name__=='__main__':main()
