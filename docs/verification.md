# Verification

The local public edition was checked with Python 3.12 on macOS. The implementation targets Python 3.10 or later, but this review does not establish coverage across every supported Python version or operating system.

## Structural checks

Fifteen regression tests pass. They exercise the useful boundaries rather than treating a successful example as sufficient:

- Required current-state files and schema validation, including duplicate JSON keys.
- Explicit route selection, ordered context paths and exact UTF-8 byte counts.
- Unknown routes, path traversal and symbolic-link failures.
- Broken local links, including a broken link in an unselected branch.
- Execution from a different working directory.
- An unchanged example tree after validation.

The checker audits structure across the workspace even when one route is selected. The returned context list includes only that route's scoped records and declared references. It does not validate heading fragments, HTML links, the complete Markdown grammar or the meaning of a note. External links are not fetched.

Both fictional routes and the no-route structural audit pass. The poster route selects nine context files; the workshop route selects five. Their different file lists demonstrate declared separation, not an observation of an AI host's actual prompt contents.

Run the checks yourself:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_workspace.py --route poster-display --json
python3 scripts/check_workspace.py --route workshop-kit --json
python3 scripts/check_workspace.py
```

## Fresh-reader exercise

An independent reader received only the route configuration and the selected fictional files, without the guide, project archive or unrelated branch. The reader recovered the current layout decision and next action, found the included proofreading issue, and identified the project artifact and handoff as the records that would need updating. It did not claim that editing, final approval or installation had happened.

This is one manual resume exercise, not a universal reasoning benchmark. Separate poster artwork is not included, so matching captions against physical posters remains outside that exercise. The shipped files stay at the starting checkpoint so another reader can repeat it.

## What remains outside these checks

Structure does not establish truth, freshness, privacy or compliance. The checker cannot resolve concurrent edits or force an agent to read the intended context. It assumes a trusted, stationary workspace and is not a sandbox against hostile filesystem changes. Windows-specific behavior, automatic instruction discovery and real-workspace recovery are not established by this fictional fixture.
