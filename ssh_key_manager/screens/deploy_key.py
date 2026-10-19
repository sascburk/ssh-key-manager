"""SSH-Key auf einen Server ausrollen (ssh-copy-id)."""
from __future__ import annotations

import subprocess

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select

from .. import ssh_config, ssh_ops
from ..widgets.smart_select import build_smart_select
from .add_host_modal import AddHostToConfigModal
from .modals import RunOutputModal


class DeployKeyScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Zurück")]

    def compose(self) -> ComposeResult:
        yield Header()
        pub_keys = ssh_ops.list_pub_keys()
        with Vertical(id="form"):
            yield Label("SSH-Key auf Server ausrollen", classes="title")
            if not pub_keys:
                yield Label("Kein Public Key gefunden. Bitte zuerst einen Key erstellen.")
            else:
                if len(pub_keys) == 1:
                    yield Label(f"Key (automatisch ausgewählt, einziger vorhandener): {pub_keys[0].name}")
                else:
                    yield Label("Public Key")
                yield build_smart_select(
                    [(p.name, str(p)) for p in pub_keys], "pub_key"
                )

                known_hosts = ssh_config.parse_ssh_config()
                if known_hosts:
                    yield Label("Bestehenden Host übernehmen (optional)")
                    yield build_smart_select(
                        [(h.alias, h.alias) for h in known_hosts], "known_host"
                    )

                yield Label("Server-Host")
                yield Input(placeholder="z.B. 192.168.1.10 oder meinserver.de", id="host")
                yield Label("Benutzername")
                yield Input(placeholder="Benutzername auf dem Server", id="user")
                yield Label("SSH-Port")
                yield Input(value="22", id="port")
                yield Button("Ausrollen", id="deploy", variant="primary")
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
        if event.button.id != "deploy":
            return

        pub_key_value = self.query_one("#pub_key", Select).value
        if pub_key_value is Select.BLANK or not pub_key_value:
            return
        from pathlib import Path
        pub_key = Path(pub_key_value)

        host = self.query_one("#host", Input).value.strip()
        user = self.query_one("#user", Input).value.strip()
        port = self.query_one("#port", Input).value.strip() or "22"
        if not host:
            return

        cmd = ssh_ops.deploy_key_command(pub_key, host, user, port)
        with self.app.suspend():
            print(f"\nFühre aus: {' '.join(cmd)}\n")
            result = subprocess.run(cmd)

        ok = result.returncode == 0
        priv_key = pub_key.with_suffix("")

        def after_result(_: None) -> None:
            if ok:
                self.app.push_screen(
                    AddHostToConfigModal(host, user, port, str(priv_key))
                )

        self.app.push_screen(
            RunOutputModal(
                "Key ausrollen",
                ok,
                "",
                "" if ok else "Siehe Terminal-Ausgabe oben für Details.",
            ),
            after_result,
        )
