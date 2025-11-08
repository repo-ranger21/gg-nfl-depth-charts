# GuerillaGenics

**Fantasy Football, But Wilder.**  
Primal, data-driven NFL DFS & betting intelligence powered by BioBoost — biometric signals fused with market data to help you make smarter, more entertaining decisions. Built for contributors, collaborators, and curious bettors.

Badges: [CHANGELOG](CHANGELOG.md) • [package.json](package.json)

---

## Quick Start

1. Install dependencies
```sh
npm install
```

2. Run the app (development)
```sh
npm run dev
```

3. Open the frontend
- Visit http://localhost:3000 after the dev server starts.

Files you’ll likely edit:
- Frontend: [client/](client/) — React + TypeScript UI (pages like [Week 1 dashboard](client/src/pages/week1.tsx))
- Backend: [server/](server/) — Node services and API routes
- Python CLI: [src/gorillagenics/cli.py](src/gorillagenics/cli.py) (see [`eval`](src/gorillagenics/cli.py) command)
- Core BioBoost logic: [server/utils/bioBoostCalculator.js](server/utils/bioBoostCalculator.js) (see [`calculateBioBoost`](server/utils/bioBoostCalculator.js))

---

## What is BioBoost?

BioBoost is GuerillaGenics' proprietary 0–100 readiness score. It combines biometric proxies (sleep, hormone proxies, hydration, recovery), matchup factors, injury status, and market signals to create:
- Score (0–100)
- Recommendation (OVER / UNDER / HOLD)
- Confidence band
- Gorillian commentary and a human-friendly explanation

Core generator locations:
- Frontend playground & calculators: [client/src/utils/bioBoostCalculator.js](client/src/utils/bioBoostCalculator.js)
- Server-side canonical scoring: [server/utils/bioBoostCalculator.js](server/utils/bioBoostCalculator.js)

---

## Features

- Weekly picks dashboard with spreads, totals, BioBoost scores, and commentary (see [client/src/pages/week1.tsx](client/src/pages/week1.tsx)).
- Juice Watch real-time line movement simulation and alerts.
- Gematria meta-layer for playful, fusion-style signals ([server/services/gematria-scoring.ts](server/services/gematria-scoring.ts)).
- Contributor-friendly architecture: clear modules for analytics, UI, and CLI.
- Responsible gaming messaging baked into the UI.

---

## Development Notes

- UI: React + TypeScript, TailwindCSS, Framer Motion, shadcn/ui + Radix primitives.
- State & fetching: React Query.
- Backend: Node (Express-style routes) + helper utilities in [server/](server/).
- Python: CLI tools and analytics helpers in [src/gorillagenics/](src/gorillagenics/) — version and exports in [`__init__.py`](src/gorillagenics/__init__.py).

Helpful scripts are defined in [package.json](package.json).

---

## CLI (Local)

The Python CLI exposes developer tools for EV calculations, bankroll management, and slip evaluation.

Example (evaluate a slip):
```sh
# see implementation: src/gorillagenics/cli.py
python -m gorillagenics.cli eval --csv examples/picks.csv --slip "1,2,3" --stake 1.0
```
See the [`eval`](src/gorillagenics/cli.py) function for options and behavior.

---

## Testing & CI

- Tests live in [tests/](tests/) (pytest for Python pieces + JS tests).
- CI is wired up for linting and pytest (see [CHANGELOG.md](CHANGELOG.md) for CI notes).
- To run Python tests:
```sh
pytest
```

---

## Contributing

We welcome pull requests and contributors. To get started:
1. Fork and branch from `main`.
2. Run the app locally and write tests for new behavior.
3. Keep changes modular — add new metrics as separate modules under `server/utils/` and new UI panels under `client/src/components/`.
4. Open a PR and describe the intent, affected files, and any manual verification steps.

Developer resources:
- Core CLI: [src/gorillagenics/cli.py](src/gorillagenics/cli.py)
- BioBoost logic: [server/utils/bioBoostCalculator.js](server/utils/bioBoostCalculator.js) and [client/src/utils/bioBoostCalculator.js](client/src/utils/bioBoostCalculator.js)

---

## Responsible Gaming & Ethics

GuerillaGenics is a satirical, entertainment-forward project. BioBoost and all outputs are for research, education, and entertainment — not financial advice. The UI includes a visible Responsible Gaming notice. Keep biometric data public/opt-in/anonymized and document sources for any derived metrics.

---

## Architecture Snapshot

- client/ — React UI (Vite, TS)
- server/ — API endpoints & scoring services
- src/gorillagenics/ — Python analytics & CLI
- tests/ — test suites
- attached_assets/ — design notes and pasted references

---

## Need Help?

- Browse the code: [client/](client/) • [server/](server/) • [src/gorillagenics/](src/gorillagenics/)
- Report issues or start a discussion via GitHub Issues.

---

Thank you for building with GuerillaGenics. Swing safe, play smart, and keep the jungle fun. 🦍