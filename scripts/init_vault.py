#!/usr/bin/env python3
"""
init_vault.py — scaffold a new multi-agent vault.

Creates the canonical _multi-agent/ folder structure inside a vault root, with
all template files populated. Idempotent: if files exist, it warns and skips
rather than overwriting.

Usage:
    python init_vault.py --vault-root <path> --agent-id <name>

Optional arguments:
    --project-name "Pesaj 2027 materials"
    --tool "claude.ai web"
    --model "claude-opus-4-7"
    --role "research and source-checking"
    --bridge-tools "claude,codex,gemini"   # which entry pointers to write at vault root
    --codex-skill / --no-codex-skill        # write .agents/skills/agent-vault/SKILL.md
    --force                                  # overwrite existing files

The bridge pointers (CLAUDE.md, AGENTS.md, GEMINI.md) are short files at the
vault root that point each tool to the canonical _multi-agent/AGENT_INSTRUCTIONS.md.
This lets Claude, Codex, and Gemini CLI all discover and follow the same protocol.
"""

import argparse
import datetime
import re
import sys
from pathlib import Path


AGENT_ID_PATTERN = re.compile(r"^[a-z][a-z0-9\-]{2,39}$")


def validate_agent_id(agent_id: str) -> None:
    if not AGENT_ID_PATTERN.match(agent_id):
        raise SystemExit(
            f"Invalid agent-id '{agent_id}'. "
            "Use lowercase ASCII, digits, and hyphens; start with a letter; "
            "length 3 to 40 characters."
        )


def now_iso(seconds: bool = True) -> str:
    fmt = "%Y-%m-%d %H:%M:%S" if seconds else "%Y-%m-%d %H:%M"
    return datetime.datetime.now(datetime.timezone.utc).strftime(fmt)


def current_quarter() -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    q = (now.month - 1) // 3 + 1
    return f"{now.year}-Q{q}"


# Templates that ship as files in ../templates/ relative to this script.
# We read them at runtime instead of embedding them as Python strings, so
# the canonical instruction file can be edited in plain markdown.
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def load_template(name: str) -> str:
    """Read a template file from the skill's templates/ directory."""
    path = TEMPLATES_DIR / name
    if not path.exists():
        raise SystemExit(
            f"Template not found: {path}. "
            "The skill folder may be incomplete; expected templates/ alongside scripts/."
        )
    return path.read_text(encoding="utf-8")


def write_if_absent(path: Path, content: str, force: bool = False) -> str:
    """Write content to path; return 'created', 'exists', or 'overwritten'."""
    if path.exists() and not force:
        return "exists"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "overwritten" if path.exists() and force else "created"


def readme_content() -> str:
    return """# Multi-Agent Coordination Folder

This folder is a coordination layer for AI agents working on this vault. It is not for human consumption in the normal flow, but humans are welcome to read along.

## What is in here

- `AGENT_INSTRUCTIONS.md`: the canonical, tool-agnostic protocol description. Every agent (Claude, Codex, Gemini CLI, others) reads this first.
- `index.md`: the canonical "where things stand" page. Read this for current state.
- `events.md`: an append-only log of everything notable that any agent has done.
- `agents/`: one folder per registered agent, containing its profile, current status, inbox, and private journal.
- `tasks/`: one file per task, owned by exactly one agent at a time.
- `decisions/`: lightweight decision records, dated.
- `handoffs/`: notes from one agent passing work to another, dated.

## Cross-tool entry points

At the vault root, there may also be `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`. These are short pointer files, one per tool, telling each AI tool how to discover this protocol on session start. They all point back to `AGENT_INSTRUCTIONS.md` in this folder. If the vault is single-tool, only one of these will exist.

For Codex specifically, there may also be a `.agents/skills/agent-vault/` folder at the vault root containing a Codex-format skill copy.

## How agents use this

Every agent reads `index.md` and its own inbox at the start of every session, posts a single line to `events.md` after each meaningful action, and updates its own status when it picks up or drops a task. Detailed work happens in project folders elsewhere in the vault.

## How to read along as a human

Start with `index.md` for the current state, then read the tail of `events.md` for recent activity. Drill into any task file or decision note that interests you.
"""


def index_content(project_name: str, agent_id: str) -> str:
    ts = now_iso()
    today = ts.split(" ")[0]
    return f"""---
last_updated: {ts}
index_keeper: {agent_id}
project_name: {project_name}
project_started: {today}
---

# {project_name}

## Project summary

(Replace with two or three sentences describing what this project is, who it is for, and what the deliverable looks like.)

## Current focus

(No tasks yet. Create one in `tasks/` and link it here.)

## Agents and roles

- `{agent_id}`: (describe role)

## Open decisions

(None yet.)

## Stale or blocked

(None yet.)
"""


def events_content(agent_id: str) -> str:
    short_ts = now_iso(seconds=False)
    quarter = current_quarter()
    return f"""---
file_type: events
rollover_policy: quarterly
current_period: {quarter}
---

- {short_ts} | {agent_id} | initialized vault | - | first commit of multi-agent protocol
"""


def profile_content(agent_id: str, model: str, tool: str, role: str) -> str:
    return f"""---
agent_id: {agent_id}
model: {model}
tool: {tool}
role: {role}
languages: []
registered: {now_iso()}
---

# Profile: {agent_id}

## Role

{role}.

## Strengths

(Describe what this agent does well and when other agents should route work here.)

## Limitations

(Describe what this agent struggles with and when work should be routed elsewhere.)

## Standing instructions

(Any persistent preferences or constraints this agent should always honor.)
"""


