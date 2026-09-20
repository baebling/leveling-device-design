"""USB serial logger and command console for the Rev E Mega2560 controller."""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path


HEADER = (
    "ms",
    "state",
    "pitch_deg",
    "roll_deg",
    "enc1",
    "enc2",
    "enc3",
    "pwm1",
    "dir1",
    "pwm2",
    "dir2",
    "pwm3",
    "dir3",
    "fault",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", help="Serial port, for example COM5")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--command", action="append", default=[])
    parser.add_argument("--duration", type=float, default=60.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        import serial
    except ImportError:
        print("pyserial is required: python -m pip install pyserial", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with serial.Serial(args.port, args.baud, timeout=0.25) as link, args.output.open(
        "w", newline="", encoding="utf-8-sig"
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(("host_time_iso",) + HEADER)
        time.sleep(2.0)
        link.reset_input_buffer()
        for command in args.command:
            link.write((command.strip() + "\n").encode("ascii"))
            time.sleep(0.2)

        deadline = time.monotonic() + args.duration
        while time.monotonic() < deadline:
            raw = link.readline().decode("ascii", errors="replace").strip()
            if not raw or raw.startswith("ms,state,"):
                continue
            fields = raw.split(",")
            if len(fields) != len(HEADER):
                print(f"ignored malformed line: {raw}", file=sys.stderr)
                continue
            host_stamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            writer.writerow((host_stamp,) + tuple(fields))
            stream.flush()
            print(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
