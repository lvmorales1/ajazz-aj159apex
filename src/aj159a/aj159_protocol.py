from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MouseCommand:
    """Represents a known mouse command."""

    name: str
    report_id: int | None
    command_bytes: bytes
    description: str


KNOWN_COMMANDS: dict[str, MouseCommand] = {
    # "dpi_800": MouseCommand(
    #     name="dpi_800",
    #     report_id=None,
    #     command_bytes=b"\x05\x00\x04\x01",
    #     description="Set DPI to 800"
    # ),
}


def encode_dpi_command(dpi: int) -> bytes:
    """    
    Args:
        dpi: DPI value (50-64000)
        
    Returns:
        The HID command bytes to send
        
    Raises:
        NotImplementedError: Protocol not yet reverse engineered
    """
    raise NotImplementedError(
        "AJAZZ AJ159 Apex DPI protocol not yet reverse engineered." 
    )
