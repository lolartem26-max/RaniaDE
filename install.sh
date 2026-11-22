#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install -Dm755 "$ROOT/src/rania-shell.py" "$HOME/.local/bin/rania-shell.py"
install -Dm644 "$ROOT/assets/rania-start-white.png" "$HOME/.local/share/icons/rania-start-white.png"
printf 'RaniaDE installed for %s.\nRun it from an active X11 session with:\n  python3 ~/.local/bin/rania-shell.py\n' "$USER"
