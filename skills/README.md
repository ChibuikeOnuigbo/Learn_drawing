# Animation skill library

Start with [animation-director](animation-director/SKILL.md), the production operating contract. Then load only the skills matching the task. Each `SKILL.md` has portable name/description frontmatter, a concrete workflow, tool routes, limits and acceptance checks.

| Skill | Use it for |
|---|---|
| [animation-director](animation-director/SKILL.md) | Brief → route → produce → inspect → deliver |
| [drawing](drawing/SKILL.md) | Construction, poses, character sheets, layered art |
| [composition](composition/SKILL.md) | Staging, focal point, camera, continuity |
| [2d-animation](2d-animation/SKILL.md) | Vector/cut-out motion, parallax, stroke reveal |
| [3d-animation](3d-animation/SKILL.md) | Blender scenes, lighting, camera, rendering |
| [character-rigging](character-rigging/SKILL.md) | Hierarchies, IK, contact, props |
| [video-editing](video-editing/SKILL.md) | Cuts, captions, narration, music |
| [reaction-timing](reaction-timing/SKILL.md) | Semantic inserts at spoken beats |
| [quality-review](quality-review/SKILL.md) | Evidence-based review and delivery |

`index.json` is the machine-readable router. These are repository instructions, not plugins that automatically install themselves into every chat. See [connect instructions](../docs/CONNECT.md).

MCP hosts can read `studio://skills`, `studio://skills/{name}` and `studio://workflow`, or call `get_skill`. The same files are included in the Python package, so resource access does not depend on the client's current directory.

To adapt the library for a host that imports skills from a specific folder, point that host at these skill directories or copy them while preserving attribution. Keep this repository copy canonical; do not maintain divergent per-client instruction copies.
