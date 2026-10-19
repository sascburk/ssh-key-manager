#!/usr/bin/env bash
# Installiert den SSH Key Manager und legt ihn unter Omarchy im App-Menü ab.
set -euo pipefail

REPO_URL="https://github.com/sascburk/ssh-key-manager.git"
APP_NAME="SSH Key Manager"
ICON_NAME="dialog-password"

install_package() {
  local source="$1"
  if command -v uv >/dev/null 2>&1; then
    uv tool install --force "$source"
  elif command -v pipx >/dev/null 2>&1; then
    pipx install --force "$source"
  else
    echo "uv oder pipx wird benötigt." >&2
    exit 1
  fi
}

if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
  script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
else
  script_dir=""
fi

if [[ -n "$script_dir" && -f "$script_dir/pyproject.toml" ]]; then
  install_package "$script_dir"
else
  install_package "git+$REPO_URL"
fi

app_exec="${HOME}/.local/bin/ssh-key-manager"
if [[ ! -x "$app_exec" ]]; then
  app_exec=$(command -v ssh-key-manager || true)
fi
if [[ -z "$app_exec" ]]; then
  echo "Der Befehl ssh-key-manager wurde nicht gefunden." >&2
  exit 1
fi

if command -v omarchy-tui-install >/dev/null 2>&1; then
  omarchy-tui-install "$APP_NAME" "$app_exec" float "$ICON_NAME"
  echo "Im Omarchy-Menü unter Apps: ${APP_NAME}"
else
  echo "Omarchy nicht erkannt. ssh-key-manager ist installiert, ein Menüeintrag wurde nicht angelegt."
fi
