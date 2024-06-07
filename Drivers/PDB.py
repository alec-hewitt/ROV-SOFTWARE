# PDB.py: A driver for the PDB
import math
import logging
from Interfaces.i2cbus import I2cBus


class PDB:

    def __init__(self, bus: I2cBus):
        """
        Initialize PDB

        :param address:
        :param position:
        :param bus:
        """
        self.logger = logging.getLogger(__name__)
        self.address = 0x0b
        self.bus = bus
        print("PDB Initialized")
        self.logger.info("PDB Initialized")
        if self.get_status():
            print("PDB Ready")
            self.logger.info("PDB Ready")
        self.get_temp()

        self.bus_enables = [0,0,0,0,0,0,0,0,0]

    def get_status(self) -> int:
        print("PDB states: {}".format(self.bus.read_register(addr=self.address, register=1,num_bytes=1)))
        return 1

    def get_temp(self) -> int:
        temp = self.bus.read_register(self.address, register=6, num_bytes=2)
        temp_cnv_bytes = temp[1] | (temp[0] << 8)
        temp_actual = (((temp_cnv_bytes / 4096) * 3.3) - 0.5 ) / 0.01
        return temp_actual

    def get_12v_bus_current(self) -> float:
        current = self.bus.read_register(self.address, register=2, num_bytes=4)
        print("12v bus current: {}".format(current))
        return current

    def set_enable_motor_buses(self):
       print("enabling motor buses")
       self.bus_enables[0:6] = [1,1,1,1,1,1]

    def set_disable_motor_buses(self):
        print("disabling motor buses")
        self.bus_enables[0:6] = [0,0,0,0,0,0]

    def _send_pdb_payload(self, velocity: int) -> bool:
        pdb_payload = [command_byte, velocity_bytes[0], velocity_bytes[1], peripheral_command_byte]
        return self.bus.write_bytes(addr=self.address, offset=0, payload=mc_payload)

    def get_pdb_status(self) -> list:
        # status of 1 is online
        status = self.bus.read_bytes(addr=self.address, register=0, num_bytes=8)
        print("PDB STATUS: {}".format(status))
        return (status)

    def update(self) -> bool:
        #send pdb commands
        print("updating pdb")
        return 1
