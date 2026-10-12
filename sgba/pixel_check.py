"""Render a few scenes on SGBA and compare the pictures with an earlier run, pixel by pixel.

    python sgba/pixel_check.py --save before     # render, keep in .bench/shots/before
    python sgba/pixel_check.py --compare before  # render, compare with the saved set (exit 1 on any difference)

Use it around a rendering change that must not alter how the game looks.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import REPO, engine_dir  # noqa: E402

SEED = "0=(function(){let s=12345;Math.random=function(){s=(s*1664525+1013904223)>>>0;return s/4294967296;};})()"   # the game uses Math.random for bobbing and sparks
START = "30=document.getElementById('btn-start').click()"
UNLOCK = "60=P.unlockAllLevels();bibooGame.unlock('laser_beam')"
SHOTS = {      # name -> (frames, input script, JavaScript at given frames)
    "title": (200, "", []),
    "level1": (300, "150:hold:right:60", [START, UNLOCK, "90=bibooGame.enterLevel(1)"]),
    "level1b": (420, "150:hold:right:60,300:tap:a:20", [START, UNLOCK, "90=bibooGame.enterLevel(1)", "100=bibooGame.setMeters(100,100,100)"]),
    "level3": (360, "150:hold:right:90,260:tap:a:12", [START, UNLOCK, "90=bibooGame.enterLevel(3)", "100=bibooGame.setMeters(100,100,100)"]),
    "level4": (360, "170:hold:right:150,250:tap:a:25", [START, UNLOCK, "90=bibooGame.enterLevel(4)"]),
    "beam": (192, "149:hold:l1:60,152:hold:a:3", [START, UNLOCK, "90=bibooGame.enterLevel(3)", "100=bibooGame.setMeters(100,100,100)"]),
    "overworld": (200, "", [START, "60=goOverworld()"]),
}


def render(engine: Path, out: Path, names) -> None:
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    for name in names:
        frames, script, js = SHOTS[name]
        command = [sys.executable, str(engine / "tools" / "js_bench.py"), str(REPO / "web"), "--frames", str(frames),
                   "--script", script or "9999:a", "--shot", str(out / f"{name}.png")]
        for item in [SEED] + js:
            command += ["--js", item]
        subprocess.run(command, check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def differences(a: Path, b: Path) -> int:
    import pygame
    x, y = pygame.image.load(str(a)), pygame.image.load(str(b))
    if x.get_size() != y.get_size():
        return -1
    count = 0
    for row in range(x.get_height()):
        for col in range(x.get_width()):
            if x.get_at((col, row)) != y.get_at((col, row)):
                count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--save")
    parser.add_argument("--compare")
    parser.add_argument("--scenes", nargs="*", default=list(SHOTS))
    args = parser.parse_args()
    engine = engine_dir()
    shots = REPO / ".bench" / "shots"
    if args.save:
        render(engine, shots / args.save, args.scenes)
        print(f"saved {len(args.scenes)} pictures in {shots / args.save}")
        return 0
    if args.compare:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        fresh = Path(tempfile.mkdtemp())
        render(engine, fresh, args.scenes)
        bad = 0
        for name in args.scenes:
            n = differences(shots / args.compare / f"{name}.png", fresh / f"{name}.png")
            print(f"{name:10s} {'identical' if n == 0 else str(n) + ' pixels differ'}")
            bad += n != 0
        return 1 if bad else 0
    parser.error("give --save NAME or --compare NAME")


if __name__ == "__main__":
    raise SystemExit(main())
