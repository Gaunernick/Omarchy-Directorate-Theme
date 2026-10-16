#!/bin/bash
# DIRECTORATE: swap the global pieces a theme can't carry itself (monospace
# font, screensaver text, bar layout) in when the theme is selected, and put
# the previous ones back when another theme is selected.

THEME_NAME="$1"
THEME_DIR="$HOME/.config/omarchy/themes/directorate"
STATE="$HOME/.local/state/omarchy/directorate-saved"
SHELL_JSON="$HOME/.config/omarchy/shell.json"
SCREENSAVER="$HOME/.config/omarchy/branding/screensaver.txt"
MENU="$HOME/.config/omarchy/extensions/omarchy-menu.jsonc"
FONT="BlexMono Nerd Font"

set_bar() {
  local tmp
  tmp=$(mktemp)
  jq --slurpfile bar "$1" '.bar = $bar[0]' "$SHELL_JSON" >"$tmp" && mv "$tmp" "$SHELL_JSON"
}

if [[ $THEME_NAME == "directorate" ]]; then
  [[ -d $THEME_DIR ]] || exit 0

  # Remember what was there before, once (re-applying the theme must not
  # overwrite the saved originals with directorate's own pieces).
  if [[ ! -d $STATE ]]; then
    mkdir -p "$STATE"
    omarchy-font-current >"$STATE/font"
    cp "$SCREENSAVER" "$STATE/screensaver.txt" 2>/dev/null
    jq '.bar' "$SHELL_JSON" >"$STATE/bar.json"
    cp "$MENU" "$STATE/omarchy-menu.jsonc" 2>/dev/null
  fi

  cp "$THEME_DIR/extras/screensaver.txt" "$SCREENSAVER"
  cp "$THEME_DIR/extras/omarchy-menu.jsonc" "$MENU"
  set_bar "$THEME_DIR/extras/bar.json"
  [[ $(omarchy-font-current) == "$FONT" ]] || omarchy-font-set "$FONT"
else
  [[ -d $STATE ]] || exit 0

  [[ -f $STATE/screensaver.txt ]] && cp "$STATE/screensaver.txt" "$SCREENSAVER"
  [[ -f $STATE/omarchy-menu.jsonc ]] && cp "$STATE/omarchy-menu.jsonc" "$MENU"
  [[ -s $STATE/bar.json ]] && set_bar "$STATE/bar.json"
  font=$(cat "$STATE/font" 2>/dev/null)
  [[ -n $font && $(omarchy-font-current) != "$font" ]] && omarchy-font-set "$font"
  rm -rf "$STATE"
fi
