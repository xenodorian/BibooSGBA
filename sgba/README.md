# SGBA settings and build

`web/` is the game and is the only copy of it. These files only describe how the SGBA runtime should treat it.

| File | Purpose |
|---|---|
| `sgba_ui.json` | Settings for the SGBA runtime: how menus are navigated, which on-screen buttons to hide on a device, image memory limit, images to preload. |
| `sgba.ref` | Which version of the SGBA engine builds the packages. |
| `build.py` | Builds the Windows and ArkOS packages from `web/`. |

## Quick loops

- **Web:** serve `web/` with any static server, or use the Grok preview or GitHub Pages. Nothing here is needed.
- **Try the very same files in SGBA on a PC:** build once (`python sgba/build.py windows-x64`), unzip `dist/parry-perry-windows-x64.zip`,
  then run the launcher with the path of your working folder: `"Parry Perry.bat" C:\path\to\BibooSGBA\web`. The packaged engine runs your live
  files, so there is nothing to rebuild between edits.
- **On the handheld:** copy `Parry Perry.sh` and the `sgba` folder from `dist/parry-perry-arkos-aarch64.zip` into the SD card's Ports
  folder and start "Parry Perry" from the Ports list. Saves are kept in the `sgba/saves` folder next to it.

## Checking compatibility

`python <SGBA>/tools/sgba_check.py web` scans the game for features SGBA cannot run (WebGL, ES modules, networking) and loads it for a few
frames, failing on any JavaScript error. CI runs it on every change.

## Performance log

While playing, SGBA writes a line every ten seconds to `sgba/sgba.log` with frame times, memory use and image counts. Send that file after a play
session on a device to see real numbers.

## `sgba_ui.json` fields

- `navigation`: `"game"` (Parry Perry already moves menu focus from the gamepad itself; SGBA only draws the menu) or `"engine"`.
- `hide`: buttons to remove on a device. A CSS selector such as `#btn-fullscreen`, or `text:Moves: Keyboard` for a button whose label starts with that text.
- `preload`: glob patterns of images to decode before play (for example `assets/layers/*.png`) so they do not cause a stall the first time they are drawn.
- `image_budget_mb`: how much decoded image memory to keep (default 96).
- `alpha`: `"threshold"` cuts faint anti-aliased edges on sprites to on/off transparency to keep them compact; `"keep"` preserves them.