def status_content(agent_id: str) -> str:
    short_ts = now_iso(seconds=False)
    return f"""---
agent_id: {agent_id}
last_active: {now_iso()}
state: idle
current_task: null
blockers: []
last_seen_event: {short_ts}
---

# Status: {agent_id}

Just registered. No current task.
"""


def inbox_content(agent_id: str) -> str:
    return f"""---
file_type: inbox
owner: {agent_id}
---

<!-- Messages from other agents appear below, newest at the bottom. -->
"""


def log_content(agent_id: str) -> str:
    today = now_iso().split(" ")[0]
    return f"""---
file_type: log
owner: {agent_id}
---

# Private log: {agent_id}

<!-- Use this file for reasoning traces, half-formed ideas, false starts, and anything that would be noise in events.md. Audience: future instances of this same agent. -->

## {today}

Registered as `{agent_id}` and initialized the vault.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a multi-agent vault under <vault-root>/_multi-agent/."
    )
    parser.add_argument("--vault-root", required=True, type=Path)
    parser.add_argument("--agent-id", required=True, type=str)
    parser.add_argument("--project-name", default="Untitled Project", type=str)
    parser.add_argument("--tool", default="unspecified", type=str)
    parser.add_argument("--model", default="unspecified", type=str)
    parser.add_argument("--role", default="general", type=str)
    parser.add_argument(
        "--bridge-tools",
        default="claude,codex,gemini",
        type=str,
        help=(
            "Comma-separated list of tools to generate entry pointers for at the "
            "vault root. Supported: claude (CLAUDE.md), codex (AGENTS.md), gemini "
            "(GEMINI.md). Pass an empty string to skip all bridges."
        ),
    )
    parser.add_argument(
        "--codex-skill",
        dest="codex_skill",
        action="store_true",
        default=True,
        help="Write a Codex-format SKILL.md at .agents/skills/agent-vault/ (default: on).",
    )
    parser.add_argument(
        "--no-codex-skill",
        dest="codex_skill",
        action="store_false",
        help="Do not write the Codex-format skill copy.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files. Off by default for safety.",
    )
    return parser.parse_args()


BRIDGE_TOOL_FILES = {
    "claude": "CLAUDE.md",
    "codex": "AGENTS.md",
    "gemini": "GEMINI.md",
}


def parse_bridge_tools(raw: str) -> list:
    """Parse the --bridge-tools argument into a list of validated tool names."""
    if not raw.strip():
        return []
    requested = [t.strip().lower() for t in raw.split(",") if t.strip()]
    unknown = [t for t in requested if t not in BRIDGE_TOOL_FILES]
    if unknown:
        raise SystemExit(
            f"Unknown bridge tool(s): {', '.join(unknown)}. "
            f"Supported: {', '.join(sorted(BRIDGE_TOOL_FILES))}."
        )
    # Preserve order, dedupe
    seen = set()
    return [t for t in requested if not (t in seen or seen.add(t))]


def main() -> int:
    args = parse_args()
    validate_agent_id(args.agent_id)
    bridge_tools = parse_bridge_tools(args.bridge_tools)

    vault_root = args.vault_root.expanduser().resolve()
    if not vault_root.exists():
        print(f"Vault root does not exist: {vault_root}", file=sys.stderr)
        print("Create the folder first, then re-run.", file=sys.stderr)
        return 1

    base = vault_root / "_multi-agent"
    agent_dir = base / "agents" / args.agent_id

    files = [
        (base / "AGENT_INSTRUCTIONS.md", load_template("AGENT_INSTRUCTIONS.md")),
        (base / "README.md", readme_content()),
        (base / "index.md", index_content(args.project_name, args.agent_id)),
        (base / "events.md", events_content(args.agent_id)),
        (agent_dir / "profile.md", profile_content(args.agent_id, args.model, args.tool, args.role)),
        (agent_dir / "status.md", status_content(args.agent_id)),
        (agent_dir / "inbox.md", inbox_content(args.agent_id)),
        (agent_dir / "log.md", log_content(args.agent_id)),
    ]

    # Bridge pointers at the vault root, one per requested tool.
    if bridge_tools:
        bridge_content = load_template("bridge_pointer.md")
        for tool in bridge_tools:
            filename = BRIDGE_TOOL_FILES[tool]
            files.append((vault_root / filename, bridge_content))

    # Codex-format skill copy inside the vault.
    if args.codex_skill:
        codex_skill_path = vault_root / ".agents" / "skills" / "agent-vault" / "SKILL.md"
        files.append((codex_skill_path, load_template("codex_skill.md")))

    # Empty container directories
    for d in [base / "tasks", base / "decisions", base / "handoffs"]:
        d.mkdir(parents=True, exist_ok=True)

    summary = {"created": 0, "exists": 0, "overwritten": 0}
    for path, content in files:
        status = write_if_absent(path, content, force=args.force)
        summary[status] = summary.get(status, 0) + 1
        rel = path.relative_to(vault_root)
        print(f"  {status:>11}  {rel}")

    print()
    print(f"Vault root: {vault_root}")
    print(f"Created: {summary['created']}, Already existed: {summary['exists']}, Overwritten: {summary['overwritten']}")

    if bridge_tools:
        print(f"Bridge pointers: {', '.join(BRIDGE_TOOL_FILES[t] for t in bridge_tools)}")
    if args.codex_skill:
        print("Codex skill: .agents/skills/agent-vault/SKILL.md")

    if summary["exists"] > 0 and not args.force:
        print()
        print("Some files already existed and were left untouched.")
        print("This is expected behavior when registering a new agent into an existing")
        print("vault, or re-running the bootstrap. Re-run with --force to overwrite.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
