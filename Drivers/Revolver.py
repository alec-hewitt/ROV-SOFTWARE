# Revolver.py: A driver for the Revolver motor controller
import math
import logging
from Interfaces.i2cbus import I2cBus


class Revolver:

    def __init__(self, address: int, position: int, bus: I2cBus):
        """
        Initialize Revolver motor controller

        :param address:
        :param position:
        :param bus:
        """
        self.logger = logging.getLogger(__name__)
        self.address = address
        self.bus = bus
        # motor parameters
        self.motor_enabled = 0
        self.motor_brake_enabled = 0
        self.set_velocity = 0
        self.velocity = 0
        # rov parameters
        self.position = position
        # protected variables
        self._max_velocity = 4000
        self.motor_awake = 0

    def set_max_velocity(self, new_maximum: int):
        try:
            if new_maximum <= 3500:
                self._max_velocity = new_maximum
        except ValueError:
            self.logger.error("Invalid velocity type")

    def enable_motor(self):
        try:
            self.logger.debug(f"🔧 Enabling thruster {self.position} at address 0x{self.address:02x}")
            self.motor_enabled = 1
            if(self._send_mc_payload(velocity=0, enable_cmd=self.motor_enabled, brake_cmd=self.motor_brake_enabled)):
                self.motor_awake = 1
                self.logger.info(f"✅ Thruster {self.position} enabled successfully")
            else:
                self.logger.error(f"❌ Failed to enable thruster {self.position}")
        except Exception as e:
            self.logger.error(f"❌ Exception enabling thruster {self.position}: {e}")

    def disable_motor(self):
        try:
            self.logger.debug(f"🔧 Disabling thruster {self.position} at address 0x{self.address:02x}")
            self.motor_enabled = 0
            if(self._send_mc_payload(velocity=0, enable_cmd=self.motor_enabled, brake_cmd=self.motor_brake_enabled)):
                self.motor_awake = 0
                self.logger.info(f"✅ Thruster {self.position} disabled successfully")
            else:
                self.logger.error(f"❌ Failed to disable thruster {self.position}")
        except Exception as e:
            self.logger.error(f"❌ Exception disabling thruster {self.position}: {e}")

    def set_speed(self, velocity_to_set: float) -> bool:
        if self.motor_enabled and self.motor_brake_enabled == 0 and self.motor_awake == 1:
            try:
                if math.fabs(velocity_to_set) <= self._max_velocity:
                    self.set_velocity = int(velocity_to_set)
            except ValueError:
                self.logger.error("Invalid velocity type: {}".format(velocity_to_set))
                return 0

            self._send_mc_payload(
                velocity=self.set_velocity,
                enable_cmd=self.motor_enabled,
                brake_cmd=self.motor_brake_enabled
            )
            self.logger.debug("Motor {} set speed to {} success.".format(self.position, velocity_to_set))
            return 1
        else:
            self.logger.warning("Cannot set speed. Motor {} is disabled or in brake mode.".format(self.position))
            return 0

    def engage_brake_motor(self):
        self.motor_brake_enabled = 1
        self._send_mc_payload(velocity=0, enable_cmd=self.motor_enabled, brake_cmd=self.motor_brake_enabled)

    def disengage_brake_motor(self):
        self.motor_brake_enabled = 0
        self._send_mc_payload(velocity=0, enable_cmd=self.motor_enabled, brake_cmd=self.motor_brake_enabled)

    def command_speed(self, speed) -> bool:
        # speed input is a float between -1 and 1
        set_spd = self._max_velocity * speed
        return self.set_speed(speed)

    def _send_mc_payload(self, velocity: int, enable_cmd: int, brake_cmd: int) -> bool:
        # compile velocity bytes
        velocity_bytes = bytearray(int(math.fabs(velocity)).to_bytes(2, 'big'))
        # set direction bit
        direction = 1 if velocity > 0 else 0
        # compile command byte
        command_byte = 0x00
        if enable_cmd == 1:
            command_byte = command_byte | 0x01
        if brake_cmd == 1:
            command_byte = command_byte | 0x02
        if direction == 1:
            command_byte = command_byte | 0x04
        # temporary empty byte
        peripheral_command_byte = 0x00

        mc_payload = [command_byte, velocity_bytes[0], velocity_bytes[1], peripheral_command_byte]
        return self.bus.write_bytes(addr=self.address, offset=0, payload=mc_payload)

    def get_mc_status(self) -> list:
        # status of 1 is online
        status = self.bus.read_bytes(addr=self.address, register=0, num_bytes=8)
        return (status[0] & 0x00000001)
