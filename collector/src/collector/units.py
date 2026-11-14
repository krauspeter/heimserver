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


def combine_u32(low_word: int, high_word: int) -> int:
    """Combine two 16-bit registers into one unsigned 32-bit value.

    Sungrow sends the LOW word first ("word swap"), so the register at the
    lower address holds bits 0-15 and the next register bits 16-31.
    """
    for word in (low_word, high_word):
        if not 0 <= word <= 0xFFFF:
            raise ValueError(f"register value out of 16-bit range: {word}")
    return (high_word << 16) | low_word


def to_signed32(raw: int) -> int:
    """Interpret an unsigned 32-bit value as two's complement."""
    if not 0 <= raw <= 0xFFFFFFFF:
        raise ValueError(f"value out of 32-bit range: {raw}")
    return raw - 0x1_0000_0000 if raw & 0x8000_0000 else raw


def registers_to_ascii(registers: list[int]) -> str:
    """Decode registers holding ASCII text (2 characters per register, high byte first)."""
    data = b"".join(word.to_bytes(2, "big") for word in registers)
    return data.decode("ascii", errors="replace").rstrip("\x00 ").strip()
