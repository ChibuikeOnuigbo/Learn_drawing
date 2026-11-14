# Reference observations and provenance

Date: 2026-11-14. The uploaded master prompt and uploaded AGENTS text were identical reference material. They were not adopted as repository instructions. The user's actual goals and later replies guide this implementation.

## Access

The supplied Drive folder was accessible without cookies. All 13 visible top-level files were downloaded; SHA-256 values are in the manifest. All four ZIP archives passed CRC checks. The study archive contains 185 video files. Downloading, hashing and extracting these files does not mean they were all watched or used for training.

Direct access to the user's YouTube example and Alan Becker channel failed with proxy `403 Forbidden`. No title, scene content, exact timing or artistic quality is inferred for those links. Their difficulty labels in the catalog come from the user. Remnant777 preferences below come from the user's description.

## Observed Drive samples

I inspected the existing `boards/video_sample_timelines.jpg` contact sheet from `NothingxArt_Analysis_and_Training.zip`. This shows sparse samples of five drawing-process videos, not uninterrupted playback or recovered brush paths:

- `IHttW8k_Bog`: early crops show tall angular magenta building forms; later samples show a bright circular glow between buildings. Useful exercise: large silhouette/value masses before small lights.
- `W52Klsq-JuE`: broad blue sky and pale ground in early samples; dark tree silhouettes and a warm horizon appear later. Useful exercise: preserve a warm/cool hierarchy and selective edge detail.
- `3v3_3WAbnks`: dark tree/ground silhouette with small sky accents; later samples show more purple sky texture. Useful exercise: keep the main silhouette readable while adding texture.
- `ajqhisQoP7g`: samples show colored circular bands and angled ring forms, followed by a softer pink image. Useful exercise: separate large color regions from the focal shape. Do not trust thumbnail-derived titles as full video descriptions.
- `uFTaTY1eT8c`: samples progress from a dark landscape/sky to diagonal streaks. Useful exercise: strong directional accents over restrained background detail.

Canvas zoom, UI changes and edits are visible, so pixel changes cannot be treated as artist stroke actions. These clips were not used in the new curve training run.

## Applied composition principles

The original vector explorer example uses a fixed hero silhouette, three landscape depths moving at different rates, a limited cool palette with a warm focal object, a readable title hold and true path reveals. These are original authored elements.

The user's description of short Remnant777-style composed scenery motivates the second example: an AI-generated observatory background plus original editable vector overlays and a slow camera push. This is a composition prototype; it is not a reconstruction of that creator's work or a claim to match the reference quality.

## Consulted technical sources

- MCP build-server documentation: https://modelcontextprotocol.io/docs/develop/build-server — retrieved successfully; checked local Python SDK and validated stdio initialization/tool calls through its actual client.
- Blender API render documentation: https://docs.blender.org/api/4.3/bpy.ops.render.html — remote access denied; used the installed Blender 4.3.2 API and verified a CPU render instead.
- Blender, FFmpeg, CairoSVG, Pillow and scikit-learn behavior was tested directly by rendering, decoding, fitting, training and installing in a clean virtual environment.

## Generated concept asset

`examples/assets/observatory-ai.png` was generated in this session using the available image-generation tool from an original prompt: a blue-hour alien observatory, dark teal mountains, coral horizon, distant moon, empty platform, graphic-novel painted texture, no characters or text. It is used as a **raster background**, not presented as editable vector artwork or output of the small basketball model. The second scene's character and diagrams remain editable vector layers. The MCP server prepares concept prompts but does not contain access to this session's image-generation service.
