"""Player actions supported by the basic round engine."""

from enum import StrEnum


class Action(StrEnum):
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"
    SURRENDER = "surrender"
