"""Developer entry point. An accessible graphical setup is still planned."""

import argparse
import json
import sys

from .config import SettingsError, default_data_dir, initialize, load_settings
from .demo import main as run_demo
from .desktop import DesktopError, MacDesktopController, build_helper


def main(argv=None):
    parser = argparse.ArgumentParser(description="Casting Partner Agent developer preview")
    parser.add_argument("command", choices=("status", "init", "demo", "desktop-build", "desktop-status", "desktop-open", "desktop-read", "desktop-click"), nargs="?", default="status")
    parser.add_argument("--data-dir", help="Absolute local settings directory; never a credential file")
    parser.add_argument("--helper", help="Absolute path to the native desktop helper")
    parser.add_argument("--url", help="Permitted URL to open, or the last observed URL for a navigation click")
    parser.add_argument("--label", help="Exact approved navigation label to click")
    args = parser.parse_args(argv)
    if args.command.startswith("desktop-"):
        if not args.helper:
            parser.error("desktop commands require --helper")
        try:
            if args.command == "desktop-build":
                result = {"ok": True, "helper": str(build_helper(args.helper))}
            else:
                controller = MacDesktopController(args.helper)
                if args.command == "desktop-status":
                    result = controller.status()
                elif args.command == "desktop-open":
                    if not args.url:
                        parser.error("desktop-open requires --url")
                    result = controller.open_url(args.url)
                elif args.command == "desktop-read":
                    result = controller.read_page()
                else:
                    if not args.url or not args.label:
                        parser.error("desktop-click requires --url and --label")
                    result = controller.click_navigation(args.url, args.label)
            print(json.dumps(result, indent=2))
            return 0
        except DesktopError as error:
            print(json.dumps({"ok": False, "error": {"code": error.code, "message": str(error)}}), file=sys.stderr)
            return 2
    if args.command == "demo":
        run_demo()
        return 0
    try:
        directory = default_data_dir(override=args.data_dir)
        settings = initialize(directory) if args.command == "init" else load_settings(directory)
    except (SettingsError, OSError):
        # Do not echo untrusted settings or exception messages containing data.
        print("Unable to use local settings. Check the directory, access, and settings format. No live connection was attempted.", file=sys.stderr)
        return 2
    print(json.dumps({
        "stage": "developer_preview",
        "data_directory": str(directory),
        "initialized": settings is not None,
        "mode": "read_only",
        "live_connections": [],
        "scheduler_running": False,
        "submissions_enabled": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
