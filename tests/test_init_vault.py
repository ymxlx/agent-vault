import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "init_vault.py"


class InitVaultTests(unittest.TestCase):
    def run_init(self, vault_root: Path, *extra_args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--vault-root",
                str(vault_root),
                "--agent-id",
                "codex-tester",
                "--project-name",
                "Regression Vault",
                "--tool",
                "unittest",
                "--model",
                "python",
                "--role",
                "test agent",
                *extra_args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_bootstrap_creates_expected_files_and_preserves_existing_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault_root = Path(tmp)

            first = self.run_init(vault_root)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("Created:", first.stdout)

            expected = [
                "_multi-agent/AGENT_INSTRUCTIONS.md",
                "_multi-agent/README.md",
                "_multi-agent/index.md",
                "_multi-agent/events.md",
                "_multi-agent/agents/codex-tester/profile.md",
                "_multi-agent/agents/codex-tester/status.md",
                "_multi-agent/agents/codex-tester/inbox.md",
                "_multi-agent/agents/codex-tester/log.md",
                "CLAUDE.md",
                "AGENTS.md",
                "GEMINI.md",
                ".agents/skills/agent-vault/SKILL.md",
            ]
            for relative_path in expected:
                self.assertTrue((vault_root / relative_path).exists(), relative_path)

            index_path = vault_root / "_multi-agent" / "index.md"
            original_index = index_path.read_text(encoding="utf-8")
            index_path.write_text(original_index + "\nmanual note\n", encoding="utf-8")

            second = self.run_init(vault_root)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("Already existed:", second.stdout)
            self.assertIn("manual note", index_path.read_text(encoding="utf-8"))

    def test_bridge_tools_can_be_limited(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault_root = Path(tmp)

            result = self.run_init(vault_root, "--bridge-tools", "codex", "--no-codex-skill")
            self.assertEqual(result.returncode, 0, result.stderr)

            self.assertTrue((vault_root / "AGENTS.md").exists())
            self.assertFalse((vault_root / "CLAUDE.md").exists())
            self.assertFalse((vault_root / "GEMINI.md").exists())
            self.assertFalse((vault_root / ".agents" / "skills" / "agent-vault" / "SKILL.md").exists())

    def test_invalid_agent_id_exits_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault_root = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--vault-root",
                    str(vault_root),
                    "--agent-id",
                    "BAD",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid agent-id", result.stderr)
            self.assertFalse((vault_root / "_multi-agent").exists())


if __name__ == "__main__":
    unittest.main()
