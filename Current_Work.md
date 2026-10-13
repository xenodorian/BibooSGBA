# Current Work

Shared task board for everyone working on this repo, humans and agents. Read the rules first.

## What this repository is

BibooSGBA is the main repository for **Perry Riposte** (the game's earlier name was Biboo). It was started clean on 2026-10-12 from the old `xenodorian/Biboo` repository (last commit there: `5ec7d90`, stage 173), which stays untouched as an archive. If a change to the art or code goes wrong, the originals are in that repo.

The goal here is a lighter, more efficient version of the game that is built to run well on **SGBA** (the owner's small console runtime for 1 GiB handhelds such as the R36S running ArkOS, and for Windows) **and** still runs unchanged in a web browser, on Grok's web preview, and on GitHub Pages. Both must keep working: edit the game, test it on the web, then run the very same files on SGBA.

## Layout

| Path | What it is |
|---|---|
| `web/` | The game. A plain static folder (`index.html`, scripts, `assets/`). It must run from any static web server with no build step. This is what Grok previews, what Pages publishes, and what SGBA runs. |
| `swingkit/`, `tools/`, `data/`, `game/`, `requirements.txt` | The art and music generators and the data they use. `python -m swingkit --web` rebuilds `web/assets` (see `docs/ART_PIPELINE.md`). |
| `tests/`, `web/tests/` | Python and Node regression tests. |
| `sgba/` | SGBA-only settings and build recipe: `sgba_ui.json` (device settings), `sgba.ref` (engine version), `build.py` (builds the Windows and ArkOS packages), `README.md`. |
| `.github/workflows/pages.yml` | Publishes the site (a redirect at `/` and the game at `/web/`). |

The old Dreamcast and MAME ports were removed on purpose and are not coming back. The old repo has them if ever needed.

## Rules for agents

**Owner rules (2026-10-12):**
- **Display and UI:** the game canvas is 640x480; do not change the resolution, the page layout/CSS in `web/index.html`, the touch controls, menus, HUD or the Menu button without the owner's explicit say-so. A refactor or an optimization is not consent. If something about the display looks wrong, tell the owner instead of changing it.
- **Images:** you may change how images are encoded (for example a more compact PNG) if it improves efficiency and the picture is visually unchanged. The originals live in the old Biboo repo. Do not resize, crop, resample or hand edit them. Show before/after if quality could change.
- **Testing:** keep it sane. Run a check only when it is relevant to the change, and ask the owner before running anything that is not clearly critical. The owner does most testing personally. Never get into long test loops.
- **Git:** work on `main`, `git pull --rebase` then push after each finished step, and end commit messages with the Co-Authored-By and Claude-Session lines.
- **Cache stamp:** after any change to the game or its assets, bump `window.BIBOO_VER` and every `?v=` in `web/index.html`: `sed -i "s/BIBOO_VER = 'stN'/BIBOO_VER = 'stN+1'/; s/v=stN/v=stN+1/g" web/index.html`.
- **Terms:** *Hitbox* is where a character can be hit and receive damage (the vulnerable area). *Hurtbox* is the parts of a character that cause damage (the attack area). The code uses the opposite words: in `data.js` and `game.js` a frame's `hurt` is the vulnerable box (a hitbox here) and `hit` / `hits` is the attack shape (a hurtbox here); `herBox()` / `hurtOf()` return vulnerable boxes. They are not renamed; translate when talking about them.

**Technical notes:**
1. `web/game/00_core.js` was once overwritten four times by a one-line placeholder (`PLACEHOLDER_AGAIN is not defined` is the symptom; the game then fails to load). The good file is about 26 KB. If it is tiny, restore it from git history. Always `git pull --rebase` before pushing.
2. All of `web/game/` is one shared global scope: classic `<script>` files, load order set in `web/index.html`, no modules. A syntax error in any file takes the whole game down. Check edits with `node -e "new Function(require('fs').readFileSync('FILE','utf8'))"`. A top-level `let screen` shadows `window.screen`.
3. Keep the web page working in plain browsers and on the Grok preview. Anything SGBA needs that the web does not should live in `sgba/`, or sit behind a `window.SGBA` check.
4. SGBA runs the game inside a small JavaScript engine with 2D canvas, Web Audio (buffer sources and gain), images, `localStorage`, `fetch` of local files and the Gamepad API. It does not support WebGL, ES modules, networking or synthesized audio. Avoid `getImageData`/`putImageData`, full-screen translucent overlays every frame, and very wide sprite sheets: they are the slowest things on a handheld.

## Project state (what exists)

**Game:** "Perry Riposte", a 2D side scroller, canvas 640x480 shown with `image-rendering: pixelated`. Live site (once Pages is enabled for this repo): https://xenodorian.github.io/BibooSGBA/web/ . Hero is Perry (full name Peregrine "Perry" Riposte; the opening line uses the full name, the title screen says Perry Riposte, all other text says Perry).

**Code layout:** `web/index.html`, `web/ui.js` (menus, shop, move lists with row cursor and Y descriptions), `web/progress.js` (saves, unlocks, ankhs without a cap), `web/levels.js` (map generator, leaves, boss maps), `web/input.js`, `web/music.js`, and the engine split into `web/game/00_core.js` to `22_test_hooks.js` (core and menus, assets, health, training, hazards, enemies in `11_enemies.js`, enemy attacks in `13_enemy_attacks.js`, player drawing, HUD, menus, story in `18_story.js`, title and overworld in `20_title.js`, test hooks in `22_test_hooks.js` which exposes `window.bibooGame`). Art and data generators are in `tools/` (creatures, arenas, backgrounds, items, music, training). Generated data: `web/assets/data.js`, `creatures.js`, `arenas.js`, `items.js`, `training.js`, `story.js`.

**Progression:** six levels (Green Trail, Mossy Falls, Sunstone Canyon, Sunset Shore, and two more; map counts per level not re-verified in this condensing) each ending in a boss map; optional Sunset Training; a Bone Merchant shop reached from the overworld. Each map's right door opens once every non-prop enemy is dead. Currency is Leaves (gold coins, start 100, never placed over pits). Gems are Bone (health), Quartz (energy), Garnet (empower), Diamond (super), Bone Powder (+25 max HP). Max HP starts at 50. Ankhs are extra lives with no cap. Unlocks are bought in the shop (Y shows what an item or unlock does); the Items menu replaced the Gems menu; Moves menus exist for gamepad and keyboard. Saving is manual (Save game writes localStorage `parryperry.manualsave.v1`). Dev cheats sit behind the L1+L2+R1+R2 chord. Hard reset wipes all saved keys.

**Controls (live game):** A attack and accept, Up jump (tap again in the air for the double jump), Y spin attack, X+Y taunt, Down then Up sky dash, hold A then release for the heavy chop, R held to recover. Energy moves use the L2, R2 and shoulder buttons.

**Combat numbers worth knowing:** parry of a melee attack deals 10 damage (`PARRY_DMG`, `05_health.js`). Enemy attacks land 300 ms after first contact so a parry up to 300 ms late counts. Bosses: Wyrm Slug (L1), Ooze Wraith (L2), Horned Dread (L3), Boar Lord (L4), Mirror Perry (final, level 5 keep). Bosses ignore taunt and plasma and drop 9 gems, 3 ankhs and a Bone Powder.

**Enemies (st162):** sight is doubled (`SIGHT_MUL = 2`). Enemies aim at the middle of Perry's body box (`herMidX()`), every enemy climbs, drops from platforms and hops pits (goblin carries 200 px, orc 70 px). **Policy:** an enemy does not stop at Perry's sword or at the end of its weapon reach. It walks until its body box meets her hitbox (`herBox`), and only then attacks. Percy uses the same rule (`duelRoom`). `strikeAttacks` must not be used as the reason to stop walking. Goblin keeps its combo-first pattern. Creature damage boxes were tightened to the leading slice of the sprite by `tools/creatures/tighten_hits.py`; run it again after `tools/creatures/build.py`.

**Story and cutscenes (st84 to st101):** `web/game/18_story.js` holds the `STORY` pages (prologue, double, ending) and a per-scene table `SC` (picture pan, Perry's feet and scale, light `L`). Text is at the top. Backgrounds are the eight scene pictures in `web/assets/story/view/`, mapped in `web/assets/story.js`; boss arenas for fungal, crypt, bone and keep use scene pictures through `ARENA_STILLS`. Perry and evil Perry (Mirror Perry sheet) are stationary, drawn at the same scale. Shadows: `castShadow()` lays a silhouette on the ground along the scene light (`sx`, `sy`, `a`, `col`); the temple scene steps it up the stair treads (`L.steps`), the cliff scene clips it at the edge (`L.clip`), the burning house flickers shear and opacity. Current shadow opacity: meadow and crowd 0.8, burning house 1.0, courtyard 0.8, temple 0.8, cliff 1.0. Miracle Island has no shadow: a rippled, fading reflection of the boat is mirrored below the hull, and the boat is still. The title screen uses the same shadow code (`20_title.js`). Gameplay (`15_draw_scenery.js`, `LIGHTS`) uses the same cast on flat ground, a pixel contact blob on platforms and in the air, a multiply grade, and a short rippled reflection on shore, falls and the fungal arena. The 1 px rim from st101 was removed in st104: it read as a white outline. The fire cutscene's orange wash is an overlay drawn after the figures. Soft glows (crates, gems, blasts, lit bombs) are 2 px stamps.

**Audio:** 17 original chiptune songs generated by `tools/music/compose.py`, played by `BibooMusic` (Web Audio, crossfade, volume Off/30/60/100).

## Tools any agent can use

**`tools/edge/spriteedge.py`: find a sprite's drawn outline, exactly.** One self-contained file (Python 3.8+, Pillow, numpy; scipy optional). Copy it to any project; its top comment is the full manual. Use it when you must cut a character off its background, recolour or isolate its outline, or check where an outline is, instead of guessing with brightness thresholds.

- **Method:** the outside is the backdrop colour plus any flat shadow colour you name (exact match); the sprite is everything else; the boundary is the sprite pixels touching the outside; the border is the boundary pixels that are dark ink. Pale boundary pixels with no black edge (drool, a tusk tip) are reported as skipped and never recoloured. Dark lines inside the sprite are never touched. Drop shadows are outside, so the border never wraps them.
- **Use:** `python3 tools/edge/spriteedge.py IMAGE --suggest` lists the likely backdrop and shadow colours (suggestions: check them). Then `python3 tools/edge/spriteedge.py IMAGE --outside 99,99,99 49,49,49` writes `IMAGE_edge/` with the original, the frame with the border in red, a transparent cutout, border and sprite masks, and a JSON report (counts, enclosed pockets, warnings). `--frames all` runs every frame of a GIF, `--thickness N`, `--ink-color` and `--show-skipped COLOR` adjust it, `--self-test` checks the tool. From Python: `find_border(rgba, outside=[...])` returns masks (`border`, `skipped`, `sprite`, `outside`) and a report.
- **Works on** exact-colour art (GIF, PNG, palette sprites). **JPEG, blurred or anti-aliased art:** use `--tolerance 14 --flood --ink-lum 60`; it is approximate (on the 450 px boar frame saved as JPEG it found 91% of the border at quality 95, 87% at 88, 71% at 75). A soft gradient shadow cannot be separated.
- **Checked on:** the 450 x 450 black boar GIF (12 frames): 2,575 border pixels on frame 0 and identical to the hand-checked picture pixel for pixel, enclosed pockets (tail curl, gap between the legs) found, shadow left alone. Tests: `tests/test_spriteedge.py`.

## Open items

- Cliff scene: Perry's shadow shoots left as a thin spike over the grass edge. The user has not decided whether to shorten or tilt it.
- Unrun or stale tests (see note 5) and the two docs fixes (note 6).
- Possible polish: per-attack reach for enemies, boss attack telegraphs, a boss unlock drop, a balance pass on boss damage.
- Heavy Horizontal reuses the slash animation.

## SGBA

`python sgba/build.py` builds `dist/parry-perry-windows-x64.zip`, `dist/parry-perry-arkos-aarch64.zip` and `dist/parry-perry.sgba` from `web/` exactly as it is. CI (`.github/workflows/sgba.yml`) checks the game runs on SGBA and attaches the packages to each run. Device-only choices (hidden buttons, memory limit, preload lists) live in `sgba/sgba_ui.json`; see `sgba/README.md`. The packages leave out the MP3 music copies, MIDI files and web tests.

## Log

- 2026-10-12: repository started clean from Biboo `5ec7d90` (stage 173). Removed `ports/` (Dreamcast and MAME), the root screenshots and `web/scale_compare*.png`; the old README became `docs/ART_PIPELINE.md`. All tools carried over.
- 2026-10-12: added `sgba/` (settings, build script, CI). The SGBA packages build and the game starts directly in them.

## SGBA optimization passes (done)
- Engine: fade baking, multiply blends honor alpha, `source-in` fills, horizontal shear (cast shadows), `SGBA.preload(urls)` hook (decodes one image per frame ahead of first draw; the game announces each map's enemy sheets in `09_maps.js`).
- Measured (sgba/bench.py, desktop CPU ms/frame, before -> after): title 5.73 -> 4.81, level1 4.48 -> 3.07, level3 3.71 -> 2.48, level4 4.92 -> 3.71.
- Not done on purpose: lossless PNG re-encode (saves ~10% disk only, no decode gain), parallax merge and sprite-sheet splitting (RLE already covers it; the 15411 px boarlord strip decodes to ~18 MB, a grid re-layout would need game code changes), rewriting draw code (flat profile, no function above 0.25 ms/frame).
- Package leaves out 10 unreferenced source images (story/N_*.png are inputs to tools/prepare_story_assets.py).

2026-10-13: OPEN, for another agent to review: the owner's device does not have the latest build
- Owner report: the crates are too small and the speed is not enough, and the owner is on the older build. The owner updates through the GitROMs updater (https://github.com/xenodorian/GitROMs). The owner has confirmed the device does NOT have the latest update.
- Reference for comparison: BibooSGBA main at d6f18d2, BIBOO_VER st177. Crates are CRATE_SCALE 2.8 in web/game/00_core.js (about 56 px wide on screen, shown in a native-runtime screenshot of level 1). If the owner's crates look smaller, the device is not running this.
- Not verified by me: which file or release GitROMs fetches, whether the "latest" release (added by another session in commit d6f18d2, rolling release from the CI workflow) has been published and contains the st177 build, and whether GitROMs installed it over the old folder. I have not read the GitROMs repo.
- Things to check: (1) the workflow run for d6f18d2 finished and updated the release; (2) the release asset is the current bundle and its README/game folder carry st177; (3) how GitROMs picks the asset (name, python bundle versus the new native bundle parry-perry-native-arkos-aarch64.zip) and whether it skips an update when the folder already exists; (4) the build stamp the owner's device reports (sgba.log or the page footer) against st177.
- Separate, not started: the owner wants crates larger than 2.8 (target size not given yet) and more speed. The native bundle has only been timed under QEMU, never on the R36S.

2026-10-13: RESOLVED (diagnosis for the item above): the owner's GitROMs saved the game to `sgba/games/parry-perry.sgba`, but the "Parry Perry" port on the device runs a different copy, the loose folder `sgba/games/parry-perry/` from the old standalone bundle, so updates never reached what ran. The latest release itself was current (st177, crates 2.8).
- New single path (owner decision: the emulator holds no real games, each game lives in its own repo): the release `latest` now carries one device asset, `parry-perry-port.zip`, built by `python sgba/build.py` (`make_port`). It holds `Parry Perry.sh` (launcher, source in `sgba/Parry Perry.sh`) and the game in its own folder `parry-perry/`. The launcher starts the separately installed SGBA emulator (`SGBA.sh`, from the SGBA repo's release) on that folder. The emulator keeps only its demo, input lab and controller setup.
- The old release assets (`parry-perry.sgba`, `parry-perry-arkos-aarch64.zip`, `parry-perry-native-arkos-aarch64.zip`) are no longer uploaded but are still attached to `latest` until someone deletes them. The standalone zips are still produced as workflow artifacts.
- GitROMs installs `parry-perry-port.zip` at the ports root and removes the old `sgba/games/parry-perry*` copies after a verified install.
