"""
Turtlesim Backend
"""
from app.ros.robot_interface import RobotInterface


class TurtlesimRobot(RobotInterface):
    
    def move_forward(self, duration: float):
        # TODO: ROS2 Publisher für /turtle1/cmd_vel
        print(f"[Turtlesim] Vorwärts {duration}s")
    
    def turn_left(self, duration: float):
        # TODO: ROS2 Publisher
        print(f"[Turtlesim] Links {duration}s")
    
    def turn_right(self, duration: float):
        # TODO: ROS2 Publisher
        print(f"[Turtlesim] Rechts {duration}s")
    
    def stop(self):
        # TODO: ROS2 Publisher
        print("[Turtlesim] Stop")
