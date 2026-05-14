---
name: agent-vault
description: Coordinate multiple AI agents (Claude sessions, Codex, Gemini CLI, or mixed) working on a shared project by treating an Obsidian vault or markdown folder as a persistent blackboard. Use whenever the user wants to set up communication between different agents, establish a shared memory or coordination protocol across agents (including heterogeneous setups mixing Claude with Codex, Gemini, or other tools), design a multi-agent workflow with persistent state, work within an existing vault that uses this protocol, register a new agent in a multi-agent vault, draft handoff or decision notes between agents, or troubleshoot sync conflicts in a shared vault. Also trigger when the user mentions a "shared vault", "agent coordination", "multi-agent project", "agent handoff", "shared scratchpad for agents", "blackboard architecture", "AGENTS.md", "CLAUDE.md", "GEMINI.md", or describes any scenario where several AI agents (regardless of vendor) need to know what each other is doing without manual relay between sessions.
---

# Agent Vault: Multi-Agent Communication via a Shared Obsidian Vault

A protocol that lets independent AI agents coordinate on a long-running project by reading and writing to a shared markdown vault. The vault acts as persistent shared memory: every agent reads context before acting and writes a small annotation after acting.

## The core idea

Treat the vault as a **blackboard**. There is no central coordinator. Every agent:

1. Reads the canonical state on entry.
2. Picks up where things left off.
3. Posts what it did in a shared, append-only log.
4. Writes detailed work to its own private namespace inside the vault.

This works for two reasons. First, markdown files on disk are the most portable substrate possible; any agent that can read and write text can participate, regardless of which model or tool it runs in. Second, by giving each agent its own write namespace and making the one shared file append-only, the protocol survives both local-filesystem and synced setups (git, Obsidian Sync, Dropbox) without any locking server.

## When this skill is active

Activate this skill when the user is doing any of the following:

- Setting up a new multi-agent workspace (creating the vault structure, registering agents, defining roles).
- Joining an existing multi-agent vault (reading current state, catching up, beginning work).
- Recording an action that other agents should know about (file changes, task pickups, decisions, blockers).
- Handing off a task to a different agent.
- Resolving a sync conflict, a stalled agent, or a duplicated effort.
- Designing a new protocol for AI-to-AI coordination where Obsidian or any shared markdown folder is on the table.

If the user describes a scenario that involves multiple agents needing to share state but does not mention Obsidian, this protocol still applies; the vault is just a folder of markdown files plus a `.obsidian/` config.

## Structure of a multi-agent vault

The protocol lives inside a folder called `_multi-agent/` at the vault root. The underscore prefix keeps it at the top of the file tree in Obsidian. The rest of the vault is for project content and is untouched by the protocol.

```
<vault-root>/
├── .obsidian/                               (Obsidian config, untouched)
├── CLAUDE.md / AGENTS.md / GEMINI.md        (cross-tool entry pointers, generated)
├── .agents/skills/agent-vault/SKILL.md      (Codex-format skill copy, generated)
├── _multi-agent/
│   ├── AGENT_INSTRUCTIONS.md                (canonical tool-agnostic protocol)
│   ├── README.md                            (protocol explainer, for humans)
│   ├── index.md                             (canonical project state)
│   ├── events.md                            (append-only chronological log)
│   ├── agents/
│   │   └── <agent-id>/
│   │       ├── profile.md                   (role, capabilities, contact)
│   │       ├── status.md                    (current task and blockers)
│   │       ├── inbox.md                     (messages from other agents)
│   │       └── log.md                       (private journal)
│   ├── tasks/
│   │   └── <task-slug>.md                   (one file per task, owned by one agent)
│   ├── decisions/
│   │   └── YYYY-MM-DD-<slug>.md             (decisions worth referencing)
│   └── handoffs/
│       └── YYYY-MM-DD-HHMM-<from>-to-<to>.md
└── <project content folders>                (untouched by the protocol)
```

