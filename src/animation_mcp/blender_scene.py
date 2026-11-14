"""Constrained 3D scene format; the server never accepts executable Blender code."""
from pathlib import Path
import json
import shutil
import subprocess
from typing import Literal
from pydantic import Field, model_validator
from .scene import Strict
from .render import inspect


class Pose(Strict):
    frame: int = Field(ge=0)
    location: tuple[float,float,float]
    rotation: tuple[float,float,float] = (0,0,0)
    scale: tuple[float,float,float] = (1,1,1)


class Object3D(Strict):
    name: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
    kind: Literal["sphere","cube","cylinder","cone","torus"]
    color: tuple[float,float,float] = (.1,.5,.8)
    location: tuple[float,float,float] = (0,0,0)
    scale: tuple[float,float,float] = (1,1,1)
    poses: list[Pose] = Field(default_factory=list,max_length=100)

    @model_validator(mode="after")
    def validate_object(self):
        if any(not 0 <= c <= 1 for c in self.color):
            raise ValueError("RGB values must be in [0,1]")
        if any(s <= 0 for s in self.scale) or any(s <= 0 for p in self.poses for s in p.scale):
            raise ValueError("Scale must be positive")
        frames = [p.frame for p in self.poses]
        if frames != sorted(set(frames)):
            raise ValueError("Poses must be strictly ordered")
        return self


class Scene3D(Strict):
    width: int = Field(default=640,ge=64,le=1920)
    height: int = Field(default=360,ge=64,le=1920)
    fps: int = Field(default=24,ge=1,le=60)
    frames: int = Field(default=48,ge=1,le=600)
    samples: int = Field(default=16,ge=1,le=128)
    camera: tuple[float,float,float] = (7,-10,6)
    target: tuple[float,float,float] = (0,0,1)
    objects: list[Object3D] = Field(min_length=1,max_length=100)

    @model_validator(mode="after")
    def validate_scene(self):
        if self.width % 2 or self.height % 2:
            raise ValueError("Video dimensions must be even")
        if self.camera == self.target:
            raise ValueError("Camera and target must differ")
        names = [o.name for o in self.objects]
        if len(names) != len(set(names)):
            raise ValueError("Object names must be unique")
        if any(p.frame > self.frames for o in self.objects for p in o.poses):
            raise ValueError("Pose outside timeline")
        return self


def render_3d(spec: dict, folder: Path) -> dict:
    scene = Scene3D.model_validate(spec)
    if scene.width*scene.height*scene.frames*scene.samples > 1_500_000_000:
        raise ValueError("3D render exceeds preview budget; reduce resolution, frames or samples")
    blender = shutil.which("blender")
    if not blender:
        raise RuntimeError("Blender must be installed for 3D rendering")
    folder.mkdir(parents=True,exist_ok=True)
    path = folder/"scene3d.json"
    path.write_text(scene.model_dump_json(indent=2))
    with (folder/"blender.log").open("w") as log:
        subprocess.run([blender,"--background","--threads","2","--python",
                        str(Path(__file__).with_name("blender_worker.py")),"--",str(path.resolve()),
                        str(folder.resolve())],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
    video = folder/"video.mp4"
    subprocess.run(["ffmpeg","-y","-v","error","-framerate",str(scene.fps),"-start_number","0",
                    "-i",str(folder/"frames"/"%04d.png"),"-frames:v",str(scene.frames),"-c:v","libx264",
                    "-threads","2","-pix_fmt","yuv420p","-crf","18","-movflags","+faststart",str(video)],check=True,timeout=120)
    report = inspect(video,folder/"inspection")
    report["technical_pass"] = report["technical_pass"] and (
        report["frames"] == scene.frames and report["fps"] == scene.fps and
        (report["width"],report["height"]) == (scene.width,scene.height))
    report["blend"] = str(folder/"scene.blend")
    (folder/"inspection"/"qa.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
