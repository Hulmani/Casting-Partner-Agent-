"""Build the native proof as a clickable macOS app; not a production installer."""

import argparse
import plistlib
from pathlib import Path

from casting_agent.desktop import build_helper


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    bundle = args.destination.expanduser()
    if not bundle.is_absolute() or bundle.suffix != ".app" or bundle.exists():
        parser.error("choose a new absolute .app path")
    executable = bundle / "Contents" / "MacOS" / "CastingDesktop"
    build_helper(executable)
    info = {
        "CFBundleName": "Casting Partner Desktop Proof",
        "CFBundleDisplayName": "Casting Partner Desktop Proof",
        "CFBundleIdentifier": "ca.castingpartner.desktopproof",
        "CFBundleExecutable": "CastingDesktop",
        "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": "0.1",
        "CFBundleVersion": "1",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "13.0",
    }
    with (bundle / "Contents" / "Info.plist").open("wb") as stream:
        plistlib.dump(info, stream)
    print(bundle)


if __name__ == "__main__":
    main()
