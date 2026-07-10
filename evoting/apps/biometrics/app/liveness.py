"""Baseline liveness / presentation-attack-detection (PAD) primitives.

The heuristic implementation here is a deterministic, ML-free STAND-IN for a
real PAD system. It only checks that the caller supplied multiple, non-identical
frames (i.e. that *some* motion is present) in response to a challenge. It does
NOT actually validate that the requested action (blink / turn / smile) was
performed, nor does it defend against replay or deepfake attacks. Replace
``HeuristicLiveness`` with a real PAD model before any production deployment.
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from typing import Protocol, runtime_checkable

CHALLENGES: tuple[str, ...] = ("blink", "turn_left", "turn_right", "smile")


def new_challenge() -> tuple[str, str]:
    """Return a ``(challenge_id, challenge)`` pair using cryptographic randomness."""

    return uuid.uuid4().hex, secrets.choice(CHALLENGES)


@runtime_checkable
class LivenessChecker(Protocol):
    """Contract for liveness checkers."""

    def check(self, frames: list[bytes], challenge: str) -> tuple[bool, float]:
        """Return ``(passed, score)`` for the given frames and challenge."""
        ...


class HeuristicLiveness:
    """Motion-presence heuristic stand-in for a real PAD model.

    Passing criterion: at least ``min_frames`` frames were supplied and at least
    two of them are distinct (by content hash). The score scales with the number
    of distinct frames, saturating at 1.0. A single frame, or frames that are all
    identical, fails with a low score.
    """

    def __init__(self, min_frames: int = 2) -> None:
        if min_frames < 2:
            raise ValueError("min_frames must be at least 2")
        self._min_frames = min_frames

    def check(self, frames: list[bytes], challenge: str) -> tuple[bool, float]:
        # ``challenge`` is accepted for interface parity with real PAD models,
        # which would validate that the specific action was performed.
        del challenge

        non_empty = [frame for frame in frames if frame]
        if len(non_empty) < self._min_frames:
            return False, 0.0

        distinct = {hashlib.sha256(frame).hexdigest() for frame in non_empty}
        distinct_count = len(distinct)
        if distinct_count < 2:
            return False, 0.1

        # Two distinct frames -> ~0.6; each additional distinct frame adds 0.2.
        score = min(1.0, 0.6 + 0.2 * (distinct_count - 2))
        return True, round(score, 4)
