# AJ159A

Linux CLI for configuring the AJAZZ AJ159 Apex mouse.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
aj159a scan
aj159a inspect --query ajazz
aj159a diagnose --query ajazz
aj159a capture --query ajazz --duration 10
aj159a set-dpi --query ajazz --dpi 1600
```

### Requirements

- Linux kernel built with HID and hidraw support (`CONFIG_HID=y` and `CONFIG_HIDRAW=y`)
- Python 3.10+

### Troubleshooting

If `diagnose` shows "No hidraw device found", your kernel may not have hidraw support. Check:

```bash
aj159a diagnose --query ajazz
```

If hidraw module is missing, either:
- Load it: `sudo modprobe hidraw` (if available in your kernel)
- Recompile kernel with `CONFIG_HIDRAW=y`
- Or check `/sys/bus/usb/devices/` for your device path and inspect it manually
## Development

```bash
python -m unittest discover -s tests
```
