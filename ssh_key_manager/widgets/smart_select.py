"""SmartSelect: Select-Widget, das bei genau einer Option diese automatisch vorbelegt."""
from __future__ import annotations

from textual.widgets import Select


def build_smart_select(options: list[tuple[str, str]], select_id: str) -> Select:
    """Baut ein Select-Widget. Gibt es genau eine Option, wird sie als Default
    vorausgewählt (allow_blank=False), der Nutzer muss nur noch bestätigen."""
    if len(options) == 1:
        return Select(options, id=select_id, allow_blank=False, value=options[0][1])
    return Select(options, id=select_id, allow_blank=True)
