from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from aj159a.discovery import find_usb_devices, load_usb_device, matches_query


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


class DiscoveryTests(unittest.TestCase):
    def test_load_usb_device_parses_metadata_and_interfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            device = root / "1-1"
            interface = device / "1-1:1.0"
            hidraw = interface / "hidraw" / "hidraw3"
            hidraw.mkdir(parents=True)

            for name, value in {
                "idVendor": "0c45\n",
                "idProduct": "6a13\n",
                "manufacturer": "AJAZZ\n",
                "product": "AJ159 Apex\n",
                "serial": "abc123\n",
                "busnum": "3\n",
                "devnum": "12\n",
                "bInterfaceNumber": "00\n",
                "bInterfaceClass": "03\n",
                "bInterfaceSubClass": "01\n",
                "bInterfaceProtocol": "02\n",
                "interface": "Mouse Interface\n",
            }.items():
                target = interface / name if name.startswith("bInterface") or name == "interface" else device / name
                _write(target, value)

            loaded = load_usb_device(device)

            self.assertEqual(loaded.short_id, "0c45:6a13")
            self.assertEqual(loaded.display_name, "AJAZZ AJ159 Apex")
            self.assertTrue(loaded.is_hid_device)
            self.assertEqual(loaded.interfaces[0].hidraw_nodes, ["/dev/hidraw3"])

    def test_find_usb_devices_filters_by_query(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            device = root / "1-1"
            device.mkdir()
            _write(device / "idVendor", "0c45\n")
            _write(device / "idProduct", "6a13\n")
            _write(device / "product", "AJ159 Apex\n")

            other = root / "1-2"
            other.mkdir()
            _write(other / "idVendor", "abcd\n")
            _write(other / "idProduct", "1234\n")
            _write(other / "product", "Keyboard\n")

            matches = find_usb_devices(query="aj159", sysfs_root=root)
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0].path.name, "1-1")

    def test_matches_query_uses_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            device = root / "1-1"
            device.mkdir()
            _write(device / "idVendor", "0c45\n")
            _write(device / "idProduct", "6a13\n")
            _write(device / "manufacturer", "AJAZZ\n")
            _write(device / "product", "AJ159 Apex\n")

            loaded = load_usb_device(device)
            self.assertTrue(matches_query(loaded, "6a13"))
            self.assertTrue(matches_query(loaded, "ajazz"))
            self.assertFalse(matches_query(loaded, "headset"))


if __name__ == "__main__":
    unittest.main()
