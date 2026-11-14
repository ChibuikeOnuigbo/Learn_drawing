# Animation Agent Studio

A GitHub-ready prompt and practice framework for making YouTube explainers, motion graphics, vector drawing and 2D animation with local/free tools.

## What this is (and is not)

- `AGENTS.md` gives detailed work standards to compatible coding agents. You can also paste its contents into an AI agent's custom instruction or system prompt. Some agents do **not** automatically read `AGENTS.md`; add it explicitly if needed.
- `training/CURRICULUM.md` outlines practice missions.
- `training/LESSONS.md` is durable project knowledge for a future agent session.
- `training/evaluation_template.json` provides a review checklist.
- `resources/LEARNING_RESOURCES.md` curates documentation and YouTube tutorials.
- `projects/eye-glitch-demo/brief.json` provides a concrete timed-effect acceptance test.
- `scripts/inspect_video.py` uses `ffmpeg` and `ffprobe` to inspect actual output metadata and extract frames from event boundaries.

This repository **does not automatically fine-tune model weights**. For genuine model fine-tuning, choose a model with trainable weights, use legally authorized data, adequate hardware, and a proper evaluation regime. For most creators, a good code/render/QA loop will help before fine-tuning is worth the expense.

## Quick start

1. Clone this repo and open it in your coding agent.
2. Give the agent: `Read AGENTS.md. Follow projects/eye-glitch-demo/brief.json. Create an original 4-second scene and inspect it after rendering.`
3. Install the chosen engine, plus local FFmpeg.
4. Generate a video, e.g. `output/eye-test.mp4` (the agent must create it; it is not included in this starter).
5. Inspect: `python scripts/inspect_video.py --video output/eye-test.mp4 --brief projects/eye-glitch-demo/brief.json --output output/inspection`
6. Inspect the PNGs in `output/inspection` and add review notes in `training/LESSONS.md`.

Do not call the render accepted unless both temporal checks and visual review pass.

## Publish the prompt in GitHub

```bash
git init
git add .
git commit -m "Add animation agent prompt and evaluation harness"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/animation-agent-studio.git
git push -u origin main
```

Create the repo on GitHub first. Replace `YOUR-USERNAME`. A GitHub credential or GitHub Desktop may be needed to push.

## Storage

Commit prompt, scripts, JSON specs, SVG and small licensed source art to GitHub. Avoid committing video renders, caches, large models and third-party copyrighted reference videos to ordinary Git. GitHub blocks normal Git files above 100 MB; Git LFS can handle larger files but uses storage and bandwidth quotas. Keep large renders private/local or in an appropriate object store or drive and version only their manifests/links where permitted.

## License and privacy

Review license requirements of every tool, example and media asset. Keep private creative work and character references in private repos. Do not put access keys, private tokens or sensitive material in commits.

## If you want to update real model weights later

See [`training/OPTIONAL_FINETUNING.md`](training/OPTIONAL_FINETUNING.md) for the distinction between prompt memory and real LoRA/SFT, dataset requirements, and a configuration example.
