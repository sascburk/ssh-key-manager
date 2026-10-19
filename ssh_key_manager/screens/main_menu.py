"""Hauptmenü."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, OptionList
from textual.widgets.option_list import Option

MENU_ITEMS = [
    ("create", "🔑 Neuen SSH-Key erstellen"),
    ("deploy", "📤 Key auf Server ausrollen"),
    ("list", "📋 Vorhandene Keys anzeigen"),
    ("hosts", "🖥️  Gespeicherte Hosts / Verbindung öffnen"),
    ("test", "🧪 Passwortlosen Login testen"),
]


class MainMenuScreen(Screen):
    BINDINGS = [("q", "quit", "Beenden")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="menu-wrap"):
            option_list = OptionList(*(Option(label, id=key) for key, label in MENU_ITEMS))
            yield option_list
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        route = event.option.id
        if route == "create":
            from .create_key import CreateKeyScreen
            self.app.push_screen(CreateKeyScreen())
        elif route == "deploy":
            from .deploy_key import DeployKeyScreen
            self.app.push_screen(DeployKeyScreen())
        elif route == "list":
            from .list_keys import ListKeysScreen
            self.app.push_screen(ListKeysScreen())
        elif route == "hosts":
            from .hosts import HostsScreen
            self.app.push_screen(HostsScreen())
        elif route == "test":
            from .test_login import TestLoginScreen
            self.app.push_screen(TestLoginScreen())

    def action_quit(self) -> None:
        self.app.exit()
