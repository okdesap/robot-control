"""
TurtleBot Backend
"""
import threading
from app.ros.robot_interface import RobotInterface
from app.ros.ros2_manager import TwistCommand, get_publisher
from geometry_msgs.msg import TwistStamped


class TurtleBotRobot(RobotInterface):

    TOPIC = "/cmd_vel"

    def _publish(self, cmd: TwistCommand, cancel_event: threading.Event | None = None):
        pub = get_publisher(self.TOPIC, TwistStamped)

        msg = TwistStamped()
        msg.header.stamp = pub._node.get_clock().now().to_msg()
        msg.twist.linear.x = float(cmd.linear_x)
        msg.twist.angular.z = float(cmd.angular_z)

        pub.publish_for(msg, cmd.duration_s, cancel_event)
    
    def move_forward(self, duration: float, cancel_event: threading.Event | None = None):
        print(f"[TurtleBot] Vorwärts {duration}s")
        self._publish(TwistCommand(linear_x=1.0, angular_z=0.0, duration_s=duration), cancel_event)
    
    def turn_left(self, duration: float, cancel_event: threading.Event | None = None):
        print(f"[TurtleBot] Links {duration}s")
        self._publish(TwistCommand(linear_x=0.0, angular_z=1.5, duration_s=duration), cancel_event)
    
    def turn_right(self, duration: float, cancel_event: threading.Event | None = None):
        print(f"[TurtleBot] Rechts {duration}s")
        self._publish(TwistCommand(linear_x=0.0, angular_z=-1.5, duration_s=duration), cancel_event)
    
    def stop(self):
        print("[TurtleBot] Stop")
        get_publisher(self.TOPIC, TwistStamped).stop()