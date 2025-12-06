"""
Controller - KEINE ROS-Imports hier!
"""
from app.core.commands import parse_command
from app.core.config import get_robot_backend


class RobotController:
    
    def __init__(self):
        self.robot = get_robot_backend()
    
    def execute_command(self, command_text: str):
        """Führt Text-Befehl aus"""
        cmd = parse_command(command_text)
        action = cmd["action"]
        duration = cmd["duration"]
        
        if action == "forward":
            self.robot.move_forward(duration)
        elif action == "left":
            self.robot.turn_left(duration)
        elif action == "right":
            self.robot.turn_right(duration)
        elif action == "stop":
            self.robot.stop()
        else:
            raise ValueError(f"Unbekannte Aktion: {action}")


# Globale Instanz
controller = RobotController()
