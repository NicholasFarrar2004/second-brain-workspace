# Architecture

Second Brain stores instructions, facts and task state in files with different jobs. A project can change its next action without rewriting the rules for every other project. Someone returning later can read the current handoff and follow references when they need more detail.

This repository is a fictional demonstration of that design. It does not connect to an account, discover tasks automatically or run an agent in the background.

## Give each kind of information a home

| Information | Home | What belongs there |
| --- | --- | --- |
| Instructions | `AGENTS.md` | How work in this scope should be handled |
| Durable facts | `MEMORY.md` | Current facts and decisions, with dates |
| Current task state | `Handoff.md` | What is done, what remains and the next action |
| Older task history | `SESSION_LOG_ARCHIVE.md` | Prior checkpoints needed to explain a decision |
| Detailed references | `00_Resources/` | Checklists and source material loaded when relevant |
| Finished projects | `Archive/` | Inactive work kept outside the active route |

The project handoff is the working record. It should point to the facts that explain a decision instead of copying them into several summaries. A dated fact changes at its owning location; the handoff records that a change happened and what to do next.

A timestamp helps identify the intended current entry, but it is not proof that a statement is correct. Confirm a disputed fact against its source. An old archived decision should not silently override the current project record.

## Scope instructions by responsibility

Instructions form a branch: workspace, Area, then project. An Area holds the context shared by a body of work; a project holds the exceptions and details for one outcome. The fictional exhibit branch uses:

```text
example/AGENTS.md
  Areas/Exhibit Projects/AGENTS.md
    Poster Display/AGENTS.md
```

Keep a shared instruction at the narrowest level that owns it. A project-specific rule should not be duplicated in the workspace root. Real agent hosts vary in how they discover nested instruction files, so the walkthrough makes the reading order explicit. These documents are guidance, not a sandbox or an access-control system.

## Make the route inspectable

The [example workspace manifest](../example/workspace.json) names two routes, `poster-display` and `workshop-kit`. A reader selects a route explicitly. Its declared context identifies the files needed to resume that branch. The checker reports this list deterministically; it does not infer a route from natural language or decide which facts matter.

The workshop branch makes the boundary visible: choosing the poster-display route does not require reading workshop task state. A reference outside the declared context remains available when an instruction or question calls for it. The manifest is a demonstration contract, not a log of everything a model actually received.

![Workspace routing and scoped context](../diagrams/context-routing.svg)

## Checkpoint work where it belongs

At a useful stopping point, update the owning handoff with the completed work, unresolved decision and next action. If a durable fact changed, update its memory entry as well. Keep the deeper explanation in a linked reference or archive rather than expanding the current handoff indefinitely.

A later session follows the same route, reads the handoff and verifies its starting state. Resume is an action taken by the reader or agent. The existence of a handoff does not prove that anyone read it.

![Work, checkpoint and resume lifecycle](../diagrams/session-lifecycle.svg)

Only one writer should update a given handoff at a time. Plain Markdown files do not merge simultaneous decisions or lock another editor out. Version control can help inspect and recover changes, but the workflow still needs coordination.

## What validation establishes

The [read-only checker](../scripts/check_workspace.py) validates the declared example structure and reports the selected context with file sizes. Its tests exercise the supported checks and failure cases. Byte counts describe files; they are not measured token use, cost savings or proof of better answers.

The [walkthrough](walkthrough.md) supplies a separate human check: after reading the selected files, can you state the current decision and precise next action without searching unrelated projects? That question tests whether the notes are useful. A structural pass alone cannot answer it.

See [evolution and tradeoffs](evolution-and-tradeoffs.md) for the design rationale and limits.
