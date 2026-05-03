from __future__ import annotations

import os
from pathlib import Path

from .discovery import UsbDevice, UsbInterface


class HidDeviceError(RuntimeError):
    pass


class HidDevice:
    """Low-level interface to a HID device via hidraw."""

    def __init__(self, device_path: str):
        self.device_path = device_path
        self._fd: int | None = None

    def open(self) -> None:
        """Open the HID device for reading/writing."""
        if self._fd is not None:
            return
        try:
            self._fd = os.open(self.device_path, os.O_RDWR)
        except OSError as e:
            raise HidDeviceError(f"Failed to open {self.device_path}: {e}")

    def close(self) -> None:
        """Close the HID device."""
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None

    def write(self, data: bytes) -> int:
        """Write data to the device."""
        if self._fd is None:
            raise HidDeviceError("Device not open")
        try:
            return os.write(self._fd, data)
        except OSError as e:
            raise HidDeviceError(f"Write failed: {e}")

    def read(self, size: int) -> bytes:
        """Read data from the device."""
        if self._fd is None:
            raise HidDeviceError("Device not open")
        try:
            return os.read(self._fd, size)
        except OSError as e:
            raise HidDeviceError(f"Read failed: {e}")

    def __enter__(self) -> HidDevice:
        self.open()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


def find_hidraw_for_device(device: UsbDevice) -> str | None:
    """Find the hidraw device node for a USB device."""
    for interface in device.interfaces:
        if interface.hidraw_nodes:
            return interface.hidraw_nodes[0]
    return None
