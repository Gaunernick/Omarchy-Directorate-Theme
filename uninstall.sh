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

# The lock screen clone, if install.sh --lock made it. Removing it restores
# Omarchy's stock lock screen.
LOCK_ID="${USER:-$(id -un)}.lock"
if grep -qsF "DIRECTORATE" "$CONFIG/plugins/$LOCK_ID/LockView.qml"; then
  omarchy plugin remove "$LOCK_ID" --yes
fi

SHELL_JSON="$CONFIG/shell.json"
if [[ -f $SHELL_JSON ]]; then
  tmp=$(mktemp)
  jq 'if .plugins then .plugins |= map(select(.id != "directorate.beacon")) else . end' "$SHELL_JSON" >"$tmp" && mv "$tmp" "$SHELL_JSON"
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
