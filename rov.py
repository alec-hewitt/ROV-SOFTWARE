import logging
from Drivers.Revolver import Revolver
from Drivers.PDB import PDB
from Interfaces.i2cbus import I2cBus
from Interfaces.rov_network import ROVNetworkClient
from controller import ThrusterManager
import time
import json
import signal
import os
import sys
import struct
from datetime import datetime
from typing import Union, Optional
# Get the absolute path to the project root
project_root = os.path.dirname(os.path.abspath(__file__))  # rov.py is in project root
sys.path.insert(0, project_root)

from rov_messages_pb2 import (
    Heartbeat, ThrusterStatus, ControlMessage, 
    ThrusterCommand, NetworkMessage, PDBBusStatus
)
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
        # Set up logging to both file and console
        log_filename = datetime.now().strftime('logging/ROVLOG_%H_%M_%d_%m_%Y.log')
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                                    datefmt='%Y-%m-%d %H:%M:%S')
        
        # File handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Reduce console spam
        console_handler.setFormatter(formatter)
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        self.logger = logging.getLogger(__name__)

        logging.basicConfig(filename='rov_session.log', level=logging.INFO)
        self.logger.info('Started logger')

        self.i2cbus = None
        self.thrusters: list[Revolver] = []
        self.pdb = None
        self.thruster_manager = None

        # run mode
        self.run_mode = 0

        # 0: NO ERROR
        # 1: THRUSTER COMMAND ERROR: DATA INVALID
        # 2: THRUSTER COMMAND ERROR: MOTOR NOT SPECIFIED
        self.surface_error_code = 0


    def initialize_interfaces(self):
        self.i2cbus = I2cBus(1)
        # Initialize robust network client
        self.network_client = ROVNetworkClient("192.168.1.1", 65432)
        
        # Set up network callbacks
        self.network_client.set_callbacks(
            on_control_message=self._on_control_message,
            on_heartbeat_request=self._on_heartbeat_request,
            on_connection_change=self._on_connection_change
        )

    def initialize_hardware(self):
        self.logger.info("Initializing hardware...")
        try:
            self.logger.debug("Initializing thrusters...")
            for n in range(6):
                self.logger.debug(f"Initializing thruster {n} at address 0x{thruster_addresses[n]:02x}")
                self.thrusters.append(Revolver(thruster_addresses[n],position=n,bus=self.i2cbus))
            self.logger.info(f"Initialized {len(self.thrusters)} thrusters")
            
            self.logger.debug("Initializing PDB...")
            self.pdb = PDB(bus=self.i2cbus)
            self.logger.info("PDB initialized")
            
            # Initialize thruster manager after thrusters are ready
            self.logger.debug("Initializing thruster manager...")
            self.thruster_manager = ThrusterManager(self.thrusters)
            self.logger.info("Thruster manager initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Hardware initialization failed: {e}")
            raise

    def _on_control_message(self, control_data):
        """Handle control message from surface station"""
        self.logger.info("🎮 Control message received")
        
        # Convert dict to ControlMessage for compatibility
        control_msg = ControlMessage()
        control_msg.run = control_data.get('run', False)
        control_msg.lights_on = control_data.get('lights_on', False)
        control_msg.camera_pan = control_data.get('camera_pan', 0.0)
        control_msg.camera_tilt = control_data.get('camera_tilt', 0.0)
        control_msg.timestamp = control_data.get('timestamp', int(time.time() * 1000))
        
        # Add thruster commands
        for thruster_data in control_data.get('thrusters', []):
            thruster_cmd = ThrusterCommand()
            thruster_cmd.id = thruster_data.get('id', 0)
            thruster_cmd.velocity = thruster_data.get('velocity', 0.0)
            thruster_cmd.enabled = thruster_data.get('enabled', False)
            control_msg.thrusters.append(thruster_cmd)
        
        # Execute the control message
        self.execute_control_message(control_msg)
    
    def _on_heartbeat_request(self):
        """Handle heartbeat request from surface station"""
        self.logger.debug("💓 Heartbeat request received")
        self._send_heartbeat()
    
    def _on_connection_change(self, connected):
        """Handle connection state changes"""
        if connected:
            self.logger.info("🔌 Connected to surface station")
        else:
            self.logger.warning("🔌 Disconnected from surface station")
            # Emergency stop when disconnected
            self.emergency_stop()
    
    def _send_heartbeat(self):
        """Send heartbeat to surface station"""
        heartbeat = self.create_heartbeat()
        success = self.network_client.send_heartbeat(heartbeat)
        if success:
            self.logger.debug(f"💓 Sent heartbeat: battery={heartbeat.battery_voltage:.1f}V")
        else:
            self.logger.error("❌ Failed to send heartbeat")
    
    def create_heartbeat(self):
        """Create a Heartbeat protobuf message with current data"""
        heartbeat = Heartbeat()
        
        # Set error code
        heartbeat.surface_error = Heartbeat.ErrorCode.NO_ERROR
        
        
        # Mock sensor readings (replace with real sensors in production)
        heartbeat.battery_voltage = 0
        heartbeat.temperature = 0
        heartbeat.pdb_temperature = self.pdb.get_temp()
        heartbeat.timestamp = int(time.time() * 1000)

        for pdb in range(1, 10):
            pdb_bus = PDBBusStatus()
            pdb_bus.id = pdb
            pdb_bus.enabled = True  # Mock enabled status
            pdb_bus.bus_current = self.pdb.get_bus_current(pdb)
            heartbeat.pdb_stati.append(pdb_bus)
        
        # Add thruster status
        if self.thruster_manager:
            thruster_status = self.thruster_manager.get_thruster_status()
            for thruster_data in thruster_status:
                thruster = ThrusterStatus()
                thruster.id = thruster_data['id']
                thruster.velocity = thruster_data['velocity']
                thruster.enabled = thruster_data['enabled']
                thruster.current = thruster_data['current']
                thruster.temperature = thruster_data['temperature']
                heartbeat.thrusters.append(thruster)
        
        return heartbeat

    def run(self):
        """Main ROV run loop - now simplified with robust network client"""
        try:
            # The network client handles all communication automatically
            # Minimal logging for high-frequency operation
            if not self.network_client.is_connected():
                self.logger.warning("⚠️ Not connected to surface station")
                
        except Exception as e:
            self.logger.error(f"❌ Error in run method: {e}")

    def execute_control_message(self, control_msg: ControlMessage):
        """Execute the received control message"""
        try:
            # Handle run mode
            if control_msg.run:
                self.logger.info("🟢 ROV run mode ENABLED")
                self.run_mode = 1
            else:
                self.logger.info("🔴 ROV run mode DISABLED")
                self.run_mode = 0

            # Handle thruster commands
            for thruster_cmd in control_msg.thrusters:
                thruster_id = thruster_cmd.id
                velocity = thruster_cmd.velocity
                enabled = thruster_cmd.enabled
                
                if 0 <= thruster_id < len(self.thrusters):
                    # Update thruster manager's current commands
                    if self.thruster_manager:
                        # Create ThrusterCommand object for thruster manager
                        command = ThrusterCommand()
                        command.id = thruster_id
                        command.velocity = velocity
                        command.enabled = enabled
                        self.thruster_manager.current_commands[thruster_id] = command
                    
                    if enabled and self.run_mode:
                        self.logger.debug(f"🚀 Thruster {thruster_id}: velocity={velocity}, enabled={enabled}")
                        try:
                            self.thrusters[thruster_id].enable_motor()
                            self.thrusters[thruster_id].set_speed(velocity)
                        except Exception as e:
                            self.logger.error(f"❌ Failed to control thruster {thruster_id}: {e}")
                    else:
                        self.logger.debug(f"⏹️  Thruster {thruster_id}: disabled")
                        try:
                            self.thrusters[thruster_id].disable_motor()
                        except Exception as e:
                            self.logger.error(f"❌ Failed to disable thruster {thruster_id}: {e}")
                else:
                    self.logger.warning(f"⚠️ Invalid thruster ID: {thruster_id}")

            # Handle other controls (lights, camera, etc.)
            if hasattr(control_msg, 'lights_on'):
                self.logger.debug(f"💡 Lights: {'ON' if control_msg.lights_on else 'OFF'}")
            
            if hasattr(control_msg, 'camera_pan'):
                self.logger.debug(f"📷 Camera pan: {control_msg.camera_pan}")
            
            if hasattr(control_msg, 'camera_tilt'):
                self.logger.debug(f"📷 Camera tilt: {control_msg.camera_tilt}")
                
        except Exception as e:
            self.logger.error(f"❌ Error executing control message: {e}")

    def main_loop(self):
        self.logger.info("Starting main loop")
        
        # Start the network client
        self.logger.info("Starting network client...")
        if not self.network_client.start():
            self.logger.error("❌ Failed to start network client")
            return
        
        self.logger.info("✅ Network client started successfully")
        
        while True:
            try:
                time.sleep(0.1)  # 10Hz control loop - safer for network
                self.run()
            except Exception as e:
                self.logger.error(f"❌ CRITICAL EXCEPTION IN MAIN LOOP: {e}")
                time.sleep(0.1)  # Brief pause on error, then continue
    
    def emergency_stop(self):
        """Emergency stop all thrusters"""
        if self.thruster_manager:
            self.thruster_manager.emergency_stop()
        self.logger.warning("Emergency stop initiated")
    
    def shutdown(self):
        """Clean shutdown of ROV systems"""
        if self.thruster_manager:
            self.thruster_manager.emergency_stop()
        
        # Stop network client
        if hasattr(self, 'network_client'):
            self.network_client.stop()
        
        if self.i2cbus:
            self.i2cbus.close_bus()
        self.logger.info("ROV shutdown completed")

def signal_handler(signum, frame):
    """Handle interrupt signals for clean shutdown"""
    print(f"\n Received signal {signum}, shutting down...")
    rov.emergency_stop()
    rov.shutdown()
    exit(0)

# Set up signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

rov = Rov()
rov.initialize_interfaces()
rov.initialize_hardware()
rov.main_loop()
rov.shutdown()
