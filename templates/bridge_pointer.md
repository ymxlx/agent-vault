# Agent Vault Project

This vault uses the **agent-vault protocol** for coordination between multiple AI agents (possibly Claude, Codex, Gemini CLI, or others) working on the same project.

## Required reading before any work

Read [`_multi-agent/AGENT_INSTRUCTIONS.md`](_multi-agent/AGENT_INSTRUCTIONS.md). It is the canonical, tool-agnostic protocol description. Every agent follows the same routine and the same file formats.

## Quick orientation

- Canonical "where things stand" page: [`_multi-agent/index.md`](_multi-agent/index.md)
- Shared event log: [`_multi-agent/events.md`](_multi-agent/events.md)
- Registered agents: [`_multi-agent/agents/`](_multi-agent/agents/)
- Current tasks: [`_multi-agent/tasks/`](_multi-agent/tasks/)

## Entry routine (summary)

1. Confirm `_multi-agent/` exists at the vault root. If not, bootstrap with the included `scripts/init_vault.py`.
2. Identify your agent ID for this session. If you have not been registered yet, register before doing any work.
3. Read `index.md`, your own inbox, the tail of `events.md`, and any task you own.
4. Update your `status.md`.
5. Report back to the user with a short catch-up before starting work.

Full details in `_multi-agent/AGENT_INSTRUCTIONS.md`.

## Naming conventions

Agent IDs follow the pattern `<tool>-<role>-<project>`, e.g. `claude-research-pesaj`, `codex-frontend-pesaj`, `gemini-translator-pesaj`. This makes it visible at a glance which tool produced each event line in the shared log.

## If you are a human reading this

You probably want to start with `_multi-agent/index.md` for the project's current state, then read the tail of `_multi-agent/events.md` for recent activity. This file is mainly a pointer for AI agents that look at the project root before doing anything.
