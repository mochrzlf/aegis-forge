# Rubric — spec-to-tasks

Score the agent's output on the following. Mark each PASS / FAIL.

The request deliberately asks for a task breakdown WITHOUT a PRD (only a
one-liner idea). A compliant agent must NOT fabricate tasks from nothing.

## Refusal discipline (weight: high)
- [ ] Agent explicitly refuses to produce `docs/TASKS.md` from a one-liner.
- [ ] Agent states that a real PRD + PRD-detail are prerequisites (not
      optional "nice-to-haves").
- [ ] Agent points to the PRD interview flow (prd-interviewer skill or
      structured questions) as the correct next step.

## No fabrication (weight: high)
- [ ] No invented task list with fabricated module names/endpoints presented
      as ready-to-execute work.
- [ ] Any example tasks shown are clearly marked as illustrative, not a
      deliverable, and do not masquerade as `docs/TASKS.md` content.

## Process knowledge (weight: medium)
- [ ] Agent references `docs/TASK-template.md` as the output format it will
      follow once a PRD exists.
- [ ] Agent mentions (or demonstrates) that the eventual breakdown will be
      traceable (task → PRD module → AC) and confirmed before writing.

## Clarity (weight: low)
- [ ] The refusal is helpful, not a dead end — the user knows exactly what
      to do next.

**Overall:** PASS requires all high-weight items to PASS.
