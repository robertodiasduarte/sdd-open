<!-- Language: **English** · [Português](pt-BR/roadmap.md) -->

# Roadmap

What SDD Open intends to add, and what it is still weighing. For what already ships, see the
[README](../README.md) and the [comparison](comparison.md).

**How to read the status column.** *planned* means the work is designed and queued, with no date:
the pace depends on review cycles, not on a calendar. *under evaluation* means the idea is being
weighed and may not happen. A theme leaves this page when it ships, and its mechanism comes with its
own document.

| Theme | What it brings | Status |
|---|---|---|
| **Chained flow** | each phase offers the next one; decision classes in the question format; a pause with a resume point when the agent cannot open a fresh session by itself | *planned* |
| **Adversarial review** | review by a second vendor over a frozen diff, with an editable registry of engines and an offline gate that checks the review really happened | *planned* |
| **Context and governance** | a map of the domain before the Define, project patterns the Design cites, and governance that blocks the Define of a financial system until it runs | *planned* |
| **`sdd-loop-builder` and `sdd-drive`** | a skill for code that calls an LLM in a loop, and one that drives several phases in a row with the same human stops | *planned* |
| **Spec ↔ code reconciliation** | checking that the file manifest covered every requirement, not only that acceptance passed | *planned* |
| **Specs as deltas** | a spec written as a difference against a canonical capability set, instead of a long-lived document | *under evaluation* |

Every theme keeps the rules the package already follows: the truth lives in a script or a git hook
that runs in all seven supported agents, and whatever depends on one agent's own tooling degrades to
a manual stop instead of breaking.
