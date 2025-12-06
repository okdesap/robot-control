"""
Abstract Robot Interface
Jedes Backend MUSS diese Funktionen implementieren
"""
from abc import ABC, abstractmethod


class RobotInterface(ABC):
    
    @abstractmethod
    def move_forward(self, duration: float):
        """Vorwärts fahren"""
        pass
    
    @abstractmethod
    def turn_left(self, duration: float):
        """Links drehen"""
        pass
    
    @abstractmethod
    def turn_right(self, duration: float):
        """Rechts drehen"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stoppen"""
        pass
