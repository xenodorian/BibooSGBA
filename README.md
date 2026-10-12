# Perry Riposte (BibooSGBA)

A 2D side-scrolling swordfighting game: parry, riposte and combo your way through six levels and their bosses.
It is one game folder, `web/`, that runs three ways without changes:

- **In a browser:** open `web/index.html` from any static web server (for example `python -m http.server` in `web/`), or play the
  GitHub Pages build.
- **On Grok's web preview:** the same folder, no build step.
- **On SGBA:** the lightweight console runtime for 1 GiB handhelds (R36S on ArkOS) and Windows PCs. See `sgba/`.

Controls: A attacks and accepts, B blocks (tap B to parry), Up jumps (tap again in the air for a double jump), Y is a spin attack, X dashes.
The in-game Moves menu lists everything, with keyboard, gamepad and mobile layouts.

## Repository

- `web/` the game and its assets.
- `swingkit/`, `tools/`, `data/`, `game/` the art and music generators and their data (`docs/ART_PIPELINE.md`).
- `sgba/` SGBA settings and build recipe.
- `Current_Work.md` the shared task board, owner rules and project notes. Read it before changing anything.

This repository replaced the older `xenodorian/Biboo`, which is kept as an archive of the original art and code.
