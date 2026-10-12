"""Measure how the game runs on SGBA across several scenes, on this machine.

    python sgba/bench.py                 # print a table
    python sgba/bench.py --save before   # also keep the numbers in .bench/before.json
    python sgba/bench.py --compare before

Numbers are from the machine you run it on. Use them as before/after comparisons, not as device speeds.
Needs the SGBA engine like build.py does.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import REPO, engine_dir  # noqa: E402

# name -> (frames, input script, JavaScript run at given frames)
SCENES = {
    "title":     (240, "", []),
    "level1":    (600, "170:hold:right:300,200:tap:a:25", ["30=document.getElementById('btn-start')&&document.getElementById('btn-start').click()", "60=P.unlockAllLevels()", "90=bibooGame.enterLevel(1)"]),
    "level3":    (600, "170:hold:right:300,200:tap:a:25", ["30=document.getElementById('btn-start')&&document.getElementById('btn-start').click()", "60=P.unlockAllLevels()", "90=bibooGame.enterLevel(3)"]),
    "level4":    (600, "170:hold:right:300,200:tap:a:25", ["30=document.getElementById('btn-start')&&document.getElementById('btn-start').click()", "60=P.unlockAllLevels()", "90=bibooGame.enterLevel(4)"]),
    "overworld": (300, "", ["30=document.getElementById('btn-start')&&document.getElementById('btn-start').click()", "60=goOverworld()"]),
}


DEVICE = {"zip": None, "mem": 640}      # set by --device: run inside the ARM bundle under QEMU instead of natively


def run_scene(engine: Path, name: str, repeats: int = 3) -> dict:
    """Best of a few runs: other work on the machine only ever makes a run slower."""
    runs = [run_once(engine, name) for _ in range(1 if DEVICE["zip"] else repeats)]
    return min(runs, key=lambda r: r["avg_ms"])


def run_once(engine: Path, name: str) -> dict:
    frames, script, js = SCENES[name]
    out = Path(tempfile.mkdtemp()) / f"{name}.json"
    command = [sys.executable, str(engine / "tools" / "js_bench.py"), str(REPO / "web"), "--frames", str(frames), "--skip", "120",
               "--json", str(out), "--script", script or "9999:a"]
    for item in js:
        command += ["--js", item]
    if DEVICE["zip"]:
        sys.path.insert(0, str(engine / "tools"))
        import device_sim
        device_sim.run(Path(DEVICE["zip"]), command[3:], DEVICE["mem"], "0", game=str(REPO / "web"))
        return json.loads(out.read_text())
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    subprocess.run(command, check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return json.loads(out.read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenes", nargs="*", default=list(SCENES))
    parser.add_argument("--save", help="store results as .bench/<name>.json")
    parser.add_argument("--compare", help="compare with .bench/<name>.json")
    parser.add_argument("--device", help="ArkOS bundle zip: run the scenes in it under QEMU (ARM, one core, limited memory) as a stand-in for the R36S")
    parser.add_argument("--mem", type=int, default=640, help="address space limit in MB for --device")
    args = parser.parse_args()
    DEVICE["zip"], DEVICE["mem"] = args.device, args.mem
    engine = engine_dir()
    results = {name: run_scene(engine, name) for name in args.scenes}
    base = {}
    if args.compare:
        base = json.loads((REPO / ".bench" / f"{args.compare}.json").read_text())
    header = f"{'scene':10s} {'avg ms':>8s} {'p95':>6s} {'p99':>6s} {'max':>6s} {'RSS MB':>7s} {'imgs MB':>8s} {'alpha kpx':>10s} {'errs':>5s}"
    print(header)
    for name, r in results.items():
        line = f"{name:10s} {r['avg_ms']:8.2f} {r['p95_ms']:6.1f} {r['p99_ms']:6.1f} {r['max_ms']:6.0f} {r['rss_mb']:7d} {r['decoded_mb']:8.1f} {r['alpha_kpx']:10d} {r['js_errors']:5d}"
        if name in base:
            b = base[name]
            line += f"   (was {b['avg_ms']:.2f} ms, {b['rss_mb']} MB, {b['decoded_mb']} MB)"
        print(line)
    if args.save:
        folder = REPO / ".bench"
        folder.mkdir(exist_ok=True)
        (folder / f"{args.save}.json").write_text(json.dumps(results, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
