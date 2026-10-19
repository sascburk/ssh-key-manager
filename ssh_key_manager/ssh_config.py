"""Parser/Writer für ~/.ssh/config (auch von VSCode Remote-SSH genutzt)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".ssh" / "config"


@dataclass
class SSHHost:
    alias: str
    hostname: str | None = None
    user: str | None = None
    port: str | None = None
    identity_file: str | None = None


def parse_ssh_config(path: Path = DEFAULT_CONFIG_PATH) -> list[SSHHost]:
    if not path.exists():
        return []

    hosts: list[SSHHost] = []
    current: SSHHost | None = None

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        key, value = parts[0].lower(), parts[1].strip()

        if key == "host":
            aliases = value.split()
            for alias in aliases:
                if "*" in alias or "?" in alias:
                    continue
                current = SSHHost(alias=alias)
                hosts.append(current)
            if not any("*" not in a and "?" not in a for a in aliases):
                current = None
            continue

        if current is None:
            continue

        if key == "hostname":
            current.hostname = value
        elif key == "user":
            current.user = value
        elif key == "port":
            current.port = value
        elif key == "identityfile":
            current.identity_file = value

    return hosts


def alias_exists(alias: str, path: Path = DEFAULT_CONFIG_PATH) -> bool:
    return any(h.alias == alias for h in parse_ssh_config(path))


def append_host_block(
    alias: str,
    hostname: str,
    user: str | None = None,
    port: str | None = None,
    identity_file: str | None = None,
    path: Path = DEFAULT_CONFIG_PATH,
) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)

    lines = [f"Host {alias}", f"  HostName {hostname}"]
    if user:
        lines.append(f"  User {user}")
    if port and port != "22":
        lines.append(f"  Port {port}")
    if identity_file:
        lines.append(f"  IdentityFile {identity_file}")

    block = "\n".join(lines) + "\n"

    existing = path.read_text() if path.exists() else ""
    separator = "\n" if existing and not existing.endswith("\n\n") else ""
    if existing and not existing.endswith("\n"):
        separator = "\n\n"

    with path.open("a") as f:
        if existing:
            f.write(separator if separator else "\n")
        f.write(block)

    path.chmod(0o600)
