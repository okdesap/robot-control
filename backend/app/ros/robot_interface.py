"""
Abstract Robot Interface
Jedes Backend MUSS diese Funktionen implementieren
"""
from abc import ABC, abstractmethod
import threading


class RobotInterface(ABC):
    
    @abstractmethod
    def move_forward(self, duration: float, cancel_event: threading.Event | None = None):
        """Vorwärts fahren"""
        pass
    
    @abstractmethod
    def turn_left(self, duration: float, cancel_event: threading.Event | None = None):
        """Links drehen"""
        pass
    
    @abstractmethod
    def turn_right(self, duration: float, cancel_event: threading.Event | None = None):
        """Rechts drehen"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stoppen"""
        pass