Project files (code, drafts, references) live outside `_multi-agent/`, in whatever organization the project needs. Agents link to them from event entries and task notes using standard Obsidian wikilinks (`[[path/to/note]]`).

## The first thing to do every session

Before touching any project file, an agent runs the entry routine, in this order:

1. **Check that the protocol exists.** Look for `_multi-agent/` at the vault root. If it does not exist, scaffold it (see "Bootstrapping").
2. **Check that this agent is registered.** Look for `_multi-agent/agents/<self>/`. If it does not exist, register (see "Registering an agent").
3. **Read `_multi-agent/index.md`.** This is the canonical "where things stand" page. It should be short enough to read in seconds.
4. **Read your own inbox.** `_multi-agent/agents/<self>/inbox.md` contains anything other agents left for you.
5. **Scan the tail of `events.md`.** Read backward from the end until you reach a timestamp you have already seen (recorded in your own `status.md` under `last_seen_event:`). This is your catch-up. If you are a brand new agent that just registered into a long-running project, your `last_seen_event` will be your registration time, which means you will see no prior events; in that case, do a one-time backread of the recent event history (the last week or so) to get context before you start work.
6. **Read tasks you own.** Any file in `_multi-agent/tasks/` with `owner: <self>` in its frontmatter.
7. **Update your `last_seen_event`.** Set it to the timestamp of the most recent event line you just processed. This is how your next session knows where to pick up. Update your `last_active` to now and your `state` to whatever describes the session.
8. **Report back to the user.** Especially when the user asked you to "catch up" or you are joining mid-flight, produce a short summary: what the project state is, what is in flight, what wants your input now, and a concrete suggestion for the first move. Without this, the entry routine is invisible to the human and they have no idea you are ready to work.

After this, you are caught up and can begin work. The whole routine usually takes one or two reads of small files.

## Recording what you did

After each meaningful action, append one line to `_multi-agent/events.md`. The line format is rigid on purpose, so other agents (and scripts) can parse it reliably:

```
- YYYY-MM-DD HH:MM | <agent-id> | <verb-phrase> | [[<wikilink>]] | <optional one-line note>
```

Examples:

```
- 2026-05-13 14:22 | claude-research | drafted outline | [[tasks/literature-review]] | covers 2019-2024, 12 papers
- 2026-05-13 14:25 | claude-code | merged auth refactor | [[tasks/jwt-rotation]] | tests passing, deploy ready
- 2026-05-13 14:40 | gpt-translator | blocked on terminology | [[tasks/spanish-rollout]] | need decision on "madrij" vs "leader"
```

A "meaningful action" is anything another agent might need to know about: a file created or substantially edited, a task picked up or completed, a decision recorded, a blocker hit, a handoff started or finished. Tiny edits, internal reasoning, and false starts stay in your own `log.md` and never reach `events.md`. The signal-to-noise ratio of the shared log is the single most important thing to protect; an unreadable log is worse than no log.

When the action affects a task you own, also update the task file's frontmatter `status:` field and its "Current state" section. When the action affects another agent's task, leave a note in that agent's `inbox.md` instead of editing their task file.

## Concurrency rules

These exist because parallel agents will sometimes touch the vault at the same time, and sync layers vary in how gracefully they merge:

1. **Only write to files you own.** Your own `agents/<self>/` folder, plus task files where your ID is in `owner:`, plus appends to `events.md` and to other agents' `inbox.md` files. Never edit `index.md` unless you are explicitly the index keeper for this session.

2. **Appends are safe, in-place edits are dangerous.** When adding to `events.md` or to an inbox, always add a new line at the very bottom. Never rewrite or reorder earlier lines. If a sync conflict produces two competing versions of an append-only file, the correct resolution is the union of all lines, re-sorted by timestamp.

3. **Task ownership is exclusive at any moment.** A task's frontmatter has an `owner:` field. Only the listed owner edits the body. To transfer ownership, file a handoff note (see "Handoffs") and update both agents' `status.md` files.

