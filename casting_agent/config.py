"""Non-secret per-user preferences; credentials and sessions do not belong here."""

import json
import os
import sys
from pathlib import Path


class SettingsError(ValueError):
    pass


def default_data_dir(override=None, *, platform=None, home=None, environ=None):
    environment = os.environ if environ is None else environ
    selected = override if override is not None else environment.get("CASTING_AGENT_DATA_DIR")
    if selected is not None:
        path = Path(selected).expanduser()
        if not selected or not path.is_absolute():
            raise SettingsError("Data directory override must be absolute")
        return path
    user_home = Path.home() if home is None else Path(home)
    system = sys.platform if platform is None else platform
    if system == "darwin":
        return user_home / "Library" / "Application Support" / "Casting Partner Agent"
    if system == "win32":
        base = Path(environment.get("LOCALAPPDATA", user_home / "AppData" / "Local"))
        return base / "Casting Partner Agent"
    base = Path(environment.get("XDG_DATA_HOME", user_home / ".local" / "share"))
    if not base.is_absolute():
        base = user_home / ".local" / "share"
    return base / "casting-partner-agent"


def _paths(directory):
    root = Path(directory)
    if not root.is_absolute():
        raise SettingsError("Data directory must be absolute")
    if any(path.is_symlink() for path in (root, *root.parents)):
        raise SettingsError("Data directory must not traverse symbolic links")
    if root.exists() and os.name != "nt" and root.stat().st_mode & 0o077:
        raise SettingsError("Use an owner-only data directory")
    return root, root / "settings.json"


def _validate(settings):
    # An allowlist keeps secrets and unsupported future options out of this file.
    expected = {"schema_version", "mode", "approval_required", "sources"}
    if not isinstance(settings, dict) or set(settings) != expected:
        raise SettingsError("Unsupported settings fields")
    if type(settings["schema_version"]) is not int or settings["schema_version"] != 1:
        raise SettingsError("Unsupported settings version")
    if settings["mode"] != "read_only" or settings["approval_required"] is not True:
        raise SettingsError("This preview does not support unattended writes")
    if settings["sources"] != []:
        raise SettingsError("Live source configuration is not implemented")
    return settings


def load_settings(directory):
    _, path = _paths(directory)
    if path.is_symlink():
        raise SettingsError("Settings must not be a symbolic link")
    if not path.exists():
        return None
    if os.name != "nt" and path.stat().st_mode & 0o077:
        raise SettingsError("Use an owner-only settings file")
    try:
        # Explicit cap prevents accidentally reading a database or large export.
        with path.open("r", encoding="utf-8") as stream:
            content = stream.read(65537)
        if len(content) > 65536:
            raise SettingsError("Settings exceed the supported size")
        return _validate(json.loads(content))
    except (json.JSONDecodeError, UnicodeError) as error:
        raise SettingsError("Invalid settings file") from error


def initialize(directory):
    root, path = _paths(directory)
    existing = load_settings(root)
    if existing is not None:
        return existing
    root.mkdir(parents=True, mode=0o700, exist_ok=True)
    settings = {"schema_version": 1, "mode": "read_only", "approval_required": True, "sources": []}
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return load_settings(root)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(json.dumps(settings, indent=2) + "\n")
    return settings
