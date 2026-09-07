# Provenance and contribution

Second Brain is a newly authored public demonstration of the architecture used in Nicholas Farrar's personal WorkOS workspace. WorkOS was developed through AI-assisted work, including Claude Cowork desktop. The public edition does not contain that live workspace or its conversation history.

## What comes from the original design

The retained design records support these mechanisms:

- Instructions scoped to the root, an area and a project.
- Durable facts stored at their owning level.
- One current handoff for a workstation, with historical checkpoints kept separately.
- References loaded when a task needs their detail.
- Routing that identifies the relevant workstation before work begins.

The design grew from a need to carry useful context between sessions. Later restructuring addressed duplicated logging and facts that could drift across competing records. Nicholas defined requirements, approved structural changes and pushed for upkeep during ordinary work instead of unnecessary recurring maintenance. Agents helped develop and implement the system. This is a system-design and iterative-development contribution; it is not a claim that every line was independently hand-written.

## What is new in this edition

All templates, fictional projects, example notes, diagrams, route configuration, validator and tests were written for this repository. The explicit `workspace.json` route list and read-only validator make the demonstration reproducible; they are not presented as the original system's production loader.

The public guide generalizes the design. It excludes live instructions, personal memories, private project records, conversation exports, credentials, integrations, organization-specific processes and machine-specific configuration. Example names, dates, measurements and decisions are independently invented, not renamed private records.

The validator's output proves only the checks it performs. The repository does not claim that a previous deployment passed these tests, that every agent host loads instructions identically, or that the design guarantees a particular context budget or productivity gain.

## Related ideas

The design can be understood alongside [AGENTS.md's scoped instruction convention](https://agents.md/), Anthropic's discussion of [context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), and its discussion of [progress records for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents). These explain relevant general patterns; they do not independently validate WorkOS or the example in this repository.

No open-source license has been selected.
