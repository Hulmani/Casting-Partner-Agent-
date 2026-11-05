# Iteration plan

## 0 — Foundation (current)

- Define product boundaries, standard opportunity data, and adapter capabilities.
- Ingest fictional records into SQLite without duplicate rows on repeated runs.
- Preserve changed listings and roll back a failed intake batch.
- Establish tests and CI.

## 1 — Gmail discovery

Read-only Gmail authorization; explicit selected senders/groups; persistent incremental cursor; distinguish Facebook previews, full casting emails, availability requests, and booking confirmations. Keep original message/post references and report intake failures. Test duplicate notifications and missing role details.

## 2 — Browser discovery

Dedicated browser profile and visible login handoff. Read Bon-Ker listings and Facebook group posts, expand full text, record evidence and canonical post identity, and detect login or challenge screens. No posting or applying. Prove extraction on user-approved sources and test failure handling.

## 3 — Profile, matching, and accessible review

User-verified profile and photo library, calendar connection, explicit travel and pay preferences. Explain fits and missing facts; suggest cross-source duplicates. Large touch targets, screen-reader labels, mouse controls, and optional voice input. User can inspect the original listing and override recommendations.

## 4 — Prepared applications and approvals

Draft submissions with exact destination, selected assets, and answers. Bind approval to the payload and current listing revision. Recheck dates; record action IDs; verify submission; do not retry ambiguous outcomes. Initially enable one supported agency workflow only.

## 5 — Booking operations and scheduled runs

Track holds, confirmations, call-time changes, cancellations, and replies. Notify on meaningful changes and urgent required responses; stay quiet on unchanged runs. Add scheduler recovery, source health, backups, retention controls, and a stop switch.

## Done for each increment

Small GitHub issue → branch → implementation → relevant checks → pull request with evidence and limitations. Do not describe a connector as live until tested against its authorized destination. No real personal data in issues, fixtures, logs, or commits.
