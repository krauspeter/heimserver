"""Helpers for converting raw Modbus register values into physical units."""


def scale_register(raw: int, factor: float) -> float:
    """Convert a raw unsigned 16-bit register value into a physical value.

    Example: a power register with factor 0.1 and raw value 1234 -> 123.4 W.
    """
    if not 0 <= raw <= 0xFFFF:
        raise ValueError(f"register value out of 16-bit range: {raw}")
    return raw * factor


def to_signed16(raw: int) -> int:
    """Interpret an unsigned 16-bit register value as two's complement.

    Needed e.g. for battery power, which is negative while discharging.
    """
    if not 0 <= raw <= 0xFFFF:
        raise ValueError(f"register value out of 16-bit range: {raw}")
    return raw - 0x10000 if raw & 0x8000 else raw
