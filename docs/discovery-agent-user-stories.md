# Discovery Agent — User Stories

**Derived from PRD v1.0 (six-phase protocol, proposal generation, meeting scheduling)**

Version 1.0 · August 2026

---

## How to read this document

- **Personas:** `Client` (the business owner being interviewed), `Consultant` (the human who reviews, sends, and attends the meeting), `Admin` (the operator configuring the deployment), `System` (non-functional / guardrail stories).
- **Priority:** `P0` = must-have for v0 internal spike · `P1` = must-have for v1 pilot release · `P2` = v1.5+.
- **IDs** are stable for traceability to the PRD (§ references included per epic).
- Every story includes acceptance criteria (AC). Stories marked ⚠ are guardrail stories — they are release-blocking regardless of priority ordering.

---

## EPIC 1 — Session start: intake and problem framing (PRD §4 Phase 0)

### US-1.1 · Start a session from a link `P0 · Client`
As a business owner, I want to open the discovery session from a simple link or QR code without creating an account, so that I can start immediately from my phone.
**AC:** Session starts from URL/QR on mobile browser; no login required; session gets a resumable ID; works on low-end Android browsers.

### US-1.2 · Know I'm talking to an AI ⚠ `P0 · Client`
As a client, I want the agent to tell me upfront that it is an AI, so that I'm never misled about who is interviewing me.
**AC:** First message contains explicit AI disclosure; disclosure also appears in the proposal footer; no message ever claims or implies the agent is human; copy reviewed by legal.

### US-1.3 · Describe my business and problem in my own words `P0 · Client`
As a client, I want to describe my business and the problem that brought me here in free-form text or a voice message, so that the interview starts from *my* situation, not a menu.
**AC:** Two intake prompts (business, problem); free-form text accepted; `stated_problem` stored **verbatim**; role, customer type, and rough size collected (size skippable).

### US-1.4 · Automatic problem framing `P0 · System`
As the system, I want to classify the stated problem into a problem class (acquisition, conversion, throughput, quality, retention, supply, risk/compliance, other) and select the matching cost formula, so that the interview computes the right numbers.
**AC:** Classifier outputs class(es) + confidence; multi-class supported; cost formula selected per class; classification logged with the session; standard test set (≥10 personas across 8 classes) classifies correctly.

### US-1.5 · One clarifying question on low confidence `P0 · System`
As the system, I want to ask exactly one disambiguating question when classification confidence is low, so that I never silently guess wrong.
**AC:** Below confidence threshold → one question, phrased conversationally; user's answer re-runs framing; never more than one disambiguation at intake.

### US-1.6 · Detect two-sided problems `P1 · System`
As the system, I want to detect when a problem involves a second market side (suppliers, vendors, talent), so that discovery covers both sides.
**AC:** Sidedness flag set at framing or mid-session; when set, value-economics/accountability/quality probes run for both sides; test persona with a supplier-and-customer problem triggers the branch.

### US-1.7 · Flag problems touching private individuals ⚠ `P1 · System`
As the system, I want to flag problems whose solutions would touch data on private persons, so that targeted risk questions are asked and the proposal carries a data-ethics commitment.
**AC:** Flag set from framing keywords/semantics; adds risk probes in Phase 2; forces the data-ethics paragraph into the proposal; test persona (consumer-facing problem) triggers all three effects.

### US-1.8 · Give informed consent ⚠ `P0 · Client`
As a client, I want a plain-language explanation of what data is collected, why, how long it's kept, and how to delete it, so that I can consent meaningfully.
**AC:** Consent shown before Phase 1; explicit accept required; decline ends session gracefully; consent event logged with timestamp; deletion request honored end-to-end (verified by test).

---

## EPIC 2 — The opening computation (PRD §4 Phase 1)

### US-2.1 · Be asked what my problem costs me `P0 · Client`
As a client, I want to be asked plainly what my problem costs me, so that I confront whether I actually know.
**AC:** Opener uses the class-appropriate phrasing; "I don't know" (or equivalent) routes into the guided computation; a confident direct answer is captured with provenance `user-stated`.

### US-2.2 · Compute my number step by step `P0 · Client`
As a client who doesn't know the number, I want the agent to walk me through a short guided estimate (hours, hour value, spend, outcomes), so that we arrive at a rough cost together.
**AC:** Inputs collected one question at a time; class-correct formula applied; **arithmetic executed in code, never by the LLM**; unit tests per formula; result matches manual computation on the test set.

