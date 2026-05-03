from __future__ import annotations

import sys
import time
from pathlib import Path

from .discovery import UsbDevice
from .hid_protocol import HidDevice, HidDeviceError, find_hidraw_for_device


def capture_device_reports(
    device: UsbDevice, duration_seconds: float = 5, report_size: int = 64
) -> list[bytes]:
    """
    Capture raw HID reports from a device for analysis.
    
    This is useful for reverse engineering the device protocol by capturing
    what the device sends when buttons are pressed or settings change.
    
    Args:
        device: The UsbDevice to capture from
        duration_seconds: How long to capture for
        report_size: Size of each report to read
        
    Returns:
        List of raw bytes captured from the device
        
    Raises:
        HidDeviceError: If the device cannot be opened or read from
    """
    hidraw_path = find_hidraw_for_device(device)
    if not hidraw_path:
        raise HidDeviceError(f"No HID device found for {device.summary()}")

    reports: list[bytes] = []
    start_time = time.time()

    try:
        with HidDevice(hidraw_path) as hid:
            while time.time() - start_time < duration_seconds:
                try:
                    data = hid.read(report_size)
                    if data:
                        reports.append(data)
                except HidDeviceError:
                    # Device may have stopped sending data
                    break
    except HidDeviceError as e:
        raise HidDeviceError(f"Failed to capture reports: {e}")

    return reports


def format_report_hex(data: bytes, width: int = 16) -> str:
    """Format a report as a hex string for easy analysis."""
    hex_str = data.hex()
    pairs = [hex_str[i : i + 2] for i in range(0, len(hex_str), 2)]
    rows = [" ".join(pairs[i : i + width]) for i in range(0, len(pairs), width)]
    return "\n".join(rows)


def print_report_analysis(reports: list[bytes]) -> None:
    """Print a human-readable analysis of captured reports."""
    print(f"Captured {len(reports)} reports\n")

    if not reports:
        print("No reports captured.")
        return

    for i, report in enumerate(reports):
        print(f"Report {i + 1} ({len(report)} bytes):")
        print(format_report_hex(report))
        print()

    if len(reports) > 1:
        print("=== Pattern Analysis ===")
        first = reports[0]
        differences = []
        for i, report in enumerate(reports[1:], 1):
            if report != first:
                diff_positions = [j for j in range(len(report)) if j < len(first) and report[j] != first[j]]
                differences.append((i, diff_positions))

        if differences:
            print("Reports that differ from the first:")
            for report_num, positions in differences:
                print(f"  Report {report_num + 1}: bytes changed at positions {positions}")
        else:
            print("All reports are identical.")
