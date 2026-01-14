"""
TurtleBot Backend
"""
import threading
from app.ros.robot_interface import RobotInterface
from app.ros.ros2_manager import TwistCommand, get_publisher


class TurtleBotRobot(RobotInterface):

    TOPIC = "/cmd_vel"
    
    def move_forward(self, duration: float, cancel_event: threading.Event | None = None):
        print(f"[TurtleBot] Vorwärts {duration}s")
        publisher = get_publisher(self.TOPIC)
        publisher.publish_for(TwistCommand(linear_x=1.0, angular_z=0.0, duration_s=duration), cancel_event)
    
    def turn_left(self, duration: float, cancel_event: threading.Event | None = None):
        print(f"[TurtleBot] Links {duration}s")
        publisher = get_publisher(self.TOPIC)
        publisher.publish_for(TwistCommand(linear_x=0.0, angular_z=1.5, duration_s=duration), cancel_event)
    
    def turn_right(self, duration: float, cancel_event: threading.Event | None = None):
        print(f"[TurtleBot] Rechts {duration}s")
        publisher = get_publisher(self.TOPIC)
        publisher.publish_for(TwistCommand(linear_x=0.0, angular_z=-1.5, duration_s=duration), cancel_event)
    
    def stop(self):
        print("[TurtleBot] Stop")
        publisher = get_publisher(self.TOPIC)
        publisher.stop()