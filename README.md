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
aj159a set-dpi --query ajazz --dpi 1600
```

## Development

```bash
python -m unittest discover -s tests
```
