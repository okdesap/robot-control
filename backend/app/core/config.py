"""Backend configuration and selection."""
import os





def get_robot_backend():
    ROBOT_BACKEND = os.getenv("ROBOT_BACKEND", "sim")
    
    """Factory: return the selected backend instance."""
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
        """Backend configuration and selection."""
        import os

        from app.ros.robot_interface import RobotInterface


        class _UnavailableRobotBackend(RobotInterface):
            def __init__(self, reason: str) -> None:
                self._reason = reason

            def execute_command(self, cmd, cancel_event=None):
                raise RuntimeError(self._reason)

            def stop(self):
                raise RuntimeError(self._reason)


        def get_robot_backend():
            backend = os.getenv("ROBOT_BACKEND", "sim")

            """Factory: return the selected backend instance."""
            if backend == "sim":
                try:
                    from app.ros.turtlesim_robot import TurtlesimRobot
                    return TurtlesimRobot()
                except Exception as exc:
                    return _UnavailableRobotBackend(
                        "ROS2 packages are missing (geometry_msgs/rclpy). "
                        "Install ROS2 or source its environment. "
                        f"Original error: {exc}"
                    )
            if backend == "real":
                try:
                    from app.ros.turtlebot_robot import TurtleBotRobot
                    return TurtleBotRobot()
                except Exception as exc:
                    return _UnavailableRobotBackend(
                        "ROS2 packages are missing (geometry_msgs/rclpy). "
                        "Install ROS2 or source its environment. "
                        f"Original error: {exc}"
                    )

            raise ValueError(f"Unknown backend: {backend}")
