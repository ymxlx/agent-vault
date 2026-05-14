# Troubleshooting and Recovery

When things go wrong with the vault, refer here. Each section names a failure mode, explains why it happens, and gives a concrete recovery procedure.

## Sync conflict on `events.md`

**Symptom.** Your sync tool produces a file named something like `events (conflict 2026-05-13).md` or `events.md.orig` alongside the real `events.md`. The two files differ in their tails.

**Why.** Two agents appended event lines while offline, then both synced. The sync layer cannot resolve appended lines automatically because it does not know that line order matters less than line preservation.

**Recovery.**

1. Open both files.
2. Verify both have the same frontmatter; if not, take the most recent `last_updated` value.
3. Take the union of all event lines from both files.
4. Sort the union by the timestamp at the start of each line.
5. Write the result back to `events.md`.
6. Delete the conflict file.
7. Post an event line acknowledging the resolution:
   ```
   - YYYY-MM-DD HH:MM | <your-agent-id> | resolved events conflict | - | merged N lines from sync conflict
   ```

## Sync conflict on a task body

**Symptom.** A task file has a conflict copy and the two versions have diverged in the body.

**Why.** Either ownership was unclear and two agents both edited the task, or one agent edited while another's offline session also edited. This is a protocol violation in the first case and an unavoidable race in the second.

**Recovery.**

1. Read both versions carefully.
2. Identify which changes are compatible and which are in tension.
3. Resolve the tensions explicitly in a new decision note (`_multi-agent/decisions/YYYY-MM-DD-<slug>-merge.md`) that records what was chosen and why.
4. Write the merged task file.
5. Delete the conflict copy.
6. If the underlying cause was unclear ownership, add a line to the task's "Handoff history" section noting the ambiguity.
7. Post a `resolved task conflict` event line and link the decision note.

## An agent has gone silent

**Symptom.** An agent's `status.md` shows `state: working`, but its `last_active` timestamp is hours or days old and no recent event lines bear its ID.

**Why.** The session ended without a clean handoff. Possible causes: the human user closed the session, an error occurred, a model rate limit was hit, or the agent simply forgot to update status.

**Recovery.**

1. Check the agent's `log.md` for clues about where it was when it stopped.
2. Read the relevant task file to see what state the work was left in.
3. Decide whether to wait or to take over. The project's "stale threshold" (default 48 hours) is a guide; use judgment.
4. If taking over, file a decision note titled `<YYYY-MM-DD>-takeover-<task-slug>.md` explaining the situation, then update the task's `owner:` field and post a `took ownership` event line.
5. Leave a note in the silent agent's inbox so that if it returns, it understands what happened.

## Duplicate work discovered after the fact

**Symptom.** Two agents independently did substantially the same work, possibly with different results.

**Why.** Either no event line was posted when the first agent started, or the second agent did not run the entry routine before beginning work. The protocol prevents this when followed; the protocol cannot prevent it when skipped.

**Recovery.**

1. Compare the two outputs. Pick the better one or merge them.
2. File a decision note explaining the choice and the cause.
3. Post an event line linking the decision.
4. If the second agent skipped the entry routine, update its `profile.md` to reinforce the protocol; do not blame in the event log.

## Inbox bloat

**Symptom.** An agent's `inbox.md` has grown to hundreds of messages, many of which have been read and acted on, and it is hard to find new ones.

**Why.** No archiving has happened. Inboxes accumulate by design until someone clears them.

**Recovery.**

1. Within the inbox, sweep through and find the boundary between "actioned" and "current."
2. Move actioned messages to `_multi-agent/agents/<agent-id>/inbox-archive.md` (or a dated archive `inbox-2026-Q2.md`).
3. Trim the live `inbox.md` to current messages only.
4. Post an event line: `- ... | maintained inbox | - | archived N old messages`.

The agent itself should do this; do not let another agent edit your inbox.

## The vault is growing too large to read on entry

**Symptom.** `events.md` is thousands of lines long; reading it on entry takes meaningful time.

**Why.** Successful, long-running projects accumulate history. This is the protocol working, not breaking. But it does require maintenance.

**Recovery.**

1. **Quarterly rollover.** At the start of each quarter, the current index keeper renames the current `events.md` to `events-<YYYY>-Q<n>.md` and starts a new empty `events.md` (with the same frontmatter, updated `current_period`). Post an event line in the new file: `... | rolled over events log | [[events-2026-Q1]] | start of 2026-Q2`.

2. **Daily files for very high-volume projects.** If a project averages more than 50 event lines per day, switch from a single `events.md` to a folder `events/YYYY-MM-DD.md` with one file per day. Update the protocol section of `README.md` to note this. Agents reading on entry then load only files newer than their `last_seen_event` date.

3. **Trim resolved tasks.** Tasks with status `done` for more than a quarter can be moved to `_multi-agent/tasks/archive/`. They are still wikilink-reachable for historical reference.

## Two agents both claim to be the index keeper

**Symptom.** Two agents both updated `index.md` near the same time, and the `index_keeper` field oscillates.

**Why.** The "index keeper" role was not handed off explicitly. The role is supposed to rotate, but the rotation needs to be made visible.

**Recovery.**

