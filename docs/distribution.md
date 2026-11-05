# Downloadable local app

## Confirmed product direction

The project is open source under the MIT license. Each person downloads and runs their own copy, grants access to the Chrome session where they already use their services, and keeps their profile, photos, browser sessions, and opportunity records in their own environment. The first workflow is browser-first: use existing sign-ins when available and hand off expired-session or verification screens. A new per-service OAuth connection is optional, not required for this initial browsing workflow. This first product does not need a shared account service or central database.

Use the same casting workflow regardless of who runs it. The initial runtime will be a local app and worker; an optional future dot/plugin integration may call the same restricted operations. A ChatGPT subscription, dot, or this repository alone does not establish a connection to any casting site. The standalone app will need separately configured AI inference if model extraction or reasoning is enabled; no model provider is connected yet.

## What is installable now

The Python package is a developer preview with status, initialization, and fictional demo commands. It is not a finished performer-facing app, signed desktop installer, autonomous agent, or live integration. The test matrix checks the core on Windows, macOS, and Linux; this does not certify browser or accessibility support on those platforms.

Developer setup on macOS/Linux (not the end-user interface):

```sh
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/casting-agent status
.venv/bin/casting-agent demo
```

On Windows, create the environment with `py -m venv .venv`, then use `.venv\Scripts\python.exe -m pip install .` and `.venv\Scripts\casting-agent.exe status` (or `demo`). No activation or keyboard shortcut is required.

`casting-agent init` creates non-secret read-only settings only. `status` creates no files. The data directory defaults to:

| System | Per-user location |
| --- | --- |
| macOS | `~/Library/Application Support/Casting Partner Agent` |
| Windows | `%LOCALAPPDATA%/Casting Partner Agent` |
| Linux | `$XDG_DATA_HOME/casting-partner-agent` or `~/.local/share/casting-partner-agent` |

`CASTING_AGENT_DATA_DIR` or `--data-dir` accepts an explicit absolute path for development or a separate local profile. On POSIX, initialization creates owner-only settings and rejects an existing shared data directory. Settings contain no credentials. OS accounts and filesystem permissions provide the current separation; this is not an application-level multi-user security boundary, Windows ACL enforcement, or encryption. No real user data should be ingested yet.

## Download and use release gates

- Mouse/touch onboarding with screen-reader labels, large controls, and no required terminal or keyboard shortcuts.
- Explain local storage, any data sent to an AI provider, costs, and selected source access before connection.
- User chooses which browser tabs/sites the agent may use and confirms their own profile facts. Reuse the selected session's existing sign-ins; private login handoff is only needed when the site requires it.
- Verify a supported local browser bridge and secure session handling. Do not copy cookies, require a fresh profile by default, or imply that launching Chrome alone grants the app control.
- A visible run/pause control, source health, failed-login handoff, approval queue, and history.
- Packaged desktop installation, supported-platform checks, signed/notarized artifacts where applicable, versioned upgrades, and user-controlled uninstall/export/delete behavior.
- Review privacy, accessibility, platform terms, dependency licenses, and security behavior. Do not label the product compliant merely because a checklist exists.

No installer or release is automatically published by this iteration. CI creates a developer wheel artifact for testing only.

Packaging reference: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
License reference: https://opensource.org/license/mit