4. **The index is touched rarely.** Updating `index.md` is like merging to a main branch. Do it when a meaningful unit of work is complete, and rotate the "index keeper" role explicitly. If two agents both need to update the index, the second one waits for an event entry from the first and then proceeds.

These rules collapse into one heuristic: **if you find yourself wanting to edit something another agent might also want to edit, write to your own log instead and link to it from an event line.**

## Bootstrapping (when `_multi-agent/` does not exist)

### Before running the script

If the user has not specified an agent ID or a role for this first agent, **ask before registering**. Renaming an agent after registration is discouraged because every event line ever written under the old ID will continue to reference it, so a thoughtful ID at the start saves cleanup later. A good prompt to the user is something like: "I am about to register the first agent. What role should it cover, and is there a preferred agent ID (the convention is something like `claude-research-<project>`)?"

If the user describes a multi-agent project but does not say how many agents there will be, do not pre-register agents that have not yet joined. Each agent registers itself on its own first session. The bootstrap establishes the protocol; it does not populate a roster.

### Running the script

Use the bundled init script. It is idempotent (will not overwrite existing files) and produces the canonical structure with all template files populated.

```bash
python scripts/init_vault.py --vault-root <path> --agent-id <name>
```

Arguments:
- `--vault-root` is the absolute path to the Obsidian vault root (the folder containing `.obsidian/`, or any folder if there is no Obsidian config yet).
- `--agent-id` is the identifier this first agent will register under (see naming guidance below).
- Optional but recommended: `--project-name`, `--tool`, `--model`, `--role`.

If a script cannot be run in the current environment (for example, claude.ai web sessions without code execution), follow the templates in `references/templates.md` to create each file manually. The result must be identical.

### After the script finishes

The bootstrap leaves the vault structurally correct but narratively empty. Three things must happen next, in this order:

1. **Update `index.md` with a real project summary.** Replace the placeholder paragraph with two or three sentences that actually describe the project, who it is for, and what the deliverable looks like. Update the "Agents and roles" section to reflect the agents that exist (registered) and the ones that are planned (not yet registered). The index is the first thing every future agent reads; placeholder text there will be copied or referenced and become harder to remove later.

2. **Fill in this agent's own `profile.md`.** Replace the placeholder sections with real descriptions of role, strengths, limitations, and any standing instructions. The profile is how other agents decide whether to hand work to this one.

3. **Tell the human user what was done.** A real cold start needs the agent to report back: where the vault lives, who is registered, who is expected to join later, and what the human needs to do to bring the next agent online (essentially: start the next session, point it at the same vault, and describe its role). Without this, the human has no idea the protocol is ready for use.

Do not seed initial tasks in the bootstrap. Tasks should flow from real work that the user has requested or that an agent has proposed in response to a concrete need. A bootstrap that pre-populates speculative tasks creates work the agents then feel obligated to do.

### Initial value of `last_seen_event`

The init script sets the first agent's `last_seen_event` field to the current timestamp at bootstrap. This means: on this agent's next session, the entry routine will see no prior events to catch up on, which is correct because there have been none. New agents that register into an existing vault later also get `last_seen_event` set to the registration time, so they will read all events from registration forward but not the history before they joined. If a new agent does need to read the back-history (for example, joining a long-running project), it should do that explicitly as a one-time read, not by manipulating `last_seen_event`.

## Registering an agent in an existing vault

If `_multi-agent/` exists but `_multi-agent/agents/<self>/` does not, this is a new agent joining a vault that already has the protocol set up. Two things matter before creating any files.

First, **ask about the agent ID if the user has not specified one**. The same principle that applies in bootstrap applies here: renaming after registration is awkward because old event lines will keep referencing the original ID. A good prompt is: "I am about to register a new agent in this vault. What role does this session cover, and what agent ID should I use? The convention is something like `claude-<role>-<project>`." If the index lists a planned agent that has not registered yet (e.g., a role described as "planned, not yet registered"), it is reasonable to propose that ID; still surface the assumption.

