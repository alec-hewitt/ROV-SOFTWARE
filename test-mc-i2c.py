import smbus

class I2CBUS(smbus.SMBus):

    def __init__(self, bus_number: int):
        self.bus_num = bus_number
        self.bus = None

    def __init__(self):
        self.open_bus(self.bus_num)

    def open_bus(self):
        bus = smbus.SMBus(self.bus_num)

    def close_bus(self):
        if self.bus is not None:
            self.bus.close()
        else:
            print("ERROR: You are trying to close a bus that has not been opened!")

    def write_byte(self, addr: int, b: int):
        if self.bus is not None:
            self.bus.write_byte(addr, b)
        else:
            print("ERROR: You are trying to write to a bus that has not been opened!")


bus = i2c_bus(1)

bus.write_byte(0x0b, 0x06)
