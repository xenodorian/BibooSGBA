#!/bin/bash
# Parry Perry: starts the SGBA emulator (installed with GitROMs) on this game's own folder.
HERE="$(cd "$(dirname "$0")" && pwd)"
GAME="$HERE/parry-perry"
if [ ! -f "$HERE/SGBA.sh" ]; then
  MSG="Parry Perry needs the SGBA emulator. Open GitROMs, choose [Check for updates] and install SGBA emulator."
  echo "$MSG" > "$GAME/launch.log"
  [ -w /dev/tty1 ] && printf '\033c%s\n' "$MSG" > /dev/tty1 2>/dev/null && sleep 6
  exit 1
fi
exec bash "$HERE/SGBA.sh" "$GAME"
