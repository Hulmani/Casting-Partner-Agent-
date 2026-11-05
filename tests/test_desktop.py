import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

from casting_agent.cli import main
from casting_agent.desktop import DesktopError, MacDesktopController, validate_url


class DesktopBoundaryTests(unittest.TestCase):
    def test_only_selected_https_services_are_allowed(self):
        for url in (
            "http://bon-kercasting.ca/my-profile", "file:///private/tmp/page.html",
            "https://example.com/", "https://facebook.com.evil.example/",
            "https://user:password@facebook.com/", "https://mail.google.com:9000/",
            "https://mail.google.com:invalid/",
        ):
            with self.subTest(url=url), self.assertRaises(DesktopError):
                validate_url(url)
        self.assertEqual(validate_url("https://bon-kercasting.ca/my-profile"),
                         "https://bon-kercasting.ca/my-profile")

    def test_submission_labels_are_not_mouse_actions(self):
        controller = MacDesktopController("/helper-not-installed")
        with self.assertRaises(DesktopError) as raised:
            controller.click_navigation("https://bon-kercasting.ca/my-profile", "I'M INTERESTED")
        self.assertEqual(raised.exception.code, "action_not_allowed")

    def test_missing_helper_never_returns_demo_data(self):
        with tempfile.TemporaryDirectory() as directory:
            controller = MacDesktopController(Path(directory) / "missing")
            with self.assertRaises(DesktopError) as raised:
                controller.read_page()
        self.assertEqual(raised.exception.code,
                         "helper_missing" if sys.platform == "darwin" else "unsupported_platform")

    def test_cli_read_failure_is_explicit_and_contains_no_fictional_record(self):
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            result = main(["desktop-read", "--helper", "/helper-not-installed"])
        self.assertEqual(result, 2)
        payload = json.loads(output.getvalue())
        self.assertFalse(payload["ok"])
        self.assertNotIn("fictional", output.getvalue().lower())
        self.assertNotIn("opportunities", payload)


if __name__ == "__main__":
    unittest.main()
