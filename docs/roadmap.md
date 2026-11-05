# Iteration plan

## 0 — Foundation

- Define product boundaries, standard opportunity data, and adapter capabilities.
- Ingest fictional records into SQLite without duplicate rows on repeated runs.
- Preserve changed listings and roll back a failed intake batch.
- Establish tests and CI.

## 0.1 — Local open-source distribution (current)

- MIT license, installable Python package, and developer entry point.
- Per-user non-secret settings outside the checkout, with read-only defaults.
- Installed-package smoke checks across macOS, Windows, and Linux.
- Document end-user release gates and an optional future dot connection.
- A graphical installer and mouse/touch onboarding are still required before advertising a download-and-use app.

## 1 — Existing-session Chrome control (next)

First prove our standalone app can read a tab in the user's existing signed-in Chrome session through a supported, explicitly authorized local browser bridge. Provide mouse/touch controls for selecting sites and stopping access. Launching Chrome alone is not the bridge. Do not copy cookies or require a new browser profile or per-service OAuth by default.

Then read Bon-Ker listings, Facebook casting posts, and Gmail pages. Expand full text, distinguish email previews from complete listings and booking/availability messages, retain original references, and detect expired sessions or verification screens. Report missing access instead of claiming success. Read only: no posting or applying.

## 2 — Optional direct email/API connections

Offer read-only Gmail OAuth when it improves reliability or scheduling, without making it mandatory for browser-based use. Preserve selected senders/groups, incremental cursors, original references, duplicate handling, and clear source health.

## 3 — Profile, matching, and accessible review

User-verified profile and photo library, calendar connection, explicit travel and pay preferences. Explain fits and missing facts; suggest cross-source duplicates. Large touch targets, screen-reader labels, mouse controls, and optional voice input. User can inspect the original listing and override recommendations.

## 4 — Prepared applications and approvals

Draft submissions with exact destination, selected assets, and answers. Bind approval to the payload and current listing revision. Recheck dates; record action IDs; verify submission; do not retry ambiguous outcomes. Initially enable one supported agency workflow only.

## 5 — Booking operations and scheduled runs

Track holds, confirmations, call-time changes, cancellations, and replies. Notify on meaningful changes and urgent required responses; stay quiet on unchanged runs. Add scheduler recovery, source health, backups, retention controls, and a stop switch.

## Done for each increment

Small GitHub issue → branch → implementation → relevant checks → pull request with evidence and limitations. Do not describe a connector as live until tested against its authorized destination. No real personal data in issues, fixtures, logs, or commits.
