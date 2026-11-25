#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SHELL_PATH="$HOME/.local/bin/rania-shell.py"
ICON_PATH="$HOME/.local/share/icons/rania-start-white.png"
APP_DIR="$HOME/.local/share/applications"

install -Dm755 "$ROOT/src/rania-shell.py" "$SHELL_PATH"
install -Dm644 "$ROOT/assets/rania-start-white.png" "$ICON_PATH"
mkdir -p "$APP_DIR"
printf '[Desktop Entry]\nType=Application\nName=RaniaDE\nName[ru]=RaniaDE\nComment=Independent Python/Qt desktop shell\nComment[ru]=Независимая оболочка рабочего стола на Python/Qt\nExec=python3 "%s"\nIcon=%s\nTerminal=false\nCategories=Utility;\n' "$SHELL_PATH" "$ICON_PATH" > "$APP_DIR/rania-de.desktop"
chmod 644 "$APP_DIR/rania-de.desktop"

printf 'RaniaDE 0.1.5 installed for %s.\nNo system packages were installed and no sudo command was run.\nLaunch from an active X11 session with:\n  python3 "%s"\nThe first-run wizard can offer optional KWin and KDE application packages.\n' "${USER:-user}" "$SHELL_PATH"
if ! python3 -c 'import PyQt5' >/dev/null 2>&1; then
    printf 'Note: Python 3 / PyQt5 is not available. Install the prerequisites listed in README.md before launching.\n' >&2
fi
