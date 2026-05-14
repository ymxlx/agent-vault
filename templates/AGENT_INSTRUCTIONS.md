# Agent Vault Protocol: Multi-Agent Coordination via a Shared Markdown Folder

You are an AI agent working in a shared vault alongside other agents. Possibly Claude, possibly Codex, possibly Gemini CLI, possibly all three. This file is the canonical protocol you and they all follow. Read it once at the start of every session, then act according to it.

## The core idea

The folder `_multi-agent/` inside this vault is a **blackboard**: a persistent shared memory that every agent reads from and writes to. There is no central coordinator. The protocol is the coordinator.

Every agent does the same four things, in the same order, every session:

1. Reads the canonical state on entry.
2. Picks up where things left off.
3. Posts a single line to a shared, append-only log after each meaningful action.
4. Writes detailed work to its own private namespace inside `_multi-agent/`.

This works because markdown files on disk are the most portable substrate possible: any tool that can read and write text can participate. Per-agent write namespaces plus an append-only shared log make the protocol survive both local-filesystem and cloud-synced setups (git, Obsidian Sync, Dropbox) without any locking server.

## Vault structure

```
<vault-root>/
├── CLAUDE.md / AGENTS.md / GEMINI.md    (entry pointers, generated)
├── .agents/skills/agent-vault/          (Codex-format skill copy, generated)
├── _multi-agent/
│   ├── AGENT_INSTRUCTIONS.md            (this file: the canonical protocol)
│   ├── README.md                        (human-facing explainer)
│   ├── index.md                         (canonical "where things stand" page)
│   ├── events.md                        (append-only chronological log)
│   ├── agents/<agent-id>/
│   │   ├── profile.md                   (role, capabilities)
│   │   ├── status.md                    (current task and blockers)
│   │   ├── inbox.md                     (messages from other agents)
│   │   └── log.md                       (private journal)
│   ├── tasks/<task-slug>.md             (one task per file, one owner each)
│   ├── decisions/YYYY-MM-DD-<slug>.md   (decision records)
│   └── handoffs/YYYY-MM-DD-HHMM-<from>-to-<to>.md
└── <project content folders>            (untouched by the protocol)
```

Project files live outside `_multi-agent/`, in whatever organization the project needs. Agents link to them from event entries and task notes using standard `[[path/to/note]]` wikilinks.

## Entry routine (every session, before any work)

1. **Confirm the protocol exists.** `_multi-agent/` should be at the vault root. If it is missing, run the bootstrap (`scripts/init_vault.py` or follow the file templates manually).
2. **Identify yourself.** Decide which agent ID applies to this session. If you have not yet been registered, see "Registering a new agent" below.
3. **Read `_multi-agent/index.md`.** This is the canonical "where things stand" page.
4. **Read your own inbox.** `_multi-agent/agents/<self>/inbox.md`.
5. **Scan the tail of `events.md`.** Read backward from the end until you reach the timestamp recorded in your `status.md` under `last_seen_event:`. That is your catch-up.
6. **Read tasks you own.** Any file under `_multi-agent/tasks/` with `owner: <self>` in its frontmatter.
7. **Update your status.** Set `last_active` to now, `last_seen_event` to the timestamp of the most recent event you just processed, and `state` to whatever describes the session.
8. **Report back to the user.** Especially when joining mid-flight, send a short summary: what the project state is, what is in flight, what wants user input now, and a concrete suggestion for the first move. Without this, the entry routine is invisible to the human.

## Recording what you did

After each meaningful action, append one line to `_multi-agent/events.md`. Format is rigid so other agents and scripts can parse it reliably:

```
- YYYY-MM-DD HH:MM | <agent-id> | <verb-phrase> | [[<wikilink>]] | <note or - >
```

Examples:

```
- 2026-05-13 14:22 | claude-research-pesaj | drafted outline | [[tasks/literature-review]] | 12 sources, 8 confirmed
- 2026-05-13 14:25 | codex-frontend-pesaj | merged auth refactor | [[tasks/jwt-rotation]] | tests passing
- 2026-05-13 14:40 | gemini-translator-pesaj | blocked on terminology | [[tasks/spanish-rollout]] | need decision on madrij vs leader
```

A "meaningful action" is anything another agent might need to know about: a file created or substantially edited, a task picked up or completed, a decision recorded, a blocker hit, a handoff started or finished. Tiny edits, internal reasoning, and false starts stay in your own `log.md` and never reach `events.md`. The signal-to-noise ratio of the shared log is the single most important thing to protect.

### Reserved verb phrases

Use these consistently when they apply; free-form verbs are fine otherwise.

- `joined vault`: agent registration.
- `left vault`: agent retirement.
- `took ownership`: claimed a task.
- `closed task`: marked a task done.
- `blocked on <something>`: cannot proceed.
- `unblocked`: resumed after being blocked.
- `decided <slug>`: recorded a decision; wikilink should point to the decision note.
- `assumed index keeper` / `released index keeper`: index-keeper role transitions.

## Concurrency rules

1. **Only write to files you own.** Your own `agents/<self>/` folder, plus task files where your ID is in `owner:`, plus appends to `events.md` and to other agents' inboxes. Never edit `index.md` unless you are the index keeper for this session.

2. **Appends are safe, in-place edits are dangerous.** When adding to `events.md` or an inbox, always add a new line at the very bottom. Never rewrite or reorder earlier lines. If a sync conflict produces two competing versions of an append-only file, the correct resolution is the union of all lines, re-sorted by timestamp.

