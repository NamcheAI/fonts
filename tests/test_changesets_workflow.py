#!/usr/bin/env python3
"""Pin the Changesets CLI/action compatibility that completes releases."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ChangesetsWorkflowTest(unittest.TestCase):
    def test_cli_v3_uses_action_v2_inputs(self) -> None:
        package = json.loads((ROOT / "packages/next/package.json").read_text())
        cli_spec = package["devDependencies"]["@changesets/cli"]
        cli_major_match = re.search(r"(\d+)", cli_spec)
        self.assertIsNotNone(cli_major_match)
        cli_major = int(cli_major_match.group(1))

        workflow = (ROOT / ".github/workflows/ci.yaml").read_text()
        step_match = re.search(
            r"      - name: Create Release Pull Request or Publish\n"
            r"(?P<step>.*?)(?=      - name: Upload font zip to GitHub Release)",
            workflow,
            re.DOTALL,
        )
        self.assertIsNotNone(step_match)
        step = step_match.group("step")

        action_match = re.search(r"uses: changesets/action@v(\d+)", step)
        self.assertIsNotNone(action_match)
        action_major = int(action_match.group(1))
        self.assertEqual(
            action_major,
            cli_major - 1,
            "Changesets CLI v3 requires changesets/action v2",
        )

        for required_input in (
            "publish-script:",
            "version-script:",
            "pr-title:",
            "commit-message:",
            "github-token:",
        ):
            self.assertIn(required_input, step)

        for legacy_input in ("publish", "version", "title", "commitMode"):
            self.assertIsNone(
                re.search(rf"^          {legacy_input}:", step, re.MULTILINE),
                legacy_input,
            )

        self.assertIn("steps.changesets.outputs.published == 'true'", workflow)


if __name__ == "__main__":
    unittest.main()
