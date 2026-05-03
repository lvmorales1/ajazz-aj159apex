from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from aj159a.debug import capture_device_reports, format_report_hex, print_report_analysis
from aj159a.discovery import UsbDevice, UsbInterface
from aj159a.hid_protocol import HidDeviceError


class DebugTests(unittest.TestCase):
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

    def test_format_report_hex_converts_bytes(self) -> None:
        data = b"\x01\x02\x03\x04"
        result = format_report_hex(data)
        self.assertIn("01 02 03 04", result)

    def test_format_report_hex_wraps_at_width(self) -> None:
        data = bytes(range(32))
        result = format_report_hex(data, width=8)
        lines = result.split("\n")
        # 32 bytes with width 8 = 4 lines
        self.assertEqual(len(lines), 4)

    def test_capture_device_reports_fails_if_no_hidraw(self) -> None:
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

        with self.assertRaises(HidDeviceError) as ctx:
            capture_device_reports(device_no_hidraw, duration_seconds=0.1)
        self.assertIn("No HID device found", str(ctx.exception))

    @patch("aj159a.debug.HidDevice")
    @patch("aj159a.debug.time.time")
    def test_capture_device_reports_reads_until_timeout(
        self, mock_time: MagicMock, mock_hid_class: MagicMock
    ) -> None:
        times = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 6.0]
        mock_time.side_effect = times

        mock_device = MagicMock()
        mock_device.read.side_effect = [b"\x01\x02", b"\x03\x04", HidDeviceError("closed")]
        mock_hid_class.return_value.__enter__.return_value = mock_device

        reports = capture_device_reports(self.device, duration_seconds=5.0)

        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0], b"\x01\x02")
        self.assertEqual(reports[1], b"\x03\x04")

    def test_print_report_analysis_handles_empty_list(self) -> None:
        print_report_analysis([])

    def test_print_report_analysis_finds_differences(self) -> None:
        reports = [
            b"\x01\x02\x03\x04",
            b"\x01\x02\x03\x05",  # Differs at byte 3
            b"\x01\x02\x03\x04",  # Same as first
        ]
        
        print_report_analysis(reports)


if __name__ == "__main__":
    unittest.main()
