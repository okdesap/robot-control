"""
Turtlesim Backend
"""
import threading
from geometry_msgs.msg import Twist
from app.ros.robot_interface import RobotInterface
from app.ros.ros2_manager import TwistCommand, get_publisher


class TurtlesimRobot(RobotInterface):

    TOPIC = "/turtle1/cmd_vel"

    def _publish(self, cmd: TwistCommand, cancel_event: threading.Event | None = None):
        pub = get_publisher(self.TOPIC, Twist)

        msg = Twist()
        msg.linear.x = float(cmd.linear_x)
        msg.angular.z = float(cmd.angular_z)
        pub.publish_for(msg, cmd.duration_s, cancel_event)
    
    def move_forward(self, duration: float, cancel_event: threading.Event | None = None):
        self._publish(TwistCommand(1.0, 0.0, duration), cancel_event)
    
    def turn_left(self, duration: float, cancel_event: threading.Event | None = None):
        self._publish(TwistCommand(0.0, 1.5, duration), cancel_event)
    
    def turn_right(self, duration: float, cancel_event: threading.Event | None = None):
        self._publish(TwistCommand(0.0, -1.5, duration), cancel_event)
    
    def stop(self):
        pub = get_publisher(self.TOPIC, Twist)
        pub.stop()
