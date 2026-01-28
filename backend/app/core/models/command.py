"""
Command data models used internally before mapping to ROS messages.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Command:
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class StopCommand(Command):
    pass


@dataclass(frozen=True)
class ForwardCommand(Command):
    velocity: float = 1.0
    duration_s: float = 1.0


@dataclass(frozen=True)
class TurnLeftCommand(Command):
    angular_velocity: float = 1.5
    duration_s: float = 1.0


@dataclass(frozen=True)
class TurnRightCommand(Command):
    angular_velocity: float = 1.5
    duration_s: float = 1.0
