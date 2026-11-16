"""Run the trusted scene worker with the isolated Blender Python module.

Usage: blender --background --python blender_launcher.py -- worker.py scene.json output/
No user-supplied executable code is accepted by the MCP.
"""
import runpy
import sys
from pathlib import Path
arguments=sys.argv[sys.argv.index('--')+1:]
worker=Path(arguments[0]).resolve()
sys.argv=[str(worker),'--',*arguments[1:]]
sys.path.insert(0,str(worker.parent))
runpy.run_path(str(worker),run_name='__main__')