Second, **read `index.md` first to understand the project context** so the role you propose actually fits.

Once you have the ID, create `agents/<agent-id>/` with the four files (profile, status, inbox, log) using the templates in `references/templates.md`. Then append a registration line to `events.md`:

```
- 2026-05-13 14:30 | claude-research-pesaj | joined vault | [[agents/claude-research-pesaj/profile]] | role: research and source-checking
```

The bundled `init_vault.py` script handles this case too: when run with an `--agent-id` that does not yet exist in a vault that already has the protocol, it creates only the new agent's folder and leaves the existing top-level files untouched. The output will note that some files "already existed" (the README, index, and events at the vault top level); that is correct behavior, not an error.

### Naming agent IDs

Use human-readable, stable identifiers. Combine the model family or tool, a role hint, and (if useful) a project slug. Good: `claude-code-frontend`, `claude-research-pesaj`, `gpt-translator-es`, `cursor-refactor`. Bad: `agent-7a3f`, `claude-2026-05-13-14-30`, `helper`.

Avoid renaming agents once registered; old event lines will still reference the original ID.

## Handoffs

When one agent finishes work and a different agent should pick up, the handoff is a small ceremony with redundancy on purpose, because handoffs are where information is most likely to be lost.

1. Create `_multi-agent/handoffs/YYYY-MM-DD-HHMM-<from>-to-<to>.md` using the template in `references/templates.md`. It must include: what's done, what's next, where the state lives (wikilinks), known issues, and a recommended first step for the recipient.
2. Update the task's `owner:` field in its frontmatter to the new agent.
3. Write a one-line pointer in the new owner's `inbox.md` linking to the handoff note.
4. Append a handoff event line to `events.md`.

## Decisions

When a choice is made that future agents will need to understand (architecture call, scope cut, naming convention, vocabulary fix), record it as a decision note. Use the format in `references/templates.md` (it follows the lightweight ADR pattern: context, options considered, choice, consequences). File it under `_multi-agent/decisions/YYYY-MM-DD-<slug>.md`, link from the relevant task, and post an event line.

The point of decisions is not bureaucracy; it is so that an agent joining the project six weeks later can answer "why did we do it this way" without re-litigating.

## Granularity guidance

A common failure mode is over-logging. Some calibration:

| Action | Goes in `events.md`? | Goes in own `log.md`? |
|---|---|---|
| Fixed a typo in a draft | No | Optional |
| Refactored a function, no behavior change | No | Yes |
| Refactored and changed the public interface | Yes | Yes |
| Read background material to orient | No | Yes |
| Drafted a new section of a deliverable | Yes | Yes |
| Spent 20 minutes stuck on something and recovered | No | Yes |
| Hit a real blocker that needs another agent | Yes (with `blocked on` verb) | Yes |
| Decided between two approaches | Yes (with link to decision note) | Yes |
| Took ownership of a task | Yes | Yes |

When in doubt, ask: would another agent waste time, duplicate work, or be confused tomorrow if I do not post this? If yes, post it.

## Failure modes and recovery

A short list of the most common failures; the extended version is in `references/troubleshooting.md`.

