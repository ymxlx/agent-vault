# File Templates

Copy-paste templates for every file the protocol uses. Replace anything in angle brackets `<like-this>`. Anything in curly brackets `{like this}` is an annotation, not literal content.

## Template: `_multi-agent/README.md`

```markdown
# Multi-Agent Coordination Folder

This folder is a coordination layer for AI agents working on this vault. It is not for human consumption in the normal flow, but humans are welcome to read along.

## What is in here

- `index.md`: the canonical "where things stand" page. Read this first.
- `events.md`: an append-only log of everything notable that any agent has done.
- `agents/`: one folder per registered agent, containing its profile, current status, inbox, and private journal.
- `tasks/`: one file per task, owned by exactly one agent at a time.
- `decisions/`: lightweight decision records, dated.
- `handoffs/`: notes from one agent passing work to another, dated.

## How agents use this

Every agent reads `index.md` and its own inbox at the start of every session, posts a single line to `events.md` after each meaningful action, and updates its own status when it picks up or drops a task. Detailed work happens in project folders elsewhere in the vault.

## How to read along as a human

Start with `index.md` for the current state, then read the tail of `events.md` for recent activity. Drill into any task file or decision note that interests you.
```

## Template: `_multi-agent/index.md`

```markdown
---
last_updated: <YYYY-MM-DD HH:MM:SS>
index_keeper: <agent-id>
project_name: <project name>
project_started: <YYYY-MM-DD>
---

# <Project Name>

## Project summary

<Two or three sentences describing what this project is, who it is for, and what the deliverable looks like.>

## Current focus

- [[tasks/<task-slug>]]: <one-line description, owner>
- [[tasks/<task-slug>]]: <one-line description, owner>

## Agents and roles

- `<agent-id-1>`: <one-line description of role>
- `<agent-id-2>`: <one-line description of role>

## Open decisions

- [[decisions/<YYYY-MM-DD-slug>]]: <one-line summary>

## Stale or blocked

- [[tasks/<task-slug>]]: blocked since <date>, reason: <reason>
```

## Template: `_multi-agent/events.md`

When initializing, the file starts with frontmatter and a single seed line:

```markdown
---
file_type: events
rollover_policy: quarterly
current_period: <YYYY-Qn>
---

- <YYYY-MM-DD HH:MM> | <bootstrap-agent-id> | initialized vault | - | first commit of multi-agent protocol
```

After that, every line is appended at the bottom, in this format:

```
- YYYY-MM-DD HH:MM | <agent-id> | <verb-phrase> | [[<wikilink>]] | <one-line note or - >
```

## Template: `_multi-agent/agents/<agent-id>/profile.md`

```markdown
---
agent_id: <agent-id>
model: <model identifier, e.g. claude-opus-4-7>
tool: <claude.ai web | claude code | cursor | other>
role: <short role description>
languages: [<lang>, <lang>]
registered: <YYYY-MM-DD HH:MM:SS>
---

# Profile: <agent-id>

## Role

<A paragraph describing what this agent is responsible for on this project.>

## Strengths

<A short paragraph or list. What does this agent do well? When should other agents route work here?>

## Limitations

<A short paragraph or list. What does this agent struggle with? When should work be routed elsewhere?>

## Standing instructions

<Any persistent preferences or constraints this agent should always honor. Used by the agent's future sessions as a self-reminder.>
```

## Template: `_multi-agent/agents/<agent-id>/status.md`

```markdown
---
agent_id: <agent-id>
last_active: <YYYY-MM-DD HH:MM:SS>
state: idle
current_task: null
blockers: []
last_seen_event: <YYYY-MM-DD HH:MM>
---

# Status: <agent-id>

<Optional one or two sentence note about what is in progress. Updated by this agent only.>
```

## Template: `_multi-agent/agents/<agent-id>/inbox.md`

When initializing, the file starts empty after the frontmatter:

```markdown
---
file_type: inbox
owner: <agent-id>
---

<!-- Messages from other agents appear below, newest at the bottom. -->
```

Each message follows this format, appended at the bottom:

```markdown

### <YYYY-MM-DD HH:MM> from <sender-agent-id>

<Short message body. One paragraph is ideal; long context belongs in a task file or decision note.>

<Optional wikilink to context: [[<path>]]>

---
```

The `---` at the end is a horizontal rule that separates messages visually.

## Template: `_multi-agent/agents/<agent-id>/log.md`

```markdown
---
file_type: log
owner: <agent-id>
---

# Private log: <agent-id>

<!-- Use this file for reasoning traces, half-formed ideas, false starts, and anything that would be noise in events.md. Audience: future instances of this same agent. -->

## <YYYY-MM-DD>

<Free-form notes, organized however the agent prefers.>
```

## Template: `_multi-agent/tasks/<task-slug>.md`

```markdown
---
task_id: <task-slug>
title: <Human-readable task title>
owner: <agent-id>
status: proposed
created: <YYYY-MM-DD HH:MM:SS>
due: <YYYY-MM-DD or null>
links: []
---

# <Task title>

## Goal

<One paragraph: what does "done" look like for this task?>

## Current state

<Updated by the owner as work progresses. The single source of truth on this task's status. One paragraph or a short list.>

## Open questions

- <Question 1>
- <Question 2>

## Work log

<Narrative of what's been done. Less granular than the agent's own log.md. Append entries with timestamps as work happens.>

### <YYYY-MM-DD HH:MM>

<What was done, with wikilinks to outputs.>

## Handoff history

<If ownership has changed, list each transfer here. One line per transfer.>

- <YYYY-MM-DD>: <from-agent-id> -> <to-agent-id>, reason: <short reason>
```

## Template: `_multi-agent/decisions/YYYY-MM-DD-<slug>.md`

```markdown
---
decision_id: <YYYY-MM-DD-slug>
title: <Short decision title>
decided_by: <agent-id>
decided_on: <YYYY-MM-DD>
affects_tasks: [<tasks/task-slug>, ...]
status: accepted
---

# <Decision title>

## Context

<What was the situation that required a decision? One or two paragraphs.>

## Options considered

1. **<Option 1>**: <one-line description>. Pros: <list>. Cons: <list>.
2. **<Option 2>**: <one-line description>. Pros: <list>. Cons: <list>.

## Choice

<Which option was picked and why. One paragraph.>

## Consequences

<What changes as a result? What is now committed? What is now harder? One or two paragraphs or a list.>
```

## Template: `_multi-agent/handoffs/YYYY-MM-DD-HHMM-<from>-to-<to>.md`

```markdown
---
handoff_id: <YYYY-MM-DD-HHMM-from-to>
from: <from-agent-id>
to: <to-agent-id>
task: <tasks/task-slug>
date: <YYYY-MM-DD HH:MM:SS>
---

# Handoff: <task title>

## What's done

- <Completed item with [[wikilink]]>
- <Completed item with [[wikilink]]>

## What's next

- <Remaining item, with any specifics the recipient needs>
- <Remaining item>

## Where the state lives

- [[<path>]]: <what is here>
- [[<path>]]: <what is here>

## Known issues and gotchas

- <Issue 1>
- <Issue 2>

## Recommended first step

<One concrete sentence: "Start by reading X and then doing Y.">
```

## A note on filling templates

When an agent fills these templates, treat the angle-bracket placeholders as required and the bracketed sections as guidance, not as literal content. Empty sections that have no content yet should be deleted, not left as `<...>` placeholders, because future readers will treat unfilled placeholders as in-progress work.
