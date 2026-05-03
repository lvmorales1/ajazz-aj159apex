from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from aj159a.hid_protocol import HidDevice, HidDeviceError, find_hidraw_for_device
from aj159a.discovery import UsbDevice, UsbInterface


class HidDeviceTests(unittest.TestCase):
    def test_hid_device_context_manager_opens_and_closes(self) -> None:
        with patch("aj159a.hid_protocol.os.open") as mock_open, patch(
            "aj159a.hid_protocol.os.close"
        ) as mock_close:
            mock_open.return_value = 42

            device = HidDevice("/dev/hidraw0")
            with device:
                self.assertEqual(device._fd, 42)

            mock_close.assert_called_once_with(42)

    def test_hid_device_write_sends_data(self) -> None:
        with patch("aj159a.hid_protocol.os.open") as mock_open, patch(
            "aj159a.hid_protocol.os.write"
        ) as mock_write, patch("aj159a.hid_protocol.os.close"):
            mock_open.return_value = 42
            mock_write.return_value = 5

            device = HidDevice("/dev/hidraw0")
            device.open()
            result = device.write(b"hello")

            self.assertEqual(result, 5)
            mock_write.assert_called_once_with(42, b"hello")

    def test_hid_device_read_receives_data(self) -> None:
        with patch("aj159a.hid_protocol.os.open") as mock_open, patch(
            "aj159a.hid_protocol.os.read"
        ) as mock_read, patch("aj159a.hid_protocol.os.close"):
            mock_open.return_value = 42
            mock_read.return_value = b"response"

            device = HidDevice("/dev/hidraw0")
            device.open()
            result = device.read(64)

            self.assertEqual(result, b"response")
            mock_read.assert_called_once_with(42, 64)

    def test_hid_device_write_raises_if_not_open(self) -> None:
        device = HidDevice("/dev/hidraw0")
        with self.assertRaises(HidDeviceError):
            device.write(b"test")

    def test_find_hidraw_for_device_returns_first_node(self) -> None:
        interface = UsbInterface(
            path=Path("/sys/devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1:1.0"),
            interface_number="00",
            interface_class="03",
            interface_subclass="01",
            interface_protocol="02",
            interface_name="Mouse",
            hidraw_nodes=["/dev/hidraw3", "/dev/hidraw4"],
        )
        device = UsbDevice(
            path=Path("/sys/devices/pci0000:00/0000:00:14.0/usb1/1-1"),
            vendor_id=0x3151,
            product_id=0x5007,
            manufacturer="AJAZZ",
            product="2.4G 8K",
            serial="abc123",
            busnum=1,
            devnum=3,
            interfaces=[interface],
        )

        result = find_hidraw_for_device(device)
        self.assertEqual(result, "/dev/hidraw3")

    def test_find_hidraw_for_device_returns_none_if_no_hidraw(self) -> None:
        interface = UsbInterface(
            path=Path("/sys/devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1:1.0"),
            interface_number="00",
            interface_class="03",
            interface_subclass="01",
            interface_protocol="02",
            interface_name="Mouse",
            hidraw_nodes=[],
        )
        device = UsbDevice(
            path=Path("/sys/devices/pci0000:00/0000:00:14.0/usb1/1-1"),
            vendor_id=0x3151,
            product_id=0x5007,
            manufacturer="AJAZZ",
            product="2.4G 8K",
            serial="abc123",
            busnum=1,
            devnum=3,
            interfaces=[interface],
        )

        result = find_hidraw_for_device(device)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
