# DIRECTORATE terminal voice. Sourced from ~/.bashrc; does nothing unless the
# theme is active (the theme-set hook keeps its state dir only while it is).
[[ -d $HOME/.local/state/omarchy/directorate-saved ]] || return 0

export STARSHIP_CONFIG="$HOME/.config/omarchy/themes/directorate/extras/starship.toml"

# A stable operator number derived from the login name: you are a number here.
DIRECTORATE_OPERATOR=$(printf '%05d' $(($(printf '%s' "$USER" | cksum | cut -d' ' -f1) % 100000)))

_directorate_dim=$'\e[38;2;92;99;96m'
_directorate_text=$'\e[38;2;176;203;208m'
_directorate_cyan=$'\e[38;2;55;168;194m'
_directorate_reset=$'\e[0m'

printf '%s\n%s\n\n' \
  "${_directorate_text}DIRECTORATE ${_directorate_dim}// TERMINAL STN-0117 // OPERATOR ${DIRECTORATE_OPERATOR}${_directorate_reset}" \
  "${_directorate_dim}SESSION OPENED $(date '+%Y.%m.%d %H:%M:%S') ${_directorate_cyan}·${_directorate_dim} ALL ACTIVITY IS RECORDED${_directorate_reset}"

_directorate_logout() {
  printf '%s\n' "${_directorate_dim}SESSION CLOSED $(date '+%H:%M:%S'). YOUR HOURS HAVE BEEN LOGGED.${_directorate_reset}"
}
trap _directorate_logout EXIT
