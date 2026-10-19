"""Vorhandene SSH-Keys anzeigen."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label

from .. import ssh_ops


class ListKeysScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Zurück")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="form"):
            yield Label("Vorhandene SSH-Keys", classes="title")
            yield DataTable(id="table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Dateiname", "Private Key", "Public Key (Auszug)")
        pub_keys = ssh_ops.list_pub_keys()
        if not pub_keys:
            table.add_row("Keine Keys gefunden", "-", "-")
            return
        for pub in pub_keys:
            priv = pub.with_suffix("")
            has_priv = "✅" if priv.exists() else "❌"
            try:
                content = pub.read_text().strip()
            except OSError:
                content = ""
            excerpt = content[:60] + ("..." if len(content) > 60 else "")
            table.add_row(pub.name, has_priv, excerpt)
