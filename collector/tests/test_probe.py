import pytest

from collector.probe import REGISTERS, RegisterSpec, decode
from collector.units import combine_u32, registers_to_ascii, to_signed32


def test_combine_u32_low_word_first() -> None:
    assert combine_u32(0x5678, 0x1234) == 0x12345678


def test_to_signed32_negative() -> None:
    assert to_signed32(0xFFFFFFFF) == -1
    assert to_signed32(0x7FFFFFFF) == 2_147_483_647


def test_registers_to_ascii_strips_padding() -> None:
    # "A2" "31" "\0\0"
    assert registers_to_ascii([0x4132, 0x3331, 0x0000]) == "A231"


def test_decode_scaled_u16() -> None:
    spec = RegisterSpec("SOC", 0, 1, "u16", scale=0.1, unit="%")
    assert decode(spec, [875]) == "87.5 %"


def test_decode_s32_export_is_negative() -> None:
    spec = RegisterSpec("Grid", 0, 2, "s32", unit="W")
    # -1500 W as two's complement, low word first
    raw = (-1500) & 0xFFFFFFFF
    assert decode(spec, [raw & 0xFFFF, raw >> 16]) == "-1500 W"


def test_decode_wrong_count_raises() -> None:
    spec = RegisterSpec("x", 0, 2, "u32")
    with pytest.raises(ValueError):
        decode(spec, [1])


def test_register_table_has_no_overlaps() -> None:
    ranges = sorted((s.address, s.address + s.count) for s in REGISTERS)
    for (_, end), (start, _) in zip(ranges, ranges[1:], strict=False):
        assert end <= start
