# PDB.py: A driver for the PDB

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
        self.logger.info("PDB Initialized")
        if self.get_status():
            self.logger.info("PDB Ready")

        self.bus_enables = [0,0,0,0,0,0,0,0,0]

    def get_status(self) -> int:
        try:
            states = self.bus.read_register(addr=self.address, register=1, num_bytes=1)
            return 1
        except Exception as e:
            self.logger.error(f"❌ Failed to read PDB status: {e}")
            return 0

    def get_temp(self) -> int:
        try:
            temp = self.bus.read_register(self.address, register=2, num_bytes=2)
            temp_cnv_bytes = temp[1] | (temp[0] << 8)
            temp_actual = (((temp_cnv_bytes / 4096) * 3.3) - 0.5 ) / 0.01
            return temp_actual
        except Exception as e:
            self.logger.error(f"❌ Failed to read PDB temperature: {e}")
            return 0

    def get_bus_current(self, bus_number: int) -> float:
        """
        Get the current of a specific bus
        :param bus_number: from 1-9
        """
        # Each bus uses 2 consecutive registers:
        # Bus 1: registers 6-7, Bus 2: registers 8-9, etc.
        current = self.bus.read_register(self.address, register=5+bus_number+((bus_number-1)), num_bytes=2)
        current_bytes = current[1] | (current[0] << 8)
        current_scaled = (((current_bytes / 4096) * 3.3) - 0.5 ) / 0.01
        return current_scaled

    def get_12v_bus_current(self) -> float:
        # was reg 2
        current = self.bus.read_register(self.address, register=4, num_bytes=2)
        current_bytes = current[1] | (current[0] << 8)
        current_scaled = (((current_bytes / 4096) * 3.3) - 0.5 ) / 0.01
        return current_scaled

    def set_enable_motor_buses(self):
       self.bus_enables[0:6] = [1,1,1,1,1,1]

    def set_disable_motor_buses(self):
        self.bus_enables[0:6] = [0,0,0,0,0,0]

    def _send_pdb_payload(self, velocity: int) -> bool:
        pdb_payload = [command_byte, velocity_bytes[0], velocity_bytes[1], peripheral_command_byte]
        return self.bus.write_bytes(addr=self.address, offset=0, payload=mc_payload)

    def update(self) -> bool:
        try:
            self.logger.debug("Updating PDB...")
            # Add any PDB update logic here
            self.logger.debug("PDB update completed")
            return 1
        except Exception as e:
            self.logger.error(f"❌ PDB update failed: {e}")
            return 0
