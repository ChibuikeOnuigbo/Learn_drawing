import argparse
import json
from pathlib import Path
from .render import render, inspect
from .blender_scene import render_3d


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command",choices=["render","render3d","inspect"])
    parser.add_argument("source",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--workspace",type=Path,default=Path.cwd())
    args=parser.parse_args()
    if args.command == "render":
        result=render(args.source,args.output,args.workspace)
    elif args.command == "render3d":
        result=render_3d(json.loads(args.source.read_text()),args.output)
    else:
        result=inspect(args.source,args.output)
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
