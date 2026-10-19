"""UI-freie SSH-Operationen: Keys erstellen, ausrollen, testen."""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

SSH_DIR = Path.home() / ".ssh"
KEY_TYPES = ["ed25519", "rsa"]

NON_KEY_FILES = {"known_hosts", "known_hosts.old", "config", "authorized_keys"}


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def list_pub_keys() -> list[Path]:
    if not SSH_DIR.exists():
        return []
    return sorted(SSH_DIR.glob("*.pub"))


def list_private_keys() -> list[Path]:
    if not SSH_DIR.exists():
        return []
    return sorted(
        p for p in SSH_DIR.glob("*")
        if p.is_file() and not p.name.endswith(".pub") and p.name not in NON_KEY_FILES
    )


def _run(cmd: list[str]) -> CommandResult:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return CommandResult(result.returncode, result.stdout, result.stderr)


def create_key(key_type: str, name: str, comment: str, overwrite: bool) -> tuple[CommandResult, Path | None]:
    key_path = SSH_DIR / name
    if key_path.exists() and not overwrite:
        return CommandResult(1, "", f"'{key_path}' existiert bereits."), None

    SSH_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)

    cmd = ["ssh-keygen", "-t", key_type, "-f", str(key_path), "-N", ""]
    if key_type == "rsa":
        cmd += ["-b", "4096"]
    if comment:
        cmd += ["-C", comment]

    result = _run(cmd)
    if result.ok:
        os.chmod(key_path, 0o600)
        os.chmod(key_path.with_suffix(".pub"), 0o644)
        return result, key_path
    return result, None


def deploy_key_command(pub_key: Path, host: str, user: str, port: str) -> list[str]:
    """Baut den auszuführenden Befehl (läuft interaktiv, braucht ein TTY)."""
    target = f"{user}@{host}" if user else host
    if shutil.which("ssh-copy-id"):
        return ["ssh-copy-id", "-i", str(pub_key), "-p", port, target]
    pub_content = pub_key.read_text().strip()
    remote_cmd = (
        "mkdir -p ~/.ssh && chmod 700 ~/.ssh && "
        f"echo '{pub_content}' >> ~/.ssh/authorized_keys && "
        "chmod 600 ~/.ssh/authorized_keys"
    )
    return ["ssh", "-p", port, target, remote_cmd]


def test_login(priv_key: Path, host: str, user: str, port: str) -> CommandResult:
    target = f"{user}@{host}" if user else host
    cmd = [
        "ssh", "-p", port, "-i", str(priv_key),
        "-o", "PasswordAuthentication=no",
        "-o", "BatchMode=yes",
        target, "echo 'Passwortloser Login erfolgreich!'",
    ]
    return _run(cmd)
