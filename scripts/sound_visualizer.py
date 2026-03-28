##
## EPITECH PROJECT, 2025
## Pharmalgo
## File description:
## sound_visualizer.py
##

#!/usr/bin/env python3
"""
Real-time sound visualizer for the pharmacy cross LED display.

Each panel represents a frequency band, with bars growing outward from
the center of the cross:

        [TOP]  treble  6k-20kHz
  [LEFT] bass  [CENTER] mid  [RIGHT] high-mid
        [BOTTOM] sub-bass 20-80Hz

Requirements:
    pip install sounddevice numpy
"""

import socket
import json
import sys
import numpy as np
import sounddevice as sd

UDP_HOST = "127.0.0.1"
UDP_PORT = 1337

SAMPLE_RATE = 44100
CHUNK = 2048

PANEL_OFFSETS = {
    "top": (0, 8),
    "left": (8, 0),
    "center": (8, 8),
    "right": (8, 16),
    "bottom": (16, 8),
}

FREQ_BANDS = {
    "top": (4000, 20000),  # Treble
    "right": (800, 4000),   # High-mid
    "bottom": (150, 800),    # Mid
    "left": (20, 150),    # Bass
    # center intentionally absent - stays dark
}

BAR_DIRECTION = {
    "top":    "up",
    "bottom": "down",
    "left":   "left",
    "right":  "right",
}

SMOOTHING = 0.65
PEAK_DECAY = 0.993


def make_panel(level: float, direction: str) -> list:
    """
    Build an 8x8 panel with 4 discrete blocks growing outward from the cross center.
    Blocks are separated by 1-pixel gaps. Each block is full-width x 1 pixel (or
    full-height x 1 pixel for horizontal bars).

    Block positions (root = nearest to cross center):
      up/down   : rows 7, 5, 3, 1  (gaps at 6, 4, 2, 0)
      left/right: cols 7, 5, 3, 1  (gaps at 6, 4, 2, 0)
    """
    N = 4
    panel = [[0] * 8 for _ in range(8)]
    lit = int(round(level * N))
    if lit == 0:
        return panel

    block_positions = [7 - seg * 2 for seg in range(N)]

    for seg in range(lit):
        pos = block_positions[seg]
        brightness = max(3, 7 - seg)

        if direction == "up":
            for col in range(8):
                panel[pos][col] = brightness

        elif direction == "down":
            row = 7 - pos
            for col in range(8):
                panel[row][col] = brightness

        elif direction == "left":
            for row in range(8):
                panel[row][pos] = brightness

        elif direction == "right":
            col = 7 - pos
            for row in range(8):
                panel[row][col] = brightness

    return panel


def band_energy(magnitudes: np.ndarray, freq_min: float, freq_max: float) -> float:
    """RMS energy for a frequency band."""
    res = SAMPLE_RATE / CHUNK
    b_min = max(0, int(freq_min / res))
    b_max = min(len(magnitudes), int(freq_max / res) + 1)
    if b_min >= b_max:
        return 0.0
    return float(np.sqrt(np.mean(magnitudes[b_min:b_max] ** 2)))


def panels_to_frame(panels: dict) -> list:
    frame = [[0] * 24 for _ in range(24)]
    for name, (row_off, col_off) in PANEL_OFFSETS.items():
        p = panels.get(name)
        for row in range(8):
            for col in range(8):
                frame[row_off + row][col_off + col] = p[row][col] if p else 0
    return frame


_smoothed = {name: 0.0 for name in PANEL_OFFSETS}
_peak = {name: 1e-6 for name in PANEL_OFFSETS}
_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def audio_callback(indata, frames, time_info, status):
    audio = indata[:, 0]

    windowed = audio * np.hanning(len(audio))
    fft = np.fft.rfft(windowed)
    magnitudes = np.abs(fft) / CHUNK

    panels = {}
    for name, (fmin, fmax) in FREQ_BANDS.items():
        raw = band_energy(magnitudes, fmin, fmax)

        _peak[name] = max(_peak[name] * PEAK_DECAY, raw, 1e-6)
        normalized  = min(raw / _peak[name], 1.0)

        _smoothed[name] = SMOOTHING * _smoothed[name] + (1.0 - SMOOTHING) * normalized

        panels[name] = make_panel(_smoothed[name], BAR_DIRECTION[name])

    frame   = panels_to_frame(panels)
    payload = json.dumps(frame).encode("utf-8")
    _sock.sendto(payload, (UDP_HOST, UDP_PORT))


def main():
    print("╔══════════════════════════════════════╗")
    print("║   Sound Visualizer — Pharmacy Cross  ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("Frequency bands:")
    for name, (fmin, fmax) in FREQ_BANDS.items():
        print(f"  {name:8s} → {fmin:5d} - {fmax:6d} Hz  [{BAR_DIRECTION[name]}]")
    print()
    print("Ctrl+C to stop.")
    print()

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=CHUNK,
            callback=audio_callback,
        ):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\nStopped — clearing display.")
        blank = json.dumps([[0] * 24 for _ in range(24)]).encode()
        _sock.sendto(blank, (UDP_HOST, UDP_PORT))
    except sd.PortAudioError as e:
        print(f"Audio error: {e}", file=sys.stderr)
        print("Check that a microphone is connected and accessible.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
