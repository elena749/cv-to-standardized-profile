# Working Conventions for AI Pair-Programming

This file defines how AI coding assistants should work in this repository.
Read this before any task in this repo.

## Project Context

This repository contains a CV extraction pipeline that maps unstructured CVs
onto a structured profile schema. The pipeline uses n8n for orchestration
and OpenAI GPT-4o for extraction.

**Code legibility matters.** This codebase is reviewed by humans, including
external evaluators. Optimize for clarity over cleverness.

## Repository Layout

```
.
├── README.md              ← architecture decisions, ADRs, roadmap
├── CHANGELOG.md           ← release notes
├── CLAUDE.md              ← this file
├── docs/adr/              ← architecture decision records
├── schema/                ← JSON schemas (canonical + strict-mode variant)
├── eval/
│   ├── cvs/               ← input CVs
│   ├── ground_truth/      ← ground-truth profiles + LABELING_CONVENTIONS
│   ├── raw_outputs/       ← pipeline outputs (created by run scripts)
│   └── results/           ← evaluation reports
└── n8n/                   ← workflow JSON exports
```

## Working Conventions

### Before any task

1. Read `README.md` to understand current state and decisions
2. Inspect `eval/` structure to understand established patterns
3. Check related conventions in `eval/ground_truth/LABELING_CONVENTIONS.md`
4. Verify which files actually exist before assuming structure

### When writing code

1. **Simplest thing that works.** No premature abstractions, no framework
   for a one-off script, no clever metaclasses.
2. **Standard library first.** Add dependencies only when they earn their
   keep. Currently approved: `requests`.
3. **Single-file scripts** for evaluation tooling. Don't split a 200-line
   script into 5 files.
4. **Functions, not classes.** Unless state actually needs to persist.
5. **Type hints where they help readability.** Not religiously everywhere.
6. **Constants at the top** for URLs, timeouts, paths.
7. **Print to stdout** for evaluation scripts run manually.

### When writing tests

Manual verification by running scripts is the current testing approach.
The evaluation pipeline itself is the test — F1 scores verify behavior.

### When writing prompts for the pipeline

`LABELING_CONVENTIONS.md` defines the labeling rules for the LLM. Any
extraction prompt must reflect those conventions verbatim or by reference.

### When you don't know something

**Ask before guessing.** Examples:
- "Should the script process files in alphabetical order or by modification time?"
- "What happens if the same CV is processed twice — overwrite or skip?"
- "Is this a fatal error or a logged warning?"

The cost of asking is small; the cost of guessing wrong and shipping it
is large.

### After completing a task

1. Show diffs before saving
2. Don't run scripts automatically — leave running to the developer
3. Don't commit on the developer's behalf
4. Summarize what was changed in 3-5 bullet points

## Anti-Patterns to Avoid

1. **Auto-running scripts.** The developer verifies before next step.
2. **Over-abstracting.** A 50-line script doesn't need class hierarchies.
3. **Adding dependencies without justification.** No `pandas`, `rich`,
   `pydantic`, etc. without explicit approval and rationale.
4. **Inferring intent beyond the prompt.** If asked for X, build X —
   not X-plus-improvements-you-thought-of.
5. **Modifying files beyond the task scope.** If asked to add a script,
   don't also "clean up" the README.

## Communication Style

- Concise. Don't restate the prompt.
- Direct. "I'll add X" not "I would propose to consider adding X."
- Show work in code, not commentary about the code.
- Brief summaries at the end of multi-step work.