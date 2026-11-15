#!/usr/bin/env python3
"""Author and render five original starter examples for the expanded skill library.

Outputs editable source, real video and measured QA under examples/05..09.
Regenerable frame sequences/intermediates are gitignored. No third-party media.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import numpy as np
import resvg_py

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from animation_mcp.scene import Scene
from animation_mcp.render import render, probe
from animation_mcp.edit import edit_video
from animation_mcp.production import color_palette, plan_shots, timing_sheet
from animation_mcp.speech import synthesize

OUT = ROOT / "examples"
FONT = ROOT / "src/animation_mcp/assets/fonts/inter-400.ttf"
FPS = 24


def track(prop, keys):
    return {"property": prop, "keys": [{"frame": f, "value": v, "easing": e} for f, v, *rest in keys for e in [rest[0] if rest else "smooth"]]}


def layer(ident, kind, **kw):
    return dict(id=ident, kind=kind, **kw)


def save_scene(folder: Path, scene: dict, name="scene.json"):
    folder.mkdir(parents=True, exist_ok=True)
    parsed = Scene.model_validate(scene)
    (folder / name).write_text(parsed.model_dump_json(indent=2) + "\n")
    return parsed


def render_scene(folder: Path, name="scene.json"):
    qa = render(folder / name, folder / "render", folder)
    (folder / "qa.json").write_text(json.dumps(qa, indent=2) + "\n")
    if not qa["technical_pass"]:
        raise RuntimeError(f"Render failed QA: {folder}: {qa['errors']}")
    return qa


def kinetic_typography():
    p = OUT / "05-kinetic-typography"
    p.mkdir(parents=True, exist_ok=True)
    pal = color_palette("#4f8cff", "analogous", True)["roles"]
    (p / "palette.json").write_text(json.dumps(pal, indent=2) + "\n")
    frames = 96
    layers = [layer("grid-accent", "rect", x=480, y=270, width=960, height=540, fill=pal["background"])]
    words = [("PLAN", 0, 32, pal["primary"]), ("BUILD", 32, 64, pal["secondary"]), ("REFINE", 64, 96, pal["accent"])]
    for i, (word, start, end, color) in enumerate(words):
        layers.append(layer(f"bar-{i}", "rect", x=480, y=330, width=220, height=8, fill=color, start=start, end=end,
                            tracks=[track("scale_x", [(start, 0.05), (start + 8, 1.0), (end - 1, 1.0)])]))
        layers.append(layer(f"word-{i}", "text", x=480, y=250, text=word, font_size=84, fill=pal["text"], start=start, end=end,
                            tracks=[track("opacity", [(start, 0), (start + 5, 1), (end - 6, 1), (end - 1, 0)]),
                                    track("y", [(start, 282), (start + 8, 250), (end - 1, 250)]),
                                    track("scale", [(start, 0.92), (start + 8, 1.0), (end - 1, 1.0)])]))
        layers.append(layer(f"step-{i}", "text", x=480, y=385, text=f"0{i+1} / 03", font_size=22, fill=pal["muted"], start=start, end=end,
                            tracks=[track("opacity", [(start, 0), (start + 8, 1), (end - 1, 1)])]))
    layers.append(layer("headline", "text", x=480, y=90, text="ONE CLEAR IDEA AT A TIME", font_size=24, fill=pal["muted"]))
    scene = dict(version=1, title="Kinetic type: plan, build, refine", width=960, height=540, fps=FPS, frames=frames,
                 background=pal["background"], layers=layers)
    save_scene(p, scene)
    (p / "shot-plan.json").write_text(json.dumps(plan_shots([
        {"title": w, "seconds": (e - s) / FPS, "visual_brief": f"Readable hold for {w}"} for w, s, e, _ in words], fps=FPS), indent=2) + "\n")
    return render_scene(p)


def _smooth(t):
    return t * t * (3 - 2 * t)


def _ik(hip, target, l1=68.0, l2=68.0):
    dx, dy = target[0] - hip[0], target[1] - hip[1]
    d = min(math.hypot(dx, dy), l1 + l2 - 1e-6)
    base = math.atan2(dy, dx)
    cos_a = max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)))
    a = base - math.acos(cos_a)
    knee = (hip[0] + l1 * math.cos(a), hip[1] + l1 * math.sin(a))
    return knee, target


def walk_svg(frame: int, cycle: int = 24):
    """Original side-view walk with two-bone legs, counter-swinging arms and treadmill ground."""
    stride, stance = 36.0, 0.6
    phase = (frame % cycle) / cycle
    bob = -3.0 * abs(math.sin(phase * math.tau))
    hip = (120.0, 120.0 + bob)
    shoulder = (120.0, 70.0 + bob)
    ground = 248.0
    root = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width="240", height="280", viewBox="0 0 240 280")
    # Treadmill stripes move at stance-foot speed so planted feet do not slide.
    speed = 2 * stride / (stance * cycle)
    offset = -(frame * speed) % 120
    ground_g = ET.SubElement(root, "g", id="ground")
    ET.SubElement(ground_g, "rect", x="0", y=str(ground), width="240", height="32", fill="#173042")
    for x in np.arange(-120 + offset, 360, 120):
        ET.SubElement(ground_g, "rect", x=str(float(x)), y=str(ground + 8), width="46", height="4", fill="#2e5366")
    def leg(name, p, color):
        if p < stance:
            u = p / stance
            x = stride * (1 - 2 * u)
            lift = 0.0
        else:
            u = (p - stance) / (1 - stance)
            x = -stride + 2 * stride * _smooth(u)
            lift = 22.0 * math.sin(math.pi * u)
        target = (hip[0] + x, ground - lift)
        knee, foot = _ik(hip, target)
        g = ET.SubElement(root, "g", id=name)
        for a, b in ((hip, knee), (knee, foot)):
            ET.SubElement(g, "line", x1=str(a[0]), y1=str(a[1]), x2=str(b[0]), y2=str(b[1]), stroke=color,
                          **{"stroke-width": "13", "stroke-linecap": "round"})
        ET.SubElement(g, "circle", cx=str(knee[0]), cy=str(knee[1]), r="7", fill=color)
        toe = 18 if p >= stance else 14
        ET.SubElement(g, "path", d=f"M {foot[0]-8} {foot[1]-5} L {foot[0]+toe} {foot[1]-2} Q {foot[0]+toe+5} {foot[1]+5} {foot[0]+toe-2} {foot[1]+7} L {foot[0]-9} {foot[1]+7} Z", fill="#e7e6d7", stroke="#142536", **{"stroke-width": "2"})
        return foot, lift
    far_foot, far_lift = leg("leg-far", (phase + 0.5) % 1, "#233849")
    # Torso and head
    ET.SubElement(root, "path", d=f"M {hip[0]-18} {hip[1]} L {shoulder[0]-15} {shoulder[1]} Q {shoulder[0]} {shoulder[1]-12} {shoulder[0]+15} {shoulder[1]} L {hip[0]+18} {hip[1]} Z", fill="#427c83", stroke="#142536", **{"stroke-width": "3"})
    ET.SubElement(root, "circle", cx=str(shoulder[0]), cy=str(shoulder[1] - 30), r="22", fill="#f3c6a5", stroke="#142536", **{"stroke-width": "3"})
    ET.SubElement(root, "path", d=f"M {shoulder[0]-20} {shoulder[1]-38} Q {shoulder[0]} {shoulder[1]-60} {shoulder[0]+20} {shoulder[1]-38} L {shoulder[0]+18} {shoulder[1]-48} Q {shoulder[0]} {shoulder[1]-66} {shoulder[0]-18} {shoulder[1]-48} Z", fill="#183b4b")
    ET.SubElement(root, "circle", cx=str(shoulder[0] + 8), cy=str(shoulder[1] - 32), r="2.6", fill="#142536")
    # Arms counter-swing; simple two-segment limbs stay attached at shoulder.
    for name, ph, color in (("arm-far", phase + 0.5, "#2d5967"), ("arm-near", phase, "#427c83")):
        swing = math.sin(ph * math.tau)
        angle = math.radians(24 * swing)
        elbow = (shoulder[0] + 34 * math.sin(angle), shoulder[1] + 34 * math.cos(angle))
        hand = (elbow[0] + 30 * math.sin(angle * 0.7), elbow[1] + 30 * math.cos(angle * 0.7))
        g = ET.SubElement(root, "g", id=name)
        for a, b in ((shoulder, elbow), (elbow, hand)):
            ET.SubElement(g, "line", x1=str(a[0]), y1=str(a[1]), x2=str(b[0]), y2=str(b[1]), stroke=color,
                          **{"stroke-width": "11", "stroke-linecap": "round"})
        ET.SubElement(g, "circle", cx=str(hand[0]), cy=str(hand[1]), r="7", fill="#f3c6a5")
    near_foot, near_lift = leg("leg-near", phase, "#31536a")
    return ET.tostring(root, encoding="unicode"), {"far_lift": far_lift, "near_lift": near_lift,
                                                   "far_foot_y": far_foot[1], "near_foot_y": near_foot[1]}


def walk_cycle():
    p = OUT / "06-2d-walk-cycle"
    p.mkdir(parents=True, exist_ok=True)
    frames, cycle = 48, 24
    seq = p / "frames"; seq.mkdir(exist_ok=True)
    stance_errors = []
    for f in range(frames):
        svg, info = walk_svg(f, cycle)
        if f == 0:
            (p / "walk.svg").write_text(svg)
        png = resvg_py.svg_to_bytes(svg_string=svg, font_files=[str(FONT)])
        (seq / f"{f:04d}.png").write_bytes(png)
        for side in ("far", "near"):
            if info[f"{side}_lift"] == 0:
                stance_errors.append(abs(info[f"{side}_foot_y"] - 248.0))
    (p / "walk-qa.json").write_text(json.dumps({"cycle_frames": cycle, "rendered_frames": frames,
        "max_stance_foot_y_error": max(stance_errors), "ground_y": 248.0,
        "scope": "Geometric treadmill contact check; not artistic gait approval"}, indent=2) + "\n")
    (p / "exposure-sheet.json").write_text(json.dumps(timing_sheet(cycle, FPS,
        [{"frame": 0, "label": "contact"}, {"frame": 6, "label": "down"}, {"frame": 12, "label": "passing"}, {"frame": 18, "label": "up"}], 2), indent=2) + "\n")
    scene = dict(version=1, title="2D walk cycle: planted stance and swing", width=640, height=360, fps=FPS, frames=frames,
                 background="#102030", layers=[
                     layer("sky", "rect", x=320, y=180, width=640, height=360, fill="#102030"),
                     layer("performer", "image", asset="frames/%04d.png", x=320, y=170, width=288, height=336),
                     layer("caption", "text", x=320, y=330, text="CONTACT · DOWN · PASSING · UP", font_size=18, fill="#9db7c4"),
                 ])
    save_scene(p, scene)
    return render_scene(p)


def particle_burst():
    p = OUT / "07-particle-burst"
    p.mkdir(parents=True, exist_ok=True)
    pal = color_palette("#ffad42", "split_complementary", True)["roles"]
    (p / "palette.json").write_text(json.dumps(pal, indent=2) + "\n")
    frames = 72
    rng = np.random.default_rng(7)
    layers = [layer("background", "rect", x=480, y=270, width=960, height=540, fill=pal["background"]),
              layer("label", "text", x=480, y=70, text="ANTICIPATION → IMPACT → FOLLOW-THROUGH", font_size=22, fill=pal["muted"])]
    layers.append(layer("core", "ellipse", x=480, y=270, width=70, height=70, fill=pal["primary"], stroke=pal["text"], stroke_width=2,
                        tracks=[track("scale_x", [(0, 1), (10, 1.25), (13, 0.7), (18, 1.05), (40, 1)]),
                                track("scale_y", [(0, 1), (10, 0.75), (13, 1.3), (18, 0.95), (40, 1)]),
                                track("opacity", [(0, 1), (13, 1), (24, 0.25), (48, 0.25)])]))
    layers.append(layer("shockwave", "ellipse", x=480, y=270, width=80, height=80, fill="none", stroke=pal["accent"], stroke_width=5,
                        start=13, end=50, tracks=[track("scale", [(13, 0.4), (30, 3.4), (49, 5.2)]),
                                                  track("opacity", [(13, 0.9), (30, 0.45), (49, 0)])]))
    for i in range(36):
        angle = float(rng.uniform(0, math.tau)); speed = float(rng.uniform(120, 300))
        birth = 14 + i % 4; death = min(frames - 1, birth + 34 + i % 12)
        x0, y0 = 480.0, 270.0
        def pos(t):
            drag = math.exp(-0.9 * t)
            x = x0 + math.cos(angle) * speed * t * drag
            y = y0 + math.sin(angle) * speed * t * drag + 110 * t * t
            return x, y
        times = [birth, birth + 6, birth + 16, death]
        xs = [(t, pos((t - birth) / FPS)[0]) for t in times]
        ys = [(t, pos((t - birth) / FPS)[1]) for t in times]
        size = float(rng.uniform(5, 13))
        color = pal["accent"] if i % 3 else pal["secondary"]
        layers.append(layer(f"spark-{i:02d}", "ellipse", x=x0, y=y0, width=size, height=size, fill=color,
                            start=birth, end=death + 1,
                            tracks=[track("x", xs), track("y", ys),
                                    track("opacity", [(birth, 0), (birth + 2, 0.95), (death - 8, 0.6), (death, 0)]),
                                    track("scale", [(birth, 1), (death, 0.35)])]))
    scene = dict(version=1, title="Authored particle burst", width=960, height=540, fps=FPS, frames=frames,
                 background=pal["background"], layers=layers)
    save_scene(p, scene)
    return render_scene(p)


def vertical_short():
    p = OUT / "08-vertical-short"
    p.mkdir(parents=True, exist_ok=True)
    pal = color_palette("#6ee7b7", "triadic", True)["roles"]
    (p / "palette.json").write_text(json.dumps(pal, indent=2) + "\n")
    frames = 120
    layers = [
        layer("background", "rect", x=270, y=480, width=540, height=960, fill=pal["background"]),
        layer("safe-top", "text", x=270, y=150, text="MAKE IT MOVE", font_size=46, fill=pal["text"],
            tracks=[track("opacity", [(0, 0), (10, 1)]), track("y", [(0, 172), (12, 150)])]),
        layer("safe-subtitle", "text", x=270, y=212, text="A portrait-first staging proof", font_size=22, fill=pal["muted"],
            tracks=[track("opacity", [(8, 0), (20, 1)])]),
        layer("halo", "ellipse", x=270, y=480, width=220, height=220, fill=pal["primary"], opacity=0.12,
            tracks=[track("scale", [(0, 0.8), (30, 1.1), (60, 0.9), (90, 1.15), (119, 1.0)])]),
        layer("hero", "ellipse", x=270, y=480, width=96, height=96, fill=pal["primary"], stroke=pal["text"], stroke_width=3,
            tracks=[track("y", [(0, 430), (24, 540, "ease_in"), (48, 430, "ease_out"), (72, 540, "ease_in"), (96, 430, "ease_out"), (119, 480)]),
                    track("scale_x", [(0, 1), (22, 0.92), (24, 1.22), (28, 0.96), (70, 0.92), (72, 1.22), (76, 0.96), (119, 1)]),
                    track("scale_y", [(0, 1), (22, 1.08), (24, 0.78), (28, 1.04), (70, 1.08), (72, 0.78), (76, 1.04), (119, 1)])]),
        layer("shadow", "ellipse", x=270, y=560, width=120, height=18, fill="#000000", opacity=0.35,
            tracks=[track("scale_x", [(0, 0.7), (24, 1.2), (48, 0.7), (72, 1.2), (96, 0.7), (119, 0.9)])]),
        layer("safe-caption", "text", x=270, y=780, text="Keep faces and text inside safe areas", font_size=22, fill=pal["text"],
            tracks=[track("opacity", [(20, 0), (32, 1), (110, 1), (119, 0.9)])]),
        layer("cta", "text", x=270, y=845, text="Plan · Preview · Refine", font_size=24, fill=pal["accent"],
            tracks=[track("opacity", [(40, 0), (52, 1)])]),
    ]
    for i in range(3):
        layers.append(layer(f"dot-{i}", "ellipse", x=234 + i * 36, y=890, width=12, height=12,
                            fill=pal["accent"] if i == 0 else pal["muted"],
                            tracks=[track("opacity", [(i * 40, 0.4), (i * 40 + 8, 1), (min(119, i * 40 + 39), 1)])]))
    scene = dict(version=1, title="Vertical short: portrait-safe staging", width=540, height=960, fps=FPS, frames=frames,
                 background=pal["background"], layers=layers)
    save_scene(p, scene)
    (p / "delivery-notes.md").write_text("# Delivery notes\n\nPortrait-first 540×960 proof. Essential text stays away from edges; inspect at phone size. This is a staging/layout example, not a platform policy guarantee.\n")
    return render_scene(p)


def _explainer_shot(index: int, title: str, frames: int, pal: dict):
    layers = [layer("background", "rect", x=640, y=360, width=1280, height=720, fill=pal["background"]),
              layer("kicker", "text", x=640, y=90, text=f"SHORT LESSON 0{index}", font_size=22, fill=pal["muted"]),
              layer("title", "text", x=640, y=150, text=title, font_size=44, fill=pal["text"])]
    if index == 1:
        layers += [layer("figure-head", "ellipse", x=640, y=300, width=70, height=70, fill=pal["primary"]),
                   layer("figure-body", "rect", x=640, y=400, width=70, height=130, fill=pal["primary"]),
                   layer("figure-arm", "rect", x=700, y=380, width=90, height=18, fill=pal["secondary"],
                       tracks=[track("rotation", [(0, -15), (frames // 2, 10), (frames - 1, 0)])])]
    elif index == 2:
        keys_y = [(0, 300), (frames // 2, 500, "ease_in"), (frames - 1, 340, "ease_out")]
        layers += [layer("floor", "rect", x=640, y=540, width=900, height=12, fill=pal["surface"]),
                   layer("ball", "ellipse", x=640, y=300, width=70, height=70, fill=pal["accent"], tracks=[track("y", keys_y)])]
    else:
        layers += [layer("sheet", "rect", x=640, y=390, width=520, height=260, fill=pal["surface"]),
                   layer("check-1", "path", points=[(480, 340), (510, 370), (570, 310)], stroke=pal["accent"], stroke_width=8,
                       tracks=[track("reveal", [(0, 0), (frames // 3, 1)])]),
                   layer("check-2", "path", points=[(480, 420), (510, 450), (570, 390)], stroke=pal["accent"], stroke_width=8,
                       tracks=[track("reveal", [(frames // 3, 0), (2 * frames // 3, 1)])])]
    return dict(version=1, title=title, width=1280, height=720, fps=FPS, frames=frames, background=pal["background"], layers=layers)


def narrated_explainer():
    p = OUT / "09-narrated-explainer"
    p.mkdir(parents=True, exist_ok=True)
    text = ("Good animation starts with a clear pose. Timing gives that pose weight. "
            "Review the result, then refine one thing at a time.")
    speech = synthesize(text, p / "speech", speed=150)
    (p / "narration.json").write_text(json.dumps(speech, indent=2) + "\n")
    audio_rel = "speech/narration.wav"
    # Partition by sentence using actual engine word events, then add short handles.
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    words = speech["words"]
    cursor = 0
    boundaries = []
    for sent in sentences:
        target = sent.lower()
        joined = ""
        start_i = cursor
        while cursor < len(words) and joined != target:
            joined = (joined + " " + words[cursor]["text"].strip().lower()).strip()
            cursor += 1
        if joined != target:
            # Punctuation may be attached; fall back to character spans.
            end_char = text.lower().find(target) + len(target)
            while cursor < len(words) and words[cursor]["char_start"] < end_char:
                cursor += 1
        end_time = words[cursor - 1]["end"] if cursor else speech["duration"]
        boundaries.append((sentences.index(sent), start_i, cursor, end_time))
    total_frames = math.ceil((speech["duration"] + 0.6) * FPS)
    cuts = [0]
    for i, (_, _, _, end_time) in enumerate(boundaries):
        cuts.append(total_frames if i == len(boundaries) - 1 else min(total_frames - 1, round(end_time * FPS)))
    cuts = sorted(set(cuts))
    while len(cuts) < len(sentences) + 1:
        cuts.insert(-1, (cuts[-2] + cuts[-1]) // 2)
    pal = color_palette("#4f8cff", "complementary", True)["roles"]
    titles = ["Start with a clear pose", "Timing gives it weight", "Review, then refine"]
    clips, captions = [], []
    shot_plan = []
    for i, (start, end) in enumerate(zip(cuts, cuts[1:]), 1):
        shot = p / f"shot-{i:02d}"
        save_scene(shot, _explainer_shot(i, titles[i - 1], end - start, pal))
        qa = render_scene(shot)
        clips.append({"path": f"shot-{i:02d}/render/video.mp4", "start": 0, "duration": (end - start) / FPS})
        _, wi0, wi1, _ = boundaries[i - 1]
        cap_start = words[wi0]["start"] if wi1 > wi0 else start / FPS
        cap_end = min(words[wi1 - 1]["end"], end / FPS) if wi1 > wi0 else end / FPS
        captions.append({"text": sentences[i - 1] + ".", "start": cap_start, "end": cap_end})
        shot_plan.append({"shot": i, "start_frame": start, "end_frame": end, "title": titles[i - 1], "technical_pass": qa["technical_pass"]})
    assert all(a["end"] <= b["start"] + 1e-9 for a, b in zip(captions, captions[1:])), "Caption cues overlap"
    edit = dict(width=1280, height=720, fps=FPS, clips=clips, captions=captions, audio=audio_rel, caption_position=0.9)
    (p / "edit.json").write_text(json.dumps(edit, indent=2) + "\n")
    qa = edit_video(edit, p, p)
    streams = probe(p / "video.mp4")["streams"]
    audio_present = any(s["codec_type"] == "audio" for s in streams)
    qa["audio_present"] = audio_present
    qa["technical_pass"] = bool(qa["technical_pass"] and audio_present and (qa["width"], qa["height"]) == (1280, 720))
    (p / "qa.json").write_text(json.dumps(qa, indent=2) + "\n")
    (p / "shot-plan.json").write_text(json.dumps({"fps": FPS, "frames": qa["frames"], "shots": shot_plan,
        "timing_source": "eSpeak engine word events plus sentence handles; synthetic demo voice"}, indent=2) + "\n")
    if not qa["technical_pass"]:
        raise RuntimeError(f"Explainer failed QA: {qa}")
    return qa


BUILDERS = {"kinetic": kinetic_typography, "walk": walk_cycle, "particles": particle_burst,
            "vertical": vertical_short, "explainer": narrated_explainer}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", choices=sorted(BUILDERS), action="append", help="Build one example; repeatable")
    args = ap.parse_args()
    selected = args.only or list(BUILDERS)
    results = {}
    for name in selected:
        print("Building", name, flush=True)
        qa = BUILDERS[name]()
        results[name] = {"technical_pass": qa["technical_pass"], "frames": qa["frames"], "fps": qa["fps"],
                         "width": qa["width"], "height": qa["height"]}
        print(name, results[name], flush=True)
    report = ROOT / ".work/skill-examples-build.json"
    report.parent.mkdir(exist_ok=True)
    report.write_text(json.dumps(results, indent=2) + "\n")
    print("COMPLETE", json.dumps(results), flush=True)


if __name__ == "__main__":
    main()
