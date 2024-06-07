import logging
from Drivers.Revolver import Revolver
from Drivers.PDB import PDB
from Interfaces.i2cbus import I2cBus
from Interfaces.Surface import Surface
from controller import Controller
import time
import json
from datetime import datetime

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
        logging.basicConfig(
            filename=datetime.now().strftime('logging/ROVLOG_%H_%M_%d_%m_%Y.log'),
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger(__name__)

        logging.basicConfig(filename='rov_session.log', level=logging.INFO)
        self.logger.info('Started logger')

        self.i2cbus = None
        self.thrusters = []
        self.pdb = None
        self.controller = Controller()

        # run mode
        self.run_mode = 0

        # 0: NO ERROR
        # 1: THRUSTER COMMAND ERROR: DATA INVALID
        # 2: THRUSTER COMMAND ERROR: MOTOR NOT SPECIFIED
        self.surface_error_code = 0

    def initialize_interfaces(self):
        self.i2cbus = I2cBus(1)
        self.surface = Surface()

    def initialize_hardware(self):
        for n in range(6):
            self.thrusters.append(Revolver(thruster_addresses[n],position=n,bus=self.i2cbus))
        self.pdb = PDB(bus=self.i2cbus)

    def get_thruster_status(self):
        for thruster in self.thrusters:
            assert thruster.get_mc_status()

    def health_check(self, hb):
        self.get_thruster_status()

    def set_run_mode(self, mode):
        if mode == self.run_mode:
            return
        self.run_mode = mode
        # TODO: be careful here, we may override special bus switch commands in cases of overcurrent faults
        if self.run_mode:
            # enable all motor controllers
            self.pdb.set_enable_motor_buses()
        else:
            self.pdb.set_disable_motor_buses()

    def build_heartbeat(self) -> dict:
        hb_msg = {}
        hb_msg['surface_error'] = self.surface_error_code
        hb_msg['battery_voltage'] = 42
        hb_msg['temp'] = 30
        for n in range(len(self.thrusters)):
            hb_msg['t{}_velocity'.format(n)] = self.thrusters[n].set_velocity
            hb_msg['t{}_enabled'.format(n)] = self.thrusters[n].motor_enabled
        hb_msg['pdb_temp'] = self.pdb.get_temp()
        return hb_msg

    def health_check(self):
        return

    def set_enable_thrusters(self, enable_list):
        for n in range(len(enable_list)):
            if enable_list[n] == 1:
                self.thrusters[n].enable_motor()
            elif enable_list[n] == 0:
                self.thrusters[n].disable_motor()

    def set_thrusters(self, speed_list):
        for n in range(len(speed_list)):
            self.thrusters[n].command_speed(speed_list[n])

    def telecontrol_update(self, msg):
        # determines run state of the rov, triggers control calculations, turns stuff on and off
        if msg == None:
            return 0
        cmds = json.loads(msg.decode())
        print('Surface message: {}'.format(cmds))
        # set run mode
        self.set_run_mode(int(cmds['run']))


    def transact_thrusters(self):
        e_list = self.controller.get_t_enables()
        v_list = self.controller.get_t_velocity()
        # motor controller enable commands
        for n in e_list:
            try:
                if n != 0 and n != 1:
                    self.surface_error_code = 2
                    return
            except TypeError as e:
                self.surface_error_code = 3
                self.logger.error("{} thruster enable value wrong type SURFACE ERROR 1 VALUE INVALID".format(n))
                return

        # motor controller speed commands
        for n in v_list:
            try:
                if n > 1 or n < -1:
                    self.surface_error_code = 2 # value invalid
                    return
            except TypeError as e:
                self.surface_error_code = 3
                self.logger.error("{} thruster speed value wrong type SURFACE ERROR 1 VALUE INVALID".format(n))
                return

        self.set_enable_thrusters(e_list)
        self.set_thrusters(v_list)

    def run(self):
        # transact motor controllers
        self.transact_thrusters()
        # transact PDB
        self.pdb.update()
        # self check
        self.health_check()

        # surface - try to open the connection
        if self.surface.open_connection():
            # surface - send hb
            hb = self.build_heartbeat()
            self.surface.pack_heartbeat(hb)
            self.surface.send_heartbeat()
            # surface - get commands
            msg = self.surface.get_message()
            self.telecontrol_update(msg) # get controls commands, light commands, etc
        else:
            self.set_run_mode(0)

    def main_loop(self):
        print("Running...")
        while True:
            try:
                time.sleep(0.5)
                self.run()
            except Exception as e:
                print(e)
                self.logger.error("CRITICAL EXCEPTION IN MAIN: {}".format(e))
                return

    def shutdown(self):
        self.i2cbus.close_bus()

rov = Rov()
rov.initialize_interfaces()
rov.initialize_hardware()
rov.main_loop()
rov.shutdown()
