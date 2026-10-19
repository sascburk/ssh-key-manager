"""Passwortlosen Login testen."""
from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select

from .. import ssh_config, ssh_ops
from ..widgets.smart_select import build_smart_select
from .modals import RunOutputModal


class TestLoginScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Zurück")]

    def compose(self) -> ComposeResult:
        yield Header()
        priv_keys = ssh_ops.list_private_keys()
        with Vertical(id="form"):
            yield Label("Passwortlosen Login testen", classes="title")
            if not priv_keys:
                yield Label("Kein Private Key gefunden.")
            else:
                if len(priv_keys) == 1:
                    yield Label(f"Key (automatisch ausgewählt, einziger vorhandener): {priv_keys[0].name}")
                else:
                    yield Label("Private Key")
                yield build_smart_select([(p.name, str(p)) for p in priv_keys], "priv_key")

                known_hosts = ssh_config.parse_ssh_config()
                if known_hosts:
                    yield Label("Bestehenden Host übernehmen (optional)")
                    yield build_smart_select([(h.alias, h.alias) for h in known_hosts], "known_host")

                yield Label("Server-Host")
                yield Input(placeholder="Host", id="host")
                yield Label("Benutzername")
                yield Input(placeholder="Benutzername", id="user")
                yield Label("SSH-Port")
                yield Input(value="22", id="port")
                yield Button("Testen", id="test", variant="primary")
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "known_host" and event.value is not Select.BLANK:
            for h in ssh_config.parse_ssh_config():
                if h.alias == event.value:
                    self.query_one("#host", Input).value = h.hostname or h.alias
                    self.query_one("#user", Input).value = h.user or ""
                    self.query_one("#port", Input).value = h.port or "22"
                    break

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "test":
            return
        priv_key_value = self.query_one("#priv_key", Select).value
        if priv_key_value is Select.BLANK or not priv_key_value:
            return
        priv_key = Path(priv_key_value)
        host = self.query_one("#host", Input).value.strip()
        user = self.query_one("#user", Input).value.strip()
        port = self.query_one("#port", Input).value.strip() or "22"
        if not host:
            return

        result = ssh_ops.test_login(priv_key, host, user, port)
        self.app.push_screen(RunOutputModal("Login-Test", result.ok, result.stdout, result.stderr))
