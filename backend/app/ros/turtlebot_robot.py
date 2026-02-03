"""
TurtleBot Backend
"""
import os
import threading
import time
from typing import Any

from geometry_msgs.msg import Twist

from app.core.models.command import (
    Command,
    DockCommand,
    ForwardCommand,
    NavigateToPoseCommand,
    StopCommand,
    TurnLeftCommand,
    TurnRightCommand,
    UndockCommand,
)
from app.ros.ros_hal import RosRobotBase


class TurtleBotRobot(RosRobotBase):

    CMD_VEL_TOPIC = "/cmd_vel"
    ODOM_TOPIC = "/odom"
    BATTERY_TOPIC = "/battery_state"
    CAMERA_TOPIC = "/camera/image_raw"
    MAP_TOPIC = "/map"
    NAV_STATUS_TOPIC = "/navigate_to_pose/_action/status"

    NAV2_ACTIVE_TIMEOUT_S = 2.0  # Reduced from 15.0 to fail faster if Nav2 is not available
    NAV2_TASK_TIMEOUT_S = 180.0

    def __init__(self) -> None:
        cmd_vel_topic = os.getenv("CMD_VEL_TOPIC", self.CMD_VEL_TOPIC)
        cmd_vel_type = (os.getenv("CMD_VEL_MSG_TYPE", "TwistStamped") or "TwistStamped").strip()

        # Important: ROS2 requires publisher/subscriber message types to match exactly.
        # TurtleBot4 uses TwistStamped on /cmd_vel with BEST_EFFORT QoS.
        msg_type: Any
        if cmd_vel_type.lower() in {"twiststamped", "stamped"}:
            from geometry_msgs.msg import TwistStamped  # type: ignore
            msg_type = TwistStamped
            self._cmd_vel_kind = "TwistStamped"
        else:
            msg_type = Twist
            self._cmd_vel_kind = "Twist"

        super().__init__(cmd_vel_topic, msg_type)

        self._last_odom = None
        self._last_battery = None
        self._last_image = None
        self._last_map = None
        self._last_nav_status = None

        try:
            from nav_msgs.msg import Odometry
            self.register_subscription("odom", self.ODOM_TOPIC, Odometry, self._on_odom)
        except Exception:
            pass

        try:
            from sensor_msgs.msg import BatteryState
            self.register_subscription("battery", self.BATTERY_TOPIC, BatteryState, self._on_battery)
        except Exception:
            pass

        try:
            from sensor_msgs.msg import Image
            self.register_subscription("camera", self.CAMERA_TOPIC, Image, self._on_image)
        except Exception:
            pass

        try:
            from nav_msgs.msg import OccupancyGrid
            self.register_subscription("map", self.MAP_TOPIC, OccupancyGrid, self._on_map)
        except Exception:
            pass

        try:
            from action_msgs.msg import GoalStatusArray
            self.register_subscription("nav_status", self.NAV_STATUS_TOPIC, GoalStatusArray, self._on_nav_status)
        except Exception:
            pass

        self._navigator = None
        self._navigator_lock = threading.RLock()

    def _get_navigator(self):
        with self._navigator_lock:
            if self._navigator is not None:
                return self._navigator
            try:
                from turtlebot4_navigation.turtlebot4_navigator import TurtleBot4Navigator
            except Exception as exc:
                raise RuntimeError(
                    "Nav2 navigator not available. Install turtlebot4_navigation and Nav2." 
                    f" Original error: {exc}"
                )
            self._navigator = TurtleBot4Navigator()
            return self._navigator

    def _env_float(self, name: str, default: float) -> float:
        try:
            return float(os.getenv(name, str(default)))
        except Exception:
            return default

    def _env_bool(self, name: str, default: bool = False) -> bool:
        raw = os.getenv(name)
        if raw is None:
            return default
        return raw.strip().lower() in {"1", "true", "yes", "on"}

    def _wait_for_nav2_active(
        self,
        navigator,
        cancel_event: threading.Event | None,
        timeout_s: float,
    ) -> None:
        if cancel_event is not None and cancel_event.is_set():
            raise RuntimeError("Cancelled")

        # Best effort: use a timeout parameter if the navigator supports it.
        for kw in ("timeout_sec", "timeout_s", "timeout"):
            try:
                navigator.waitUntilNav2Active(**{kw: timeout_s})
                return
            except TypeError:
                pass

        # Fallback: run the blocking call in a helper thread and enforce timeout.
        done = threading.Event()
        err: list[Exception] = []

        def _run() -> None:
            try:
                navigator.waitUntilNav2Active()
            except Exception as exc:
                err.append(exc)
            finally:
                done.set()

        t = threading.Thread(target=_run, name="nav2-wait", daemon=True)
        t.start()

        start = time.time()
        while not done.is_set():
            if cancel_event is not None and cancel_event.is_set():
                raise RuntimeError("Cancelled")
            if time.time() - start > timeout_s:
                raise TimeoutError("Nav2 not active (timeout)")
            time.sleep(0.1)

        if err:
            raise RuntimeError(f"Nav2 activation failed: {err[0]}")

    def _wait_task_complete(
        self,
        navigator,
        cancel_event: threading.Event | None,
        timeout_s: float,
    ) -> None:
        start = time.time()
        while not navigator.isTaskComplete():
            if cancel_event is not None and cancel_event.is_set():
                try:
                    navigator.cancelTask()
                except Exception:
                    pass
                return
            if time.time() - start > timeout_s:
                try:
                    navigator.cancelTask()
                except Exception:
                    pass
                raise TimeoutError("Nav2 task did not complete (timeout)")
            time.sleep(0.1)

    def _on_odom(self, msg) -> None:
        self._last_odom = msg

    def _on_battery(self, msg) -> None:
        self._last_battery = msg

    def _on_image(self, msg) -> None:
        self._last_image = msg

    def _on_map(self, msg) -> None:
        self._last_map = msg

    def _on_nav_status(self, msg) -> None:
        self._last_nav_status = msg

    def get_last_odom(self):
        return self._last_odom

    def get_last_battery(self):
        return self._last_battery

    def get_last_image(self):
        return self._last_image

    def get_last_map(self):
        return self._last_map

    def get_last_nav_status(self):
        return self._last_nav_status

    def get_docking_status(self) -> dict:
        try:
            navigator = self._get_navigator()
        except Exception as exc:
            return {"available": False, "reason": str(exc)}

        missing = [name for name in ("dock", "undock") if not hasattr(navigator, name)]
        if missing:
            return {"available": False, "reason": f"Navigator missing: {', '.join(missing)}"}

        nav2_required = self._env_bool("DOCK_REQUIRE_NAV2", False)
        active_timeout = self._env_float("NAV2_ACTIVE_TIMEOUT_S", self.NAV2_ACTIVE_TIMEOUT_S)
        quick_timeout = min(2.0, float(active_timeout))

        try:
            self._wait_for_nav2_active(navigator, None, quick_timeout)
            nav2_active = True
        except Exception as exc:
            nav2_active = False
            if nav2_required:
                return {"available": False, "reason": f"Nav2 not active: {exc}"}

        return {"available": True, "nav2_active": nav2_active}

    def execute_command(self, cmd: Command, cancel_event: threading.Event | None = None):
        if isinstance(cmd, StopCommand):
            self.stop()
            return

        # For movement commands (forward, turn), publish directly without waiting for Nav2
        msg = self._new_cmd_vel_msg()
        duration_s = 0.0

        if isinstance(cmd, ForwardCommand):
            self._set_cmd_vel(msg, linear_x=float(cmd.velocity), angular_z=0.0)
            duration_s = cmd.duration_s
        elif isinstance(cmd, TurnLeftCommand):
            self._set_cmd_vel(msg, linear_x=0.0, angular_z=float(cmd.angular_velocity))
            duration_s = cmd.duration_s
        elif isinstance(cmd, TurnRightCommand):
            self._set_cmd_vel(msg, linear_x=0.0, angular_z=-float(cmd.angular_velocity))
            duration_s = cmd.duration_s
        elif isinstance(cmd, NavigateToPoseCommand):
            self._navigate_to_pose(cmd, cancel_event)
            return
        elif isinstance(cmd, DockCommand):
            self._dock(cancel_event)
            return
        elif isinstance(cmd, UndockCommand):
            self._undock(cancel_event)
            return
        else:
            raise ValueError(f"Unsupported command: {type(cmd).__name__}")

        # Publish the movement command
        self._publish_for(msg, duration_s, cancel_event)

    def stop(self):
        msg = self._new_cmd_vel_msg()
        self._set_cmd_vel(msg, linear_x=0.0, angular_z=0.0)
        self._publish(msg)

    def _new_cmd_vel_msg(self):
        if getattr(self, "_cmd_vel_kind", "Twist") == "TwistStamped":
            from geometry_msgs.msg import TwistStamped  # type: ignore
            return TwistStamped()
        return Twist()

    def _set_cmd_vel(self, msg, linear_x: float, angular_z: float) -> None:
        # Supports Twist and TwistStamped.
        if hasattr(msg, "twist"):
            msg.twist.linear.x = float(linear_x)
            msg.twist.angular.z = float(angular_z)
        else:
            msg.linear.x = float(linear_x)
            msg.angular.z = float(angular_z)

    def _navigate_to_pose(self, cmd: NavigateToPoseCommand, cancel_event: threading.Event | None = None) -> None:
        navigator = self._get_navigator()
        active_timeout = self._env_float("NAV2_ACTIVE_TIMEOUT_S", self.NAV2_ACTIVE_TIMEOUT_S)
        task_timeout = self._env_float("NAV2_TASK_TIMEOUT_S", self.NAV2_TASK_TIMEOUT_S)
        self._wait_for_nav2_active(navigator, cancel_event, active_timeout)
        goal_pose = navigator.getPoseStamped([cmd.x, cmd.y], cmd.yaw_deg)
        navigator.startToPose(goal_pose)
        self._wait_task_complete(navigator, cancel_event, task_timeout)

    def _dock(self, cancel_event: threading.Event | None = None) -> None:
        try:
            navigator = self._get_navigator()
            active_timeout = self._env_float("NAV2_ACTIVE_TIMEOUT_S", self.NAV2_ACTIVE_TIMEOUT_S)
            task_timeout = self._env_float("NAV2_TASK_TIMEOUT_S", self.NAV2_TASK_TIMEOUT_S)
            if self._env_bool("DOCK_REQUIRE_NAV2", False):
                self._wait_for_nav2_active(navigator, cancel_event, active_timeout)
            navigator.dock()
            self._wait_task_complete(navigator, cancel_event, task_timeout)
        except Exception as e:
            import logging
            logger = logging.getLogger("backend.core.turtlebot")
            logger.warning("Dock command failed (Nav2 may not be available): %s", str(e))
            # Don't raise - just log and continue

    def _undock(self, cancel_event: threading.Event | None = None) -> None:
        try:
            navigator = self._get_navigator()
            active_timeout = self._env_float("NAV2_ACTIVE_TIMEOUT_S", self.NAV2_ACTIVE_TIMEOUT_S)
            task_timeout = self._env_float("NAV2_TASK_TIMEOUT_S", self.NAV2_TASK_TIMEOUT_S)
            if self._env_bool("DOCK_REQUIRE_NAV2", False):
                self._wait_for_nav2_active(navigator, cancel_event, active_timeout)
            navigator.undock()
            self._wait_task_complete(navigator, cancel_event, task_timeout)
        except Exception as e:
            import logging
            logger = logging.getLogger("backend.core.turtlebot")
            logger.warning("Undock command failed (Nav2 may not be available): %s", str(e))
            # Don't raise - just log and continue