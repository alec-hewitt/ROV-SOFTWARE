import logging
from Drivers.Revolver import Revolver
from Interfaces.i2cbus import I2cBus
import time

logging.basicConfig(filename='myapp.log', level=logging.INFO)


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

#        print(self.motor.get_mc_status())

 #       quit()

        self.motor.set_speed(2000)
        time.sleep(5)
        self.motor.set_speed(-2000)
        time.sleep(5)
        self.motor.set_speed(0)
        time.sleep(5)

        self.motor.disable_motor()

  #      print(self.motor.get_mc_status())

    def main_loop(self):
        self.logger.info("running!")

rov = Rov()
rov.initialize_interfaces()
rov.initialize_hardware()
