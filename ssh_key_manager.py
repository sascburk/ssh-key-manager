#!/usr/bin/env python3
"""
SSH Key Manager - TUI Tool
Erstellt SSH-Keys und rollt sie auf Server aus, damit man sich
danach passwortlos per SSH anmelden kann.

Nur Python-Standardbibliothek (curses, subprocess) - keine Abhängigkeiten.
"""
import curses
import os
import subprocess
import shutil
import sys
from pathlib import Path

SSH_DIR = Path.home() / ".ssh"

KEY_TYPES = ["ed25519", "rsa"]


def run_in_terminal(func):
    """Verlässt curses temporär, führt func aus (mit normalem stdin/stdout), kehrt danach zurück."""
    def wrapper(stdscr, *args, **kwargs):
        curses.def_prog_mode()
        curses.endwin()
        try:
            func(*args, **kwargs)
        finally:
            input("\nWeiter mit ENTER...")
            stdscr.clear()
            curses.reset_prog_mode()
            stdscr.refresh()
    return wrapper


def list_keys():
    if not SSH_DIR.exists():
        print("Kein ~/.ssh Verzeichnis gefunden.")
        return
    pub_keys = sorted(SSH_DIR.glob("*.pub"))
    if not pub_keys:
        print("Keine SSH-Public-Keys in ~/.ssh gefunden.")
        return
    print("Gefundene SSH-Keys:\n")
    for pub in pub_keys:
        priv = pub.with_suffix("")
        exists_priv = "OK" if priv.exists() else "FEHLT"
        print(f"  {pub.name:30s}  (Private Key: {exists_priv})")
        try:
            content = pub.read_text().strip()
            print(f"      {content[:80]}{'...' if len(content) > 80 else ''}")
        except OSError:
            pass


def create_key():
    print("=== Neuen SSH-Key erstellen ===\n")
    print("Verfügbare Typen: ed25519 (empfohlen), rsa")
    key_type = input("Key-Typ [ed25519]: ").strip() or "ed25519"
    if key_type not in KEY_TYPES:
        print(f"Unbekannter Typ '{key_type}', verwende 'ed25519'.")
        key_type = "ed25519"

    default_name = f"id_{key_type}"
    name = input(f"Dateiname [{default_name}]: ").strip() or default_name
    key_path = SSH_DIR / name

    if key_path.exists():
        overwrite = input(f"'{key_path}' existiert bereits. Überschreiben? [j/N]: ").strip().lower()
        if overwrite != "j":
            print("Abgebrochen.")
            return

    comment = input("Kommentar (z.B. deine E-Mail, optional): ").strip()

    SSH_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)

    cmd = ["ssh-keygen", "-t", key_type, "-f", str(key_path), "-N", ""]
    if key_type == "rsa":
        cmd += ["-b", "4096"]
    if comment:
        cmd += ["-C", comment]

    print("\nErstelle Key ohne Passphrase (für passwortlosen Login)...")
    result = subprocess.run(cmd)
    if result.returncode == 0:
        os.chmod(key_path, 0o600)
        os.chmod(key_path.with_suffix(".pub"), 0o644)
        print(f"\nKey erfolgreich erstellt: {key_path}")
        print(f"Public Key: {key_path}.pub")
    else:
        print("\nFehler beim Erstellen des Keys.")


