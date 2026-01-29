"""
TurtleBot Backend
"""
import threading
import time
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry

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

    def __init__(self) -> None:
        super().__init__(self.CMD_VEL_TOPIC, TwistStamped)

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

    def execute_command(self, cmd: Command, cancel_event: threading.Event | None = None):
        if isinstance(cmd, StopCommand):
            self.stop()
            return

        msg = TwistStamped()
        duration_s = 0.0

        if isinstance(cmd, ForwardCommand):
            msg.twist.linear.x = float(cmd.velocity)
            msg.twist.angular.z = 0.0
            duration_s = cmd.duration_s
        elif isinstance(cmd, TurnLeftCommand):
            msg.twist.linear.x = 0.0
            msg.twist.angular.z = float(cmd.angular_velocity)
            duration_s = cmd.duration_s
        elif isinstance(cmd, TurnRightCommand):
            msg.twist.linear.x = 0.0
            msg.twist.angular.z = -float(cmd.angular_velocity)
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

        self._publish_for(msg, duration_s, cancel_event)

    def stop(self):
        msg = TwistStamped()
        msg.twist.linear.x = 0.0
        msg.twist.angular.z = 0.0
        self._publish(msg)

    def _navigate_to_pose(self, cmd: NavigateToPoseCommand, cancel_event: threading.Event | None = None) -> None:
        navigator = self._get_navigator()
        navigator.waitUntilNav2Active()
        goal_pose = navigator.getPoseStamped([cmd.x, cmd.y], cmd.yaw_deg)
        navigator.startToPose(goal_pose)

        while not navigator.isTaskComplete():
            if cancel_event is not None and cancel_event.is_set():
                try:
                    navigator.cancelTask()
                except Exception:
                    pass
                break
            time.sleep(0.1)

    def _dock(self, cancel_event: threading.Event | None = None) -> None:
        navigator = self._get_navigator()
        navigator.waitUntilNav2Active()
        navigator.dock()

        while not navigator.isTaskComplete():
            if cancel_event is not None and cancel_event.is_set():
                try:
                    navigator.cancelTask()
                except Exception:
                    pass
                break
            time.sleep(0.1)

    def _undock(self, cancel_event: threading.Event | None = None) -> None:
        navigator = self._get_navigator()
        navigator.waitUntilNav2Active()
        navigator.undock()

        while not navigator.isTaskComplete():
            if cancel_event is not None and cancel_event.is_set():
                try:
                    navigator.cancelTask()
                except Exception:
                    pass
                break
            time.sleep(0.1)