"""ROS HAL base classes to keep ROS specifics out of core."""
from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod

from app.ros.robot_interface import RobotInterface
from app.ros.ros2_manager import ROS2Publisher, get_publisher


class RosRobotBase(RobotInterface, ABC):
    """Base class for ROS-backed robots.

    Provides shared publishing and optional subscriptions.
    """

    def __init__(self, topic: str, msg_type, default_key: str = "cmd_vel") -> None:
        self._default_key = default_key
        self._publishers: dict[str, ROS2Publisher] = {}
        self._subscriptions: dict[str, object] = {}
        self.register_publisher(default_key, topic, msg_type)

    def register_publisher(self, key: str, topic: str, msg_type) -> None:
        self._publishers[key] = get_publisher(topic, msg_type)

    def register_subscription(self, key: str, topic: str, msg_type, callback, qos: int = 10) -> None:
        publisher = self._publishers[self._default_key]
        self._subscriptions[key] = publisher.create_subscription(topic, msg_type, callback, qos)

    def _publisher(self, key: str | None = None) -> ROS2Publisher:
        return self._publishers[key or self._default_key]

    def _refresh_timestamp(self, msg, key: str | None = None) -> None:
        if hasattr(msg, "header"):
            msg.header.stamp = self._publisher(key).now()

    def _publish(self, msg, key: str | None = None) -> None:
        self._refresh_timestamp(msg, key)
        self._publisher(key).publish(msg)

    def _publish_for(
        self,
        msg,
        duration_s: float,
        cancel_event: threading.Event | None = None,
        key: str | None = None,
    ) -> None:
        """Publish a message for the given duration, then stop."""
        end = time.time() + max(0.0, float(duration_s))
        if duration_s <= 0:
            self._publish(msg, key)
            self.stop()
            return

        while time.time() < end:
            if cancel_event is not None and cancel_event.is_set():
                break
            self._publish(msg, key)
            time.sleep(0.05)

        self.stop()

    @abstractmethod
    def stop(self) -> None:
        """Stop the robot (publish zero velocity)."""
        raise NotImplementedError
