"""SSH Key Manager - Textual-App mit Omarchy-Farbschema."""
from __future__ import annotations

from pathlib import Path

from textual.app import App

from .screens.main_menu import MainMenuScreen
from .theme import apply_omarchy_theme

STYLES_PATH = Path(__file__).parent / "styles.tcss"


class SSHKeyManagerApp(App):
    CSS_PATH = str(STYLES_PATH)
    TITLE = "SSH Key Manager"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_omarchy_theme(self)

    def on_mount(self) -> None:
        self.push_screen(MainMenuScreen())


def main() -> None:
    SSHKeyManagerApp().run()


if __name__ == "__main__":
    main()
