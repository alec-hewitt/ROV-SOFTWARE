#!/usr/bin/env python3
"""
Surface Station Script for ROV Communication
Uses the new robust network communication system
"""

import time
import argparse
import logging
from typing import Dict, Any

# Import the new robust network server
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from surface.surface_network import SurfaceNetworkServer
from rov_messages_pb2 import Heartbeat, ControlMessage, ThrusterCommand


class SurfaceStation:
    """Surface station using the new robust network communication"""
    
    def __init__(self, host_ip: str = "0.0.0.0", host_port: int = 65432):
        self.host_ip = host_ip
        self.host_port = host_port
        self.server = SurfaceNetworkServer(host_ip, host_port)
        self.running = False
        
        # Statistics
        self.heartbeat_count = 0
        self.control_message_count = 0
        
        # Set up callbacks
        self.server.set_callbacks(
            on_heartbeat=self._on_heartbeat,
            on_connection_change=self._on_connection_change
        )
    
    def start(self) -> bool:
        """Start the surface station"""
        print(f"🚀 Starting surface station on {self.host_ip}:{self.host_port}")
        success = self.server.start()
        if success:
            self.running = True
            print("✅ Surface station started successfully")
        else:
            print("❌ Failed to start surface station")
        return success
    
    def stop(self):
        """Stop the surface station"""
        print("🛑 Stopping surface station...")
        self.running = False
        self.server.stop()
        print("✅ Surface station stopped")
    
    def send_control_message(self, run: bool = False, thruster_commands: list = None, 
                           lights_on: bool = False, camera_pan: float = 0.0, 
                           camera_tilt: float = 0.0) -> bool:
        """Send control message to all connected ROVs"""
        # Create control message protobuf
        control_msg = ControlMessage()
        control_msg.run = run
        control_msg.lights_on = lights_on
        control_msg.camera_pan = camera_pan
        control_msg.camera_tilt = camera_tilt
        control_msg.timestamp = int(time.time() * 1000)
        
        # Add thruster commands
        if thruster_commands is None:
            thruster_commands = []
            for i in range(6):
                thruster_commands.append({
                    'id': i,
                    'velocity': 0.0,
                    'enabled': False
                })
        
        for thruster_data in thruster_commands:
            thruster_cmd = ThrusterCommand()
            thruster_cmd.id = thruster_data.get('id', 0)
            thruster_cmd.velocity = thruster_data.get('velocity', 0.0)
            thruster_cmd.enabled = thruster_data.get('enabled', False)
            control_msg.thrusters.append(thruster_cmd)
        
        success = self.server.send_control_message(control_msg)
        if success:
            self.control_message_count += 1
            # Only log every 100th control message to reduce spam
            if self.control_message_count % 100 == 0:
                print(f"📤 Sent control message #{self.control_message_count}: run={run}, thrusters={len(thruster_commands)}")
        else:
            print("❌ Failed to send control message")
        
        return success
    
    def send_heartbeat_request(self) -> bool:
        """Send heartbeat request to all connected ROVs"""
        success = self.server.send_heartbeat_request()
        if success:
            print("📤 Sent heartbeat request")
        else:
            print("❌ Failed to send heartbeat request")
        return success
    
    def get_status(self) -> Dict[str, Any]:
        """Get surface station status"""
        connections = self.server.get_connection_info()
        return {
            'running': self.running,
            'connection_count': len(connections),
            'connections': connections,
            'heartbeat_count': self.heartbeat_count,
            'control_message_count': self.control_message_count
        }
    
    def _on_heartbeat(self, conn_id: str, heartbeat: Heartbeat):
        """Handle heartbeat from ROV"""
        self.heartbeat_count += 1
        
        # Only show heartbeat every 10th message to reduce spam
        if self.heartbeat_count % 10 == 0:
            print(f"💓 Heartbeat #{self.heartbeat_count} from {conn_id}:")
            print(f"   Battery: {heartbeat.battery_voltage:.1f}V")
            print(f"   Temperature: {heartbeat.temperature:.1f}°C")
            print(f"   PDB Temperature: {heartbeat.pdb_temperature:.1f}°C")
            print(f"   Thrusters: {len(heartbeat.thrusters)}")
            print(f"   PDB Buses: {len(heartbeat.pdb_stati)}")
            
            # Show active thrusters
            active_thrusters = [t for t in heartbeat.thrusters if t.enabled]
            if active_thrusters:
                print(f"   Active thrusters: {[t.id for t in active_thrusters]}")
            
            # Show PDB bus currents
            for b in heartbeat.pdb_stati:
                print(f"   PDB {b.id}: {b.bus_current:.1f}A")

            # Show PDB bus status
            active_buses = [b for b in heartbeat.pdb_stati if b.enabled]
            if active_buses:
                print(f"   Active PDB buses: {[b.id for b in active_buses]}")

    
    def _on_connection_change(self, connected: bool, conn_id: str, address: tuple):
        """Handle connection changes"""
        status = "Connected" if connected else "Disconnected"
        print(f"🔌 {status}: {conn_id} ({address[0]}:{address[1]})")
        
        if connected:
            print(f"   Total connections: {self.server.get_connection_count()}")


def main():
    """Main surface station loop"""
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ROV Surface Station')
    parser.add_argument('--host', default='0.0.0.0', help='Host IP address (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=65432, help='Port number (default: 65432)')
    parser.add_argument('--interval', type=float, default=2.0, help='Message interval in seconds (default: 2.0)')
    args = parser.parse_args()
    
    # Create and start surface station
    surface = SurfaceStation(args.host, args.port)
    
    if not surface.start():
        print("❌ Failed to start surface station")
        return 1
    
    try:
        print("\n🎮 Surface station running! Press Ctrl+C to stop.")
        print("📊 Status updates every 10 seconds")
        
        cycle_count = 0
        while True:
            cycle_count += 1
            
            # Send heartbeat request every 10 cycles (1Hz)
            if cycle_count % 10 == 0:
                surface.send_heartbeat_request()
            
            # Send control message every other cycle
            if cycle_count % 2 == 0:
                # Example control: enable thruster 0 with 50% power
                surface.send_control_message(
                    run=True,
                    thruster_commands=[{
                        'id': 0,
                        'velocity': 0.5,
                        'enabled': True
                    }],
                    lights_on=False,
                    camera_pan=0.0,
                    camera_tilt=0.0
                )
            else:
                # Stop all thrusters
                surface.send_control_message(
                    run=False,
                    thruster_commands=[{
                        'id': 0,
                        'velocity': 0.0,
                        'enabled': False
                    }],
                    lights_on=False,
                    camera_pan=0.0,
                    camera_tilt=0.0
                )
            
            # Show status every 10 cycles
            if cycle_count % 10 == 0:
                status = surface.get_status()
                print(f"\n📊 Status Report:")
                print(f"   Running: {status['running']}")
                print(f"   Connected ROVs: {status['connection_count']}")
                print(f"   Heartbeats received: {status['heartbeat_count']}")
                print(f"   Control messages sent: {status['control_message_count']}")
                
                if status['connections']:
                    print("   Active connections:")
                    for conn in status['connections']:
                        print(f"     {conn['id']}: {conn['state']}")
                print()
            
            time.sleep(0.1)  # 10Hz control loop - safer for network
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down surface station...")
        surface.stop()
        print("👋 Surface station shutdown complete")
        return 0
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        surface.stop()
        return 1


if __name__ == "__main__":
    main()
