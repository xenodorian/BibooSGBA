"""Build the SGBA packages for this game (Windows and ArkOS handhelds such as the R36S).

    python sgba/build.py                  # both targets into dist/
    python sgba/build.py windows-x64      # one target

It needs the SGBA engine. It looks for, in order: the SGBA_DIR environment variable, a sibling folder named SGBA,
and otherwise downloads the version named in sgba/sgba.ref into .sgba-engine/. The game itself is built from web/ exactly as it is,
so whatever runs in the browser is what runs on the device.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
NAME = "Parry Perry"
# Files the browser needs but a device does not: MP3 copies of the Ogg music, MIDI sources, and the web tests.
EXCLUDE = ["*.mp3", "*.mid", "tests/*", "*.test.js", ".DS_Store"]


def engine_dir() -> Path:
    env = os.environ.get("SGBA_DIR")
    if env and (Path(env) / "tools" / "build_bundle.py").is_file():
        return Path(env)
    sibling = REPO.parent / "SGBA"
    if (sibling / "tools" / "build_bundle.py").is_file():
        return sibling
    ref = [line.strip() for line in (HERE / "sgba.ref").read_text().splitlines() if line.strip() and not line.startswith("#")][0]
    target = REPO / ".sgba-engine"
    if not target.exists():
        subprocess.run(["git", "clone", "--depth", "1", "--branch", ref, "https://github.com/xenodorian/SGBA", str(target)], check=True)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("targets", nargs="*", default=["windows-x64", "arkos-aarch64"])
    parser.add_argument("--out", type=Path, default=REPO / "dist")
    args = parser.parse_args()
    engine = engine_dir()
    for target in args.targets:
        command = [sys.executable, str(engine / "tools" / "build_bundle.py"), target, "--web", str(REPO / "web"), "--name", NAME,
                   "--ui-config", str(HERE / "sgba_ui.json"), "--out", str(args.out)]
        for pattern in EXCLUDE:
            command += ["--exclude", pattern]
        subprocess.run(command, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
