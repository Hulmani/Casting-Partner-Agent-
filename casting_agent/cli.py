"""Developer entry point. An accessible graphical setup is still planned."""

import argparse
import json
import sys

from .config import SettingsError, default_data_dir, initialize, load_settings
from .demo import main as run_demo


def main(argv=None):
    parser = argparse.ArgumentParser(description="Casting Partner Agent developer preview")
    parser.add_argument("command", choices=("status", "init", "demo"), nargs="?", default="status")
    parser.add_argument("--data-dir", help="Absolute local settings directory; never a credential file")
    args = parser.parse_args(argv)
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
