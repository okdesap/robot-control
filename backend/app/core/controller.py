"""
Controller - KEINE ROS-Imports hier!
"""
import threading

from app.core.commands import parse_command
from app.core.config import get_robot_backend
from app.core.command_queue import CommandQueueManager


class RobotController:
    
    def __init__(self):
        self.robot = get_robot_backend()
        self.command_queue = CommandQueueManager(
            execute_fn=self.execute_one_command,
            stop_fn=self.robot.stop,
            max_queue_size=40,
        )
        
        self.command_queue.start()
    
    def enqueue_command(self, command_text: str):
        """Enqueue a command and return its job_id."""
        return self.command_queue.enqueue(command_text)
    

    def emergency_stop(self) -> None:
        """cancel current command and clear the queue."""
        self.command_queue.emergency_stop(clear_queue=True) 

    def status(self) -> dict:
        """Get current status of the command queue."""
        return {
            "robot_backend": type(self.robot).__name__,
            **self.command_queue.get_status(),
        }
    
    def shutdown(self) -> None:
        """Shut down the controller and its command queue."""
        self.command_queue.shutdown(timeout_s=2.0)

    def execute_one_command(self, command_text: str, cancel_event: threading.Event) -> None:
        """Führt Text-Befehl aus"""
        if cancel_event.is_set():
            return  # Befehl wurde abgebrochen
        
        cmd = parse_command(command_text)
        action = cmd["action"]
        duration = cmd["duration"]

        if cancel_event.is_set():
            return  # Befehl wurde abgebrochen
        
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

    def health(self) -> dict:
        """Quick health info for debugging."""
        return {
            "robot_backend": type(self.robot).__name__,
        }


    def take_photo(self) -> str:
        print("Taking picture") # Not implemented yet
        photo = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="  # Placeholder for image data
        return photo
    
    def _stop_robot_immediately(self) -> None:
        """Stoppt den Roboter sofort."""
        self.robot.stop()
    
    def execute_command(self, command_text: str) -> None:
        """backwards compatible wrapper.
        old code expects this to exexute immediately, but now it enqueues the command.
        """
        self.enqueue_command(command_text)


# Globale Instanz
controller = RobotController()
