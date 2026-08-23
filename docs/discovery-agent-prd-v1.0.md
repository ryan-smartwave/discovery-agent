# PRD — Discovery Agent

**An AI-led discovery interview for any client problem — structured by the three-move methodology, ending in a generated proposal**

Version 1.0 · August 2026 · Owner: [TBD] · Status: Pre-development

---

## 1. Overview

### 1.1 One-line summary

A conversational AI application that interviews a prospective client about **any business problem they bring** — using the three-move consultative methodology: **ask difficult questions → provide frameworks → provide case studies** — dynamically generating its questions from six discovery dimensions, computing the client's own numbers live, and ending with an auto-generated, human-reviewed proposal tailored to that problem.

### 1.2 The core idea

Skilled consultative discovery follows a known structure: hard questions the client can't comfortably answer, a live computation of what the problem actually costs, a framework that organizes the mess, proof that someone like them already fixed it, and a small provable first engagement. Today that structure lives in the head of a senior consultant and costs 1–2 hours per prospect before anyone knows whether the prospect is even qualified.

This product moves the *interviewer* role to an AI agent while keeping the methodology fixed:

| | Human-led discovery | This product |
|---|---|---|
| Who asks | Senior consultant | The AI agent |
| Where | Live meeting, 60–120 min | Chat interface, self-paced |
| Input | Spoken conversation | Text chat or voice messages |
| Adaptation | Consultant's judgment | Dynamic follow-ups inside a fixed protocol |
| Output | Notes → manual proposal, days later | Auto-generated draft proposal, human-reviewed |

The agent is **not** a free-styling chatbot. It executes a defined interview protocol — six dimensions, live cost computation, findings read-back, qualification gates — with dynamic phrasing, ordering, and follow-ups.

**What is fixed vs. flexible:**

| Fixed (the methodology — never changes per problem) | Flexible (generated or configured per problem) |
|---|---|
| The three moves and their order | The actual question wording |
| The six discovery dimensions and their intent | Which follow-ups to ask, in what order |
| The live computation pattern ("what does this problem cost you?") | Which cost formula applies (cost per lost customer, cost per hour of manual work, cost per failure, cost per day of delay…) |
| The findings read-back gate ("Fair summary?") | The findings content |
| The value-tree structure: value pool → financial line → operational driver → action + owner | The rows' content, built from the client's answers |
| The qualification gates (number, owner, core, reachable) | Gate thresholds per deployment |
| Proposal skeleton and honesty rules | Frameworks filled in, case studies matched, pilot scoped |

**Design principle:** the methodology is deterministic scaffolding; the LLM operates only *inside* it — phrasing questions, choosing follow-ups, drafting prose. It can never skip a phase, skip a gate, invent a number, or fabricate a case study.

### 1.3 Why this product

1. **Discovery is the expensive, unscalable step.** The agent runs the interview at zero marginal cost, in parallel, 24/7 — and only qualified prospects consume consultant time.
2. **The proposal is pre-sold by construction.** It is assembled from the client's own words and numbers — the core persuasion mechanic of the methodology: *"you told us X costs you ₱Y a month and nobody owns it; here is the fix, and here is who owns it."*
3. **It qualifies as it discovers.** Clients who hit the gates arrive pre-qualified with findings attached; clients who don't receive a respectful "not now" memo with the reason recorded for re-engagement.
4. **Human-in-the-loop by design:** the agent interviews and drafts; the consultant reviews, edits, prices, and closes. Nothing reaches a client unreviewed.

### 1.4 Who operates it

The **operator** is any consultancy, dev shop, agency, or services firm that installs the agent as its front door. The operator configures its own service catalog, case-study library, pilot templates, pricing blocks, and trust language. The product itself is solution-agnostic: it discovers and frames problems; the operator's catalog determines what gets proposed.

### 1.5 Out of scope (v1)