### US-2.3 · Answer roughly, with ranges `P0 · Client`
As a client, I want to give rough answers and ranges ("10 to 15 hours siguro"), so that I'm not forced into false precision.
**AC:** Ranges parsed and stored as ranges; provenance flag per figure (`user-stated` / `suggested-range`); agent offers typical ranges when the client is stuck; no question demands exact figures.

### US-2.4 · Hear the number played back in one sentence `P0 · Client`
As a client, I want the computed cost played back in one plain sentence, so that the finding lands.
**AC:** Single-sentence playback using the client's currency/units; references at least one thing the client said; a second value anchor (what solving it is worth) is attempted and stored when obtainable.

### US-2.5 · Capture and price war stories `P1 · System`
As the system, I want to capture incident stories (the vendor that flaked, the order that shipped wrong) as structured records and price them when possible, so that lived incidents become proposal-grade numbers.
**AC:** `war_story` records: what happened, consequence, participants, any figures; calculator prices the story when inputs suffice; priced stories appear in findings and proposal with permission wording.

---

## EPIC 3 — The six-dimension interview (PRD §4 Phase 2)

### US-3.1 · Cover all six dimensions, adaptively `P0 · System`
As the system, I want to guarantee coverage of all six dimensions (value economics, accountability, quality system, talent enablement, risk, resilience) with 2–3 dynamically chosen questions each, so that no discovery is structurally incomplete.
**AC:** Coverage tracker per dimension; session cannot reach Phase 3 with an uncovered dimension (excluding client-parked ones, which are logged); question order biased by loudest-pain hypothesis but coverage never skipped.

### US-3.2 · One question at a time `P0 · Client`
As a client, I want to receive one question per message, so that I never face a wall of stacked questions.
**AC:** Interviewer output validated: exactly one interrogative per message; violations blocked and regenerated; verified across the full test suite.

### US-3.3 · Feel heard between questions `P0 · Client`
As a client, I want a short reflection of what I just said before the next question ("So growth happens *to* you, not *by* you — noted."), so that the interview feels like a conversation, not an interrogation.
**AC:** Lock-in reflection (≤1 line) after each substantive answer; reflections restate, never lecture or pitch; tone check in QA review of sample transcripts.

### US-3.4 · Answer in my own language mix `P1 · Client`
As a Taglish-speaking client, I want to answer in whatever mix of English and Tagalog comes naturally — typed or spoken — and have the agent mirror it, so that the session feels natural.
**AC:** Taglish input understood by extractor (standard test set); agent mirrors the client's mix; voice messages in Taglish transcribe correctly (see US-3.5).

### US-3.5 · Answer by voice message `P1 · Client`
As a client on my phone, I want to answer by recording a voice message instead of typing, so that long answers are effortless.
**AC:** In-chat recording; transcription of Taglish audio; low-confidence transcripts shown for one-tap correction ("Did I get that right?"); recordings deleted post-transcription per retention config.

### US-3.6 · Skip or park a question `P1 · Client`
As a client, I want to say "skip" on any question, so that I'm never stuck.
**AC:** Skip parks the question; one retry later with different phrasing; permanently skipped items logged and visible to the consultant; skipping never blocks session completion (gates may still fail as designed).

### US-3.7 · Pause and resume `P1 · Client`
As a busy client, I want to drop off mid-session and resume later, so that I can answer between real work.
**AC:** State persisted continuously; on return, a two-line recap then the next question; sessions resumable for a configurable window (default 7 days); reminder nudge optional and rate-limited.

### US-3.8 · Never be pitched during discovery `P0 · Client` ⚠
As a client, I want the agent to hold off on selling anything during the interview, so that discovery stays honest.
**AC:** Phases 0–3 contain no product names, prices, or pitches; "what do you sell?" gets the deflection line and continues; verified on transcript QA.

### US-3.9 · Re-frame when the real problem emerges `P1 · System`
As the system, I want to re-frame mid-session when answers contradict the intake classification, so that the interview follows the truth, not the first guess.
**AC:** Contradiction detection triggers re-framing; missing probes for the new class backfilled; both classifications logged; test persona ("no customers" that is actually a quality problem) passes.

### US-3.10 · See my progress `P1 · Client`
As a client, I want to see how far along I am ("4 of 6 areas covered"), so that I know the end is near.
**AC:** Progress indicator visible and accurate; total expected time stated at start; per-phase drop-off analytics captured.

---

## EPIC 4 — Findings read-back (PRD §4 Phase 3)

