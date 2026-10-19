"""Fragt nach Deploy, ob der Host in ~/.ssh/config (VSCode Remote-SSH) eingetragen werden soll."""
from __future__ import annotations

from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from .. import ssh_config


class AddHostToConfigModal(ModalScreen[bool]):
    DEFAULT_CSS = """
    AddHostToConfigModal {
        align: center middle;
    }
    AddHostToConfigModal > Vertical {
        width: 70%;
        height: auto;
        background: $panel;
        border: thick $primary;
        padding: 1 2;
    }
    AddHostToConfigModal Input {
        margin: 1 0;
    }
    AddHostToConfigModal #error {
        color: $error;
        height: auto;
    }
    AddHostToConfigModal Horizontal {
        height: auto;
        margin-top: 1;
        align: center middle;
    }
    """

    def __init__(self, host: str, user: str, port: str, identity_file: str | None):
        super().__init__()
        self.host = host
        self.user = user
        self.port = port
        self.identity_file = identity_file

    def compose(self):
        with Vertical():
            yield Label(
                f"Key erfolgreich auf {self.host} ausgerollt.\n"
                "Soll dieser Host in ~/.ssh/config eingetragen werden?\n"
                "(Diese Datei nutzt auch VSCode Remote-SSH.)"
            )
            yield Input(placeholder="Alias-Name", value=self.host, id="alias")
            yield Label("", id="error")
            with Horizontal():
                yield Button("Eintragen", id="add", variant="primary")
                yield Button("Nein danke", id="skip")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "skip":
            self.dismiss(False)
            return

        alias = self.query_one("#alias", Input).value.strip()
        error_label = self.query_one("#error", Label)
        if not alias:
            error_label.update("Bitte einen Alias-Namen angeben.")
            return
        if ssh_config.alias_exists(alias):
            error_label.update(f"Alias '{alias}' existiert bereits in ~/.ssh/config.")
            return

        ssh_config.append_host_block(
            alias=alias,
            hostname=self.host,
            user=self.user or None,
            port=self.port or None,
            identity_file=self.identity_file,
        )
        self.dismiss(True)
