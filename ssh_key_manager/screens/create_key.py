"""Neuen SSH-Key erstellen."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select

from .. import ssh_ops
from .modals import ConfirmModal, RunOutputModal


class CreateKeyScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Zurück")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="form"):
            yield Label("Neuen SSH-Key erstellen", classes="title")
            yield Label("Key-Typ")
            yield Select(
                [(t, t) for t in ssh_ops.KEY_TYPES],
                id="key_type",
                value="ed25519",
                allow_blank=False,
            )
            yield Label("Dateiname")
            yield Input(value="id_ed25519", id="name")
            yield Label("Kommentar (optional)")
            yield Input(placeholder="z.B. deine E-Mail", id="comment")
            yield Button("Erstellen", id="create", variant="primary")
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "key_type" and event.value is not Select.BLANK:
            self.query_one("#name", Input).value = f"id_{event.value}"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "create":
            return
        key_type = self.query_one("#key_type", Select).value
        name = self.query_one("#name", Input).value.strip() or f"id_{key_type}"
        comment = self.query_one("#comment", Input).value.strip()

        key_path = ssh_ops.SSH_DIR / name
        if key_path.exists():
            def handle_overwrite(overwrite: bool | None) -> None:
                if overwrite:
                    self._do_create(key_type, name, comment, overwrite=True)
            self.app.push_screen(
                ConfirmModal(f"'{key_path}' existiert bereits. Überschreiben?"),
                handle_overwrite,
            )
        else:
            self._do_create(key_type, name, comment, overwrite=False)

    def _do_create(self, key_type: str, name: str, comment: str, overwrite: bool) -> None:
        result, key_path = ssh_ops.create_key(key_type, name, comment, overwrite)
        extra = f"Key: {key_path}\nPublic Key: {key_path}.pub" if key_path else ""
        self.app.push_screen(
            RunOutputModal("Key erstellen", result.ok, result.stdout, result.stderr, extra)
        )
