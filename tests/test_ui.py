from __future__ import annotations

import os
import json
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
)

from qlu_toolbox.core.metadata import AUTHOR_EMAIL, AUTHOR_GITHUB_URL, AUTHOR_NAME  # noqa: E402
from qlu_toolbox.core.paths import AppPaths  # noqa: E402
from qlu_toolbox.core.settings import AppSettings, SettingsStore  # noqa: E402
from qlu_toolbox.core.tasks import TaskStore  # noqa: E402
from qlu_toolbox.core.tools import ToolRegistry  # noqa: E402
from qlu_toolbox.modules.grade_export import MANIFEST  # noqa: E402
from qlu_toolbox.modules.grade_export.page import WorkerProcess  # noqa: E402
from qlu_toolbox.ui.main_window import MainWindow  # noqa: E402
from qlu_toolbox.ui.pages import AboutPage  # noqa: E402


class UiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def test_main_window_contains_all_v1_pages(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = AppPaths(root / "config", root / "data", root / "logs", root / "profiles")
            paths.ensure()
            settings = AppSettings(welcome_accepted=True, default_output_dir=str(root))
            settings_store = SettingsStore(paths)
            tasks = TaskStore(root / "tasks.sqlite3")
            registry = ToolRegistry()
            registry.register(MANIFEST)
            window = MainWindow(paths, settings, settings_store, tasks, registry)
            self.assertEqual(window.stack.count(), 6)
            self.assertEqual(window.tasks_page.table.columnCount(), 4)
            self.assertEqual(window.settings_page.browser.objectName(), "SettingsCombo")
            self.assertEqual(
                len(window.settings_page.findChildren(QLineEdit, "DataPath")), 5
            )
            self.assertIsNotNone(window.settings_page.findChild(QScrollArea))
            window.open_tool(MANIFEST.id)
            self.assertEqual(window.stack.currentIndex(), MainWindow.PAGE_GRADE_EXPORT)
            self.assertEqual(window.windowTitle(), "QLU 工具箱")
            window.close()

    def test_about_page_exposes_author_and_support_channels(self):
        page = AboutPage()
        self.assertIsNotNone(page.findChild(QScrollArea))

        visible_text = "\n".join(label.text() for label in page.findChildren(QLabel))
        self.assertIn(AUTHOR_NAME, visible_text)
        self.assertIn(AUTHOR_EMAIL, visible_text)
        self.assertIn(AUTHOR_GITHUB_URL, visible_text)

        button_text = {button.text() for button in page.findChildren(QPushButton)}
        self.assertIn("提交 Bug / 建议", button_text)
        self.assertIn("作者 GitHub", button_text)
        self.assertIn("邮件联系作者", button_text)
        page.deleteLater()

    def test_worker_reads_event_file_and_deduplicates_stdout_events(self):
        with tempfile.TemporaryDirectory() as temporary:
            runner = WorkerProcess()
            events: list[dict] = []
            runner.event_received.connect(events.append)
            runner.event_path = Path(temporary) / "events.jsonl"
            payloads = [
                {"type": "status", "stage": "save", "message": "正在保存", "_seq": 1},
                {"type": "success", "path": "C:/result.xlsx", "_seq": 2},
            ]
            runner.event_path.write_text(
                "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in payloads),
                encoding="utf-8",
            )

            runner._read_event_file()
            runner._dispatch_event(payloads[1])

            self.assertEqual([event["type"] for event in events], ["status", "success"])
            self.assertTrue(runner.terminal_event_received)
            runner._cleanup_event_file()


if __name__ == "__main__":
    unittest.main()
