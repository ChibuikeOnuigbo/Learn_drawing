"""Remnant777-style narrated talking scene: AI scenery plates, parallax cloud drift,
and a PNGTuber cutout avatar with word-synced mouth swaps, blink cycle and talk bounce.

Layers (bottom to top): sky plate with a slow camera push, wispy far clouds drifting
slowly, cumulus near clouds drifting faster (independent depth rates per the research
playbook), grass/stone ground with matching parallax, then the avatar stack:
  mouth-closed idle plate -> mouth-open talk plate (opacity held to the voice)
  -> eyes-closed blink plate (short opacity spikes).
"""
from __future__ import annotations

import math
from pathlib import Path

from animation_mcp.render import render
from animation_mcp.speech import synthesize

ROOT = Path(__file__).resolve().parents[1]

NARRATION = ("Here is a narrated story scene. The sky and the grass are generated art plates. "
             "The clouds drift at different depths, so the picture feels alive. Our cutout "
             "character blinks, bounces, and talks right along with this voice. Simple layers, "
             "real timing.")


def hold_track(prop, keys):
    return dict(property=prop, keys=[dict(frame=int(f), value=v, easing="hold") for f, v in keys])


def smooth_track(prop, keys):
    return dict(property=prop, keys=[dict(frame=int(f), value=v, easing="smooth") for f, v in keys])


def linear_track(prop, keys):
    return dict(property=prop, keys=[dict(frame=int(f), value=v, easing="linear") for f, v in keys])


def main() -> None:
    folder = ROOT / "exmapels/talking-scene"
    folder.mkdir(parents=True, exist_ok=True)
    audio = synthesize(NARRATION, folder / "speech", 148)
    fps = 24
    frames = math.ceil((audio["duration"] + 0.8) * fps)

    layers = []

    def add(ident, kind, parent=None, **kwargs):
        value = dict(id=ident, kind=kind, **kwargs)
        if parent:
            value["parent"] = parent
        layers.append(value)
        return value

    # --- Scenery: sky push, two cloud depths, parallax ground -----------------
    add("sky", "image", asset="examples/assets/sky-day-clean.jpg",
        x=640, y=360, width=1280, height=720,
        tracks=[smooth_track("scale", [(0, 1.06), (frames - 1, 1.10)])])

    add("clouds-far-a", "image", asset="examples/assets/clouds-b.png",
        x=330, y=140, width=620, height=344, opacity=0.9,
        tracks=[linear_track("x", [(0, 330), (frames - 1, 330 - 34)])])
    add("clouds-far-b", "image", asset="examples/assets/clouds-b.png",
        x=1020, y=105, width=520, height=288, opacity=0.8,
        tracks=[linear_track("x", [(0, 1020), (frames - 1, 1020 - 26)])])

    add("clouds-near-a", "image", asset="examples/assets/clouds-a.png",
        x=380, y=205, width=560, height=280,
        tracks=[linear_track("x", [(0, 380), (frames - 1, 380 - 88)])])
    add("clouds-near-b", "image", asset="examples/assets/clouds-a.png",
        x=1130, y=170, width=430, height=215, opacity=0.92,
        tracks=[linear_track("x", [(0, 1130), (frames - 1, 1130 - 118)])])

    add("ground", "image", asset="examples/assets/ground-cutout.png",
        x=640, y=690, width=1360, height=576,
        tracks=[linear_track("x", [(0, 640), (frames - 1, 640 - 46)])])

    # --- Avatar: three pixel-aligned state plates in one bounce group --------
    words = [w for w in audio["words"] if w["end"] > w["start"]]
    mouth_keys = [(0, 0.0)]
    last_end = 0.0
    for w in words:
        start, end = w["start"], w["end"]
        if start - last_end > 0.22:  # real pause -> close the mouth
            mouth_keys.append((round(last_end * fps) + 1, 0.0))
        s = max(round(start * fps), int(mouth_keys[-1][0]) + 1)
        mouth_keys.append((s, 1.0))
        e = max(round(end * fps) + 1, s + 1)
        mouth_keys.append((e, 0.0))
        last_end = end
    if mouth_keys[-1][1] != 0.0:
        mouth_keys.append((round(last_end * fps) + 1, 0.0))

    blink_keys = []
    b = 66
    while b < frames - 10:
        blink_keys += [(b - 1, 0.0), (b, 1.0), (b + 5, 0.0)]
        b += 74  # roughly a 3.1 s cycle at 24 fps

    # Gentle talk bounce: vertical bob keys across the whole narration.
    bob = []
    span = frames - 1
    step = 9
    for i, f in enumerate(range(0, frames, step)):
        bob.append((min(f, span), -3.2 if i % 2 else 3.2))
    bob[-1] = (span, 0.0)

    add("avatar", "group", x=1010, y=420,
        tracks=[smooth_track("y", [(f, 420 + v) for f, v in bob])])
    add("avatar-idle", "image", "avatar", asset="examples/assets/avatar-mouth-closed.png",
        x=0, y=0, width=372, height=413)
    add("avatar-talk", "image", "avatar", asset="examples/assets/avatar-cutout.png",
        x=0, y=0, width=372, height=413,
        tracks=[hold_track("opacity", mouth_keys)])
    add("avatar-blink", "image", "avatar", asset="examples/assets/avatar-eyes-closed.png",
        x=0, y=0, width=372, height=413,
        tracks=[hold_track("opacity", blink_keys)])

    # --- Caption strip: one timed text layer per narration line ---------------
    add("caption-bg", "rect", x=640, y=662, width=1180, height=54,
        fill="#101820", opacity=0.62)
    lines = [line.strip() for line in NARRATION.split(".") if line.strip()]
    words = audio["words"]
    if sum(len(line.split()) for line in lines) == len(words):
        chunks, wi = [], 0
        for line in lines:
            n = len(line.split())
            chunks.append(words[wi:wi + n])
            wi += n
    else:  # fall back to even distribution across the clip
        step = max(1, len(words) // len(lines))
        chunks = [words[i * step:(i + 1) * step] for i in range(len(lines))]
        chunks[-1] = chunks[-1] + words[len(chunks) * step:]
    for i, (line, chunk) in enumerate(zip(lines, chunks)):
        start_f = max(0, round(chunk[0]["start"] * fps) - 2) if chunk else 0
        end_f = min((round(chunk[-1]["end"] * fps) + 12 if chunk else frames), frames)
        add(f"caption-{i}", "text", x=640, y=672, font_size=26,
            text=line + ".", fill="#ffffff", start=start_f, end=end_f)
    # Half-open intervals must not overlap: close each caption when the next starts.
    caps = [l for l in layers if l["kind"] == "text"]
    for a, b in zip(caps, caps[1:]):
        a["end"] = max(a["start"] + 1, b["start"])

    scene = dict(
        version=1, title="Talking scene — scenery, clouds and a PNGTuber cutout",
        width=1280, height=720, fps=fps, frames=frames,
        background="#8ecae6", audio="exmapels/talking-scene/speech/narration.wav",
        layers=layers,
    )
    import json
    (folder / "scene.json").write_text(json.dumps(scene, indent=1) + "\n")
    result = render(folder / "scene.json", folder / "render", ROOT)
    print(json.dumps({k: result[k] for k in
                      ("video", "frames", "fps", "technical_pass", "errors")}, indent=1))


if __name__ == "__main__":
    main()