- Live real-time voice calls (v1 = text chat + async **voice messages**).
- Autonomous sending: every proposal passes human review.
- Delivering the solution; the product ends at a proposal and a **booked meeting with the human consultant**. Scheduling that meeting IS in scope (see Phase 5) — attending it is not: **the AI never joins the call; the consultant does.**
- CRM replacement (v1 exports; doesn't manage pipeline).
- Pricing decisions by the AI: prices come only from operator-configured blocks.

---

## 2. Users

| Persona | Description | Needs |
|---|---|---|
| **Client** (interviewee) | A business owner or manager with a problem — often SME-scale, answering from a phone between real work, often mixing English and Tagalog, often preferring voice messages to typing | A low-effort way to explain their problem; something concrete at the end; not feeling interrogated or sold to |
| **Consultant** (operator's seller) | Receives completed discoveries | Trustworthy findings, an editable draft proposal, a clear qualified/not signal with reasons |
| **Admin** (operator) | Configures the deployment | Service catalog, story library, pilot templates, price blocks, gate thresholds, tone and language settings |

---

## 3. Goals and success metrics

| # | Goal | v1 target |
|---|---|---|
| G1 | Clients finish discovery without a human | ≥ 50% completion of started sessions |
| G2 | Discovery yields a usable problem-cost number | ≥ 70% of completed sessions |
| G3 | Proposals are usable | ≥ 80% sent with < 15 min of consultant edits |
| G4 | Qualification accuracy | Consultant agrees with the agent's Now/Later ≥ 85% |
| G5 | Client effort | Median ≤ 25 min; post-session CSAT ≥ 4/5 |
| G6 | Generality | Coherent findings + framework + proposal on ≥ 8 of 10 distinct test problems spanning operations, sales, support, inventory, HR, and process domains |
| G7 | Meetings booked | ≥ 60% of gate-passing sessions end with a confirmed calendar invite; no-show rate ≤ 25% |

**Non-goals:** maximizing session length or engagement; closing deals autonomously.

---

## 4. The interview protocol (functional core)

Six phases. Phases and gates are deterministic; question generation within phases is dynamic.

### Phase 0 — Intake and problem framing (~2–3 min)

**0a · Intake.** The agent discloses it is an AI (mandatory, always), then asks two things:

1. **"What is your business?"** — free-form text or voice.
2. **"What problem brought you here — in your own words?"** — stored **verbatim** as `stated_problem`.

Plus: business name, respondent role, who their customers are, rough size (skippable).

**0b · Problem framing (automatic).** From the intake, the agent builds a **problem frame**:

- **Problem class** — classified into a small open taxonomy the methodology can compute against: *acquisition* (not enough customers), *conversion* (prospects don't close, customers don't buy more), *throughput* (work takes too long / too much manual effort), *quality* (errors, rework, inconsistency), *retention* (customers or staff leave), *supply* (vendors, inventory, sourcing), *risk/compliance*, *other*. Multi-class allowed; "other" is legal and handled honestly (see §5 and §10).
- **Cost formula selection** — each class maps to a live-computation pattern (Phase 1 table).
- **Sidedness detection** — does the problem involve a second market side (suppliers, vendors, talent as well as customers)? If yes, discovery branches to cover both sides.
- **Loudest-pain hypothesis** — the stated problem biases which dimension Phase 2 opens with. It biases *order only*; all six dimensions must still be covered.
- **Private-individuals flag** — if solving the problem would plausibly involve data on private persons (consumers, patients, minors), the flag (a) inserts targeted risk questions in Phase 2 and (b) forces a data-ethics commitment paragraph into the proposal (§5, §8).
- Low classification confidence → the agent asks exactly **one** disambiguating question; it never guesses silently.

**0c · Consent.** Plain-language data notice; explicit accept required to proceed.

**The stated problem is a persuasion asset, not just routing metadata.** It is echoed once in the read-back ("You came in saying *'[stated_problem]'* — here's what that turned out to be in numbers") and printed verbatim on the proposal cover, so the final document visibly answers the exact sentence the client typed.

### Phase 1 — The opening computation: "What does this problem cost you?"

The methodology's opener: a question the client should be able to answer but almost never can. Asked plainly, expecting "I don't know," then computed live from the client's rough inputs. **All arithmetic runs in code, never in the LLM.**

Cost-formula patterns by problem class (operator-extensible):

| Problem class | Live computation | Anchor number produced |
|---|---|---|
| Acquisition | (owner/staff hours × hour value + spend) ÷ wins | Cost per customer won; customer lifetime value |
| Conversion | proposals/quotes written vs. closed × hours each | Cost of the deals that die |
| Throughput | hours of manual work × people × hour value; delay days × value per day | Monthly cost of the manual process / of delay |
| Quality | error rate × rework hours × hour value + write-offs + appeasement discounts | Monthly cost of rework and failure |
| Retention | churned customers × lifetime value; staff turnover × replacement cost | Annual cost of churn |
| Supply | failure incidents × rescue cost (rush fees, discounts, owner weekends); stockouts × missed sales | Cost per supplier failure / stockout |
| Risk/compliance | fall back to "the cost of the last incident" the client has lived through | Cost of one incident |
| Other / unclassified | Generic pattern: hours spent on it + money spent on it + revenue missed because of it | A defensible rough monthly cost |

Behavior requirements:

- Rough estimates and ranges accepted; stored as ranges with **provenance flags** (user-stated vs. suggested-range).
- The agent offers typical ranges when the client is stuck ("Most businesses your size say 10–40 hours — where do you fall?").
- The result is played back in **one plain sentence**: *"So this problem is quietly costing you about ₱[X] a month — and that's before counting [the thing they mentioned]."*
- A second **value anchor** is always attempted: what solving it is worth (lifetime value, capacity freed, margin recovered).

### Phase 2 — The six dimensions (dynamic core, ~12–18 min)

The six dimensions are **problem-agnostic by design** — they interrogate any business problem. The agent must cover all six, 2–3 questions each, dynamically phrased and ordered. Fixed intent per dimension, with the generalized probe pattern:

| Dimension | Fixed intent — what must be captured for ANY problem | Generalized probe pattern |
|---|---|---|
| 1 · **Value economics** — "Where's the money?" | A cost/value number, or the explicit finding "no number has ever existed" | "What does [problem] cost per month? What would fixing it be worth? What did last [period]'s version of it cost?" |
| 2 · **Accountability** — "Who owns it?" | A named owner, or the finding "owned by the busiest person, in spare time / owned by nobody" | "Who, by name, is responsible for [the metric behind the problem]? If it's worse next month, whose problem is that, officially?" |
| 3 · **Quality system** — "Design or luck?" | Whether good outcomes are repeatable by design | "Your best [period] on this — do you know why? Could you repeat it on purpose? Would two of your people handle the same case the same way?" |
| 4 · **Talent enablement** — "Where does your best person's time go?" | The split between low-value grind and work only that person can do; where expertise leaks | "Of the hours spent on [problem area], how much truly needs you or your best people? What happens to what your staff notices day-to-day — does it go anywhere?" |
| 5 · **Risk** — "What could go wrong, and would you catch it?" | Past failed attempts + named fears (legal, brand, safety, data) about fixing it | "What have you already tried, and why didn't it stick? What's the worst thing a fix could get wrong? Any legal or brand landmines here?" *(private-individuals flag adds targeted probes)* |
| 6 · **Resilience** — "Does it survive your worst day?" | Whether the current approach depends on memory, spare attention, or one person; seasonality and lead-time traps | "What happens to this in your busiest month? If you were out for two weeks? When the person who handles it leaves?" *(businesses with long sales/booking lead times get the "the famine is planted months before you feel it" sequence)* |

**Conversation rules (hard requirements):**

- One question per message; never stacked.
- After each meaningful answer: a one-line **lock-in reflection** in plain language ("So growth happens *to* you, not *by* you — noted."), then move on. No lecturing, no pitching.
- Mirror the client's language mix (Taglish in ↔ Taglish out), including in voice-message transcription.
- Never demand precision; never pitch, name a product, or mention price in Phases 0–3. If asked "what do you sell?": *"Whether anything we do fits depends on your answers — let me keep asking."*
- Skip/park allowed on any question; parked questions retried once with different phrasing.
- Sessions resumable with a two-line recap.
- **War-story capture:** when the client tells an incident story (the vendor that flaked, the order that shipped wrong, the hire that quit mid-project), the extractor captures it as a structured `war_story`, and the Phase-1 calculator prices it if possible — lived incidents are the most persuasive numbers in the proposal.
- **Mid-session re-framing:** if answers contradict the intake classification (a "not enough customers" problem reveals itself as a quality problem), the orchestrator re-frames and backfills the missing probes.

### Phase 3 — The findings read-back (gate)

- The agent composes the **six-findings summary** in the client's own numbers and lightly-cleaned own words, opening with the stated-problem echo, closing with: *"Fair summary?"*
- The client corrects → findings update. **No proposal generates until the client confirms the summary is fair.** This is the methodology's consent-to-the-problem-definition step, and it is the source of the proposal's authority.

### Phase 4 — Qualification gates, then proposal

| Gate | Pass condition | On fail |
|---|---|---|
| G1 · Number exists | A problem-cost or value number computed or stated | **Later — no baseline**; output becomes a short "here's the number to start tracking" note |
| G2 · Owner pain | Ownership finding captured and acknowledged | **Later — no owner** |
| G3 · Core problem | Client confirms this is a real current constraint (not hypothetical, not already solved, not "at capacity and fine") | **Later — not the bottleneck**; graceful exit |
| G4 · Reachable | Contact details + consent to receive the document | Hard stop; nothing sent |

- **Pass →** proposal generated (§5) → consultant review queue.
- **Fail →** a **Later memo**: the findings, the failed gate and its reason, respectful exit text ("Based on your answers, this may not be your bottleneck right now — here's what we found, keep it."), stored for re-engagement when the condition changes. **The willingness to say "not now" is a product feature, not an error state** — the methodology's credibility depends on it.

### Phase 5 — Scheduling the decision meeting (gated pass only)

Once the gates pass, the agent books the **decision meeting** — the live call where the client meets the human consultant. The agent is explicit about the hand-off:

> *"The next step is a short call to walk through your document — with [consultant name], a human on our team, not me. When are you generally available this week or next?"*

**Flow:**

1. **Availability capture, conversationally.** The client answers in natural language ("weekday afternoons," "Tuesday after 3", "kahit anong umaga next week") — text or voice. The extractor parses it into candidate windows; ambiguity gets one clarifying question, never a form.
2. **Calendar matching.** The scheduler checks the assigned consultant's connected calendar and offers up to **3 concrete slots** inside the client's stated windows, in the client's timezone (default Asia/Manila).
3. **Confirmation → invite.** On the client's pick, the system sends a **calendar invite** (email .ics / Google Calendar) to both parties. Invite contents: meeting title referencing the stated problem ("Reviewing: '[stated_problem]' — [Business] × [Operator]"), the consultant's name and role, video link or phone details, and — once the proposal is approved — the proposal attached or linked.
4. **Sequencing with review.** Scheduling can run before proposal approval (book early, momentum matters), but the invite/reminder states the document arrives before the call. If the consultant's review will miss the slot, the consultant is alerted to either expedite or let the system propose a reschedule.
5. **Reminders and changes.** Automated reminder 24h before; client can reschedule or cancel in chat; changes sync to the consultant's calendar and notify them.
6. **No-availability fallback.** If no overlap is found or the client stalls, the agent captures "best way and time to reach you," hands the thread to the consultant, and marks the session **Booked-pending**.

**Hard rules:**
- The invite always names the **human** who will attend. The agent never implies it will be on the call, and never books anything without the client's explicit slot confirmation.
- Scheduling questions come only after gates pass — never as pressure during discovery.
- Later-classified sessions get no scheduling push; the Later memo may include a low-key "reply anytime to talk to [consultant]" line instead.
- Calendar access is scoped to free/busy + event creation on the consultant's designated calendar; the agent cannot read event contents.

---

## 5. The generated proposal (output spec)

Fixed skeleton; contents assembled per-problem from session data + operator-approved blocks.

1. **Cover** — client business, date, and the stated problem **quoted verbatim**: "You came to us with: *'[stated_problem]'*." The document visibly exists to answer that sentence.
2. **What you told us** — the six findings, the client's confirmed numbers, their war stories (with permission wording). Leads the document because it is the persuasion engine.
3. **Your numbers** — the live computation as a small table with provenance flags ("your estimate" / "range you selected"), the problem's monthly cost, and the value anchor.
4. **The framework — your problem, organized** — a **dynamically constructed value tree** for this problem: 1–3 rows of *value pool → financial line → operational driver → action + owner*, where:
   - The **filled row** is built from the loudest confirmed pain: the financial line = the Phase-1 number; the driver = the mechanism the findings exposed; the action = drawn from the operator's **service catalog** (mapped by problem class); the row always ends with a **named client-side owner** taken from the accountability finding.
   - 1–2 additional rows appear **sketched but unfilled** — the expansion story, preserved by design.
   - **Composer constraint:** every cell must trace to a schema field or a catalog entry. If no catalog service maps to the problem class, the action cell states honestly: "scoping workshop — this isn't an off-the-shelf fix," and the pilot block becomes a paid discovery/scoping engagement.
5. **How we work** — the operator's configured trust framework: how they deliver, where automation sits vs. human judgment, what the client can verify. If the **private-individuals flag** is set, a data-ethics commitment paragraph is mandatory and auto-included (e.g., "we never profile private individuals — only public requests and consented data").
6. **Proof** — case-study and credibility blocks **matched from the operator's library by problem class and industry**. Matching only: **the agent can never fabricate or embellish a case study, client name, or result.** If the library has no match, the section uses the operator's honest fallback blocks (method-credibility stories: how they work, what they've deliberately said no to) or is omitted entirely.
7. **The pilot — smallest provable engagement** — generated from the operator's pilot templates per problem class: fixed scope, a **falsifiable exit criterion the client judges** ("onboarding time cut from X to Y on 10 real cases," "zero stockouts on the top 20 SKUs for 6 weeks," "error rate below N% on one month of live work"), fixed timeline, a scheduled decision meeting, and a cheap exit for both sides. Pricing appears only here and only from operator price blocks.
8. **Appendix** — full findings detail; a note that all figures came from the client's own session answers.

**Formats and flow:** Markdown → PDF + .docx. **Human review is a hard requirement:** the consultant edits (swap the filled row, adjust scope, set price), approves, then the system sends or the consultant sends manually. Nothing reaches a client unreviewed.

---

## 6. User flows

**Client:** entry link/QR → intake ("your business? your problem, in your own words?") → framing + consent → Phases 1–2 (text/voice, resumable, question order biased by the stated problem) → read-back opens with their own sentence, confirm → gates → **Phase 5 in-chat scheduling: "when are you available?" → picks a slot → calendar invite received, naming the human consultant** → "your document is on its way" → receives the reviewed proposal answering their exact sentence → attends the decision meeting with the consultant.

**Consultant:** notification "Discovery complete — [Business] · [problem class] · NOW · meeting requested [slot]" → review screen (transcript, findings, numbers with provenance, gate results, draft proposal, booked slot) → edit → approve & send (system warns if review pace threatens the booked slot) → attends the meeting prepared with the findings.

**Admin:** configure service catalog (problem class → services → tree-row action templates), pilot templates, case-study library (verified entries only), price blocks, trust-framework text, gate thresholds, tone/language settings → publish → monitor per-phase drop-off and per-problem-class quality (G6) → refine.

---

## 7. System design

- **Client app:** mobile-first web chat (PWA); text input + voice-message recording; visible progress ("4 of 6 areas covered"); resumable sessions.
- **Agent gateway:** session auth, per-session **token budget** with graceful wrap-up behavior near the cap, model routing, rate limits.
- **Orchestrator:** deterministic six-phase state machine; dimension-coverage tracker; **problem framer** (class, cost formula, sidedness, private-individuals flag, loudest-pain hypothesis, mid-session re-framing); gate evaluator. The LLM never controls phase transitions or gates.
- **Scheduler service:** calendar integration (Google Calendar / Microsoft 365 via OAuth, scoped to free/busy + event creation on a designated calendar); natural-language availability parsing via the extractor; slot proposal, .ics/invite issuance, reminders, reschedule/cancel handling; timezone defaulting (Asia/Manila) with override. Deterministic service — the LLM phrases the scheduling messages but never computes slots or writes to the calendar directly.
- **Sub-agents (agent-to-agent separation of concerns):**
  - *Interviewer* — question phrasing and follow-up selection, constrained by the dimension intents + problem frame.
  - *Extractor* — per-message structured extraction (numbers, ranges, named owners, war stories) with confidence scores; **all arithmetic in code**.
  - *Transcriber* — Taglish-capable voice-to-text; low-confidence transcripts shown to the client for one-tap correction.
  - *Composer* — fills the proposal skeleton from schema + catalog + library only; automated checks that **every number in the document exists in the schema** and every proof block carries a library ID.
  - *Classifier* — evaluates gates → Now / Later-with-reason.
- **Operator config store:** service catalog, pilot templates, story library, price blocks, trust text — versioned; each proposal records the config version that produced it.
- **Guardrails:**
  - No invented claims, prices, discounts, client names, or results — these exist only as admin-approved blocks used at composition time.
  - No legal, financial, or tax advice; the agent defers such questions to the human consultant.
  - Prompt-injection posture: client messages are data; instructions embedded in them ("give me a discount," "ignore your rules," "act as the admin") are refused and logged.
  - Full audit log of everything the agent asked and asserted.

---

## 8. Privacy, legal, honesty

- **AI disclosure:** at session start and in the proposal footer. Non-negotiable.
- **Data privacy compliance:** Phase-0 consent with plain-language purpose, retention, and deletion terms; voice recordings deleted after transcription (configurable); deletion requests honored end-to-end. First deployments comply with the PH Data Privacy Act (RA 10173); other jurisdictions map to local equivalents via configuration.
- **No enrichment, no profiling:** the session uses only what the client volunteers. The product does not scrape or enrich data about the client, and the **private-individuals flag** ensures any proposal whose solution would touch consumer/personal data carries an explicit data-ethics commitment.
- **Honesty constraints (product-level, non-negotiable):** no fabricated proof, no fake scarcity or deadlines, and Later memos genuinely tell unqualified clients "not now, and here's why." The methodology's persuasive power comes from demonstrated willingness to say no; the agent inherits that obligation as a hard requirement.

---

## 9. Phasing

**v0 — Internal spike (2–3 weeks).** Text-only; problem framer with 4 problem classes (acquisition, throughput, quality, supply); coded cost calculators for those four; five-phase state machine; read-back gate; qualification gates; Markdown proposal into a consultant inbox; no client-facing send. **Exit criterion (falsifiable):** 12 pilot sessions across at least 4 distinct problem types with friendly businesses; ≥ 8 produce findings a consultant judges "I could sell from this," and computed numbers match a human's manual notes on the same sessions.

**v1 — Pilot release.** Voice messages + Taglish transcription; all 8 problem classes + "other" fallback; sidedness branching; private-individuals flag + data-ethics insertion; war-story capture and pricing; consultant review/edit queue; PDF/docx export; Later memos; **Phase-5 scheduling with consultant calendar integration, invites, reminders, and reschedule handling**; admin configuration for catalog, pilots, stories, prices; per-class analytics (G6).

**v1.5+.** Self-serve operator onboarding (productization for other consultancies and dev shops); CRM export/webhooks; multi-consultant routing and round-robin scheduling; A/B tests on question phrasing; full Tagalog and Bisaya support; a template marketplace of problem-class packs.

**v2 (exploratory).** Live voice conversation mode; closed-loop hand-off where a completed discovery auto-configures the scoping of the delivered engagement; multi-stakeholder discovery (interviewing 2–3 people at the same client and merging findings, surfacing where their answers disagree — often the most valuable finding of all).

---

## 10. Risks and open questions

| Risk / question | Mitigation / note |
|---|---|
| **Generality dilutes quality** — a framework can produce shallow questions on unfamiliar problem classes | The six dimensions are genuinely problem-agnostic, but cost formulas and follow-up quality are not free: the G6 metric + per-class test personas from day one; ship classes incrementally (v0 = 4 classes done well, not 8 done poorly) |
| Clients won't give 20 minutes to a bot | Voice input (lower effort than typing), resumability, visible progress, and a concrete document promised at the end; per-phase drop-off measured from day one |
| Robotic or interrogating feel | Lock-in reflections, one question per message, language mirroring; test with real owners early and iterate on the question bank's conversational variants |
| Garbage numbers in → confident garbage out | Provenance flags on every figure; ranges stored as ranges; the proposal displays provenance ("your estimate"); consultant review as backstop |
| LLM fabrication in proposals | Composer whitelist + automated number-provenance check + library-ID check on every proof block |
| "Other" problem class produces mush | Honest fallback path: the generic cost pattern + a scoping-workshop pilot; monitor how often "other" fires — if > 20% of sessions, the taxonomy needs new classes |
| Unmapped problems (no catalog service fits) | The action cell says so honestly and the pilot becomes paid scoping — turning a gap into a legitimate engagement type rather than a forced fit |
| Over- vs. under-qualification (gates too strict kill pipeline; too loose flood consultants) | Gate thresholds configurable per deployment; track consultant agreement rate (G4) and tune |
| Internal tool first, or productized for operators from day one? | v0/v1 internal-first for the operator building it; the operator-config layer is built from the start so productization is a packaging decision, not a rebuild |
| Ever send unreviewed proposals at volume? | Deliberately deferred; the v1 answer is never. Revisit only with quality data |

---

## 11. Acceptance criteria (v1)

- [ ] Session opens with intake (business + stated problem, stored verbatim) before any discovery question; consent cannot be skipped; AI disclosure present at session start and in the document footer.
- [ ] Problem framer classifies the standard test set (≥ 10 personas across the 8 classes) correctly, sets sidedness and private-individuals flags, and asks exactly one disambiguation question on low-confidence input.
- [ ] Mid-session re-framing works: a persona whose stated problem misidentifies the real problem class gets re-framed, with missing dimension probes backfilled.
- [ ] Correct cost formula selected per class; all arithmetic in code; result played back in one sentence; a second value anchor attempted.
- [ ] All six dimensions covered on every completed session regardless of problem class; one question per message; lock-in reflections present.
- [ ] War stories captured as structured records and priced where possible.
- [ ] Read-back gate blocks proposal generation until confirmed; stated problem echoed in the read-back and printed on the proposal cover.
- [ ] All four gates evaluate; Later memos generated with the failed-gate reason and respectful exit copy.
- [ ] Proposal contains: findings-first structure, numbers table with provenance, dynamically built value tree (every cell of the filled row traces to schema or catalog; 1–2 sketched rows), operator trust framework, library-matched proof only (or honest fallback), pilot with a falsifiable client-judged exit criterion, price only from operator blocks.
- [ ] Composer provenance checks pass: no number outside the schema; no proof block without a library ID.
- [ ] Private-individuals flag forces the data-ethics paragraph into the proposal.
- [ ] Taglish voice message → transcription → extraction passes the standard test set.
- [ ] Nothing sends without consultant approval; consultant edits (row swap, scope, price) supported.
- [ ] Prompt-injection suite passes (discount demands, instruction overrides, fake authority claims → refused and logged).
- [ ] Phase-5 scheduling triggers only after gates pass; natural-language availability ("Tuesday after 3", "kahit anong umaga next week") parses to correct candidate windows; up to 3 valid slots offered from the consultant's real free/busy.
- [ ] Calendar invite issues to both parties on confirmation, names the human consultant, references the stated problem, and never implies the AI attends; reschedule and cancel from chat sync correctly.
- [ ] Scheduling-before-approval sequencing works: consultant is warned when review pace threatens a booked slot; no-overlap fallback captures contact preference and marks Booked-pending.
- [ ] Later-classified sessions receive no scheduling push.
- [ ] G6 generality test: coherent findings + tree + proposal on ≥ 8 of 10 distinct problem types, judged by two consultants.

---

*This PRD encodes the three-move consultative methodology (difficult questions → frameworks → case studies), the six discovery dimensions (value economics, accountability, quality system, talent enablement, risk, resilience), the live "what does this problem cost you?" computation, the findings read-back, the four qualification gates, the value-tree structure (value pool → financial line → operational driver → action + owner), and the smallest-provable-pilot close — applied to any client problem. Changes to the methodology trigger review of §4 and §5.*
