"""
Config - Backend Auswahl
"""
import os


ROBOT_BACKEND = os.getenv("ROBOT_BACKEND", "sim")


def get_robot_backend():
    """Factory: Gibt richtiges Backend zurück"""
    from app.ros.turtlesim_robot import TurtlesimRobot
    from app.ros.turtlebot_robot import TurtleBotRobot
    
    if ROBOT_BACKEND == "sim":
        return TurtlesimRobot()
    elif ROBOT_BACKEND == "real":
        return TurtleBotRobot()
    else:
        raise ValueError(f"Unbekanntes Backend: {ROBOT_BACKEND}")
