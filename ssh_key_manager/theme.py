"""Liest das aktuelle Omarchy-Farbschema und baut ein Textual-Theme daraus."""
from __future__ import annotations

import tomllib
from pathlib import Path

from textual.app import App
from textual.theme import Theme

CURRENT_THEME_COLORS = Path.home() / ".local/state/omarchy/current/theme/colors.toml"

FALLBACK_COLORS = {
    "mode": "dark",
    "accent": "#e68e0d",
    "selection": "#2a2a2a",
    "muted": "#333333",
    "background": "#121212",
    "lighter_background": "#1e1e1e",
    "foreground": "#bebebe",
    "red": "#D35F5F",
    "green": "#FFC107",
    "blue": "#e68e0d",
    "orange": "#c63d3d",
    "yellow": "#b91c1c",
}


def _load_colors() -> dict:
    try:
        with CURRENT_THEME_COLORS.open("rb") as f:
            return tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return FALLBACK_COLORS


def build_theme(colors: dict) -> Theme:
    get = colors.get
    return Theme(
        name="omarchy",
        primary=get("accent", FALLBACK_COLORS["accent"]),
        secondary=get("blue", get("accent", FALLBACK_COLORS["accent"])),
        warning=get("orange", get("yellow", "#c63d3d")),
        error=get("red", FALLBACK_COLORS["red"]),
        success=get("green", FALLBACK_COLORS["green"]),
        accent=get("accent", FALLBACK_COLORS["accent"]),
        foreground=get("foreground", FALLBACK_COLORS["foreground"]),
        background=get("background", FALLBACK_COLORS["background"]),
        surface=get("lighter_background", get("selection", FALLBACK_COLORS["selection"])),
        panel=get("selection", FALLBACK_COLORS["selection"]),
        dark=get("mode", "dark") == "dark",
        variables={
            "omarchy-muted": get("muted", FALLBACK_COLORS["muted"]),
            "omarchy-selection": get("selection", FALLBACK_COLORS["selection"]),
        },
    )


def apply_omarchy_theme(app: App) -> None:
    colors = _load_colors()
    try:
        theme = build_theme(colors)
    except Exception:
        theme = build_theme(FALLBACK_COLORS)
    app.register_theme(theme)
    app.theme = theme.name
