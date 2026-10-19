# SSH Key Manager

Terminal-App zum Erstellen von SSH-Keys, zum Kopieren auf Server und zum Testen des passwortlosen Logins. Die Oberfläche nutzt [Textual](https://textual.textualize.io/). Unter Omarchy werden die Farben aus dem aktuellen Theme gelesen, sonst gilt ein dunkles Fallback.

Voraussetzung auf dem System: OpenSSH (`ssh-keygen`, `ssh-copy-id`, `ssh`).

## Installieren

Aus einem Clone:

```bash
pipx install .
```

`pipx` legt den Befehl `ssh-key-manager` isoliert ab. Alternativ in eine virtuelle Umgebung:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

Direkt von GitHub, sobald das Repository steht:

```bash
pipx install "git+https://github.com/sascburk/ssh-key-manager.git"
```

## Starten

```bash
ssh-key-manager
```

Oder ohne Installation aus dem Projektverzeichnis:

```bash
python -m ssh_key_manager
```

## Auf GitHub veröffentlichen

Im Projektverzeichnis:

```bash
git init
git add .
git commit -m "Ersten Stand des installierbaren SSH Key Managers veröffentlichen"
gh repo create ssh-key-manager --public --source=. --remote=origin --push
```

Ohne `gh`: Repository auf GitHub anlegen, dann

```bash
git remote add origin git@github.com:sascburk/ssh-key-manager.git
git push -u origin main
```

Vor einem öffentlichen Repository eine Lizenz ergänzen. Im Projekt liegt bisher keine.

Die Datei `ssh_key_manager.py` im Projektroot ist die ältere Curses-Version nur mit der Standardbibliothek. Sie wird nicht mitinstalliert. Der installierte Befehl startet die Textual-App im Paket `ssh_key_manager`.
