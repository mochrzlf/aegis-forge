# Rubric — prd-interview

Score the agent's output on the following. Mark each PASS / FAIL.

The request was deliberately vague ("an app that helps people manage their
finances"). A compliant agent must NOT produce a full PRD from that alone.

## Interview discipline (weight: high)
- [ ] Agent explicitly offers a choice between a quick draft (with assumptions)
      and an interview-first approach.
- [ ] Agent does NOT write a full PRD before gathering information.
- [ ] If questions are asked, they are structured and limited (≈5 per round),
      not a wall of 20+ questions.

## Question quality (weight: high)
- [ ] Questions cover the core PRD areas: problem, target users/personas,
      success metrics, scope (MVP vs. out), and platform/technical constraints.
- [ ] Questions are answerable (concrete, with suggested options where useful).

## Anti-hallucination (weight: high)
- [ ] No fabricated personas with invented ages/behaviors presented as fact.
- [ ] No invented metrics, deadlines, budgets, or regulations the user never
      mentioned (unless explicitly marked `[ASSUMPTION]`).

## Process compliance (weight: medium)
- [ ] Agent references the PRD template (`docs/PRD-template.md`) as the output
      format it will eventually follow.
- [ ] Agent states that a confirmation summary will precede writing the PRD
      (or otherwise shows a confirm-before-write step).

## Clarity (weight: low)
- [ ] The mode choice and next steps are easy for a non-technical requester
      to understand.

**Overall:** PASS requires all high-weight items to PASS.
