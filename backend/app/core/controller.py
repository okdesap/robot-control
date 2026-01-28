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
        self._queue = CommandQueueManager(
            execute_fn=self._execute_one_command,
            stop_fn=self._stop_robot_immediately,
            max_queue_size=40,
        )

        self._queue.start()

    """Public methods for controlling the robot and its command queue."""

    def enqueue_command(self, command_text: str):
        """Enqueue a command and return its job_id.
        this is non-blocking. REST API can return immediately."""
        return self._queue.enqueue(command_text)

    def emergency_stop(self) -> None:
        """cancel current command and clear the queue."""
        self._queue.emergency_stop(clear_queue=True) 


    def status(self) -> dict:
        """Get current status of the command queue."""
        return {
            "robot_backend": type(self.robot).__name__,
            **self._queue.get_status(),
        }
    
    def shutdown(self) -> None:
        """calls this on app shutdown to stop worker thread and robot."""
        self._queue.shutdown(timeout_s=2.0)
    
    def health(self) -> dict:
        """Quick health info for debugging."""
        return {
            "robot_backend": type(self.robot).__name__,
        }
    
    def take_photo(self) -> str:
        print("Taking picture") # Not implemented yet
        photo = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="  # Placeholder for image data
        return photo
    
    """ internal methods for executing commands and stopping the robot."""

    def _execute_one_command(self, command_text: str, cancel_event: threading.Event) -> None:
        """Execute a single command 
        this runs in the worker thread."""
        #if a stop has been requested before we start, do nothing
        if cancel_event.is_set():
            return  
        
        cmd = parse_command(command_text)

        #check again before executing
        if cancel_event.is_set():
            return

        self.robot.execute_command(cmd, cancel_event)
    

    def _stop_robot_immediately(self) -> None:
        """Stop the robot immediately
        for true cancellation of current command, the ROS publisher must cooperate."""
        self.robot.stop()
    



# Globale Instanz
controller = RobotController()
