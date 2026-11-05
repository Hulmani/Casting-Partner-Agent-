# Architecture

## Product flow

Discover → retrieve full listing → normalize → detect duplicates → check completeness and expiry → compare verified profile and availability → review → prepare application → approve exact action → execute once → verify → track replies.

## Components and boundaries

| Component | Responsibility |
| --- | --- |
| Source adapters | Independent Gmail, agency, Facebook-browser, and manual-link inputs. Advertise capabilities instead of assuming all sources support writes. |
| Intake | Retain source ID, external ID, original URL, observation time, evidence text, and missing details. An email preview is a lead, not a complete listing. |
| Opportunity store | Stable source identity, revision history, and duplicate candidates across sources. Never merge separate roles merely because production names match. |
| Matching | Explain fit, known conflicts, missing facts, and dates using a user-verified profile. Never infer skills or sensitive attributes from photos. |
| Application preparation | Select approved assets, draft answers, and name the exact recipient/site and data to send. |
| Approval and action executor | Bind approval to one revision and exact payload, expire stale approvals, avoid repeated sends, and verify results. |
| Booking tracker | Keep submitted, availability requested, held, booked, declined, cancelled, and completed distinct. A hold does not become a booking automatically. |
| Accessible dashboard | Large Approve, Skip, Details, Take over, and Stop controls. No keyboard-only action; voice input is optional and must not submit accidentally. |
| Scheduler and notifications | Persist cursors, retry read failures with backoff, report expired sessions, and notify on relevant leads or required action. |

## Proposed runtime

Distribute a local app that each person installs and connects to their own accounts. Start live integration testing on the user's Mac; test portable core behavior on Windows and Linux as well. Keep the computer awake and online for scheduled local runs. The first integration will control a user-authorized existing signed-in Chrome session through a local browser bridge. Read Gmail, Facebook, and agency pages in that session; separate Gmail OAuth is not a prerequisite. An optional dedicated profile may be offered if the user wants one. Reuse access through the supported browser connection rather than exporting cookies or copying browser profiles. Store non-secret settings in the per-user application data directory rather than the source checkout. A shared hosted account service is outside the first product scope. See [distribution](distribution.md).

An optional future [dot integration](dot-integration.md) can reuse restricted workflow operations. Standalone use must not require a dot, and no runtime inherits this chat's accounts or browser sessions.

The desktop chat's `cua_repl` access is not a dependency we can assume is available to this app. Implement a replaceable browser-driver interface. The first technical spike must prove that our own app can read an existing signed-in Chrome tab through a supported, explicitly authorized connection. Merely launching Chrome does not supply that control. Choose the bridge after that validation; do not assume a standard Playwright launch inherits an existing profile. Add screenshot-based computer use where necessary after verifying API access and behavior. Public reference: https://developers.openai.com/api/docs/guides/tools-computer-use

Suggested later code layout:

```text
casting_agent/
  models.py             # Standard records
  adapters/             # Independent source integrations
  store.py              # Local persistence and history
  matching/             # Evidence-backed fit checks
  approvals/            # Exact-action approvals
  actions/              # Submission and verification
  worker/               # Scheduling and recovery
dashboard/              # Accessible review interface
tests/                  # Fictional fixtures and meaningful behavior checks
```

## Reliability requirements

- Track per-source health: ready, needs login, unavailable, or disabled. A failed source must not make the whole run appear successful.
- Resolve relative dates against post time and source timezone; show dates in America/Toronto. Unknown dates stay unknown.
- Retrieve the full post before matching requirements. Record image-only requirements as incomplete until read and verified.
- Use stable Facebook post IDs to connect email notices to browser listings. Cross-source similarity creates a review suggestion rather than silently dropping a lead.
- Re-read a listing and recheck calendar conflicts before approving a submission.
- An interrupted submission enters an unknown-result state. Verify at the destination before retrying.
- Allow the user to pause a source or all actions, revoke connections, and correct profile facts.

## This iteration's limits

Models, adapter interfaces, fictional intake, SQLite history, package entry points, and non-secret local settings are implemented. A native macOS control prototype now compiles and exposes URL launch, Accessibility reads, and bounded mouse navigation. Its live desktop test is blocked; no real page read is verified. The full approval workflow, scheduler, end-user UI, calendar, dot integration, and autonomous browser agent remain unimplemented. See [desktop proof](desktop-proof.md).
