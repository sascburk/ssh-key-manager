"""Gespeicherte Hosts aus ~/.ssh/config anzeigen und Verbindung öffnen."""
from __future__ import annotations

import subprocess

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label

from .. import ssh_config


class HostsScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Zurück")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="form"):
            yield Label("Gespeicherte Hosts (~/.ssh/config)", classes="title")
            yield DataTable(id="table", cursor_type="row")
            with Horizontal(id="host-actions"):
                yield Button("Verbindung im Terminal öffnen", id="connect", variant="primary")
            yield Label("", id="status")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Alias", "HostName", "User", "Port")
        self._hosts = ssh_config.parse_ssh_config()
        if not self._hosts:
            self.query_one("#status", Label).update(
                "Keine Hosts in ~/.ssh/config gefunden. Lege zuerst einen Key an und rolle ihn aus."
            )
            self.query_one("#connect", Button).disabled = True
            return
        for h in self._hosts:
            table.add_row(h.alias, h.hostname or "-", h.user or "-", h.port or "22")
        # Einziger Host -> automatisch vorausgewählt (Cursor steht bereits auf Zeile 0)
        table.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "connect" or not self._hosts:
            return
        table = self.query_one(DataTable)
        row_index = table.cursor_row
        if row_index is None or row_index < 0 or row_index >= len(self._hosts):
            return
        alias = self._hosts[row_index].alias
        try:
            subprocess.Popen(["omarchy-launch-terminal", "ssh", alias])
            self.query_one("#status", Label).update(f"Verbindung zu '{alias}' wird im Terminal geöffnet...")
        except FileNotFoundError:
            subprocess.Popen(["ssh", alias])
            self.query_one("#status", Label).update(f"Verbindung zu '{alias}' gestartet (Fallback ohne Omarchy-Terminal).")
