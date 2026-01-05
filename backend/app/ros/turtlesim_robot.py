"""
Turtlesim Backend
"""

"""
from app.ros.robot_interface import RobotInterface
from app.ros.ros2_manager import TwistCommand, get_publisher


class TurtlesimRobot(RobotInterface):

    TOPIC = "/turtle1/cmd_vel"
    
    def move_forward(self, duration: float):
        pub = get_publisher(self.TOPIC)
        pub.publish_for(TwistCommand(linear_x=1.0, angular_z=0.0, duration_s=duration))
    
    def turn_left(self, duration: float):
        pub = get_publisher(self.TOPIC)
        pub.publish_for(TwistCommand(linear_x=0.0, angular_z=1.5, duration_s=duration))
    
    def turn_right(self, duration: float):
        pub = get_publisher(self.TOPIC)
        pub.publish_for(TwistCommand(linear_x=0.0, angular_z=-1.5, duration_s=duration))
    
    def stop(self):
        pub = get_publisher(self.TOPIC)
        pub.stop()
"""
# ÄNDERUNGEN: Node und Publisher direkt erstellen und warten bis die Verbindung steht
from app.ros.robot_interface import RobotInterface
import rclpy
from geometry_msgs.msg import Twist
import time

class TurtlesimRobot(RobotInterface):
    
    def __init__(self):
        print("🐢 FIX: Starte Turtlesim Verbindung...")
        
        # ROS starten
        if not rclpy.ok():
            rclpy.init()
            
        # Node und Publisher erstellen
        self.node = rclpy.create_node('turtlesim_fix_node')
        self.publisher = self.node.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # DER WICHTIGSTE TEIL: Warten, bis die Leitung steht!
        time.sleep(1.0) 
        print("✅ FIX: Verbindung steht dauerhaft!")

    def _send(self, linear, angular):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.publisher.publish(msg)
        print(f"📡 Sende Befehl an Turtle: {linear} | {angular}")

    def move_forward(self, duration: float):
        self._send(2.0, 0.0)

    def turn_left(self, duration: float):
        self._send(0.0, 2.0)

    def turn_right(self, duration: float):
        self._send(0.0, -2.0)

    def stop(self):
        self._send(0.0, 0.0)