### US-4.1 · Hear my findings in my own words and numbers `P0 · Client`
As a client, I want a summary of the six findings built from my own numbers and (lightly cleaned) words, opening with the exact problem sentence I typed, so that I recognize my situation in it.
**AC:** Read-back covers all six dimensions; opens with verbatim `stated_problem` echo; every number traces to the schema; language mix mirrored.

### US-4.2 · Correct the record `P0 · Client`
As a client, I want to correct any finding before anything is generated, so that the document is built on what I actually meant.
**AC:** Per-finding correction in chat; corrections update the schema with an audit trail; corrected read-back re-presented.

### US-4.3 · The "Fair summary?" gate ⚠ `P0 · System`
As the system, I want to block proposal generation until the client confirms the summary is fair, so that the proposal's authority rests on the client's own sign-off.
**AC:** Hard gate: no confirmation → no proposal; confirmation event logged; declining to confirm routes to correction flow or graceful exit, never to generation.

---

## EPIC 5 — Qualification gates (PRD §4 Phase 4)

### US-5.1 · Evaluate the four gates `P0 · System`
As the system, I want to evaluate Number-exists, Owner-pain, Core-problem, and Reachable automatically, so that every session ends classified Now or Later-with-reason.
**AC:** All four gates evaluate on every confirmed session; classification + reason stored; consultant sees gate-by-gate results; thresholds configurable per deployment.

### US-5.2 · A respectful "not now" ⚠ `P0 · Client`
As an unqualified client, I want an honest, respectful memo telling me this isn't my bottleneck right now — with what was found and what to start tracking — so that I leave with value, not a hard sell.
**AC:** Later memo: findings, failed gate + reason, "start tracking this" guidance where applicable; **no scheduling push**; optional low-key "reply anytime to reach [consultant]" line; stored for re-engagement.

### US-5.3 · Re-engage when conditions change `P2 · Consultant`
As a consultant, I want Later-classified sessions stored with their failed-gate reason and surfaced for re-engagement, so that today's "not now" becomes next quarter's meeting.
**AC:** Later queue filterable by reason/date; export supported; optional reminder scheduling for the consultant.

---

## EPIC 6 — Proposal generation (PRD §5)

### US-6.1 · Generate the proposal from my session `P0 · Client`
As a qualified client, I want a proposal document built from my session — my problem sentence on the cover, my findings first, my numbers with their provenance — so that the document visibly answers what I asked.
**AC:** Skeleton order enforced (cover w/ verbatim problem → findings → numbers table w/ provenance flags → framework → how-we-work → proof → pilot → appendix); Markdown → PDF and .docx.

### US-6.2 · Build the value tree dynamically `P0 · System`
As the system, I want to construct 1–3 value-tree rows (value pool → financial line → operational driver → action + owner) from the findings, filling one row completely and sketching the rest, so that the framework organizes this client's problem specifically.
**AC:** Filled row: financial line = Phase-1 number, driver = the exposed mechanism, action = service-catalog entry mapped by class, owner = named person from the accountability finding; 1–2 sketched rows present; **every filled cell traces to a schema field or catalog entry** (automated check).

### US-6.3 · Handle unmapped problems honestly `P1 · System`
As the system, I want the action cell to say "scoping workshop — this isn't an off-the-shelf fix" when no catalog service maps to the problem class, so that gaps become legitimate engagements instead of forced fits.
**AC:** No-mapping detection; honest action cell text; pilot block swaps to the paid-scoping template; occurrence rate tracked.

### US-6.4 · Match proof, never fabricate it ⚠ `P0 · System`
As the system, I want proof sections filled only from the operator's verified case-study library (matched by class/industry) or honest fallback blocks, so that no fabricated client, name, or result can ever appear.
**AC:** Every proof block carries a library ID (automated check); no match → fallback blocks or section omitted; generation-time attempt to introduce unlisted proof is blocked and logged.

### US-6.5 · Scope the pilot with a falsifiable exit criterion `P1 · System`
As the system, I want the pilot section generated from the class-matched template with fixed scope, a client-judged falsifiable exit criterion, a timeline, and a decision meeting, so that the close is a small provable engagement.
**AC:** Template fields filled from session data; exit criterion phrased as client-judgeable; price only from operator price blocks; decision-meeting reference consistent with the booked slot (Epic 8).

### US-6.6 · Every number provable ⚠ `P0 · System`
As the system, I want an automated pre-send check that every number in the document exists in the session schema, so that the LLM cannot introduce figures.
**AC:** Number extraction + schema diff on the final document; any orphan number blocks send and alerts the consultant; check covers tables and prose.

