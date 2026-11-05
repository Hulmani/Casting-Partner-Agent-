# Native desktop-control proof (macOS)

This is real control source, not a Gmail mock or a completed casting agent. It uses AppKit, Accessibility, and Core Graphics. There is no extension, OAuth setup, cookie copying, browser-debugging port, or model API.

## Implemented operations

- Open an approved HTTPS URL in the installed Chrome through NSWorkspace.
- Check Accessibility trust without requesting or changing permission.
- Read Chrome's actual focused web area's verified URL, title, observation time, text, and control bounds.
- Send a physical left-click to a unique visible, exact-match navigation control after checking the page URL and foreground Chrome process. Submission labels are rejected.
- Display results and errors in a clickable native test window.

A sent click is explicitly not verified successful navigation. Read again to inspect the result. Screenshots, scrolling, extraction into opportunity records, scheduling, and an autonomous reasoning loop are not implemented.

## Permission and data boundary

The user must enable Accessibility in macOS for this prototype. That OS permission can allow reading and controlling other apps; our implementation restricts its targets to Chrome and selected Bon-Ker, Facebook, and Gmail origins. Opening Accessibility Settings does not enable permission. No permission is requested automatically.

Reads skip secure text fields and omit editable-field values. Text stays in process output or the local test window. No AI service or repository receives it. Never attach real page snapshots, screenshots, or personal details to GitHub issues.

## Manual validation with mouse/touch

Download the macos-desktop-proof-not-notarized artifact from the PR's Actions run and unpack its included app ZIP. This is a development build, not a signed/notarized release. If macOS blocks it, stop and report the message; do not disable security protections.

1. Open Casting Partner Desktop Proof.
2. Click Check Access to inspect the real permission status.
3. If you choose to grant access, click Open Accessibility Settings, review the OS permission, and enable the prototype yourself. Reopen it if macOS asks.
4. With your ordinary Chrome signed in, click Open Chrome Page.
5. Click Read Chrome Page. Success requires actual page text, URL, title, and source=macos_accessibility. An error is a failed read.
6. On the Bon-Ker profile page, read first, optionally click Open Jobs with Mouse, then read again to verify navigation.

The proof is complete only after this independently running app reads a real page. CI builds and permission-status calls do not satisfy that test.

## Developer build

Requires macOS 13+, Python 3.9+, and Apple's Swift command-line tools. Build a new absolute app path:

    python3 -m casting_agent.build_desktop_app "/absolute/path/Casting Partner Desktop Proof.app"

CLI commands with an explicit --helper path: desktop-build, desktop-status, desktop-open, desktop-read, desktop-click. The wheel includes native Swift source.

## Actual validation results

Native source compiled on macOS 15.8.1. The real status call returned Accessibility=false. A real read returned accessibility_required with no substituted record.

Opening Chrome failed in the execution environment with NSCocoaErrorDomain 259; LaunchServices also reported kLSNoExecutableErr despite the bundle being present. The native AppKit window aborted in _RegisterApplication during NSApplication initialization before reaching the window implementation. The chat's computer-control connection also failed to start.

No authenticated page read or mouse navigation has been verified. A normal desktop-session run and the user's Accessibility authorization are still required. These failures remain open until a successful independent run is recorded.

Apple API references:
- https://developer.apple.com/documentation/applicationservices/1462085-axuielementcopyattributevalue
- https://developer.apple.com/documentation/coregraphics/cgevent
- https://developer.apple.com/documentation/appkit/nsworkspace
