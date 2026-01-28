"""
Config - Backend Auswahl
"""
import os





def get_robot_backend():
    ROBOT_BACKEND = os.getenv("ROBOT_BACKEND", "sim")
    
    """Factory: Gibt richtiges Backend zurück"""
    from app.ros.turtlesim_robot import TurtlesimRobot
    from app.ros.turtlebot_robot import TurtleBotRobot
    
    if ROBOT_BACKEND == "sim":
        return TurtlesimRobot()
    elif ROBOT_BACKEND == "real":
        return TurtleBotRobot()
    else:
        raise ValueError(f"Unbekanntes Backend: {ROBOT_BACKEND}")


from app.ros.robot_interface import RobotInterface


class _UnavailableRobotBackend(RobotInterface):
    def __init__(self, reason: str) -> None:
        self._reason = reason

    def execute_command(self, cmd, cancel_event=None):
        raise RuntimeError(self._reason)

    def stop(self):
        raise RuntimeError(self._reason)


def get_robot_backend():
    ROBOT_BACKEND = os.getenv("ROBOT_BACKEND", "sim")

    """Factory: Gibt richtiges Backend zurück"""
    if ROBOT_BACKEND == "sim":
        try:
            from app.ros.turtlesim_robot import TurtlesimRobot
            return TurtlesimRobot()
        except Exception as exc:
            return _UnavailableRobotBackend(
                "ROS2 Pakete fehlen (geometry_msgs/rclpy). "
                "Bitte ROS2 installieren/sourcen oder ROBOT_BACKEND=real/sim korrekt setzen. "
                f"Original error: {exc}"
            )
    elif ROBOT_BACKEND == "real":
        try:
            from app.ros.turtlebot_robot import TurtleBotRobot
            return TurtleBotRobot()
        except Exception as exc:
            return _UnavailableRobotBackend(
                "ROS2 Pakete fehlen (geometry_msgs/rclpy). "
                "Bitte ROS2 installieren/sourcen oder ROBOT_BACKEND=real/sim korrekt setzen. "
                f"Original error: {exc}"
            )
    else:
        raise ValueError(f"Unbekanntes Backend: {ROBOT_BACKEND}")
