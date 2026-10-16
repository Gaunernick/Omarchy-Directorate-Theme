#!/bin/bash
# DIRECTORATE: remove the theme and its shell pieces.
#
# Usage: ./uninstall.sh [other-theme]   (default: tokyo-night)
#
# Switching away first lets the theme-set hook restore your previous bar
# layout, menu, font and screensaver before anything is removed.

set -euo pipefail

NEXT=${1:-tokyo-night}
CONFIG="$HOME/.config/omarchy"

if [[ $(omarchy theme current 2>/dev/null | tr '[:upper:]' '[:lower:]') == "directorate" ]]; then
  omarchy theme set "$NEXT"
fi

rm -rf "$CONFIG"/plugins/directorate.*
rm -f "$CONFIG"/bar/modules/directorate-*.qml
rm -f "$CONFIG/hooks/theme-set.d/directorate.sh"
rm -rf "$CONFIG/themes/directorate"

omarchy restart shell >/dev/null 2>&1 || true

cat <<'EOF'
DIRECTORATE removed. Your hours have been logged.

Left in place (harmless, remove by hand if you like):
  - the "DIRECTORATE keybindings" block in ~/.config/hypr/bindings.lua
    (it still toggles the stock widgets)
  - the terminal.sh line in ~/.bashrc (it does nothing once the theme is gone)
EOF
