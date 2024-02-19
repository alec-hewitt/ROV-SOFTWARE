import logging
from Drivers.Revolver import Revolver
from Interfaces.i2cbus import I2cBus
import time

logging.basicConfig(filename='myapp.log', level=logging.INFO)

"""
Motor Controller Addresses:
T0: 00100000: 0x20, 32 - 7-bit 0x10
T1: 00100010: 0x22, 34 - 7-bit 0x11
T2: 00100100: 0x24, 36 - 7-bit 0x12
T3: 00100110: 0x26, 38 - 7-bit 0x13
T4: 00101000: 0x28, 40 - 7-bit 0x14
T5: 00101010: 0x2A, 42 - 7-bit 0x15
"""

class Rov:

    def __init__(self):
        logging.basicConfig(filename='logging/rov.log', level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info('hello rov')

        self.main_loop()

        self.i2cbus = None
        self.motor = None

    def initialize_interfaces(self):
        self.i2cbus = I2cBus(1)

    def initialize_hardware(self):
        self.motor = Revolver(address=0x11,position=0, bus=self.i2cbus)
        self.motor.enable_motor()

        time.sleep(5)

        print(self.motor.get_mc_status())

 #       quit()

        self.motor.set_speed(3500)
        time.sleep(5)
        self.motor.set_speed(-3500)
        time.sleep(5)
        self.motor.set_speed(0)
        time.sleep(1)

        self.motor.disable_motor()

  #      print(self.motor.get_mc_status())

    def main_loop(self):
        self.logger.info("running!")

rov = Rov()
rov.initialize_interfaces()
rov.initialize_hardware()