---

## EPIC 7 — Consultant review and send (PRD §5–6)

### US-7.1 · Get notified with the essentials `P0 · Consultant`
As a consultant, I want a notification when a discovery completes — business, problem class, Now/Later, and requested meeting slot — so that I can prioritize instantly.
**AC:** Notification within 1 minute of completion; contains the four essentials; deep-links to the review screen.

### US-7.2 · Review everything in one screen `P0 · Consultant`
As a consultant, I want one screen with the transcript, findings, numbers (with provenance), gate results, skipped questions, and the draft proposal, so that I can judge quality in minutes.
**AC:** All artifacts on one screen; findings link back to source transcript moments; provenance visible per figure.

### US-7.3 · Edit before sending `P0 · Consultant`
As a consultant, I want to edit the draft — swap the filled tree row, adjust pilot scope, set the price — before approving, so that my judgment shapes what the client receives.
**AC:** Row swap among candidate rows; pilot/price fields editable within operator blocks; edits tracked; re-render to PDF/docx after edit.

### US-7.4 · Nothing sends without me ⚠ `P0 · Consultant`
As a consultant, I want a hard guarantee that no proposal reaches a client without my approval, so that the human stays accountable for every promise made.
**AC:** Send blocked pre-approval at the API level (not just UI); approval event logged with user + timestamp; bulk/auto-approve does not exist in v1.

### US-7.5 · Beat the booked slot `P1 · Consultant`
As a consultant, I want a warning when my review pace threatens an already-booked meeting slot, so that the client never shows up to a call without the document.
**AC:** Countdown vs. booked slot on the review screen; escalating alerts; one-tap option to trigger the reschedule flow.

---

## EPIC 8 — Scheduling the decision meeting (PRD §4 Phase 5)

### US-8.1 · Be told a human takes it from here ⚠ `P0 · Client`
As a client, I want the agent to say explicitly that the meeting will be with a named human consultant — not the AI — so that expectations are exactly right.
**AC:** Scheduling opener names the consultant and states the AI won't attend; invite names the human; no copy anywhere implies AI attendance.

### US-8.2 · State my availability naturally `P1 · Client`
As a client, I want to say when I'm free in plain language ("Tuesday after 3", "kahit anong umaga next week") by text or voice, so that booking doesn't feel like filling a form.
**AC:** NL availability parsing to candidate windows (test set incl. Taglish expressions); ambiguity → one clarifying question; timezone defaults Asia/Manila, overridable.

### US-8.3 · Pick from real slots `P1 · Client`
As a client, I want to choose from up to 3 concrete slots that actually fit the consultant's calendar, so that my pick sticks.
**AC:** Slots computed from real free/busy inside my stated windows; slot selection confirms in chat; double-booking impossible (verified under concurrent-booking test).

### US-8.4 · Receive a proper calendar invite `P1 · Client`
As a client, I want a calendar invite (.ics / Google) naming the consultant, referencing my stated problem, and containing the call link, so that the meeting is real and findable.
**AC:** Invite to both parties on confirmation; title format "Reviewing: '[stated_problem]' — [Business] × [Operator]"; video/phone details included; proposal attached or linked once approved.

### US-8.5 · Reminders, reschedule, cancel `P1 · Client`
As a client, I want a 24-hour reminder and the ability to reschedule or cancel in chat, so that changes are painless.
**AC:** Reminder fires T-24h; reschedule re-runs slot offering; cancel notifies the consultant; all changes sync both calendars.

### US-8.6 · Fallback when we can't match `P1 · System`
As the system, I want to capture "best way and time to reach you" and mark the session Booked-pending when no slot overlap exists or the client stalls, so that no qualified lead dies in scheduling.
**AC:** Fallback triggers on no-overlap or timeout; contact preference captured; consultant notified with the thread; state = Booked-pending.

### US-8.7 · Schedule only after gates pass ⚠ `P0 · System`
As the system, I want scheduling questions to appear only after gates pass — never during discovery, never for Later sessions — so that booking is a next step, not pressure.
**AC:** Phase-5 unreachable pre-gates in the state machine; Later memos contain no scheduling push; verified in tests.

### US-8.8 · Minimal calendar permissions ⚠ `P1 · Admin`
As an operator, I want the agent's calendar access scoped to free/busy and event creation on a designated calendar only, so that it can book meetings but never read my other events.
**AC:** OAuth scopes limited accordingly (Google / Microsoft 365); scope verified in integration tests; the LLM never calls the calendar directly — only the deterministic scheduler service does.

