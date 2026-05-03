from __future__ import annotations

import tempfile
import unittest
import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from aj159a.cli import main


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


class CliTests(unittest.TestCase):
    def test_scan_uses_sysfs_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            device = root / "1-1"
            device.mkdir()
            _write(device / "idVendor", "0c45\n")
            _write(device / "idProduct", "6a13\n")
            _write(device / "manufacturer", "AJAZZ\n")
            _write(device / "product", "AJ159 Apex\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--sysfs-root", str(root), "scan"])

            self.assertEqual(exit_code, 0)
            self.assertIn("AJAZZ AJ159 Apex", stdout.getvalue())

    def test_set_dpi_dry_run_prints_planned_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            device = root / "1-1"
            device.mkdir()
            _write(device / "idVendor", "0c45\n")
            _write(device / "idProduct", "6a13\n")
            _write(device / "product", "AJ159 Apex\n")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--sysfs-root", str(root), "set-dpi", "--query", "aj159", "--dpi", "1600", "--dry-run"])

            self.assertEqual(exit_code, 0)
            self.assertIn("Planned DPI change", stdout.getvalue())

    def test_set_dpi_without_backend_reports_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            device = root / "1-1"
            device.mkdir()
            _write(device / "idVendor", "0c45\n")
            _write(device / "idProduct", "6a13\n")
            _write(device / "product", "AJ159 Apex\n")

            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(["--sysfs-root", str(root), "set-dpi", "--query", "aj159", "--dpi", "1600"])

            self.assertEqual(exit_code, 3)
            self.assertEqual(stdout.getvalue(), "")
            error_msg = stderr.getvalue().lower()
            self.assertTrue(
                "backend not implemented" in error_msg or "no hid device" in error_msg,
                f"Expected backend error, got: {error_msg}"
            )


if __name__ == "__main__":
    unittest.main()
