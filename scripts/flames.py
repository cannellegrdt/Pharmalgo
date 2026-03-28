##
## EPITECH PROJECT, 2025
## Pharmalgo
## File description:
## flames.py
##

#!/usr/bin/env python3
"""
Infinite fire/flames effect for the pharmacy cross LED display.

Classic "doom fire" algorithm: each cell's heat diffuses upward with
slight horizontal drift and random cooling, producing realistic-looking flames.

Cross layout (24x24 grid, 5 panels of 8x8):
    cols 8-15 : rows 0-7   (TOP)
    cols 0-7  : rows 8-15  (LEFT)
    cols 8-15 : rows 8-15  (CENTER)
    cols 16-23: rows 8-15  (RIGHT)
    cols 8-15 : rows 16-23 (BOTTOM)
"""

import json
import random
import socket
import time

UDP_HOST = "127.0.0.1"
UDP_PORT = 1337

FPS = 20
MAX_HEAT = 7

COLUMN_RANGES = {
    **{c: (8, 16) for c in range(0, 8)},
    **{c: (0, 24) for c in range(8, 16)},
    **{c: (8, 16) for c in range(16, 24)},
}

CROSS_CELLS = {
    (row, col)
    for col, (rmin, rmax) in COLUMN_RANGES.items()
    for row in range(rmin, rmax)
}


def make_grid() -> dict:
    """Heat map: cell -> float heat in [0, MAX_HEAT]."""
    return {cell: 0.0 for cell in CROSS_CELLS}


def ignite(heat: dict):
    """Keep the bottom row of each column at full heat."""
    for col, (rmin, rmax) in COLUMN_RANGES.items():
        bottom = rmax - 1
        heat[(bottom, col)] = MAX_HEAT * (0.85 + random.random() * 0.15)


def spread(heat: dict):
    """Propagate heat upward with drift and cooling (Doom fire algorithm)."""
    new_heat = dict(heat)

    for (row, col), _ in heat.items():
        rmin, rmax = COLUMN_RANGES[col]
        if row == rmax - 1:
            continue

        drift = random.randint(-1, 1)
        src_col = col + drift
        src_cell = (row + 1, src_col)

        if src_cell in heat:
            src_heat = heat[src_cell]
        else:
            src_heat = heat.get((row + 1, col), 0.0)

        cooling = random.uniform(0.5, 1.5)
        new_heat[(row, col)] = max(0.0, src_heat - cooling)

    return new_heat


def render(heat: dict) -> list:
    frame = [[0] * 24 for _ in range(24)]
    for (row, col), h in heat.items():
        frame[row][col] = round(h)
    return frame


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    heat = make_grid()

    print("╔══════════════════════════════════════╗")
    print("║      Flames - Pharmacy Cross         ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("Ctrl+C to stop.")

    interval = 1.0 / FPS
    try:
        while True:
            ignite(heat)
            heat = spread(heat)
            payload = json.dumps(render(heat)).encode("utf-8")
            sock.sendto(payload, (UDP_HOST, UDP_PORT))
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nStopped - clearing display.")
        blank = json.dumps([[0] * 24 for _ in range(24)]).encode()
        sock.sendto(blank, (UDP_HOST, UDP_PORT))


if __name__ == "__main__":
    main()
