"""Synthesized audio: chiptune music, engine hum, and crash SFX.

Sounds are generated procedurally so the game runs with zero external
assets (per agent.md: handle missing asset fallbacks gracefully).
If the audio device is unavailable, the manager degrades to a no-op.
"""

import array
import math
import random
from typing import Optional, Sequence, Tuple

import pygame

SAMPLE_RATE: int = 44100

# Simple A-minor arpeggio loop (frequency Hz, duration ms)
_MELODY: Sequence[Tuple[float, int]] = (
    (440.00, 150), (523.25, 150), (659.25, 150), (880.00, 150),
    (659.25, 150), (523.25, 150), (440.00, 150), (349.23, 150),
    (392.00, 150), (493.88, 150), (587.33, 150), (783.99, 150),
    (587.33, 150), (493.88, 150), (392.00, 150), (329.63, 150),
)


def _pcm_bytes(mono: array.array) -> Optional[bytes]:
    """Interleave mono 16-bit samples to match the active mixer format."""
    info = pygame.mixer.get_init()
    if info is None or info[1] != -16:
        return None
    channels: int = info[2]
    pcm = array.array("h")
    for sample in mono:
        for _ in range(channels):
            pcm.append(sample)
    return pcm.tobytes()


def _make_sound(mono: array.array) -> Optional[pygame.mixer.Sound]:
    data = _pcm_bytes(mono)
    if data is None:
        return None
    try:
        return pygame.mixer.Sound(buffer=data)
    except pygame.error:
        return None


def _music_sound() -> Optional[pygame.mixer.Sound]:
    """Square-wave chiptune melody (2.4-second loop)."""
    mono = array.array("h")
    volume: float = 0.20
    for freq, ms in _MELODY:
        count: int = int(SAMPLE_RATE * ms / 1000)
        step: float = 2.0 * math.pi * freq / SAMPLE_RATE
        for i in range(count):
            envelope: float = 1.0 - (i / count) * 0.35
            wave: float = 1.0 if math.sin(step * i) >= 0.0 else -1.0
            mono.append(int(wave * envelope * volume * 32767))
    return _make_sound(mono)


def _engine_sound() -> Optional[pygame.mixer.Sound]:
    """Low sine hum (1-second seamless loop) for the engine."""
    mono = array.array("h")
    volume: float = 0.10
    for i in range(SAMPLE_RATE):
        t: float = i / SAMPLE_RATE
        value: float = (
            0.7 * math.sin(2.0 * math.pi * 55.0 * t)
            + 0.3 * math.sin(2.0 * math.pi * 110.0 * t)
        )
        mono.append(int(value * volume * 32767))
    return _make_sound(mono)


def _crash_sound() -> Optional[pygame.mixer.Sound]:
    """Decaying white-noise burst for collisions."""
    mono = array.array("h")
    volume: float = 0.55
    count: int = int(SAMPLE_RATE * 0.45)
    for i in range(count):
        decay: float = math.exp(-6.0 * i / count)
        noise: float = random.uniform(-1.0, 1.0)
        mono.append(int(noise * decay * volume * 32767))
    return _make_sound(mono)


class AudioManager:
    """Procedural audio manager with graceful no-op fallback."""

    def __init__(self) -> None:
        self.enabled: bool = False
        self._music: Optional[pygame.mixer.Sound] = None
        self._engine: Optional[pygame.mixer.Sound] = None
        self._crash: Optional[pygame.mixer.Sound] = None
        self._engine_channel: Optional[pygame.mixer.Channel] = None

    def initialize(self) -> None:
        """Initialize the mixer, synthesize sounds, start music loop."""
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(
                    frequency=SAMPLE_RATE, size=-16,
                    channels=2, buffer=1024,
                )
            self._music = _music_sound()
            self._engine = _engine_sound()
            self._crash = _crash_sound()
            self.enabled = self._music is not None
        except (pygame.error, OSError):
            self.enabled = False

        if self.enabled and self._music is not None:
            self._music.set_volume(0.35)
            self._music.play(loops=-1)

    def start_engine(self) -> None:
        """Start the looping engine hum (idempotent)."""
        if not self.enabled or self._engine is None:
            return
        self._engine.set_volume(0.5)
        if self._engine_channel is None or not self._engine_channel.get_busy():
            self._engine_channel = self._engine.play(loops=-1)

    def stop_engine(self) -> None:
        """Stop the engine hum."""
        if self._engine_channel is not None:
            self._engine_channel.stop()
            self._engine_channel = None

    def play_crash(self) -> None:
        """Play the crash sound effect (once)."""
        if not self.enabled or self._crash is None:
            return
        self._crash.set_volume(0.8)
        self._crash.play()

    def shutdown(self) -> None:
        """Stop all audio channels."""
        self.stop_engine()
        if self._music is not None:
            self._music.stop()