---

## EPIC 9 — Admin configuration (PRD §6–7)

### US-9.1 · Configure the service catalog `P1 · Admin`
As an operator, I want to map problem classes to my services with tree-row action templates, so that proposals propose what *my firm* actually delivers.
**AC:** CRUD for catalog entries (class → service → action template); versioned; proposals record the config version used.

### US-9.2 · Maintain the proof library `P1 · Admin`
As an operator, I want a case-study library where only verified entries (with class/industry tags) exist, so that proof matching can never draw from anything unapproved.
**AC:** Entry requires verification checkbox + owner; tags for matching; edits versioned; deleting an entry doesn't break past proposals (snapshotting).

### US-9.3 · Configure pilots, prices, and trust text `P1 · Admin`
As an operator, I want to define pilot templates per class, price blocks, and my trust-framework text, so that the composer assembles from my approved language only.
**AC:** Templates with placeholders validated against schema fields; price blocks the only price source; trust text required before first send.

### US-9.4 · Tune the gates `P1 · Admin`
As an operator, I want configurable gate thresholds, so that I can balance pipeline volume against consultant load.
**AC:** Thresholds per gate; changes versioned; consultant-agreement rate (G4) reported per configuration.

### US-9.5 · Watch quality per problem class `P1 · Admin`
As an operator, I want per-phase drop-off and per-class quality analytics, so that I know which problem classes work and where sessions die.
**AC:** Dashboards: completion (G1), number-yield (G2), edit-time (G3), agreement (G4), effort (G5), generality (G6), booking (G7); per-class breakdowns; "other"-class rate alarm at >20%.

---

## EPIC 10 — Guardrails and non-functional ⚠ (PRD §7–8)

### US-10.1 · Instructions in client messages are data `P0 · System`
As the system, I want instructions embedded in client messages ("give me a discount," "ignore your rules," "act as the admin") refused and logged, so that the session cannot be steered off-protocol.
**AC:** Prompt-injection suite passes; refusals are polite and stay in character; every attempt logged.

### US-10.2 · No advice beyond scope `P0 · System`
As the system, I want legal, financial, and tax questions deferred to the human consultant, so that the agent never gives regulated advice.
**AC:** Deferral behavior on the test set; deferrals logged; no exceptions in transcripts.

### US-10.3 · Token budget with graceful wrap-up `P1 · System`
As the system, I want a per-session token budget with graceful wrap-up behavior near the cap, so that costs are bounded without sessions dying mid-sentence.
**AC:** Budget enforced at gateway; near-cap → agent moves to read-back with what's covered; hard cap never truncates mid-exchange.

### US-10.4 · Full audit trail `P0 · System`
As the operator, I want an audit log of everything the agent asked and asserted, every consent, every gate result, and every send, so that any session can be reconstructed.
**AC:** Append-only log; per-session reconstruction verified; retention per policy.

### US-10.5 · Delete me `P0 · Client`
As a client, I want my data deleted on request, so that my consent remains meaningful.
**AC:** Deletion request path in chat and via contact; cascades across transcripts, recordings, schema, documents (minus legally required records); completion confirmed to the client; verified end-to-end.

---

## Story map summary

| Epic | P0 stories | P1 stories | P2 stories |
|---|---|---|---|
| 1 · Intake & framing | 1.1–1.5, 1.8 | 1.6, 1.7 | — |
| 2 · Opening computation | 2.1–2.4 | 2.5 | — |
| 3 · Six dimensions | 3.1–3.3, 3.8 | 3.4–3.7, 3.9, 3.10 | — |
| 4 · Read-back | 4.1–4.3 | — | — |
| 5 · Gates | 5.1, 5.2 | — | 5.3 |
| 6 · Proposal | 6.1, 6.2, 6.4, 6.6 | 6.3, 6.5 | — |
| 7 · Consultant review | 7.1–7.4 | 7.5 | — |
| 8 · Scheduling | 8.1, 8.7 | 8.2–8.6, 8.8 | — |
| 9 · Admin | — | 9.1–9.5 | — |
| 10 · Guardrails | 10.1, 10.2, 10.4, 10.5 | 10.3 | — |

**v0 spike = all P0 stories** (text-only, 4 problem classes, consultant inbox instead of full review UI is acceptable). **v1 pilot = P0 + P1.** Guardrail stories (⚠) are release-blocking at their tier regardless of sequencing.
