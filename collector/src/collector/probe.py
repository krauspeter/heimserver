"""Read-only Modbus TCP probe for the Sungrow hybrid inverter.

Checks whether the inverter answers on Modbus TCP and prints a few known values.
It only uses "read input registers" (function code 0x04) - it never writes anything.

Usage (Git Bash, venv active):
    python -m collector.probe --host 192.168.178.50

Register addresses follow the Sungrow "Communication Protocol of Residential Hybrid
Inverter" as used by the open-source integrations for the SH series. The protocol
document counts registers from 1; Modbus/pymodbus addresses count from 0, so the
addresses below are "document number - 1". Verify them against the register manual
for the SH10T.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Literal

from collector.units import combine_u32, registers_to_ascii, to_signed16, to_signed32

Kind = Literal["u16", "s16", "u32", "s32", "ascii"]


@dataclass(frozen=True)
class RegisterSpec:
    """Description of one value to read from the inverter."""

    name: str
    address: int  # 0-based Modbus address
    count: int
    kind: Kind
    scale: float = 1.0
    unit: str = ""


REGISTERS: tuple[RegisterSpec, ...] = (
    RegisterSpec("Seriennummer", 4989, 10, "ascii"),
    RegisterSpec("Gerätetyp-Code", 4999, 1, "u16"),
    RegisterSpec("PV-Leistung (DC gesamt)", 5016, 2, "u32", unit="W"),
    RegisterSpec("Betriebszustand (Code)", 13000, 1, "u16"),
    RegisterSpec("PV-Ertrag heute", 13001, 1, "u16", scale=0.1, unit="kWh"),
    RegisterSpec("Hausverbrauch", 13007, 2, "s32", unit="W"),
    RegisterSpec("Netz-Leistung (Einspeisung/Bezug)", 13009, 2, "s32", unit="W"),
    RegisterSpec("Batterie-Leistung", 13021, 1, "u16", unit="W"),
    RegisterSpec("Batterie-Ladestand", 13022, 1, "u16", scale=0.1, unit="%"),
)


def decode(spec: RegisterSpec, registers: list[int]) -> str:
    """Turn raw register words into a human-readable value."""
    if len(registers) != spec.count:
        raise ValueError(f"expected {spec.count} registers, got {len(registers)}")

    if spec.kind == "ascii":
        return registers_to_ascii(registers)

    value: int
    if spec.kind == "u16":
        value = registers[0]
    elif spec.kind == "s16":
        value = to_signed16(registers[0])
    elif spec.kind == "u32":
        value = combine_u32(registers[0], registers[1])
    else:  # s32
        value = to_signed32(combine_u32(registers[0], registers[1]))

    scaled = value * spec.scale
    number = f"{scaled:.1f}" if spec.scale != 1.0 else str(value)
    return f"{number} {spec.unit}".strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Modbus TCP test for Sungrow inverters")
    parser.add_argument("--host", required=True, help="IP address of the inverter")
    parser.add_argument("--port", type=int, default=502, help="Modbus TCP port (default 502)")
    parser.add_argument("--device-id", type=int, default=1, help="Modbus unit/slave id (default 1)")
    parser.add_argument("--timeout", type=float, default=5.0, help="timeout in seconds")
    args = parser.parse_args(argv)

    # Imported here so that `decode` can be tested without pymodbus installed.
    from pymodbus.client import ModbusTcpClient
    from pymodbus.exceptions import ModbusException

    print(f"Verbinde mit {args.host}:{args.port} (Device-ID {args.device_id}) ...")
    client = ModbusTcpClient(args.host, port=args.port, timeout=args.timeout)
    if not client.connect():
        print("FEHLER: Keine TCP-Verbindung. IP richtig? Modbus TCP am Wechselrichter aktiv?")
        return 2

    print("TCP-Verbindung steht. Lese Register (nur lesend) ...\n")
    ok = 0
    try:
        for spec in REGISTERS:
            label = f"{spec.name:<36} [{spec.address}]"
            try:
                response = client.read_input_registers(
                    spec.address, count=spec.count, device_id=args.device_id
                )
            except ModbusException as exc:
                print(f"  {label}  FEHLER: {exc}")
                continue
            if response.isError():
                print(f"  {label}  keine Antwort / nicht unterstützt ({response})")
                continue
            raw: list[int] = list(response.registers)
            print(f"  {label}  {decode(spec, raw):<20} roh={raw}")
            ok += 1
    finally:
        client.close()

    print(f"\n{ok} von {len(REGISTERS)} Werten gelesen.")
    if ok == 0:
        print("Verbindung steht, aber keine Antwort: Device-ID (--device-id) oder Port prüfen.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
