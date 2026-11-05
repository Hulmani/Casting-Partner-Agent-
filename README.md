# Casting Partner Agent

A personal casting assistant that brings agency listings, Facebook leads, and email into one review queue. It helps a performer find suitable roles, prepare accurate submissions, and track availability requests, holds, and confirmed bookings.

Open source under the [MIT license](LICENSE). The product direction is a downloadable local app: each person runs their own copy and connects their own accounts. A dot integration is optional and planned.

## Current iteration: desktop-control proof (not live-validated)

Working: a standard opportunity record, source adapter contract, SQLite intake with duplicate protection and revision history, an installable Python package, non-secret per-user settings, and a local demo using fictional data.

New code: a native macOS Chrome launcher, Accessibility reader, bounded mouse navigation, and a clickable test window. The code compiles, but the current execution environment blocks the live test. **No successful real-page read is verified yet.** See [the exact validation results and manual test](docs/desktop-proof.md).

Planned next: connect to the user's existing signed-in Chrome session through an explicitly authorized local browser-control bridge, then read Bon-Ker, Facebook casting posts, and Gmail pages. Direct Gmail/API connections are optional later integrations. Matching against a verified profile and calendar, an accessible approval dashboard, and submission tracking remain planned. No live account integration, AI calls, scheduler, or application submission is enabled yet. This project does not inherit tools or login sessions from the chat that created it.

## Try the foundation

Requires Python 3.9 or later; no third-party packages are needed for this iteration.

```sh
python3 -m casting_agent.demo
python3 -m casting_agent status
python3 -m unittest discover -s tests -v
```

The demo prints fictional opportunities and persists nothing. Status creates no files. These commands are for development only; the downloadable graphical app and mouse/touch onboarding are not ready yet. See [installation and release gates](docs/distribution.md).

## Design

- [Architecture](docs/architecture.md)
- [Iteration plan](docs/roadmap.md)
- [Data and approval rules](docs/data-and-approvals.md)
- [Local distribution](docs/distribution.md)
- [Optional dot integration](docs/dot-integration.md)

## Repository workflow

One issue per useful increment, one branch and reviewable pull request per issue. Include what works, how it was checked, and remaining limitations. Merge only after required checks pass. Keep real photos, email bodies, profiles, credentials, browser sessions, and local databases out of Git.
