"""Wiederverwendbare Modal-Screens: Ergebnisanzeige, Ja/Nein-Bestätigung."""
from __future__ import annotations

from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, RichLog


class RunOutputModal(ModalScreen[None]):
    """Zeigt das Ergebnis eines ausgeführten Befehls (stdout/stderr/Status)."""

    DEFAULT_CSS = """
    RunOutputModal {
        align: center middle;
    }
    RunOutputModal > Vertical {
        width: 80%;
        height: auto;
        max-height: 80%;
        background: $panel;
        border: thick $primary;
        padding: 1 2;
    }
    RunOutputModal RichLog {
        height: auto;
        max-height: 20;
        margin: 1 0;
    }
    RunOutputModal .status-ok {
        text-style: bold;
        color: $success;
    }
    RunOutputModal .status-fail {
        text-style: bold;
        color: $error;
    }
    """

    def __init__(self, title: str, ok: bool, stdout: str = "", stderr: str = "", extra: str = ""):
        super().__init__()
        self._title = title
        self._ok = ok
        self._stdout = stdout
        self._stderr = stderr
        self._extra = extra

    def compose(self):
        status = "✅ Erfolgreich" if self._ok else "❌ Fehlgeschlagen"
        status_class = "status-ok" if self._ok else "status-fail"
        with Vertical():
            yield Label(f"{self._title}", classes="title")
            yield Label(status, classes=status_class)
            log = RichLog(wrap=True, markup=False)
            yield log
            if self._extra:
                yield Label(self._extra)
            yield Button("OK", id="ok", variant="primary")
        self._pending_log = log

    def on_mount(self) -> None:
        text = (self._stdout or "") + (("\n" + self._stderr) if self._stderr else "")
        if text.strip():
            self._pending_log.write(text.strip())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)


class ConfirmModal(ModalScreen[bool]):
    """Einfaches Ja/Nein-Modal."""

    DEFAULT_CSS = """
    ConfirmModal {
        align: center middle;
    }
    ConfirmModal > Vertical {
        width: 60%;
        height: auto;
        background: $panel;
        border: thick $primary;
        padding: 1 2;
    }
    ConfirmModal Horizontal {
        height: auto;
        margin-top: 1;
        align: center middle;
    }
    """

    def __init__(self, message: str, yes_label: str = "Ja", no_label: str = "Nein"):
        super().__init__()
        self._message = message
        self._yes_label = yes_label
        self._no_label = no_label

    def compose(self):
        from textual.containers import Horizontal
        with Vertical():
            yield Label(self._message)
            with Horizontal():
                yield Button(self._yes_label, id="yes", variant="primary")
                yield Button(self._no_label, id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")
