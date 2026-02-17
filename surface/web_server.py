#!/usr/bin/env python3
"""
ROV Web Server - Integrates surface network with React UI
Serves the web interface and provides WebSocket connection for real-time data
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List
import threading
from pathlib import Path

# Web server imports
from aiohttp import web, WSMsgType
import aiohttp_cors

# Import protobuf classes
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import our surface network
from surface_network import SurfaceNetworkServer
from rov_messages_pb2 import Heartbeat, ControlMessage, ThrusterCommand


class ROVWebServer:
    """Web server that integrates surface network with React UI"""
    
    def __init__(self, host_ip: str = "0.0.0.0", host_port: int = 65432, web_port: int = 3000):
        self.host_ip = host_ip
        self.host_port = host_port
        self.web_port = web_port
        
        # Surface network server
        self.surface_server = SurfaceNetworkServer(host_ip, host_port)
        
        # Web server
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()
        
        # WebSocket connections
        self.websocket_connections: List[web.WebSocketResponse] = []
        
        # ROV data state
        self.rov_data = {
            'connection': {
                'isConnected': False,
                'signalStrength': 0,
                'latency': 0
            },
            'masterEnable': False,
            'pdb': {
                'isConnected': False,
                'batteryVoltage': 0.0,
                'soc': 0,
                'mainSwitchEnabled': False,
                'mainSwitchCurrent': 0.0,
                'temperature': 0.0,
                'switchChannels': []
            },
            'thrusters': [],
            'environmental': {
                'depth': 0.0,
                'pressure': 0.0,
                'temperature': 0.0
            },
            'auxiliary': {
                'lights': {
                    'left': False,
                    'right': False
                }
            },
            'controller': {
                'leftStick': {'x': 0, 'y': 0},
                'rightStick': {'x': 0, 'y': 0},
                'buttons': {
                    'cross': False,
                    'circle': False,
                    'square': False,
                    'triangle': False,
                    'l1': False,
                    'r1': False,
                    'l2': 0,
                    'r2': 0
                }
            }
        }
        
        # Statistics
        self.heartbeat_count = 0
        self.control_message_count = 0
        
        # Thread-safe asyncio handling
        self._loop = None
        self._pending_broadcasts = []
        
        # Set up surface network callbacks
        self.surface_server.set_callbacks(
            on_heartbeat=self._on_heartbeat,
            on_connection_change=self._on_connection_change
        )
        
        self.logger = logging.getLogger(__name__)
    
    def setup_routes(self):
        """Set up web routes"""
        # Serve static files from web/dist (built React app)
        web_path = Path(__file__).parent / "web"
        dist_path = web_path / "dist"
        
        if dist_path.exists():
            # Serve built React app static files
            self.app.router.add_static('/assets', dist_path / 'assets', name='assets')
        else:
            # Serve development files
            self.app.router.add_static('/static', web_path, name='static')
        
        # Root route - serve index.html
        self.app.router.add_get('/', self.serve_index)
        
        # API routes
        self.app.router.add_get('/api/status', self.get_status)
        self.app.router.add_get('/api/rov-data', self.get_rov_data)
        self.app.router.add_post('/api/control', self.send_control)
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Fallback to index.html for SPA routing
        self.app.router.add_get('/{path:.*}', self.serve_index)
    
    def setup_cors(self):
        """Set up CORS for development"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def serve_index(self, request):
        """Serve index.html for SPA routing"""
        web_path = Path(__file__).parent / "web"
        dist_path = web_path / "dist"
        
        if dist_path.exists():
            index_path = dist_path / "index.html"
        else:
            index_path = web_path / "index.html"
        
        if index_path.exists():
            return web.FileResponse(index_path)
        else:
            return web.Response(text="ROV Web Interface - Build the React app first", status=404)
    
    async def get_status(self, request):
        """Get server status"""
        connections = self.surface_server.get_connection_info()
        return web.json_response({
            'running': True,
            'connection_count': len(connections),
            'connections': connections,
            'heartbeat_count': self.heartbeat_count,
            'control_message_count': self.control_message_count,
            'websocket_connections': len(self.websocket_connections)
        })
    
    async def get_rov_data(self, request):
        """Get current ROV data"""
        return web.json_response(self.rov_data)
    
    async def send_control(self, request):
        """Send control message to ROV"""
        try:
            data = await request.json()
            
            # Create control message
            control_msg = ControlMessage()
            
            # Handle master enable
            master_enable = data.get('masterEnable', False)
            if master_enable:
                control_msg.run = True
                self.logger.info("🟢 Master enable activated - enabling ROV and all thrusters")
            else:
                control_msg.run = False  # Disable ROV when master enable is off
                self.logger.info("🔴 Master enable deactivated - disabling ROV and all thrusters")
            
            control_msg.lights_on = data.get('lights_on', False)
            control_msg.camera_pan = data.get('camera_pan', 0.0)
            control_msg.camera_tilt = data.get('camera_tilt', 0.0)
            control_msg.timestamp = int(time.time() * 1000)
            
            # Handle thruster commands
            thrusters_data = data.get('thrusters', [])
            
            # Handle thruster commands based on master enable state
            if master_enable:
                # Enable all 6 thrusters with neutral velocities
                for thruster_id in range(6):
                    thruster_cmd = ThrusterCommand()
                    thruster_cmd.id = thruster_id
                    thruster_cmd.velocity = 0.0  # Neutral position
                    thruster_cmd.enabled = True   # Enable all thrusters
                    control_msg.thrusters.append(thruster_cmd)
            else:
                # Disable all thrusters when master enable is off
                for thruster_id in range(6):
                    thruster_cmd = ThrusterCommand()
                    thruster_cmd.id = thruster_id
                    thruster_cmd.velocity = 0.0  # Stop thrusters
                    thruster_cmd.enabled = False  # Disable all thrusters
                    control_msg.thrusters.append(thruster_cmd)
            
            # Send to ROV
            success = self.surface_server.send_control_message(control_msg)
            
            if success:
                self.control_message_count += 1
                
                # Update local ROV data to reflect control state
                self.rov_data['masterEnable'] = master_enable
                # Update thruster states
                for thruster_cmd in control_msg.thrusters:
                    if thruster_cmd.id < len(self.rov_data['thrusters']):
                        self.rov_data['thrusters'][thruster_cmd.id]['enabled'] = thruster_cmd.enabled
                        self.rov_data['thrusters'][thruster_cmd.id]['commandVelocity'] = thruster_cmd.velocity
                
                message = "Master enable activated" if master_enable else "Master enable deactivated"
                return web.json_response({'success': True, 'message': message})
            else:
                return web.json_response({'success': False, 'message': 'Failed to send control'}, status=500)
                
        except Exception as e:
            self.logger.error(f"Control error: {e}")
            return web.json_response({'success': False, 'message': str(e)}, status=500)
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections for real-time data"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_connections.append(ws)
        self.logger.info(f"WebSocket connected. Total connections: {len(self.websocket_connections)}")
        
        # Start periodic task to process pending broadcasts
        async def process_broadcasts_periodically():
            while ws in self.websocket_connections:
                await self._process_pending_broadcasts()
                await asyncio.sleep(0.1)  # Check every 100ms
        
        # Start periodic task to request heartbeats
        async def request_heartbeats_periodically():
            while ws in self.websocket_connections:
                # Request heartbeat from ROV every 1 second
                self.surface_server.send_heartbeat_request()
                await asyncio.sleep(1.0)
        
        # Start the periodic tasks
        broadcast_task = asyncio.create_task(process_broadcasts_periodically())
        heartbeat_task = asyncio.create_task(request_heartbeats_periodically())
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        # Handle incoming WebSocket messages
                        if data.get('type') == 'ping':
                            await ws.send_str(json.dumps({'type': 'pong'}))
                    except json.JSONDecodeError:
                        pass
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f'WebSocket error: {ws.exception()}')
                    break
        finally:
            # Cancel the tasks
            broadcast_task.cancel()
            heartbeat_task.cancel()
            self.websocket_connections.remove(ws)
            self.logger.info(f"WebSocket disconnected. Total connections: {len(self.websocket_connections)}")
        
        return ws
    
    async def broadcast_data(self, data: Dict[str, Any]):
        """Broadcast data to all WebSocket connections"""
        if not self.websocket_connections:
            return
        
        message = json.dumps(data)
        disconnected = []
        
        for ws in self.websocket_connections:
            try:
                await ws.send_str(message)
            except Exception as e:
                self.logger.error(f"WebSocket send error: {e}")
                disconnected.append(ws)
        
        # Remove disconnected clients
        for ws in disconnected:
            if ws in self.websocket_connections:
                self.websocket_connections.remove(ws)
    
    def _on_heartbeat(self, conn_id: str, heartbeat: Heartbeat):
        """Handle heartbeat from ROV"""
        self.heartbeat_count += 1
        
        # Update ROV data - don't override connection status here
        # Connection status is managed by _on_connection_change
        self.rov_data['connection']['signalStrength'] = None  # No real data available
        self.rov_data['connection']['latency'] = None  # No real data available
        
        # Update PDB data
        self.rov_data['pdb']['isConnected'] = True
        self.rov_data['pdb']['batteryVoltage'] = heartbeat.battery_voltage
        self.rov_data['pdb']['temperature'] = heartbeat.pdb_temperature
        self.rov_data['pdb']['switchChannels'] = []
        
        for pdb_status in heartbeat.pdb_stati:
            self.rov_data['pdb']['switchChannels'].append({
                'id': pdb_status.id,
                'enabled': pdb_status.enabled,
                'voltage': None,  # No real data available
                'current': pdb_status.bus_current
            })
        
        # Update thrusters - preserve control state
        for thruster_status in heartbeat.thrusters:
            thruster_id = thruster_status.id
            if thruster_id < len(self.rov_data['thrusters']):
                # Update existing thruster data, preserve control state
                self.rov_data['thrusters'][thruster_id]['velocity'] = thruster_status.velocity
                self.rov_data['thrusters'][thruster_id]['current'] = thruster_status.current
                # Only update enabled state if not under control
                if not self.rov_data['masterEnable']:
                    self.rov_data['thrusters'][thruster_id]['enabled'] = thruster_status.enabled
            else:
                # Add new thruster
                self.rov_data['thrusters'].append({
                    'id': thruster_status.id,
                    'name': f'T{thruster_status.id}',
                    'isConnected': True,
                    'enabled': thruster_status.enabled,
                    'velocity': thruster_status.velocity,
                    'commandVelocity': thruster_status.velocity,
                    'current': thruster_status.current
                })
        
        # Update environmental data
        self.rov_data['environmental']['temperature'] = heartbeat.temperature
        # No real depth/pressure sensors available
        self.rov_data['environmental']['depth'] = None
        self.rov_data['environmental']['pressure'] = None
        
        # Broadcast to WebSocket clients
        self.logger.debug(f"💓 Heartbeat from {conn_id}: battery={heartbeat.battery_voltage:.1f}V")
        
        # Broadcast heartbeat data using thread-safe method
        self._schedule_broadcast({
            'type': 'heartbeat',
            'data': self.rov_data
        })
    
    def _on_connection_change(self, connected: bool, conn_id: str, address: tuple):
        """Handle connection changes"""
        self.rov_data['connection']['isConnected'] = connected
        
        if not connected:
            # Reset data when disconnected
            self.rov_data['pdb']['isConnected'] = False
            self.rov_data['thrusters'] = []
        
        # Broadcast connection status using thread-safe method
        self._schedule_broadcast({
            'type': 'connection_change',
            'connected': connected,
            'connection_id': conn_id
        })
        
        status = "Connected" if connected else "Disconnected"
        self.logger.info(f"🔌 {status}: {conn_id} ({address[0]}:{address[1]})")
    
    def _schedule_broadcast(self, data: dict):
        """Thread-safe method to schedule a broadcast"""
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # We're in the main thread with an event loop
                asyncio.create_task(self.broadcast_data(data))
            else:
                # We're in a different thread, queue the broadcast
                self._pending_broadcasts.append(data)
        except RuntimeError:
            # No event loop running, queue the broadcast
            self._pending_broadcasts.append(data)
    
    async def _process_pending_broadcasts(self):
        """Process any pending broadcasts from other threads"""
        while self._pending_broadcasts:
            data = self._pending_broadcasts.pop(0)
            await self.broadcast_data(data)
    
    def start(self):
        """Start both surface server and web server"""
        # Start surface network server
        self.logger.info("🚀 Starting surface network server...")
        if not self.surface_server.start():
            self.logger.error("❌ Failed to start surface network server")
            return False
        
        # Start web server with global heartbeat requests
        self.logger.info(f"🌐 Starting web server on port {self.web_port}...")
        
        # Start global heartbeat request loop in a background thread
        def heartbeat_request_loop():
            while True:
                try:
                    # Request heartbeat from ROV every 1 second
                    self.surface_server.send_heartbeat_request()
                    time.sleep(1.0)
                except Exception as e:
                    self.logger.error(f"Heartbeat request error: {e}")
                    time.sleep(1.0)
        
        heartbeat_thread = threading.Thread(target=heartbeat_request_loop, daemon=True)
        heartbeat_thread.start()
        
        web.run_app(self.app, host=self.host_ip, port=self.web_port)
        return True
    
    def stop(self):
        """Stop both servers"""
        self.logger.info("🛑 Stopping servers...")
        self.surface_server.stop()
        # Web server will stop when the process exits


def main():
    """Main function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start web server
    web_server = ROVWebServer("0.0.0.0", 65432, 3000)
    
    try:
        web_server.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down web server...")
        web_server.stop()
        print("👋 Web server shutdown complete")


if __name__ == "__main__":
    main()