- **An agent has gone silent.** Check its `status.md` and the last event line under its name. If the task is blocked, post to its inbox. If the agent is clearly inactive (no events for the project's "stale" threshold; default 48 hours), file a decision note transferring ownership, then proceed.

- **Two agents both wrote to the same task body.** Recoverable. Take the union of changes, re-resolve in the task file, post a decision note explaining the merge. Treat as a learning moment: ownership was unclear.

- **Sync produced a conflict file.** Most sync tools name these something like `events (conflict 2026-05-13).md`. Open both, take the union of lines, re-sort by timestamp, delete the conflict copy. For non-append-only files (task bodies, the index), do a manual merge and post a decision note.

- **The vault is growing too large to read on entry.** Roll over `events.md` quarterly into `events-YYYY-Qn.md` archives; keep only the current quarter live. Same for inboxes: archive read messages into `inbox-archive.md`. For very high-traffic projects, switch to daily event files (`events/2026-05-13.md`) and have agents read only files newer than their `last_seen_event`.

## Working alongside non-Claude agents

The protocol is tool-agnostic. The same vault can be shared between Claude (this skill), Codex, Gemini CLI, and any other tool that reads markdown. What differs is **how each tool discovers the protocol on entry**, and the bootstrap handles that automatically.

### What the bootstrap writes for cross-tool support

By default, `init_vault.py` writes four extra files in addition to the `_multi-agent/` structure:

- `<vault-root>/CLAUDE.md`: an entry pointer Claude Code reads at the project root.
- `<vault-root>/AGENTS.md`: an entry pointer Codex reads (also the format recognized by Jules, Aider, goose, opencode, Zed, Warp, VS Code, and Devin).
- `<vault-root>/GEMINI.md`: an entry pointer Gemini CLI reads.
- `<vault-root>/.agents/skills/agent-vault/SKILL.md`: a Codex-format skill copy, so Codex can trigger the protocol implicitly the way Claude does via this skill.

All four point to the same canonical file: `_multi-agent/AGENT_INSTRUCTIONS.md`. Updating the protocol means editing that one file; the pointers do not need to change.

To control which entry pointers are written, pass `--bridge-tools claude,codex,gemini` (the default) or a subset. To skip the Codex skill copy, pass `--no-codex-skill`. Both options are documented in the script's `--help`.

### Agent IDs encode the tool

The naming convention `<tool>-<role>-<project>` (for example `claude-research-pesaj`, `codex-frontend-pesaj`, `gemini-translator-pesaj`) is now load-bearing. The tool prefix is what lets any agent reading `events.md` see at a glance which tool produced which event, and decide where to route handoffs based on real fit (Codex tends to be the right recipient for heavy code edits; Claude or Gemini for research, writing, and translation work).

### What Claude specifically should do

When you (Claude) are working in a vault that already has CLAUDE.md, AGENTS.md, or GEMINI.md at the root, treat them as a strong signal that the protocol is in use. Do not edit those entry files; they are stable pointers. The canonical instructions in `_multi-agent/AGENT_INSTRUCTIONS.md` are also stable, and they say essentially the same thing this SKILL.md does. Loading this skill into your context is equivalent to reading that file; the protocol is the same.

When other agents leave you tasks or messages, you will see their IDs (`codex-...`, `gemini-...`) in `events.md`, in task `owner:` fields, and in inbox sender lines. Treat them as peers: their profiles describe what they do well, and a thoughtful handoff to one of them is just as valid as a handoff to another Claude session.

If you find an agent in the vault whose tool you do not recognize, do not assume malice or error; check its `profile.md` first.

### When a tool ignores its entry file

Some tools or some configurations will not actually pick up the entry pointer on session start. If you are working with a user whose tool is not following the protocol, the practical workaround is to inline the protocol: at the start of the user's first message to that tool in a fresh session, have them paste the contents of `_multi-agent/AGENT_INSTRUCTIONS.md` directly. Once the protocol is in context, the tool can follow it like any other.

## References

For deeper detail, consult these files (each is short and focused):

- `references/protocol-spec.md` for the full schema: every frontmatter field, every file format, naming conventions, and the exact event line grammar.
- `references/templates.md` for copy-paste templates of every file the protocol uses, with annotations.
- `references/troubleshooting.md` for extended failure modes, recovery procedures, and scaling guidance.
- `templates/AGENT_INSTRUCTIONS.md` for the tool-agnostic canonical protocol that gets written into each vault on bootstrap. If you ever need to refresh or fix an existing vault's instructions file, this is the source of truth.

Read the spec when you need to validate a file format. Read the templates when bootstrapping or registering. Read the troubleshooting reference when something has gone wrong.
