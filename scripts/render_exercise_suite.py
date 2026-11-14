"""Reproducible four-tier CPU exercise renders, with at most two Blender jobs."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from animation_mcp.presets import scene_preset
from animation_mcp.blender_scene import render_3d


def main():
    root=Path(__file__).resolve().parents[1]
    def run(level):
        folder=root/'exmapels/3d'/level
        scene=scene_preset(level,480,270,16)
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'brief.json').write_text(json.dumps(dict(level=level,
            goal={'easy':'gravity, impacts, squash/stretch','simple':'weighted humanoid wave with IK',
                  'medium':'root travel, planted feet, IK walk and moving camera',
                  'hard':'reach, squat, grasp and carry a prop with skeleton-driven motion'}[level],
            scope='toolkit exercise difficulty; not a claim of parity with advanced reference films'),indent=2)+'\n')
        qa=render_3d(scene,folder)
        print(level,qa['technical_pass'],flush=True)
        return level,qa
    with ThreadPoolExecutor(max_workers=2) as pool:results=dict(pool.map(run,['easy','simple','medium','hard']))
    (root/'exmapels/3d/summary.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':main()
