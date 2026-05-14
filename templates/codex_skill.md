---
name: agent-vault
description: Multi-agent coordination via a shared markdown vault. Trigger when working in a project that contains a `_multi-agent/` folder, when the user mentions agent handoffs, a shared vault, multi-agent project state, or coordination between Codex and other AI tools (Claude, Gemini CLI) on the same project. The protocol uses an append-only event log, per-agent write namespaces, explicit task ownership, and dated decision and handoff notes. Also trigger when the user wants to register a new agent in an existing vault, hand off work to another agent, record a decision, or resolve a sync conflict.
---

# Agent Vault (Codex skill)

You are working in a project that uses the agent-vault protocol for coordination between multiple AI agents. The canonical, tool-agnostic protocol description lives at `_multi-agent/AGENT_INSTRUCTIONS.md` at the project root.

## What to do

1. **Read `_multi-agent/AGENT_INSTRUCTIONS.md` first.** It defines every file format, the entry routine, the concurrency rules, and the granularity guidance. Everything in this skill assumes you have read it.

2. **Run the entry routine before any work.** Identify your agent ID for this session (the convention is `codex-<role>-<project>`, e.g. `codex-frontend-pesaj`), register if not already registered, read `index.md` and your inbox, scan the tail of `events.md`, read tasks you own, update your `status.md`, and report back to the user.

3. **Record meaningful actions in `events.md`.** Append one line per action in the format `- YYYY-MM-DD HH:MM | <agent-id> | <verb-phrase> | [[<wikilink>]] | <note or - >`. Skip trivial edits.

4. **Write detail to your own log, not the shared log.** Reasoning, false starts, and intermediate state belong in `_multi-agent/agents/<self>/log.md`.

5. **Respect ownership.** Only edit task files where your agent ID is in the `owner:` frontmatter field. To transfer ownership, file a handoff note.

6. **Use append-only edits on shared files.** `events.md` and other agents' `inbox.md` files are append-only. Never rewrite earlier lines.

## When you are about to do something the protocol forbids

If you find yourself wanting to edit a file owned by another agent, edit `index.md` without being the index keeper, or rewrite an earlier event line: stop and write to your own log instead, then link to it from a single event line. The protocol's job is to prevent silent conflicts; following it is non-negotiable.

## Cross-tool routing

The vault may also contain agents running under Claude (via the Anthropic skill of the same name) or Gemini CLI. Their event lines will appear in `events.md` with their respective tool prefixes (`claude-...`, `gemini-...`). When deciding whom to hand off to, look at the agent's `profile.md` to understand its role, not just its tool.
