from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from aj159a.backend import (
    BackendUnavailableError,
    ProtocolError,
    apply_dpi_change,
    plan_dpi_change,
)
from aj159a.discovery import UsbDevice, UsbInterface


class BackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.device = UsbDevice(
            path=Path("/sys/devices/pci0000:00/0000:00:14.0/usb1/1-1"),
            vendor_id=0x3151,
            product_id=0x5007,
            manufacturer="AJAZZ",
            product="2.4G 8K",
            serial="abc123",
            busnum=1,
            devnum=3,
            interfaces=[
                UsbInterface(
                    path=Path("/sys/devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1:1.0"),
                    interface_number="00",
                    interface_class="03",
                    interface_subclass="01",
                    interface_protocol="02",
                    interface_name="Mouse",
                    hidraw_nodes=["/dev/hidraw0"],
                )
            ],
        )

    def test_plan_dpi_change_validates_range(self) -> None:
        with self.assertRaises(ValueError):
            plan_dpi_change(self.device, 30)  # Too low
        with self.assertRaises(ValueError):
            plan_dpi_change(self.device, 70000)  # Too high

    def test_plan_dpi_change_accepts_valid_values(self) -> None:
        request = plan_dpi_change(self.device, 1600)
        self.assertEqual(request.value, 1600)
        self.assertEqual(request.device, self.device)

    def test_apply_dpi_change_fails_if_no_hidraw(self) -> None:
        device_no_hidraw = UsbDevice(
            path=Path("/sys/devices/test"),
            vendor_id=0x3151,
            product_id=0x5007,
            manufacturer="AJAZZ",
            product="2.4G 8K",
            serial="abc123",
            busnum=1,
            devnum=3,
            interfaces=[],
        )
        request = plan_dpi_change(device_no_hidraw, 1600)

        with self.assertRaises(BackendUnavailableError) as ctx:
            apply_dpi_change(request)
        self.assertIn("No HID device found", str(ctx.exception))

    def test_apply_dpi_change_reports_protocol_not_implemented(self) -> None:
        request = plan_dpi_change(self.device, 1600)

        with self.assertRaises(BackendUnavailableError) as ctx:
            apply_dpi_change(request)
        self.assertIn("not yet reverse engineered", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
