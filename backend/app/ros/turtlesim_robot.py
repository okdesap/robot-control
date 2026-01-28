"""
Turtlesim Backend
"""
import threading
from geometry_msgs.msg import Twist

from app.core.models.command import (
    Command,
    ForwardCommand,
    StopCommand,
    TurnLeftCommand,
    TurnRightCommand,
)
from app.ros.ros_hal import RosRobotBase


class TurtlesimRobot(RosRobotBase):

    TOPIC = "/turtle1/cmd_vel"

    def __init__(self) -> None:
        super().__init__(self.TOPIC, Twist)

    def execute_command(self, cmd: Command, cancel_event: threading.Event | None = None):
        if isinstance(cmd, StopCommand):
            self.stop()
            return

        msg = Twist()
        duration_s = 0.0

        if isinstance(cmd, ForwardCommand):
            msg.linear.x = float(cmd.velocity)
            msg.angular.z = 0.0
            duration_s = cmd.duration_s
        elif isinstance(cmd, TurnLeftCommand):
            msg.linear.x = 0.0
            msg.angular.z = float(cmd.angular_velocity)
            duration_s = cmd.duration_s
        elif isinstance(cmd, TurnRightCommand):
            msg.linear.x = 0.0
            msg.angular.z = -float(cmd.angular_velocity)
            duration_s = cmd.duration_s
        else:
            raise ValueError(f"Unsupported command: {type(cmd).__name__}")

        self._publish_for(msg, duration_s, cancel_event)

    def stop(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self._publish(msg)
