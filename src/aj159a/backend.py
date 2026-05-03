from __future__ import annotations

from dataclasses import dataclass

from .aj159_protocol import encode_dpi_command
from .discovery import UsbDevice
from .hid_protocol import HidDevice, HidDeviceError, find_hidraw_for_device


class BackendUnavailableError(RuntimeError):
    pass


class ProtocolError(RuntimeError):
    pass


@dataclass(slots=True)
class DpiRequest:
    value: int
    device: UsbDevice


def plan_dpi_change(device: UsbDevice, value: int) -> DpiRequest:
    if value < 50 or value > 64000:
        raise ValueError("dpi must be between 50 and 64000")
    return DpiRequest(value=value, device=device)


def apply_dpi_change(request: DpiRequest) -> None:
    """Apply a DPI change to the device via HID."""
    hidraw_path = find_hidraw_for_device(request.device)
    if not hidraw_path:
        raise BackendUnavailableError(
            f"No HID device found for {request.device.summary()}. "
            "The device may not expose a mouse interface or hidraw device."
        )

    try:
        command = encode_dpi_command(request.value)
    except NotImplementedError as exc:
        raise BackendUnavailableError(str(exc))

    try:
        with HidDevice(hidraw_path) as device:
            device.write(command)
    except HidDeviceError as exc:
        raise ProtocolError(f"Failed to send command: {exc}")