1. Read both versions and take the union of changes.
2. Choose one agent as the new index keeper. Usually this is whichever agent is most actively coordinating right now.
3. Update `index.md` once, with the chosen `index_keeper`.
4. Post an event line: `... | assumed index keeper | [[index]] | rotated from <previous-keeper>`.
5. Other agents should not update `index.md` without first confirming via inbox that the current keeper is willing to hand off the role.

## A decision turns out to be wrong

**Symptom.** A decision recorded weeks ago is now blocking work, or new information makes it clearly incorrect.

**Why.** Decisions are made with the information available at the time. Sometimes information changes.

**Recovery.**

Decisions are immutable in spirit; never rewrite an accepted decision. Instead:

1. Create a new decision note that supersedes the old one. The new decision's `affects_tasks` should include any task touched by the original.
2. In the new decision's "Context" section, explain what changed since the original decision.
3. Update the old decision's frontmatter: set `status: superseded` and add `superseded_by: <new-decision-id>`.
4. Post an event line referencing the new decision.

This pattern preserves history. An agent reading the old decision still finds it, follows the `superseded_by` pointer, and sees the current state.

## A new agent cannot tell whether to join

**Symptom.** A new agent (or a new instance of an existing agent) is unclear whether to register or to take over an existing registration.

**Why.** The protocol does not enforce one-to-one mapping between humans-running-Claude-Code and registered agents; it leaves this as a project decision.

**Recovery.**

The rule of thumb: register a new agent if the role is meaningfully different. Reuse an existing agent ID if the role is the same and only the session has changed. For example, every claude.ai session that does Pesaj research is the same `claude-research-pesaj` agent; a session that does code generation is a different agent, `claude-code-pesaj`.

When in doubt, write a quick note in the existing agent's `log.md` describing the new session, run the entry routine as that agent, and proceed.

## The protocol itself needs to change

**Symptom.** The project has outgrown some part of the protocol, or the team wants to extend it.

**Why.** The protocol is a starting point, not a rulebook.

**Recovery.**

Treat the protocol as code: change it deliberately. File a decision note titled `<YYYY-MM-DD>-protocol-change-<slug>.md` describing what changes, why, and how existing files are affected. Update the templates and the spec if needed. If existing files need to be migrated to a new format, do it in a single batch and note it in the decision.

## Cross-tool: an agent is not following the protocol

**Symptom.** A session running under Codex or Gemini CLI (or some other non-Claude tool) is writing to the vault without following the entry routine, or producing event lines in the wrong format, or editing files it does not own.

**Why.** Most likely, the tool did not actually load the entry pointer at the project root. Possible causes: the tool's working directory is wrong, the entry file is empty or malformed, the tool has a non-default config that ignores the standard filename, or the tool's hierarchical-instruction system is hitting a parent override that takes precedence.

**Recovery.**

1. Confirm the entry pointer exists at the vault root. The expected files are `AGENTS.md` for Codex, `GEMINI.md` for Gemini CLI, `CLAUDE.md` for Claude Code. If any are missing, re-run `init_vault.py` with `--bridge-tools` set appropriately. The script is idempotent and will not touch other files.

2. Confirm the entry pointer's content is intact (it should reference `_multi-agent/AGENT_INSTRUCTIONS.md`). If a previous edit has stripped it, restore from `templates/bridge_pointer.md`.

3. As a one-time workaround in the current session, ask the user to paste the contents of `_multi-agent/AGENT_INSTRUCTIONS.md` directly into the session. Once the protocol is in context, the tool can follow it like any other.

4. If the misbehavior persists across sessions, file a decision note titled `<YYYY-MM-DD>-tool-bridge-<tool>.md` documenting the workaround needed for that specific tool (e.g., "Codex on this machine requires the protocol to be inlined in the first message"). Other agents reading the vault later will then know what to expect.

## Cross-tool: agent ID conflicts between tools

**Symptom.** Two agents under different tools have ended up with similar or confusable IDs (e.g., `claude-frontend-pesaj` and `claude-frontend-pesaj-v2`, or `frontend-claude` and `claude-frontend`).

**Why.** The naming convention `<tool>-<role>-<project>` was not consistently followed at registration time.

**Recovery.**

Pick the canonical ID and document it. File a decision note pinning the canonical name. Do not rename the agent in old event lines (those are historical and immutable). Going forward, that agent uses the canonical ID. If both agents have been writing in parallel, audit the recent event log and any inboxes to make sure no messages were sent to the wrong ID.

## Cross-tool: a tool writes outside the protocol

**Symptom.** A tool creates files in the vault outside of `_multi-agent/` and outside of normal project content folders. For example, a Codex session creates `TEST.md` or `REQUIREMENTS.md` at the vault root because its default workflow does that.

**Why.** Some agents come with their own conventions baked in. They are not aware of the protocol's preference for keeping the vault root clean.

**Recovery.**

The protocol does not forbid project files at the vault root; it only forbids editing files in `_multi-agent/` outside your namespace. If the rogue files are legitimate project content, leave them in place and link to them from the relevant task. If they are scratch files the tool should have put in its own log, move them to that agent's `log.md` (or a subfolder of `_multi-agent/agents/<self>/`) and update any references. Then update that agent's `profile.md` standing instructions to note that the tool tends to create these files and that they should be redirected.
