"""Constrained 3D scene format; the server never accepts executable Blender code."""
from pathlib import Path
import json
import os
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


class RigTarget(Strict):
    frame: int = Field(ge=0)
    control: Literal['hand.R','hand.L','foot.R','foot.L']
    location: tuple[float,float,float]


class Rig(Strict):
    name: str = Field(pattern=r'^[A-Za-z][A-Za-z0-9_-]{0,63}$')
    action: Literal['idle','wave','walk','pickup','reach'] = 'wave'
    position: tuple[float,float,float] = (0,0,0)
    color: tuple[float,float,float] = (.10,.55,.62)
    target_keys: list[RigTarget] = Field(default_factory=list,max_length=400)

    @model_validator(mode='after')
    def valid_rig(self):
        if any(not 0<=c<=1 for c in self.color):raise ValueError('Rig colors must be in [0,1]')
        keys=[(k.control,k.frame) for k in self.target_keys]
        if len(keys)!=len(set(keys)):raise ValueError('Duplicate rig target key')
        return self


class CameraPose(Strict):
    frame: int = Field(ge=0)
    location: tuple[float,float,float]
    target: tuple[float,float,float]

    @model_validator(mode='after')
    def valid_camera(self):
        if self.location==self.target:raise ValueError('Camera location and target must differ')
        return self


class Scene3D(Strict):
    width: int = Field(default=640,ge=64,le=1920)
    height: int = Field(default=360,ge=64,le=1920)
    fps: int = Field(default=24,ge=1,le=60)
    frames: int = Field(default=48,ge=1,le=600)
    samples: int = Field(default=16,ge=1,le=128)
    denoise: bool = False
    art_direction: Literal['basic','easy','simple','medium','hard'] = 'basic'
    camera: tuple[float,float,float] = (7,-10,6)
    target: tuple[float,float,float] = (0,0,1)
    objects: list[Object3D] = Field(default_factory=list,max_length=100)
    rigs: list[Rig] = Field(default_factory=list,max_length=4)
    camera_poses: list[CameraPose] = Field(default_factory=list,max_length=100)

    @model_validator(mode="after")
    def validate_scene(self):
        if self.width % 2 or self.height % 2:
            raise ValueError("Video dimensions must be even")
        if self.camera == self.target:
            raise ValueError("Camera and target must differ")
        if not self.objects and not self.rigs and self.art_direction=='basic':
            raise ValueError('Supply an object or rig, or choose an art_direction preset')
        names = [o.name for o in self.objects]+[r.name for r in self.rigs]
        if len(names) != len(set(names)):
            raise ValueError("Object names must be unique")
        if any(p.frame > self.frames for o in self.objects for p in o.poses):
            raise ValueError("Pose outside timeline")
        if any(k.frame>self.frames for r in self.rigs for k in r.target_keys):
            raise ValueError('Rig key outside timeline')
        camera_frames=[k.frame for k in self.camera_poses]
        if camera_frames!=sorted(set(camera_frames)) or any(f>self.frames for f in camera_frames):
            raise ValueError('Camera keys must be ordered and inside timeline')
        return self


def render_3d(spec: dict, folder: Path) -> dict:
    scene = Scene3D.model_validate(spec)
    if scene.width*scene.height*scene.frames*scene.samples > 1_500_000_000:
        raise ValueError("3D render exceeds preview budget; reduce resolution, frames or samples")
    from .doctor import resolve_command
    blender = resolve_command("blender")
    if not blender:
        raise RuntimeError("Blender must be installed for 3D rendering (or set ANIMATION_BLENDER)")
    folder.mkdir(parents=True,exist_ok=True)
    path = folder/"scene3d.json"
    path.write_text(scene.model_dump_json(indent=2))
    with (folder/"blender.log").open("w") as log:
        subprocess.run([blender,"--background","--threads","2","--python",
                        str(Path(__file__).with_name("blender_launcher.py")),"--",
                        str(Path(__file__).with_name("blender_worker.py")),str(path.resolve()),
                        str(folder.resolve())],stdout=log,stderr=subprocess.STDOUT,check=True,
                       timeout=int(os.environ.get('ANIMATION_BLENDER_TIMEOUT','3600')))
    video = folder/"video.mp4"
    subprocess.run(["ffmpeg","-y","-v","error","-framerate",str(scene.fps),"-start_number","0",
                    "-i",str(folder/"frames"/"%04d.png"),"-frames:v",str(scene.frames),"-c:v","libx264",
                    "-threads","2","-pix_fmt","yuv420p","-crf","18","-movflags","+faststart",str(video)],check=True,timeout=120)
    check_frames=list(range(0,scene.frames,max(1,scene.fps//4))) if scene.rigs else None
    report = inspect(video,folder/"inspection",frames=check_frames)
    report["technical_pass"] = report["technical_pass"] and (
        report["frames"] == scene.frames and report["fps"] == scene.fps and
        (report["width"],report["height"]) == (scene.width,scene.height))
    report["blend"] = str(folder/"scene.blend")
    if scene.rigs:
        rig_reports=json.loads((folder/'rig-qa.json').read_text())
        rig_pass=all(r['geometry_pass'] and r['armature_modifier'] and r['weighted_vertices']>0 for r in rig_reports)
        report['rig_pass']=rig_pass;report['rig_report']=str(folder/'rig-qa.json')
        report['technical_pass']=report['technical_pass'] and rig_pass
        if not rig_pass:report['errors'].append('Rig geometry/attachment check failed')
    (folder/"inspection"/"qa.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
