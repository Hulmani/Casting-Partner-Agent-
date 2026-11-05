import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from casting_agent.cli import main
from casting_agent.config import SettingsError, default_data_dir, initialize, load_settings


class LocalSettingsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        # macOS temporary-directory paths can have system-level symlink aliases.
        self.root = Path(self.temporary.name).resolve() / "profile"

    def test_status_is_read_only_even_before_setup(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(["status", "--data-dir", str(self.root)])
        self.assertEqual(result, 0)
        self.assertFalse(self.root.exists())
        self.assertFalse(json.loads(output.getvalue())["submissions_enabled"])
        self.assertFalse(json.loads(output.getvalue())["initialized"])

    def test_reinitializing_preserves_existing_file(self):
        settings = initialize(self.root)
        path = self.root / "settings.json"
        original = path.read_bytes()
        self.assertEqual(initialize(self.root), settings)
        self.assertEqual(path.read_bytes(), original)
        if os.name != "nt":
            self.assertEqual(self.root.stat().st_mode & 0o777, 0o700)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_os_accounts_get_separate_default_directories(self):
        for platform in ("darwin", "linux", "win32"):
            first = default_data_dir(platform=platform, home=self.root / "alice", environ={})
            second = default_data_dir(platform=platform, home=self.root / "bob", environ={})
            self.assertNotEqual(first, second)
            self.assertNotIn("outputs", first.parts)

    def test_relative_override_is_rejected(self):
        with self.assertRaises(SettingsError):
            default_data_dir(override="data", environ={})

    def test_unattended_writes_and_credentials_are_rejected(self):
        initialize(self.root)
        path = self.root / "settings.json"
        original = path.read_text()
        for change in ({"approval_required": False}, {"api_key": "fictional"}, {"mode": "automatic"}, {"sources": ["gmail"]}):
            settings = json.loads(original)
            settings.update(change)
            path.write_text(json.dumps(settings))
            with self.assertRaises(SettingsError):
                load_settings(self.root)

    def test_corrupt_settings_are_not_overwritten(self):
        initialize(self.root)
        path = self.root / "settings.json"
        path.write_text("invalid JSON")
        with self.assertRaises(SettingsError):
            initialize(self.root)
        self.assertEqual(path.read_text(), "invalid JSON")

    @unittest.skipIf(os.name == "nt", "Creating symlinks may require Windows privileges")
    def test_settings_symlink_is_rejected(self):
        initialize(self.root)
        other = self.root.parent / "other.json"
        other.write_text("{}")
        path = self.root / "settings.json"
        path.unlink()
        path.symlink_to(other)
        with self.assertRaises(SettingsError):
            load_settings(self.root)
        self.assertEqual(other.read_text(), "{}")

    def test_cli_error_does_not_echo_file_content(self):
        initialize(self.root)
        (self.root / "settings.json").write_text("fictional-private-data")
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            self.assertEqual(main(["status", "--data-dir", str(self.root)]), 2)
        self.assertNotIn("fictional-private-data", output.getvalue())

    @unittest.skipIf(os.name == "nt", "POSIX permissions only")
    def test_existing_shared_settings_are_rejected_without_chmod(self):
        initialize(self.root)
        path = self.root / "settings.json"
        path.chmod(0o644)
        with self.assertRaises(SettingsError):
            load_settings(self.root)
        self.assertEqual(path.stat().st_mode & 0o777, 0o644)

    @unittest.skipIf(os.name == "nt", "POSIX permissions only")
    def test_existing_shared_directory_is_rejected_without_chmod(self):
        initialize(self.root)
        self.root.chmod(0o755)
        with self.assertRaises(SettingsError):
            initialize(self.root)
        self.assertEqual(self.root.stat().st_mode & 0o777, 0o755)


if __name__ == "__main__":
    unittest.main()
