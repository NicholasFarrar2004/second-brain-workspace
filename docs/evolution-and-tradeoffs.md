# Evolution and tradeoffs

Second Brain is a public example drawn from the design of WorkOS, an earlier personal workspace. The public files are newly written around fictional projects. They demonstrate selected architectural ideas, not the original workspace, its records or its full operating policies.

## Start with the repeated work

The original design problem was duplicated session information and facts that could become stale across several summaries. Repeating the same update at multiple levels made ownership unclear: which file should a later session trust?

The redesign assigned one live handoff to each workstation. Durable facts kept their own dated file, while instructions stayed separate from the session record. That division gives a future reader a place to look for the current state and a different place to look for the reason behind it.

## Organize by shared context

Areas group a body of work with shared context. Projects sit inside an Area when they need those shared instructions and facts. The Area name communicates a responsibility rather than a sequence of steps.

The public exhibit and workshop branches make this distinction concrete. A poster display belongs with exhibit work; a workshop kit has a separate route. These examples were invented for this repository and do not reproduce any private projects.

## Keep one source for each instruction

One canonical instruction at the appropriate level is easier to inspect than several copies that can drift. Longer references sit behind links so the working record can remain readable. The public manifest adds an explicit list of context files for demonstration and static validation.

This structure is not automatic enforcement. An agent may ignore a file, a host may load instructions differently, or a person may choose the wrong route. Clear instructions and checked paths help expose those mistakes; they do not make them impossible.

## Pilot a change before spreading it

The development plan separated design from execution and called for a small pilot and verification before broader changes. That is useful when a change affects how future sessions find information. A template can look complete yet still leave a new reader unable to identify the next action.

For this edition, the testable pilot is the fictional poster-display walkthrough. Its checker covers file structure; a fresh reader checks the meaning of the saved state. The public example does not claim that a successful fixture proves every real workspace can resume reliably.

## Maintain notes during ordinary work

The design favors upkeep at task checkpoints rather than adding a separate recurring maintenance system. A completed decision is a reason to update the handoff. A changed durable fact is a reason to update its owning memory entry. Older detail can leave the active record while remaining available in an archive.

Passive upkeep depends on people or agents actually doing it. A project that nobody touches may still contain outdated notes. There is no scheduled cleanup or automatic freshness service in this repository.

## Limits worth keeping visible

| Choice | Benefit | Cost or limit |
| --- | --- | --- |
| Plain files | Readable without a database or hosted service | Concurrent writers can overwrite one another |
| Scoped context | Makes the intended reading boundary explicit | A relevant dependency may need a separate reference |
| One owning fact | Avoids competing copies | Moving the file can break links |
| Current handoff plus archive | Keeps the next action easy to find | Someone must decide which history to retain |
| Dated entries | Makes changes easier to compare | Dates do not prove truth or settle conflicting sources |
| Read-only validation | Catches supported structural errors without rewriting notes | Does not judge factual accuracy or agent behavior |

No speed, token, productivity or universal-compatibility claim follows from these design choices. The [provenance record](../PROVENANCE.md) distinguishes user direction, AI assistance and new work in this public edition.

## Further reading

The [AGENTS.md convention](https://agents.md/) describes a common format for agent instructions. Anthropic's [context-engineering discussion](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) covers selective retrieval and persistent notes; its [long-running agent harness discussion](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) explains why later sessions need usable progress records. These sources support the general patterns. They are not independent evaluations of this example.
