"""
Abstract Robot Interface
Jedes Backend MUSS diese Funktionen implementieren
"""
from abc import ABC, abstractmethod
import threading

from app.core.models.command import Command


class RobotInterface(ABC):
    
    @abstractmethod
    def execute_command(self, cmd: Command, cancel_event: threading.Event | None = None):
        """Execute a high-level command model."""
        raise NotImplementedError
    
    @abstractmethod
    def stop(self):
        """Stoppen"""
        raise NotImplementedError
