"""Find the game's slowest JavaScript functions inside the SGBA engine (self time, interpreter).

    python sgba/profile_js.py [--scene level1] [--frames 300]

Wraps every global function the game defines with a timer, plays the scene, and prints the top ones.
Timings include some measurement overhead, so use them to rank functions, not as absolute costs.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import REPO, engine_dir  # noqa: E402
from bench import SCENES  # noqa: E402

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

WRAP = r"""
(() => {
  const skip = new Set(['__sgba_tick','__sgba_key','__sgba_ui','__sgba_audio_tick']);
  const stats = globalThis.__prof = { self: {}, calls: {}, stack: [], names: [], ops: {} };
  const names = Object.getOwnPropertyNames(globalThis).filter(n => {
    try { return typeof globalThis[n] === 'function' && !n.startsWith('__') && !skip.has(n) && /^[a-z]/.test(n) && !globalThis[n].toString().includes('[native code]'); } catch (e) { return false; }
  });
  for (const n of names) {
    const orig = globalThis[n];
    try {
      globalThis[n] = function (...a) {
        const st = stats.stack, t0 = __py_now();
        st.push(0); stats.names.push(n);
        try { return orig.apply(this, a); }
        finally {
          const dt = __py_now() - t0, child = st.pop(); stats.names.pop();
          stats.self[n] = (stats.self[n] || 0) + (dt - child);
          stats.calls[n] = (stats.calls[n] || 0) + 1;
          if (st.length) st[st.length - 1] += dt;
        }
      };
    } catch (e) {}
  }
  const origCall = globalThis.__py_call;
  globalThis.__py_call = function (...a) { const n = stats.names[stats.names.length - 1] || '(top)'; stats.ops[n] = (stats.ops[n] || 0) + 1; return origCall.apply(this, a); };
  return names.length;
})()
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scene", default="level1", choices=list(SCENES))
    parser.add_argument("--frames", type=int, default=300)
    args = parser.parse_args()
    sys.path.insert(0, str(engine_dir()))
    sys.path.insert(0, str(engine_dir() / "tools"))
    import pygame
    import js_bench
    import runtime
    import sgba_js
    pygame.init()
    pygame.display.set_mode((640, 480))
    import tempfile
    game = sgba_js.JSGame(REPO / "web", save_dir=Path(tempfile.mkdtemp()), log=lambda *a: None)
    game.config["navigation"] = "game"
    game.host.ctx.add_callable("__py_now", lambda: time.perf_counter() * 1000.0)
    inputs = runtime.InputState()
    surface = pygame.Surface(game.logical_size, 0, game.surface_depth)
    total, script, js = SCENES[args.scene]
    by_frame = js_bench.parse_script(script, 100000)
    js_at = {}
    for item in js:
        at, _, code = item.partition("=")
        js_at.setdefault(int(at), []).append(code)

    def step(frame):
        for code in js_at.get(frame, []):
            game.host.ctx.eval(code)
        for action, down in by_frame.get(frame, []):
            inputs._set(action, ("prof",), down)
        game.update(1 / 60, inputs)
        inputs.consume_edges()
        game.draw(surface)

    for frame in range(200):
        step(frame)
    wrapped = game.host.ctx.eval(WRAP)
    t0 = time.perf_counter()
    for frame in range(200, 200 + args.frames):
        step(frame)
    wall = (time.perf_counter() - t0) / args.frames * 1000
    stats = game.host.ctx.eval("JSON.stringify(__prof)")
    import json
    data = json.loads(stats)
    selfms = data["self"]
    total_js = sum(selfms.values()) / args.frames
    print(f"scene {args.scene}: {args.frames} frames, {wall:.2f} ms/frame wall (with timers), {total_js:.2f} ms/frame inside {wrapped} wrapped game functions")
    print(f"{'function':28s} {'ms/frame':>9s} {'calls/frame':>12s} {'canvas cmds/frame':>18s}")
    for name, ms in sorted(selfms.items(), key=lambda x: -x[1])[:22]:
        print(f"{name:28s} {ms / args.frames:9.3f} {data['calls'][name] / args.frames:12.1f} {data['ops'].get(name, 0) / args.frames:18.1f}")
    print(f"total canvas commands per frame: {sum(data['ops'].values()) / args.frames:.0f}")
    print("most commands:", ", ".join(f"{n} {c / args.frames:.0f}" for n, c in sorted(data["ops"].items(), key=lambda x: -x[1])[:8]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
