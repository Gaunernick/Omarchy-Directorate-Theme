#!/bin/bash
# DIRECTORATE: install the theme and the shell pieces a theme cannot carry
# itself (bar widgets, theme-set hook, keybindings, terminal greeting).
#
# Usage: ./install.sh [--lock]
#
#   --lock  also style the lock screen (clones Omarchy's lock plugin and
#           patches its view; see README)
#
# Use this rather than `omarchy theme install <url>`: that drops hyprland.lua
# and never installs the bar widgets, hook or keybindings.

set -euo pipefail

LOCK=0
for arg in "$@"; do
  case $arg in
  --lock) LOCK=1 ;;
  *) echo "Usage: ./install.sh [--lock]" >&2; exit 1 ;;
  esac
done

SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
CONFIG="$HOME/.config/omarchy"
THEME_DIR="$CONFIG/themes/directorate"
BINDINGS="$HOME/.config/hypr/bindings.lua"
BASHRC="$HOME/.bashrc"
MARKER="-- DIRECTORATE keybindings"

echo "Installing DIRECTORATE…"

# The theme speaks IBM Plex Mono.
if ! fc-list | grep -q "BlexMono Nerd Font"; then
  omarchy pkg add ttf-ibmplex-mono-nerd
fi

# Theme files. Repo-only pieces (installer, widgets, docs) stay out.
mkdir -p "$THEME_DIR"
rsync -a --delete \
  --exclude .git --exclude plugins --exclude bar-modules \
  --exclude install.sh --exclude uninstall.sh --exclude README.md --exclude LICENSE --exclude docs \
  "$SRC/" "$THEME_DIR/"

# Bar widgets and popups.
mkdir -p "$CONFIG/plugins" "$CONFIG/bar/modules"
for plugin in "$SRC"/plugins/directorate.*; do
  rm -rf "$CONFIG/plugins/$(basename "$plugin")"
  cp -a "$plugin" "$CONFIG/plugins/"
done
cp "$SRC"/bar-modules/*.qml "$CONFIG/bar/modules/"

# STN-0117 beacon: a service plugin, so it is switched on in shell.json rather
# than placed in the bar.
SHELL_JSON="$CONFIG/shell.json"
if [[ -f $SHELL_JSON ]] && ! jq -e '(.plugins // []) | any(.id == "directorate.beacon")' "$SHELL_JSON" >/dev/null; then
  cp "$SHELL_JSON" "$SHELL_JSON.bak.$(date +%s)"
  tmp=$(mktemp)
  jq '.plugins = ((.plugins // []) + [{"id": "directorate.beacon"}])' "$SHELL_JSON" >"$tmp" && mv "$tmp" "$SHELL_JSON"
fi

# Theme-set hook: swaps the bar layout, menu, font and screensaver in while the
# theme is selected and restores yours afterwards.
mkdir -p "$CONFIG/hooks/theme-set.d"
install -m 0755 "$THEME_DIR/extras/theme-set-hook.sh" "$CONFIG/hooks/theme-set.d/directorate.sh"

# Keybindings: the stock popup keys look for the stock widget ids. Toggle both
# so the keys keep working under every theme.
if [[ -f $BINDINGS ]] && ! grep -qF -- "$MARKER" "$BINDINGS"; then
  cp "$BINDINGS" "$BINDINGS.bak.$(date +%s)"
  cat >>"$BINDINGS" <<'EOF'

-- DIRECTORATE keybindings: the theme swaps these widgets for its own clones.
-- Toggle both ids; only the one in the bar responds.
hl.unbind("SUPER + CTRL + ALT + D")
o.bind("SUPER + CTRL + ALT + D", "Calendar", "omarchy-shell shell toggle directorate.clock; omarchy-shell shell toggle omarchy.clock")
hl.unbind("SUPER + CTRL + A")
o.bind("SUPER + CTRL + A", "Audio", "omarchy-shell shell toggle directorate.audio; omarchy-shell shell toggle omarchy.audio")
hl.unbind("SUPER + CTRL + B")
o.bind("SUPER + CTRL + B", "Bluetooth", "omarchy-shell shell toggle directorate.bluetooth; omarchy-shell shell toggle omarchy.bluetooth")
hl.unbind("SUPER + CTRL + D")
o.bind("SUPER + CTRL + D", "Display", "omarchy-shell shell toggle directorate.monitor; omarchy-shell shell toggle omarchy.monitor")
hl.unbind("SUPER + CTRL + W")
o.bind("SUPER + CTRL + W", "Network", "omarchy-shell shell toggle directorate.network; omarchy-shell shell toggle omarchy.network")
EOF
fi

# Terminal greeting and prompt. terminal.sh does nothing unless the theme is
# active.
LINE='[[ -r ~/.config/omarchy/themes/directorate/extras/terminal.sh ]] && source ~/.config/omarchy/themes/directorate/extras/terminal.sh'
if [[ -f $BASHRC ]] && ! grep -qF "$LINE" "$BASHRC"; then
  printf '\n%s\n' "$LINE" >>"$BASHRC"
fi

# Lock screen (opt-in): clone the stock lock plugin and patch only its view.
# Authentication stays the stock code. If Omarchy has changed its lock screen
# since this patch was made, the clone is removed and the stock lock stays.
if ((LOCK)); then
  LOCK_ID="${USER:-$(id -un)}.lock"
  LOCK_DIR="$CONFIG/plugins/$LOCK_ID"
  if [[ -d $LOCK_DIR ]]; then
    if grep -qF "DIRECTORATE" "$LOCK_DIR/LockView.qml"; then
      cp "$SRC/plugins/directorate.beacon/StationPulse.qml" "$LOCK_DIR/"
    else
      echo "Skipping the lock screen: you already have your own lock clone at $LOCK_DIR" >&2
    fi
  elif ! command -v patch >/dev/null; then
    echo "Skipping the lock screen: 'patch' is not installed" >&2
  else
    omarchy plugin clone omarchy.lock
    if patch -d "$LOCK_DIR" -p1 --forward --quiet <"$SRC/extras/lock/LockView.patch"; then
      cp "$SRC/plugins/directorate.beacon/StationPulse.qml" "$LOCK_DIR/"
    else
      echo "The lock screen patch no longer applies; keeping Omarchy's stock lock screen" >&2
      omarchy plugin remove "$LOCK_ID" --yes
    fi
  fi
fi

omarchy theme set directorate
omarchy restart shell >/dev/null 2>&1 || true

cat <<'EOF'

DIRECTORATE installed. Your station is ready.

Optional: style the boot unlock screen (needs sudo, rebuilds the initramfs):
  omarchy plymouth set by theme directorate
EOF
