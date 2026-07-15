from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class BridgeIntegrationTests(unittest.TestCase):
    def test_bridge_bootstrap_and_settings_round_trip(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            environment = {
                **os.environ,
                "APPDATA": str(root / "roaming"),
                "LOCALAPPDATA": str(root / "local"),
                "PYTHONUTF8": "1",
            }
            process = subprocess.Popen(
                [sys.executable, "main.py", "--bridge"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                env=environment,
            )
            assert process.stdin is not None and process.stdout is not None
            process.stdin.write(json.dumps({"id": "1", "method": "bootstrap", "params": {}}) + "\n")
            process.stdin.flush()
            bootstrap = json.loads(process.stdout.readline())
            self.assertEqual(bootstrap["channel"], "response")
            self.assertEqual(bootstrap["result"]["tool"]["id"], "grade-export")

            process.stdin.write(json.dumps({"id": "2", "method": "saveSettings", "params": {"theme": "dark"}}) + "\n")
            process.stdin.flush()
            saved = json.loads(process.stdout.readline())
            self.assertEqual(saved["result"]["theme"], "dark")
            process.stdin.close()
            process.wait(timeout=5)
            process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