3. **Task ownership is exclusive at any moment.** A task's frontmatter has an `owner:` field. Only the listed owner edits the body. To transfer ownership, file a handoff note and update both agents' `status.md` files.

4. **The index is touched rarely.** Updating `index.md` is like merging to a main branch. Do it when a meaningful unit of work is complete. The "index keeper" role rotates; transitions go through the reserved `assumed index keeper` / `released index keeper` events.

In one heuristic: **if you find yourself wanting to edit something another agent might also want to edit, write to your own log instead and link to it from an event line.**

## Registering a new agent

If `_multi-agent/agents/<self>/` does not exist for the agent ID this session uses, you need to register before doing any work.

**Before creating files, confirm the agent ID with the user** if it has not been specified. Renaming after registration is awkward because every event line ever written under the old ID will continue to reference it. A good prompt: "I am about to register a new agent in this vault. What role does this session cover, and what agent ID should I use?"

Naming conventions for agent IDs: lowercase ASCII, hyphens, format `<tool>-<role>-<project>`. Examples: `claude-research-pesaj`, `codex-frontend-pesaj`, `gemini-translator-pesaj`. Length 3 to 40 characters. The tool prefix is important because it lets other agents see at a glance which tool produced each event line, which helps with routing decisions.

To register, create the four standard files in `_multi-agent/agents/<agent-id>/`: `profile.md`, `status.md`, `inbox.md`, `log.md`. Use the templates in `_multi-agent/README.md` or in the skill's `references/templates.md`. Then append a registration event line:

```
- YYYY-MM-DD HH:MM | <agent-id> | joined vault | [[agents/<agent-id>/profile]] | role: <short description>
```

## Handoffs

When one agent finishes work and another should pick up, the handoff is a small ceremony with redundancy by design, because handoffs are where information is most likely to be lost.

1. Create `_multi-agent/handoffs/YYYY-MM-DD-HHMM-<from>-to-<to>.md` with these sections: what's done, what's next, where the state lives (wikilinks), known issues, and a recommended first step.
2. Update the task's `owner:` field to the new agent.
3. Leave a one-line pointer in the new owner's `inbox.md` linking to the handoff note.
4. Append a handoff event line to `events.md`.

Handoffs are also where cross-tool routing happens. If a research agent (claude) finishes its part and the next step is heavy code editing, the natural recipient is a codex agent. The handoff note should explicitly name the agent ID, not just the tool, so the routing is unambiguous.

## Decisions

When a choice is made that future agents will need to understand (architecture, scope, naming, vocabulary), record it as a decision note. The format is the lightweight ADR pattern: context, options considered, choice, consequences. File under `_multi-agent/decisions/YYYY-MM-DD-<slug>.md` and link from the relevant task. Post a `decided <slug>` event line.

Decisions are immutable in spirit. If a decision turns out to be wrong, write a new decision that supersedes the old one. Set the old decision's `status:` to `superseded` and add a `superseded_by:` pointer; do not rewrite the body.

## Granularity (what goes in events.md vs your own log.md)

Over-logging is the most common failure mode. Calibration:

| Action | events.md? | own log.md? |
|---|---|---|
| Fixed a typo in a draft | No | Optional |
| Refactored a function, no behavior change | No | Yes |
| Refactored and changed a public interface | Yes | Yes |
| Read background material to orient | No | Yes |
| Drafted a new section of a deliverable | Yes | Yes |
| Spent 20 minutes stuck and recovered | No | Yes |
| Hit a real blocker that needs another agent | Yes (with `blocked on` verb) | Yes |
| Decided between two approaches | Yes (with link to decision note) | Yes |
| Took ownership of a task | Yes | Yes |

When in doubt, ask: would another agent waste time, duplicate work, or be confused tomorrow if I do not post this? If yes, post it.

## Tool-specific notes

The protocol is identical across tools. A few practical notes:

- **Claude (Claude Code, claude.ai with skills):** The skill called `agent-vault` provides the full protocol description plus the bootstrap script and references. Loading it before working in a vault gives Claude the same instructions you are reading now. The entry pointer is `CLAUDE.md` at the vault root.

- **Codex:** Codex reads `AGENTS.md` at the project root, and also reads skills from `.agents/skills/` directories. Both are present in a properly bootstrapped vault. The skill ships in `.agents/skills/agent-vault/` so Codex can trigger it implicitly.

- **Gemini CLI:** Gemini CLI reads `GEMINI.md` at the project root and walks up the tree. Gemini has no skill system, so it relies entirely on the entry pointer plus this canonical instructions file.

If you are operating under any other tool, the rule of thumb is the same: find the convention that tool uses for an instructions file at the project root, point it at this `AGENT_INSTRUCTIONS.md`, and follow the protocol.

## Failure modes

The full troubleshooting guide is in the skill's `references/troubleshooting.md`. The most common cases in brief:

- **Sync conflict on `events.md`**: take the union of lines from both versions, sort by timestamp, write back. Post a `resolved events conflict` event line.
- **Agent gone silent**: check its last event and `status.md`. If past the project's stale threshold (default 48 hours), file a decision note transferring ownership, then proceed.
- **Duplicate work**: compare outputs, pick or merge, file a decision note explaining the cause, post an event line.
- **Sync conflict on a task body**: read both versions, resolve in a new decision note that records what was chosen and why, then write the merged task file.

## Project content lives outside `_multi-agent/`

The protocol is for coordination, not for the actual deliverables. Put code, drafts, references, source materials, and anything else the project produces in normal folders at the vault root. Link to them from task files and event lines via wikilinks. Keep `_multi-agent/` lean.
