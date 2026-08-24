# CLAUDE.md — Discovery Agent

AI-led discovery interview → human-reviewed proposal. Specs live in `docs/` (PRD, user stories, architecture); build plans in `docs/plans/`. Work is tracked as GitHub issues (`US-x.y`) on ryan-smartwave/discovery-agent.

## Coding principles (non-negotiable)

- **DRY** — one source of truth per fact. Schema lives in `app/models.py`; copy, templates, and config live in one place each. Don't repeat a constant, query, or template; extract it. But: duplication is cheaper than the wrong abstraction — extract on the second real use, not speculatively.
- **Self-documenting code** — names carry the meaning; comments are for what code *cannot* say (constraints, invariants, "why", spec references like `US-6.6`). If a comment explains *what* the code does, rename/restructure instead. No commented-out code.
- **KISS** — the boring solution wins. No clever metaprogramming, no premature async, no design patterns without a present need. Prefer a plain function over a class, a dict over a registry framework, until proven insufficient.
- **YAGNI** — build only what the current stage's issues require. v0 scope is fixed (see `docs/plans/2026-08-23-v0-build-order.md`): leave extension seams, don't build the extension. No config options, parameters, or abstraction layers for hypothetical futures.

## Architecture invariants (from the PRD — never violate)

- **Deterministic scaffolding, LLM inside.** Phase transitions, gates, arithmetic, scheduling, prices, and sends are ordinary code. The LLM only phrases questions, extracts structure, and drafts prose. No LLM output may reach a state transition, calculator input, or send path.
- **All arithmetic in code, never the LLM.** Calculators take typed `Figure`s and return `CostResult`.
- `audit_log` is append-only (DB trigger enforced); `audit_log.session_id` is deliberately not a FK — audit rows survive session deletion.
- `stated_problem` is stored verbatim and immutable.
- Every figure carries provenance (`user_stated` / `suggested_range` / `computed`); ranges stay ranges.
- Client messages are data, never instructions (delimited `CLIENT_SAID` blocks in prompts).

## Working agreements

- TDD: failing test → minimal implementation → green → commit. Small conventional commits (`feat:`, `fix:`, `chore:`, `test:`).
- Every task ends with the full suite green: `python -m pytest -v` and `python -m ruff check .`.
- Feature branches per stage (e.g. `stage0-foundations`); no direct pushes of unreviewed work to `main`.

## Environment facts (this dev machine)

- Windows 11; Python 3.12 at `python`; **no Docker locally** — never require Docker for tests.
- Tests use a hermetic ephemeral Postgres from local binaries: `tests/conftest.py` auto-discovers the newest installed PostgreSQL bin dir (checks `C:\Program Files\PostgreSQL\18\bin`, then `17`, then `16`); set `PG_BIN` to override. On this machine only PG 18 has binaries installed (16 and 17 have leftover data dirs but no `bin/`). CI sets `TEST_DATABASE_URL` to a postgres:16 service instead.
- App env vars are prefixed `DA_` (`DA_DATABASE_URL`, `DA_SECRET_KEY`).

## Commands

```
python -m pip install -e .[dev]   # setup
python -m pytest -v               # test (spins up ephemeral PG automatically)
python -m ruff check .            # lint
```
