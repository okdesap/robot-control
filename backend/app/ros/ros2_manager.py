"""ROS2 manager for publishing Twist commands.

This keeps ROS2-specific imports and lifecycle contained in the ros layer.

Notes (Windows): ROS2 Python packages (rclpy, geometry_msgs) typically come
from the ROS2 installation, not conda. If they are unavailable, this module
will raise a clear error when used.
"""

from __future__ import annotations

import threading
from typing import Optional


class ROS2NotAvailableError(RuntimeError):
    pass


class ROS2Publisher:
    """Base class for ROS2 publishers"""

    def __init__(self, topic: str, msg_type) -> None:
        self._topic = topic
        self._msg_type = msg_type
        self._lock = threading.RLock()
        self._spin_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Deferred imports so the rest of the backend runs without ROS2.
        try:
            import rclpy  # type: ignore
            from rclpy.node import Node  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise ROS2NotAvailableError(
                "ROS2 Python packages not available. "
                "Ensure ROS2 is installed and its environment is sourced so 'import rclpy' works. "
                f"Original error: {exc}"
            )

        self._rclpy = rclpy
    

        if not self._rclpy.ok():
            self._rclpy.init(args=None)

        topic_name = self._topic.replace("/", "_").strip("_")
        self._node: Node = Node(f"backend_publisher_{topic_name}")

        self._pub = self._node.create_publisher(self._msg_type, self._topic, 10)

        self._ensure_spinning()

    def _ensure_spinning(self) -> None:
        with self._lock:
            if self._spin_thread and self._spin_thread.is_alive():
                return

            self._stop_event.clear()

            def _spin() -> None:
                while not self._stop_event.is_set() and self._rclpy.ok():
                    self._rclpy.spin_once(self._node, timeout_sec=0.1)

            self._spin_thread = threading.Thread(target=_spin, name="ros2-spin", daemon=True)
            self._spin_thread.start()

    def shutdown(self) -> None:
        with self._lock:
            self._stop_event.set()
            try:
                self._node.destroy_node()
            finally:
                if self._rclpy.ok():
                    self._rclpy.shutdown()

    def now(self):
        return self._node.get_clock().now().to_msg()

    def publish(self, msg) -> None:
        self._pub.publish(msg)

    def create_subscription(self, topic: str, msg_type, callback, qos: int = 10):
        return self._node.create_subscription(msg_type, topic, callback, qos)


_publishers: dict[tuple[str, object], ROS2Publisher] = {}


def get_publisher(topic_name: str, msg_type) -> ROS2Publisher:
    key = (topic_name, msg_type)
    if key not in _publishers:
        print(f"Creating new ROS2Publisher for topic: {topic_name} with msg_type: {msg_type}")
        _publishers[key] = ROS2Publisher(topic=topic_name, msg_type=msg_type)
    return _publishers[key]