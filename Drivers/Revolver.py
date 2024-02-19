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
        self.logger.info('hello revolver')
        self.address = address
        self.bus = bus
        # motor parameters
        self.motor_enabled = 0
        self.motor_brake_enabled = 0
        self.set_velocity = 0
        # rov parameters
        self.position = position
        # protected variables
        self._max_velocity = 3500

    def set_max_velocity(self, new_maximum: int):
        try:
            if new_maximum <= 3500:
                self._max_velocity = new_maximum
        except ValueError:
            self.logger.error("Invalid velocity type")

    def enable_motor(self):
        self.motor_enabled = 1
        self._send_mc_payload(velocity=0, enable_cmd=self.motor_enabled, brake_cmd=self.motor_brake_enabled)

    def disable_motor(self):
        self.motor_enabled = 0
        self._send_mc_payload(velocity=0, enable_cmd=self.motor_enabled, brake_cmd=self.motor_brake_enabled)

    def set_speed(self, velocity_to_set: float) -> bool:
        if self.motor_enabled and self.motor_brake_enabled == 0:
            try:
                if math.fabs(velocity_to_set) <= self._max_velocity:
                    self.set_velocity = int(velocity_to_set)
            except ValueError:
                self.logger.error("Invalid velocity type")
                return 0

            self._send_mc_payload(
                velocity=self.set_velocity,
                enable_cmd=self.motor_enabled,
                brake_cmd=self.motor_brake_enabled
            )
            return 1
        else:
            self.logger.error("Cannot set speed. Motor is disabled or in brake mode.")
            return 0

    def engage_brake_motor(self):
        self.motor_brake_enabled = 1
        self._send_mc_payload(velocity=0, enable_cmd=self.motor_enabled, brake_cmd=self.motor_brake_enabled)

    def disengage_brake_motor(self):
        self.motor_brake_enabled = 0
        self._send_mc_payload(velocity=0, enable_cmd=self.motor_enabled, brake_cmd=self.motor_brake_enabled)

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
        print("address")
        print(self.address)
        print(hex(self.address))
        return self.bus.write_bytes(addr=self.address, offset=0, payload=mc_payload)

    def check_status(self) -> list:
        return self.get_mc_status([0])  # awake bit

    def get_mc_status(self) -> list:
        return self.bus.read_bytes(addr=self.address, register=0, num_bytes=8)
