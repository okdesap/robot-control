"""
ROS HAL base classes to keep ROS specifics out of core.
"""
from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod

from app.ros.robot_interface import RobotInterface
from app.ros.ros2_manager import ROS2Publisher, get_publisher


class RosRobotBase(RobotInterface, ABC):
    """Base class for ROS-backed robots.

    Handles publisher lifecycle and time-based publishing.
    """

    def __init__(self, topic: str, msg_type) -> None:
        self._topic = topic
        self._msg_type = msg_type
        self._publisher: ROS2Publisher = get_publisher(topic, msg_type)

    def _refresh_timestamp(self, msg) -> None:
        if hasattr(msg, "header"):
            msg.header.stamp = self._publisher.now()

    def _publish(self, msg) -> None:
        self._refresh_timestamp(msg)
        self._publisher.publish(msg)

    def _publish_for(self, msg, duration_s: float, cancel_event: threading.Event | None = None) -> None:
        """Publish a message for the given duration, then stop."""
        end = time.time() + max(0.0, float(duration_s))
        if duration_s <= 0:
            self._publish(msg)
            self.stop()
            return

        while time.time() < end:
            if cancel_event is not None and cancel_event.is_set():
                break
            self._publish(msg)
            time.sleep(0.05)

        self.stop()

    @abstractmethod
    def stop(self) -> None:
        """Stop the robot (publish zero velocity)."""
        raise NotImplementedError
