import pytest

from collector.units import scale_register, to_signed16


def test_scale_register() -> None:
    assert scale_register(1234, 0.1) == pytest.approx(123.4)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(0x0000, 0), (0x7FFF, 32767), (0x8000, -32768), (0xFFFF, -1)],
)
def test_to_signed16(raw: int, expected: int) -> None:
    assert to_signed16(raw) == expected


@pytest.mark.parametrize("raw", [-1, 0x10000])
def test_out_of_range_raises(raw: int) -> None:
    with pytest.raises(ValueError):
        to_signed16(raw)
    with pytest.raises(ValueError):
        scale_register(raw, 1.0)
