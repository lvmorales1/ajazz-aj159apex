from __future__ import annotations

from dataclasses import dataclass

from .discovery import UsbDevice


class BackendUnavailableError(RuntimeError):
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
    raise BackendUnavailableError(
        "Mouse protocol backend not implemented yet. "
        f"A DPI change to {request.value} for {request.device.summary()} is planned, "
        "but the vendor command format still needs to be reverse engineered."
    )
