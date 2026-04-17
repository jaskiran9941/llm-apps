# Examples

This folder stores real input/output pairs that improve future runs of this skill.

## Structure

```
examples/
├── good/          ← outputs that worked well (high-rated feedback)
└── corrections/   ← before/after pairs showing what was wrong and how it was fixed
```

## Adding Examples

**Good example** — when a run gets a 4 or 5 rating, save the output:
```
examples/good/YYYY-MM-DD-brief-description.md
```

**Correction** — when you fix a bad output, save both versions:
```
examples/corrections/YYYY-MM-DD-what-was-wrong.md
```
Format:
```
## Input
[the research question or topic]

## Bad Output
[what the skill originally produced]

## Corrected Output
[what it should have said]

## Why
[the lesson to learn]
```

## How Examples Are Used

When EVOLVE MODE runs, Claude reads all files in this folder as few-shot examples. Good examples reinforce what to keep; corrections teach what to avoid. The more examples you accumulate, the more calibrated the skill becomes.
