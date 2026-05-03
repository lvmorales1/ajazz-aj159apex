from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .discovery import UsbDevice


def check_hidraw_support() -> bool:
    """Check if hidraw module is loaded."""
    try:
        result = subprocess.run(["lsmod"], capture_output=True, text=True, timeout=5)
        return "hidraw" in result.stdout
    except Exception:
        return False


def check_sysfs_hidraw(device: UsbDevice) -> dict[str, str]:
    """Check what hidraw devices exist in sysfs for a device."""
    results = {}
    
    if device.path.exists():
        results["device_path"] = str(device.path)
        
        for interface in device.interfaces:
            hidraw_dir = interface.path / "hidraw"
            if hidraw_dir.exists():
                hidraw_nodes = sorted(hidraw_dir.iterdir())
                results["hidraw_in_sysfs"] = ", ".join([n.name for n in hidraw_nodes])
            
            if interface.path.exists():
                results[f"interface_{interface.interface_number}"] = str(interface.path)
    
    return results


def check_device_permissions(device: UsbDevice) -> dict[str, bool]:
    """Check if the current user can access the device."""
    results = {}
    
    if device.busnum and device.devnum:
        usb_path = Path(f"/dev/bus/usb/{device.busnum:03d}/{device.devnum:03d}")
        results["usb_device_exists"] = usb_path.exists()
        if usb_path.exists():
            results["usb_device_readable"] = os.access(usb_path, os.R_OK)
            results["usb_device_writable"] = os.access(usb_path, os.W_OK)
    
    hidraw_test = Path("/dev/hidraw0")
    if hidraw_test.exists():
        results["sample_hidraw_readable"] = os.access(hidraw_test, os.R_OK)
        results["sample_hidraw_writable"] = os.access(hidraw_test, os.W_OK)
    
    return results


def print_diagnostics(device: UsbDevice) -> None:
    """Print diagnostic information for a device."""
    print(f"Device: {device.summary()}\n")
    
    print("=== Kernel Support ===")
    if check_hidraw_support():
        print("✓ hidraw module is loaded")
    else:
        print("✗ hidraw module is NOT loaded")
        print("  Try: sudo modprobe hidraw\n")
    
    print("=== Sysfs Check ===")
    sysfs_info = check_sysfs_hidraw(device)
    for key, value in sysfs_info.items():
        print(f"  {key}: {value}")
    
    if "hidraw_in_sysfs" not in sysfs_info:
        print("  ✗ No hidraw device found in sysfs")
        print("  The kernel HID driver may not have bound to this device.\n")
    
    print("=== Permissions ===")
    perms = check_device_permissions(device)
    for key, value in perms.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value}")
    
    if not perms.get("usb_device_writable", False):
        print("\n  Consider running with sudo or adding udev rules for write access.")
    
    print("\n=== Troubleshooting ===")
    print("1. Load hidraw module:")
    print("   sudo modprobe hidraw")
    print("\n2. Check kernel messages:")
    print("   dmesg | tail -20")
    print("\n3. Replug the device and check dmesg for bind/unbind messages")
