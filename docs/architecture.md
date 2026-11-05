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

Start on the user's Mac with a local service and SQLite. Keep the computer awake and online for scheduled runs. Use a dedicated browser profile for the worker, with the user signing in normally. Gmail uses its own authorized connection. A future hosted deployment needs its own credentials, browser environment, and operational setup.

The desktop chat's `cua_repl` access is not a dependency we can assume is available to this app. Implement a replaceable browser-driver interface. Evaluate Playwright/browser control first for sites; add screenshot-based computer use where necessary after verifying API access and behavior. Public reference: https://developers.openai.com/api/docs/guides/tools-computer-use

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

Only models, adapter interfaces, fictional intake, and SQLite history are implemented. The planned action states, approvals, scheduler, UI, calendar, and browser driver are not executable yet.
