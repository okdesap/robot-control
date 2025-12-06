"""
TurtleBot Backend
"""
from app.ros.robot_interface import RobotInterface


class TurtleBotRobot(RobotInterface):
    
    def move_forward(self, duration: float):
        # TODO: ROS2 Publisher für /cmd_vel
        print(f"[TurtleBot] Vorwärts {duration}s")
    
    def turn_left(self, duration: float):
        # TODO: ROS2 Publisher
        print(f"[TurtleBot] Links {duration}s")
    
    def turn_right(self, duration: float):
        # TODO: ROS2 Publisher
        print(f"[TurtleBot] Rechts {duration}s")
    
    def stop(self):
        # TODO: ROS2 Publisher
        print("[TurtleBot] Stop")
