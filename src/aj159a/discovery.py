from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class UsbInterface:
    path: Path
    interface_number: str | None
    interface_class: str | None
    interface_subclass: str | None
    interface_protocol: str | None
    interface_name: str | None
    hidraw_nodes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class UsbDevice:
    path: Path
    vendor_id: int | None
    product_id: int | None
    manufacturer: str | None
    product: str | None
    serial: str | None
    busnum: int | None
    devnum: int | None
    interfaces: list[UsbInterface] = field(default_factory=list)

    @property
    def short_id(self) -> str:
        if self.vendor_id is None or self.product_id is None:
            return "unknown"
        return f"{self.vendor_id:04x}:{self.product_id:04x}"

    @property
    def display_name(self) -> str:
        parts = [part for part in [self.manufacturer, self.product] if part]
        if parts:
            return " ".join(parts)
        return self.path.name

    @property
    def is_hid_device(self) -> bool:
        return any(interface.interface_class == "03" for interface in self.interfaces)

    def summary(self) -> str:
        label = self.display_name
        details = [self.short_id]
        if self.serial:
            details.append(f"serial={self.serial}")
        if self.busnum is not None and self.devnum is not None:
            details.append(f"bus={self.busnum:03d} dev={self.devnum:03d}")
        if self.is_hid_device:
            details.append("hid")
        return f"{label} ({', '.join(details)})"


def _read_text(path: Path) -> str | None:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return value or None


def _read_int(path: Path, base: int = 10) -> int | None:
    raw = _read_text(path)
    if raw is None:
        return None
    try:
        return int(raw, base)
    except ValueError:
        return None


def _collect_hidraw_nodes(interface_path: Path) -> list[str]:
    nodes: list[str] = []
    hidraw_root = interface_path / "hidraw"
    if hidraw_root.exists():
        for child in sorted(hidraw_root.iterdir()):
            if child.name.startswith("hidraw"):
                nodes.append(f"/dev/{child.name}")
    return nodes


def _load_interface(path: Path) -> UsbInterface:
    number = _read_text(path / "bInterfaceNumber")
    interface_class = _read_text(path / "bInterfaceClass")
    interface_subclass = _read_text(path / "bInterfaceSubClass")
    interface_protocol = _read_text(path / "bInterfaceProtocol")
    interface_name = _read_text(path / "interface")
    return UsbInterface(
        path=path,
        interface_number=number,
        interface_class=interface_class,
        interface_subclass=interface_subclass,
        interface_protocol=interface_protocol,
        interface_name=interface_name,
        hidraw_nodes=_collect_hidraw_nodes(path),
    )


def load_usb_device(path: Path) -> UsbDevice:
    interfaces: list[UsbInterface] = []
    for child in sorted(path.iterdir()):
        if not child.is_dir():
            continue
        if ":" not in child.name:
            continue
        interfaces.append(_load_interface(child))

    return UsbDevice(
        path=path,
        vendor_id=_read_int(path / "idVendor", 16),
        product_id=_read_int(path / "idProduct", 16),
        manufacturer=_read_text(path / "manufacturer"),
        product=_read_text(path / "product"),
        serial=_read_text(path / "serial"),
        busnum=_read_int(path / "busnum", 10),
        devnum=_read_int(path / "devnum", 10),
        interfaces=interfaces,
    )


def iter_usb_devices(sysfs_root: Path | None = None) -> list[UsbDevice]:
    root = sysfs_root or Path("/sys/bus/usb/devices")
    if not root.exists():
        return []

    devices: list[UsbDevice] = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if ":" in entry.name:
            continue
        if not (entry / "idVendor").exists():
            continue
        devices.append(load_usb_device(entry))
    return devices


def matches_query(device: UsbDevice, query: str) -> bool:
    needle = query.strip().lower()
    haystack = [
        device.path.name,
        device.display_name,
        device.short_id,
        device.manufacturer or "",
        device.product or "",
        device.serial or "",
    ]
    return any(needle in value.lower() for value in haystack)


def find_usb_devices(query: str | None = None, sysfs_root: Path | None = None) -> list[UsbDevice]:
    devices = iter_usb_devices(sysfs_root=sysfs_root)
    if not query:
        return devices
    return [device for device in devices if matches_query(device, query)]
