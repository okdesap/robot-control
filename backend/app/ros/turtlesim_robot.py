"""
Turtlesim Backend
"""
from app.ros.robot_interface import RobotInterface
from app.ros.ros2_manager import TwistCommand, get_turtlesim_publisher


class TurtlesimRobot(RobotInterface):
    
    def move_forward(self, duration: float):
        pub = get_turtlesim_publisher()
        pub.publish_for(TwistCommand(linear_x=1.0, angular_z=0.0, duration_s=duration))
    
    def turn_left(self, duration: float):
        pub = get_turtlesim_publisher()
        pub.publish_for(TwistCommand(linear_x=0.0, angular_z=1.5, duration_s=duration))
    
    def turn_right(self, duration: float):
        pub = get_turtlesim_publisher()
        pub.publish_for(TwistCommand(linear_x=0.0, angular_z=-1.5, duration_s=duration))
    
    def stop(self):
        pub = get_turtlesim_publisher()
        pub.stop()
