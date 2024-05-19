import logging
from Drivers.Revolver import Revolver
from Interfaces.i2cbus import I2cBus
from Interfaces.Surface import Surface
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

thruster_addresses = [0x10, 0x11, 0x12, 0x13, 0x14, 0x15]

class Rov:

    def __init__(self):
        logging.basicConfig(filename='logging/rov.log', level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info('hello rov')

        logging.basicConfig(filename='rov_session.log', level=logging.INFO)
        self.logger.info('Started logger')

        self.i2cbus = None
        self.thrusters = []

    def initialize_interfaces(self):
        self.i2cbus = I2cBus(1)

    def initialize_hardware(self):
        for n in range(6):
            self.thrusters.append(Revolver(thruster_addresses[n],position=n,bus=self.i2cbus))

    def initialize_comms(self):
        self.surface = Surface()
        self.surface.open_connection()

    def test_thrusters(self):

        for thruster in self.thrusters:
            print("Address: {}".format(thruster.address))
            thruster.enable_motor()
            time.sleep(1)
            thruster.set_speed(3500)
            time.sleep(5)
            thruster.set_speed(-3500)
            time.sleep(5)
            thruster.set_speed(0)
            time.sleep(1)
            thruster.disable_motor()

    def build_heartbeat(self) -> dict:
        hb_msg = {}
        hb_msg['battery_voltage'] = 42
        hb_msg['temp'] = 30
        return hb_msg

    def health_check(self):
        return

    def update(self):
        # self check
        self.health_check()

        # send heartbeat message
        self.surface.pack_heartbeat(self.build_heartbeat())
        self.surface.send_heartbeat()
        # get commands from surface

    def main_loop(self):
        while True:
            self.logger.info("running!")

            time.sleep(1)
            self.update()

    def shutdown(self):
        self.i2cbus.close_bus()

rov = Rov()
rov.initialize_interfaces()
rov.initialize_hardware()
rov.initialize_comms()

rov.main_loop()
#rov.test_thrusters()
rov.shutdown()
