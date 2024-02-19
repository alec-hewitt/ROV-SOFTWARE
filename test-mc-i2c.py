import smbus
import math

class I2CBUS():

    def __init__(self, bus_number: int):
        self.bus_num = bus_number
        self.bus = smbus.SMBus(self.bus_num)

    def close_bus(self):
        self.bus.close()

    def write_byte(self, addr: int, b: int):
        self.bus.write_byte(addr, b)

i2cbus = I2CBUS(1)

# MC COMMANDS
set_v = 0

v_bytes = bytearray(int(math.fabs(set_v)).to_bytes(2, 'big'))
stop = 1
brake = 1

direction = 1
if set_v < 0:
    direction = 0

byte0 = 0x00

if stop == 1:
    byte0 = byte0 | 0x01
if brake == 1:
    byte0 = byte0 | 0x02
if direction == 1:
    byte0 = byte0 | 0x04

print(byte0)
print(v_bytes[0])
print(v_bytes[1])

mc_commands = [byte0, v_bytes[0], v_bytes[1],4]

try:
    i2cbus.bus.write_block_data(0x11, 0x00, mc_commands)
except Exception as e:
    print(e)

i2cbus.close_bus()