def select_pub_key():
    pub_keys = sorted(SSH_DIR.glob("*.pub")) if SSH_DIR.exists() else []
    if not pub_keys:
        print("Kein Public Key gefunden. Bitte zuerst einen Key erstellen.")
        return None
    print("Verfügbare Public Keys:\n")
    for i, pub in enumerate(pub_keys, 1):
        print(f"  {i}) {pub.name}")
    choice = input(f"\nKey auswählen [1-{len(pub_keys)}]: ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(pub_keys):
            return pub_keys[idx]
    except ValueError:
        pass
    print("Ungültige Auswahl.")
    return None


def deploy_key():
    print("=== SSH-Key auf Server kopieren (passwortloser Login) ===\n")
    pub_key = select_pub_key()
    if pub_key is None:
        return

    print()
    host = input("Server-Host (z.B. 192.168.1.10 oder meinserver.de): ").strip()
    if not host:
        print("Kein Host angegeben. Abgebrochen.")
        return
    user = input("Benutzername auf dem Server: ").strip()
    port = input("SSH-Port [22]: ").strip() or "22"

    target = f"{user}@{host}" if user else host

    if shutil.which("ssh-copy-id"):
        print(f"\nKopiere '{pub_key.name}' nach {target} (Port {port}) mit ssh-copy-id...")
        print("Du wirst jetzt einmalig nach dem Passwort für den Server gefragt.\n")
        cmd = ["ssh-copy-id", "-i", str(pub_key), "-p", port, target]
        result = subprocess.run(cmd)
    else:
        print(f"\n'ssh-copy-id' nicht gefunden, nutze Fallback über ssh...")
        pub_content = pub_key.read_text().strip()
        remote_cmd = (
            "mkdir -p ~/.ssh && chmod 700 ~/.ssh && "
            f"echo '{pub_content}' >> ~/.ssh/authorized_keys && "
            "chmod 600 ~/.ssh/authorized_keys"
        )
        cmd = ["ssh", "-p", port, target, remote_cmd]
        result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"\nKey erfolgreich auf {target} installiert.")
        print(f"Teste den Login mit:  ssh -p {port} -i {pub_key.with_suffix('')} {target}")
    else:
        print("\nFehler beim Kopieren des Keys auf den Server.")


def test_login():
    print("=== Passwortlosen Login testen ===\n")
    priv_keys = [p for p in sorted(SSH_DIR.glob("*")) if p.is_file() and not p.name.endswith(".pub") and p.name not in ("known_hosts", "config", "authorized_keys")]
    if not priv_keys:
        print("Kein Private Key gefunden.")
        return
    print("Verfügbare Private Keys:\n")
    for i, k in enumerate(priv_keys, 1):
        print(f"  {i}) {k.name}")
    choice = input(f"\nKey auswählen [1-{len(priv_keys)}]: ").strip()
    try:
        idx = int(choice) - 1
        key_path = priv_keys[idx]
    except (ValueError, IndexError):
        print("Ungültige Auswahl.")
        return

    host = input("Server-Host: ").strip()
    user = input("Benutzername: ").strip()
    port = input("SSH-Port [22]: ").strip() or "22"
    target = f"{user}@{host}" if user else host

    cmd = ["ssh", "-p", port, "-i", str(key_path),
           "-o", "PasswordAuthentication=no",
           "-o", "BatchMode=yes",
           target, "echo 'Passwortloser Login erfolgreich!'"]
    print(f"\nTeste: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("\nLogin ohne Passwort hat nicht funktioniert (Key evtl. noch nicht auf dem Server hinterlegt).")


MENU_ITEMS = [
    ("Neuen SSH-Key erstellen", create_key),
    ("SSH-Key auf Server kopieren (passwortloser Login)", deploy_key),
    ("Vorhandene Keys anzeigen", list_keys),
    ("Passwortlosen Login testen", test_login),
    ("Beenden", None),
]


def draw_menu(stdscr, selected):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "SSH Key Manager - passwortloser Server-Login"
    stdscr.addstr(1, max(0, (w - len(title)) // 2), title, curses.A_BOLD)
    stdscr.addstr(2, max(0, (w - len(title)) // 2), "-" * len(title))

    for idx, (label, _) in enumerate(MENU_ITEMS):
        y = 4 + idx
        x = 4
        if idx == selected:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, f"> {label}")
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, f"  {label}")

    stdscr.addstr(h - 2, 2, "Pfeiltasten/j,k: navigieren | Enter: auswählen | q: beenden")
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    selected = 0
    while True:
        draw_menu(stdscr, selected)
        key = stdscr.getch()

        if key in (curses.KEY_UP, ord('k')):
            selected = (selected - 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_DOWN, ord('j')):
            selected = (selected + 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_ENTER, ord('\n'), ord('\r')):
            label, action = MENU_ITEMS[selected]
            if action is None:
                break
            run_in_terminal(action)(stdscr)
        elif key in (ord('q'), 27):
            break


if __name__ == "__main__":
    if not shutil.which("ssh-keygen"):
        print("Fehler: 'ssh-keygen' wurde nicht gefunden. Bitte OpenSSH installieren.")
        sys.exit(1)
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("Auf Wiedersehen!")
