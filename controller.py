# controller.py: A class to handle control methods for the ROV
import math
import logging

class Controller:

    def __init__(self):
        """
        """
        self.logger = logging.getLogger(__name__)
        self._t_velocity = [0,0,0,0,0,0] # thruster velocity command array
        self._t_enables = [0,0,0,0,0,0] # thruster enable command array

    def get_t_velocity(self) -> list:
        return self._t_velocity

    def get_t_enables(self) -> list:
        return self._t_enables
