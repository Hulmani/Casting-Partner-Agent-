# Casting Agent

A personal casting assistant that brings agency listings, Facebook leads, and email into one review queue. It helps a performer find suitable roles, prepare accurate submissions, and track availability requests, holds, and confirmed bookings.

## Current iteration: foundation

Working: a standard opportunity record, source adapter contract, SQLite intake with duplicate protection and revision history, and a local demo using fictional data.

Planned: Gmail intake, a dedicated signed-in browser worker, matching against a verified profile and calendar, an accessible approval dashboard, and submission tracking. No live account integration, AI calls, scheduler, or application submission is enabled yet. This project does not inherit tools or login sessions from the chat that created it.

## Try the foundation

Requires Python 3.9 or later; no third-party packages are needed for this iteration.

```sh
python3 -m casting_agent.demo
python3 -m unittest discover -s tests -v
```

The demo prints fictional opportunities and persists nothing. Future user controls must be available through large buttons and voice-friendly flows; these commands are for development only.

## Design

- [Architecture](docs/architecture.md)
- [Iteration plan](docs/roadmap.md)
- [Data and approval rules](docs/data-and-approvals.md)

## Repository workflow

One issue per useful increment, one branch and reviewable pull request per issue. Include what works, how it was checked, and remaining limitations. Merge only after required checks pass. Keep real photos, email bodies, profiles, credentials, browser sessions, and local databases out of Git.
