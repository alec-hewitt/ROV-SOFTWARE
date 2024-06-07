import smbus
import logging


class I2cBus:
    """
    I2C Bus Interface
    """

    def __init__(self, bus_number: int):
        """
        init
        :param bus_number:
        """
        self.logger = logging.getLogger(__name__)  # What do I have to enter here?
        self.logger.info('hello i2c bus')

        self.bus_num = bus_number
        self.bus = smbus.SMBus(self.bus_num)

    def close_bus(self):
        """
        Close I2C bus
        """
        self.bus.close()

    def write_byte(self, addr: int, byte: int) -> bool:
        """
        Write a single byte to i2c bus
        :param addr:
        :param byte:

        Returns: (bool) True if write successful, False otherwise
        """
        try:
            self.bus.write_byte(addr, byte)
            return True
        except Exception as err:
            self.logger.error(err)
            return False

    def write_bytes(self, addr: int, offset: int, payload: list) -> bool:
        """
        Write block data to i2c bus
        :param addr:
        :param offset:
        :param payload:

        Returns: (bool) True if write successful, False otherwise
        """
        try:
            self.bus.write_block_data(addr, offset, payload)
            return True
        except Exception as err:
            self.logger.error(err)
            print(err)
            return False

    def read_register(self, addr: int, register: int, num_bytes: int) -> list:
        read = []
        r = self.read_bytes(addr, register, num_bytes)
        return r

    def read_bytes(self, addr: int, register: int, num_bytes: int) -> list:
        """
        Read data from the i2c bus
        :param addr:
        :param register:
        :param num_bytes:

        Returns: (list) bytes received from i2c bus
        """
        try:
            p = self.bus.read_i2c_block_data(addr, register, num_bytes)
            print(p)
            return p
        except Exception as err:
            print(err)
            self.logger.error(err)
            return []
