---
name: tldr-this
description: Simplify a supplied or recent long assistant output into a concise, actionable brief. Use only when the user explicitly invokes $tldr-this or /tldr-this; do not apply this style automatically.
disable-model-invocation: true
license: MIT
metadata:
  short-description: Make a long output scannable and actionable
---

# TL;DR This

Turn one targeted long output into a compact, decision-ready brief. This skill affects only the requested summary; it does not change the response style for later turns.

The objective is not simply fewer words. The reader should be able to see what happened, what matters, and what to do next without reading the original output.

## Select the source

- If the invocation includes text, a file, or a link, summarize that target.
- If invoked without a target, summarize the most recent substantial assistant output in the conversation.
- If no target is available, ask the user to paste it or identify the message to simplify.
- Read the whole target before writing. Keep facts, inferences, completed work, and open questions distinct.
- Do not carry this style into later replies unless the user invokes `$tldr-this` or `/tldr-this` again.

## Choose the right amount of detail

- For a simple answer, use one conclusion sentence and up to three supporting points.
- For a task, investigation, or status report, lead with the current state, then give the smallest ordered set of next actions.
- For a decision with alternatives, give the recommendation first and at most three compact trade-offs.
- For a failure, state the failing point, known cause, and the next useful diagnostic or repair.
- For an output that is already concise, preserve its structure and improve clarity rather than forcing a shorter format.

Keep the main brief to five visible items or fewer. This is a presentation limit, not permission to omit an important blocker or safety constraint.

## Write the brief

1. Start with the answer, decision, current state, or next action. Do not announce that a summary is coming.
2. Use numbered steps when the reader must do something. Each step should be one bounded action.
3. Use `Key points:` with bullets when the source is informational rather than actionable.
4. Make completed work visible in concrete terms: what now works, what changed, or what was verified.
5. Add `Watch for:` only for a material risk, blocker, uncertainty, or unverified assumption.

Use short sentences and plain language. Remove process narration, duplicate detail, sidebars, generic closers, and nonessential background. Do not invent facts, certainty, or recommendations absent from the source.

## Preserve what must remain exact

- Keep commands, file paths, identifiers, versions, dates, quantities, error text, and test results exact when they are needed to act or verify the outcome.
- Retain the difference between a completed action, a planned action, and an inferred conclusion.
- State uncertainty directly. Do not turn a possibility into a conclusion just to make the brief cleaner.
- If the source contains a safety, cost, data-loss, or deployment consequence, keep it visible even when it makes the summary longer.

## Adapt to common source types

**Technical investigation:** lead with the diagnosed cause or the strongest finding. Include the evidence only when it supports the decision.

**Command or test output:** name the result first. For a failure, include the first useful error and the next diagnostic; do not paste repeated logs.

**Implementation report:** state what changed, the verification result, and any remaining limitation.

**Plan or checklist:** reduce it to the next one to five actions, in order. Keep dependencies and required approvals explicit.

**Decision memo:** state the recommendation, why it wins, and the material downside of the alternatives.

## Response shape

Use this default structure when it fits:

```markdown
[One-sentence conclusion or next action]

1. [Action or key point]
2. [Action or key point]

Watch for: [Only if material]
```

When there are no actions, replace the numbered list with `Key points:` and up to five bullets.

## Pre-send check

Before sending, verify:

1. The first line tells the reader the important result or next action.
2. A reader can separate done, blocked, and next without opening the original.
3. Exact details that affect action or verification survived compression.
4. The response contains no more than five visible actions or key points unless completeness requires more.
5. The final line ends with the answer, a material watch-out, or the next action; it does not add a generic closing.
