from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .backend import BackendUnavailableError, apply_dpi_change, plan_dpi_change
from .discovery import UsbDevice, find_usb_devices


def _format_device(device: UsbDevice) -> str:
    interface_bits = []
    for interface in device.interfaces:
        descriptor = interface.interface_name or interface.interface_number or interface.path.name
        if interface.hidraw_nodes:
            descriptor = f"{descriptor} [{', '.join(interface.hidraw_nodes)}]"
        interface_bits.append(descriptor)

    lines = [f"{device.summary()}"]
    if interface_bits:
        lines.append(f"  interfaces: {', '.join(interface_bits)}")
    return "\n".join(lines)


def _print_devices(devices: list[UsbDevice]) -> int:
    if not devices:
        print("No USB devices matched the current filter.")
        return 1

    for device in devices:
        print(device.summary())
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aj159a")
    parser.add_argument("--sysfs-root", type=Path, default=None, help="override the Linux USB sysfs root")

    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="list detected USB devices")
    scan_parser.add_argument("--query", help="only show devices matching this string")

    inspect_parser = subparsers.add_parser("inspect", help="show detailed information for a device")
    inspect_parser.add_argument("--query", help="select a device by matching metadata")
    inspect_parser.add_argument("--path", type=Path, help="select a device directly by sysfs path")

    dpi_parser = subparsers.add_parser("set-dpi", help="prepare a DPI change for the target device")
    dpi_parser.add_argument("--query", help="select a device by matching metadata")
    dpi_parser.add_argument("--path", type=Path, help="select a device directly by sysfs path")
    dpi_parser.add_argument("--dpi", type=int, required=True, help="requested DPI value")
    dpi_parser.add_argument("--dry-run", action="store_true", help="do not apply, only print the planned action")

    return parser


def _select_device(args: argparse.Namespace) -> UsbDevice | None:
    if args.path is not None:
        return next((device for device in find_usb_devices(sysfs_root=args.sysfs_root) if device.path == args.path), None)

    query = getattr(args, "query", None)
    matches = find_usb_devices(query=query, sysfs_root=args.sysfs_root)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print("Multiple devices matched. Please narrow the query or use --path.", file=sys.stderr)
        for device in matches:
            print(device.summary(), file=sys.stderr)
    return None


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        devices = find_usb_devices(query=args.query, sysfs_root=args.sysfs_root)
        return _print_devices(devices)

    if args.command == "inspect":
        device = _select_device(args)
        if device is None:
            print("No device matched the selection.", file=sys.stderr)
            return 1
        print(_format_device(device))
        return 0

    if args.command == "set-dpi":
        device = _select_device(args)
        if device is None:
            print("No device matched the selection.", file=sys.stderr)
            return 1

        try:
            request = plan_dpi_change(device, args.dpi)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2

        if args.dry_run:
            print(f"Planned DPI change: {request.device.summary()} -> {request.value}")
            return 0

        try:
            apply_dpi_change(request)
        except BackendUnavailableError as exc:
            print(str(exc), file=sys.stderr)
            return 3
        return 0

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
