from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from aj159a.diagnose import check_device_permissions, check_hidraw_support, check_sysfs_hidraw
from aj159a.discovery import UsbDevice, UsbInterface


class DiagnoseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.device = UsbDevice(
            path=Path("/sys/devices/test"),
            vendor_id=0x3151,
            product_id=0x5007,
            manufacturer="AJAZZ",
            product="2.4G 8K",
            serial="abc123",
            busnum=1,
            devnum=3,
            interfaces=[
                UsbInterface(
                    path=Path("/sys/devices/test/1-1:1.0"),
                    interface_number="00",
                    interface_class="03",
                    interface_subclass="01",
                    interface_protocol="02",
                    interface_name="Mouse",
                    hidraw_nodes=["/dev/hidraw0"],
                )
            ],
        )

    @patch("aj159a.diagnose.subprocess.run")
    def test_check_hidraw_support_detects_module(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="hidraw 1234 0\n", stderr="")
        self.assertTrue(check_hidraw_support())

    @patch("aj159a.diagnose.subprocess.run")
    def test_check_hidraw_support_detects_missing_module(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="some_other_module 1234 0\n", stderr="")
        self.assertFalse(check_hidraw_support())

    def test_check_sysfs_hidraw_returns_dict(self) -> None:
        results = check_sysfs_hidraw(self.device)
        self.assertIsInstance(results, dict)

    def test_check_device_permissions_returns_dict(self) -> None:
        results = check_device_permissions(self.device)
        self.assertIsInstance(results, dict)


if __name__ == "__main__":
    unittest.main()
