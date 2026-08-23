# Discovery Agent

An AI-led discovery interview for any client problem — structured by the three-move consultative methodology (**difficult questions → frameworks → case studies**), ending in a generated, human-reviewed proposal and a booked decision meeting.

**Status:** Pre-development · PRD v1.0 · August 2026

## What it is

A conversational AI application that interviews a prospective client about any business problem, using a fixed six-phase protocol:

0. **Intake & problem framing** — AI disclosure, verbatim `stated_problem`, automatic problem-class framing, consent
1. **The opening computation** — "What does this problem cost you?" computed live, in code
2. **The six dimensions** — value economics, accountability, quality system, talent enablement, risk, resilience
3. **Findings read-back** — the "Fair summary?" gate
4. **Qualification gates** — Number exists · Owner pain · Core problem · Reachable → Now / Later-with-reason
5. **Scheduling** — books the decision meeting with a named human consultant

**Design principle:** deterministic scaffolding, LLM inside. The protocol, gates, arithmetic, scheduling, and composition checks are ordinary code. The LLM only phrases questions, extracts structure, and drafts prose — it can never skip a phase, invent a number, or fabricate a case study.

## Documents

| Doc | Contents |
|---|---|
| [PRD v1.0](docs/discovery-agent-prd-v1.0.md) | Product spec: protocol, proposal spec, goals G1–G7, phasing, acceptance criteria |
| [User Stories v1.0](docs/discovery-agent-user-stories.md) | 45 stories across 10 epics, with acceptance criteria and priorities |
| [Architecture v1.0](docs/discovery-agent-architecture.md) | OSS-first system design: FastAPI + LangGraph + Postgres + Redis + Whisper, docker-compose deployment |

## Planned stack

React/Vite PWA · Python FastAPI · LangGraph orchestrator · PostgreSQL 16 · Redis + Celery · faster-whisper (Taglish STT) · WeasyPrint/docxtpl · Google Calendar API or Cal.com · Langfuse · Docker Compose on one VM.

## Roadmap

- **v0 — Internal spike (2–3 weeks):** text-only, 4 problem classes, five-phase state machine, Markdown proposal to a consultant inbox. Exit: 12 pilot sessions, ≥8 sellable-findings, numbers match manual notes.
- **v1 — Pilot release:** voice + Taglish, all 8 classes, war stories, consultant review queue, PDF/docx, scheduling with calendar integration, admin config, analytics.
- **v1.5+:** self-serve operator onboarding, CRM export, multi-consultant routing, template marketplace.

## Working with the issues

Every user story is a GitHub issue (`US-x.y`), labeled by epic, priority (`P0`/`P1`/`P2`), persona, and `guardrail` (⚠ release-blocking). Epic tracking issues carry the story checklists. Milestones map to the roadmap: **v0 = all P0 stories, v1 = P0 + P1, v1.5+ = P2.**
