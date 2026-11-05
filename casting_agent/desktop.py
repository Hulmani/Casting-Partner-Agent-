"""Real macOS control bridge. It never substitutes demo data for failed reads."""

import json
import platform as platform_info
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"bon-kercasting.ca", "www.bon-kercasting.ca", "facebook.com", "www.facebook.com", "mail.google.com"})
NAVIGATION_LABELS = frozenset({"My Profile", "Photos & Documents", "Open Jobs", "Discussion", "See more"})


class DesktopError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def validate_url(url):
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as error:
        raise DesktopError("url_not_allowed", "The page URL is invalid.") from error
    if (parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS
            or parts.username is not None or parts.password is not None
            or port not in (None, 443)):
        raise DesktopError("url_not_allowed", "Choose an HTTPS Bon-Ker, Facebook, or Gmail page.")
    return url


def build_helper(destination):
    if sys.platform != "darwin":
        raise DesktopError("unsupported_platform", "Desktop control currently supports macOS only.")
    compiler = shutil.which("swiftc")
    if compiler is None:
        raise DesktopError("compiler_missing", "The developer prototype needs Apple's Swift command-line tools.")
    destination = Path(destination).expanduser()
    if not destination.is_absolute():
        raise DesktopError("invalid_helper_path", "Choose an absolute output path.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).with_name("native") / "DesktopControl.swift"
    try:
        with tempfile.TemporaryDirectory(prefix="casting-swift-cache-") as cache:
            subprocess.run([compiler, str(source), "-o", str(destination),
                            "-target", platform_info.machine() + "-apple-macos13.0",
                            "-framework", "AppKit", "-framework", "ApplicationServices",
                            "-module-cache-path", cache],
                           check=True, capture_output=True, text=True, timeout=120)
    except (subprocess.SubprocessError, OSError) as error:
        raise DesktopError("build_failed", "The native helper could not be compiled.") from error
    return destination


class MacDesktopController:
    def __init__(self, helper):
        self.helper = Path(helper).expanduser()

    def _run(self, *arguments):
        if sys.platform != "darwin":
            raise DesktopError("unsupported_platform", "Desktop control currently supports macOS only.")
        if not self.helper.is_absolute() or not self.helper.is_file():
            raise DesktopError("helper_missing", "Build the native helper before using desktop control.")
        try:
            result = subprocess.run([str(self.helper), *arguments], capture_output=True,
                                    text=True, timeout=25)
            payload = json.loads(result.stdout)
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
            raise DesktopError("helper_failed", "The native helper did not return a valid result.") from error
        if not isinstance(payload, dict):
            raise DesktopError("invalid_result", "The helper response was not an object.")
        if result.returncode != 0 or not payload.get("ok"):
            failure = payload.get("error", {})
            raise DesktopError(failure.get("code", "helper_failed"),
                               failure.get("message", "Desktop operation failed."))
        return payload

    def status(self):
        return self._run("status")

    def open_url(self, url):
        return self._run("open", validate_url(url))

    def read_page(self):
        result = self._run("read")
        validate_url(result["url"])
        if result.get("source") != "macos_accessibility" or not result.get("nodes"):
            raise DesktopError("invalid_snapshot", "No real Accessibility page content was returned.")
        return result

    def click_navigation(self, observed_url, label):
        validate_url(observed_url)
        if label not in NAVIGATION_LABELS:
            raise DesktopError("action_not_allowed", "Only approved navigation controls are supported.")
        return self._run("click", observed_url, label)
