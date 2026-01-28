"""
TurtleBot Backend
"""
import threading
from geometry_msgs.msg import TwistStamped

from app.core.models.command import (
    Command,
    ForwardCommand,
    StopCommand,
    TurnLeftCommand,
    TurnRightCommand,
)
from app.ros.ros_hal import RosRobotBase


class TurtleBotRobot(RosRobotBase):

    TOPIC = "/cmd_vel"

    def __init__(self) -> None:
        super().__init__(self.TOPIC, TwistStamped)

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
        else:
            raise ValueError(f"Unsupported command: {type(cmd).__name__}")

        self._publish_for(msg, duration_s, cancel_event)

    def stop(self):
        msg = TwistStamped()
        msg.twist.linear.x = 0.0
        msg.twist.angular.z = 0.0
        self._publish(msg)