# Resume the poster-display project

A community exhibit needs four posters arranged on existing boards. The available width changed from an assumed 240 cm to a measured 180 cm. The saved decision is a two-by-two layout, with caption proofreading still pending.

Every project, measurement, date and checkpoint in this example is fictional. The January 12 and 13, 2026 entries demonstrate a sequence of decisions; they are not a current event schedule.

## Select the route

From the repository root, with Python 3.10 or newer:

```sh
python3 scripts/check_workspace.py --route poster-display
```

The checker uses `example/` by default. For machine-readable output:

```sh
python3 scripts/check_workspace.py --route poster-display --json
```

The route is explicit. Typing a sentence about a poster display will not make the checker infer one. The [manifest](../example/workspace.json) declares the route and its references.

A successful result reports `ok: true`, the selected route and a `context` list of relative paths with byte sizes. It also reports `total_context_bytes`. Those values describe the declared files; they do not measure an agent's actual context window or token use.

## Read the selected branch

The route brings together the workspace instructions and facts, the exhibit Area context, the poster-display project context, its current handoff, the display checklist and the four draft captions. Start with the scoped instructions, then read the owning handoff for the task state. Follow its fact and reference pointers to verify the details.

| File | What it answers |
| --- | --- |
| [Workspace instructions](../example/AGENTS.md) | How to use this fictional workspace |
| [Workspace facts](../example/MEMORY.md) | What belongs in the example project catalog |
| [Exhibit instructions](<../example/Areas/Exhibit Projects/AGENTS.md>) | What is shared across exhibit work |
| [Exhibit facts](<../example/Areas/Exhibit Projects/MEMORY.md>) | Which facts belong at the Area level |
| [Poster instructions](<../example/Areas/Exhibit Projects/Poster Display/AGENTS.md>) | What applies specifically to this project |
| [Poster facts](<../example/Areas/Exhibit Projects/Poster Display/MEMORY.md>) | The current width, poster count and reuse decision |
| [Poster handoff](<../example/Areas/Exhibit Projects/Poster Display/Handoff.md>) | The current stage and next action |
| [Display checklist](../example/00_Resources/display-checklist.md) | What to check when preparing the display |
| [Draft captions](<../example/Areas/Exhibit Projects/Poster Display/captions.md>) | The four unapproved captions to proofread |

A reference is loaded because the selected task calls for it. Other projects and archived details are not needed just to resume the current work.

## Explain the current decision

After reading, you should be able to answer:

- The current available width is 180 cm. The 240 cm assumption is superseded.
- The display has four posters, arranged two by two on existing boards.
- The layout is ready. Caption proofreading and approval remain open.
- The next action is to proofread four captions against the display checklist, then prepare an installation checklist. Installation has not happened.

The project memory owns the durable facts. The handoff owns the task state. The [project archive](<../example/Areas/Exhibit Projects/Poster Display/SESSION_LOG_ARCHIVE.md>) explains the older assumption if you need the history; it does not supply the current measurement.

## Try a fresh-session handoff

Give a reader or file-capable agent only the repository and the route ID. Ask them to read the selected context and state the current decision, next action and unresolved approval. Compare their answer with the points above.

This is a reproducible exercise, not a claimed automated reasoning test. The checker verifies structure and links; a reader must verify whether the saved context actually supports the answer. Do not infer that proofreading or approval is complete simply because the plan says what to do next.

For a checkpoint exercise, work in your own copy. Use the linked caption drafts and checklist to perform the pending review. After actually proofreading the fictional captions, update the project's handoff with what was checked and what still needs approval. Keep the 180 cm measurement in its owning memory entry rather than copying it into several project summaries. Do not rewrite workspace instructions to record a one-time result.

## Compare the unrelated branch

```sh
python3 scripts/check_workspace.py --route workshop-kit --json
```

That route concerns six reusable workshop kits with an inventory check pending. Its context should identify the workshop branch rather than the poster-display project. This separation is visible in the declared path lists, not assumed from an agent's behavior.

Run the checker without a route for a structural audit of the example. No route means no selected context list:

```sh
python3 scripts/check_workspace.py
```

Neither command changes a note, performs proofreading or installs anything. See [architecture](architecture.md) for the file model and [tradeoffs](evolution-and-tradeoffs.md) for the limits.
