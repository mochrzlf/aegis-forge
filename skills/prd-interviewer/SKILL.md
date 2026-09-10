---
name: prd-interviewer
description: Produces accurate PRDs for aegis-forge projects by interviewing the requester before writing. Use whenever asked to create, draft, or update docs/PRD.md or docs/PRD-detail.md. Offers two modes — (1) quick draft from assumptions, or (2) structured interview for higher accuracy — and defaults to recommending the interview.
---

# PRD Interviewer

A PRD written without verified input is a hallucinated requirement document.
This skill exists to stop that. Source of truth for the output format:
`docs/PRD-template.md` (main PRD) and `docs/PRD-detail-template.md`
(user stories & acceptance criteria). Output that does not follow those
templates is defective.

## Mode Selection (mandatory first step)

When asked to create a PRD, ALWAYS present the choice before writing:

> **How do you want to build this PRD?**
> 1. **Quick draft** — I write it now from your short description + stated
>    assumptions. Fast, but sections may miss the mark.
> 2. **Interview first (recommended)** — I ask structured questions, you
>    answer, I confirm a summary, then I write. More accurate.

If the user picks mode 1, proceed to "Quick Draft Mode".
If the user picks mode 2 (or gives no clear preference), run the interview.

## Quick Draft Mode

1. Write the PRD from the information given.
2. Mark EVERY unverified statement with `[ASSUMPTION: ...]` inline.
3. End with a short list of the top 5 assumptions the user should confirm.
4. Offer: "Want me to run the interview to replace these assumptions?"

Never present a quick draft as final — it is explicitly a draft.

## Interview Mode

### Rules

- **Never write the PRD before the interview is complete.** If asked to skip
  ahead, remind the user that unverified input produces hallucinated PRDs.
- Ask **at most 5 questions per round** — never a wall of 20 questions.
- Provide **suggested options** with each question when plausible, so the
  user can answer by picking a letter/number.
- **Reject vague answers and follow up.** "For everyone" → "What age range?
  What do they do today without this product? What frustrates them most?"
- Track what is answered vs. still open; tell the user what remains.
- Cover **all five areas below** before writing, unless the user explicitly
  defers an area (mark deferred items `[OPEN QUESTION]` in the PRD).

### Area 1 — Problem & Solution
- What real problem does this solve? Who hurts today, and how?
- What do they use instead right now (the "competitor" — even if it's Excel)?
- What is the single core value proposition in one sentence?

### Area 2 — Users & Personas
- Who are the 1–3 primary personas? (age, role, daily workflow)
- What is each persona's #1 frustration and #1 needed feature?
- Who is explicitly NOT a target user?

### Area 3 — Goals & Success Metrics
- What business outcome defines success at 3 / 6 / 12 months?
- What is the North Star Metric (one measurable user action)?
- Which existing baselines (current numbers) can we compare against?

### Area 4 — Scope & Priorities
- What MUST be in the MVP, in priority order?
- What is explicitly OUT of scope for v1?
- Hard deadline or budget constraints?

### Area 5 — Technical & Compliance Constraints
- Target platform(s): web / mobile (native/cross) / API-only / trading?
- Regulatory or compliance needs: GDPR/PDP, financial regulator rules,
  audit-trail requirements, data-residency limits?
- Existing systems to integrate with (auth provider, payment, broker, ERP)?
- Non-functional requirements: expected load, uptime, latency budgets?

### Confirmation Gate (mandatory)

Before writing anything:

1. Present a **structured summary** of all answers, grouped by area.
2. List remaining `[OPEN QUESTION]` items explicitly.
3. Ask: "Is this correct and complete enough to write the PRD?"
4. Only after an affirmative answer, write the PRD.

## Writing the PRD

- Follow `docs/PRD-template.md` section-for-section; do not invent sections.
- For user stories & AC, follow `docs/PRD-detail-template.md` — including
  the security ACs already shown there (token handling, RTR, anti-IDOR,
  audit logging). Do not weaken baseline security requirements to fit a
  user's answer; flag conflicts instead.
- Unanswered items become `[OPEN QUESTION: ...]`, never silently filled.
- Quick-draft leftovers keep their `[ASSUMPTION: ...]` markers.
- Save to `docs/PRD.md` (and `docs/PRD-detail.md` if stories were covered).

## Anti-Patterns to Refuse

- Writing a full PRD from a one-line request without offering the interview
- Asking all questions at once in one giant message
- Accepting "for everyone / all users" as a persona
- Inventing metrics, deadlines, or regulations the user never stated
- Dropping baseline security ACs because the user didn't mention security —
  security is non-negotiable in this baseline; the PRD must carry it
