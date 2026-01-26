"""
Turtlesim Backend
"""
import threading
from app.ros.robot_interface import RobotInterface
from app.ros.ros2_manager import TwistCommand, get_publisher


class TurtlesimRobot(RobotInterface):

    TOPIC = "/turtle1/cmd_vel"
    
    def move_forward(self, duration: float, cancel_event: threading.Event | None = None):
        pub = get_publisher(self.TOPIC)
        pub.publish_for(TwistCommand(linear_x=1.0, angular_z=0.0, duration_s=duration), cancel_event)
    
    def turn_left(self, duration: float, cancel_event: threading.Event | None = None):
        pub = get_publisher(self.TOPIC)
        pub.publish_for(TwistCommand(linear_x=0.0, angular_z=1.5, duration_s=duration), cancel_event)
    
    def turn_right(self, duration: float, cancel_event: threading.Event | None = None):
        pub = get_publisher(self.TOPIC)
        pub.publish_for(TwistCommand(linear_x=0.0, angular_z=-1.5, duration_s=duration), cancel_event)
    
    def stop(self):
        pub = get_publisher(self.TOPIC)
        pub.stop()
