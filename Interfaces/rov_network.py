#!/usr/bin/env python3
"""
ROV Network Client - Robust communication with surface station
Handles connection, reconnection, and message framing automatically
"""

import socket
import struct
import time
import hashlib
import logging
import threading
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Import protobuf classes
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from rov_messages_pb2 import (
        Heartbeat, ThrusterStatus, ControlMessage, 
        ThrusterCommand, NetworkMessage, HeartbeatRequest
    )
    PROTOBUF_AVAILABLE = True
except ImportError:
    PROTOBUF_AVAILABLE = False


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"


@dataclass
class MessageFrame:
    """Represents a framed message with length, checksum, and data"""
    length: int
    checksum: bytes
    data: bytes
    
    @classmethod
    def create(cls, data: bytes) -> 'MessageFrame':
        """Create a framed message from raw data"""
        checksum = hashlib.md5(data).digest()[:4]
        return cls(length=len(data), checksum=checksum, data=data)
    
    def to_bytes(self) -> bytes:
        """Convert frame to bytes for transmission"""
        return struct.pack('>I', self.length) + self.checksum + self.data
    
    def validate(self) -> bool:
        """Validate the frame checksum"""
        expected_checksum = hashlib.md5(self.data).digest()[:4]
        return self.checksum == expected_checksum


class ROVNetworkClient:
    """Robust ROV network client with auto-reconnection and error recovery"""
    
    def __init__(self, surface_ip: str = "192.168.1.1", surface_port: int = 65432):
        self.surface_ip = surface_ip
        self.surface_port = surface_port
        self.socket = None
        self.state = ConnectionState.DISCONNECTED
        self.logger = logging.getLogger(__name__)
        
        # Connection management
        self.reconnect_interval = 2.0  # seconds
        self.heartbeat_interval = 1.0  # seconds (1Hz max) - safer
        self.last_heartbeat = 0
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
        
        # Threading
        self.running = False
        self.network_thread = None
        self.heartbeat_thread = None
        self.lock = threading.Lock()
        
        # Callbacks
        self.on_control_message: Optional[Callable] = None
        self.on_heartbeat_request: Optional[Callable] = None
        self.on_connection_change: Optional[Callable] = None
        
        # Message buffer for partial reads
        self.recv_buffer = b''
        
    def set_callbacks(self, 
                     on_control_message: Optional[Callable] = None,
                     on_heartbeat_request: Optional[Callable] = None,
                     on_connection_change: Optional[Callable] = None):
        """Set callback functions for different message types"""
        self.on_control_message = on_control_message
        self.on_heartbeat_request = on_heartbeat_request
        self.on_connection_change = on_connection_change
    
    def start(self) -> bool:
        """Start the network client"""
        if self.running:
            self.logger.warning("Network client already running")
            return True
            
        self.running = True
        self.network_thread = threading.Thread(target=self._network_loop, daemon=True)
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        
        self.network_thread.start()
        self.heartbeat_thread.start()
        
        self.logger.info("🚀 ROV Network client started")
        return True
    
    def stop(self):
        """Stop the network client"""
        self.running = False
        
        # Close socket immediately to break any blocking operations
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Wait for threads with shorter timeout
        if self.network_thread and self.network_thread.is_alive():
            self.network_thread.join(timeout=0.5)
        
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=0.5)
        
        self._disconnect()
        self.logger.info("🛑 ROV Network client stopped")
    
    def send_heartbeat(self, heartbeat: Heartbeat) -> bool:
        """Send heartbeat message to surface station"""
        if not PROTOBUF_AVAILABLE:
            self.logger.error("Protobuf not available")
            return False
            
        if self.state != ConnectionState.CONNECTED:
            return False
        
        try:
            # Wrap heartbeat in network message
            network_msg = NetworkMessage()
            network_msg.type = NetworkMessage.HEARTBEAT
            network_msg.payload = heartbeat.SerializeToString()
            
            return self._send_message(network_msg.SerializeToString())
            
        except Exception as e:
            self.logger.error(f"Failed to send heartbeat: {e}")
            return False
    
    def _network_loop(self):
        """Main network loop - handles connection and message processing"""
        while self.running:
            try:
                if self.state == ConnectionState.DISCONNECTED:
                    self._connect()
                elif self.state == ConnectionState.CONNECTED:
                    self._process_messages()
                elif self.state == ConnectionState.RECONNECTING:
                    time.sleep(self.reconnect_interval)
                    self.state = ConnectionState.DISCONNECTED
                    
            except Exception as e:
                self.logger.error(f"Network loop error: {e}")
                self._handle_connection_error()
            
            time.sleep(0.1)  # Small delay to prevent busy waiting
    
    def _heartbeat_loop(self):
        """Heartbeat monitoring loop"""
        while self.running:
            if self.state == ConnectionState.CONNECTED:
                current_time = time.time()
                if current_time - self.last_heartbeat > self.heartbeat_interval * 3:
                    self.logger.warning("Heartbeat timeout - connection may be lost")
                    self._handle_connection_error()
            
            time.sleep(0.5)
    
    def _connect(self) -> bool:
        """Attempt to connect to surface station"""
        try:
            self.state = ConnectionState.CONNECTING
            self.logger.info(f"🔌 Connecting to surface station {self.surface_ip}:{self.surface_port}")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)  # 5 second timeout
            
            self.socket.connect((self.surface_ip, self.surface_port))
            
            self.state = ConnectionState.CONNECTED
            self.reconnect_attempts = 0
            self.last_heartbeat = time.time()
            
            self.logger.info("✅ Connected to surface station")
            
            if self.on_connection_change:
                self.on_connection_change(True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            self._handle_connection_error()
            return False
    
    def _disconnect(self):
        """Disconnect from surface station"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self.state = ConnectionState.DISCONNECTED
        self.recv_buffer = b''
        
        if self.on_connection_change:
            self.on_connection_change(False)
    
    def _handle_connection_error(self):
        """Handle connection errors and initiate reconnection"""
        self.logger.warning("🔌 Connection error - initiating reconnection")
        self._disconnect()
        
        self.reconnect_attempts += 1
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.state = ConnectionState.DISCONNECTED
        else:
            self.state = ConnectionState.RECONNECTING
    
    def _process_messages(self):
        """Process incoming messages from surface station"""
        try:
            # Receive data
            data = self.socket.recv(4096)
            if not data:
                raise ConnectionError("Connection closed by surface station")
            
            self.recv_buffer += data
            self.last_heartbeat = time.time()
            
            # Process complete messages
            while len(self.recv_buffer) >= 8:  # Need at least length + checksum
                try:
                    # Parse frame header
                    msg_length, checksum = struct.unpack('>I4s', self.recv_buffer[:8])
                    
                    # Check if we have complete message
                    if len(self.recv_buffer) < 8 + msg_length:
                        break  # Wait for more data
                    
                    # Extract message data
                    message_data = self.recv_buffer[8:8+msg_length]
                    
                    # Validate checksum
                    expected_checksum = hashlib.md5(message_data).digest()[:4]
                    if checksum != expected_checksum:
                        self.logger.error("Invalid message checksum - discarding")
                        self.recv_buffer = self.recv_buffer[8+msg_length:]
                        continue
                    
                    # Process the message
                    self._handle_message(message_data)
                    
                    # Remove processed message from buffer
                    self.recv_buffer = self.recv_buffer[8+msg_length:]
                    
                except struct.error as e:
                    self.logger.error(f"Message parsing error: {e}")
                    self.recv_buffer = b''  # Clear buffer on parsing error
                    break
                    
        except socket.timeout:
            pass  # Normal timeout, continue
        except Exception as e:
            self.logger.error(f"Message processing error: {e}")
            raise
    
    def _handle_message(self, message_data: bytes):
        """Handle incoming message based on type"""
        if not PROTOBUF_AVAILABLE:
            self.logger.warning("Protobuf not available - cannot parse message")
            return
        
        try:
            network_msg = NetworkMessage()
            network_msg.ParseFromString(message_data)
            
            if network_msg.type == NetworkMessage.CONTROL:
                self._handle_control_message(network_msg.payload)
            elif network_msg.type == NetworkMessage.HEARTBEAT_REQUEST:
                self._handle_heartbeat_request(network_msg.payload)
            else:
                self.logger.warning(f"Unknown message type: {network_msg.type}")
                
        except Exception as e:
            self.logger.error(f"Message handling error: {e}")
    
    def _handle_control_message(self, payload: bytes):
        """Handle control message from surface"""
        try:
            control_msg = ControlMessage()
            control_msg.ParseFromString(payload)
            
            # Convert to dict for callback
            control_data = {
                'run': control_msg.run,
                'lights_on': control_msg.lights_on,
                'camera_pan': control_msg.camera_pan,
                'camera_tilt': control_msg.camera_tilt,
                'timestamp': control_msg.timestamp,
                'thrusters': []
            }
            
            for thruster_cmd in control_msg.thrusters:
                control_data['thrusters'].append({
                    'id': thruster_cmd.id,
                    'velocity': thruster_cmd.velocity,
                    'enabled': thruster_cmd.enabled
                })
            
            if self.on_control_message:
                self.on_control_message(control_data)
            
            self.logger.debug(f"📥 Received control message: run={control_msg.run}, thrusters={len(control_msg.thrusters)}")
            
        except Exception as e:
            self.logger.error(f"Control message parsing error: {e}")
    
    def _handle_heartbeat_request(self, payload: bytes):
        """Handle heartbeat request from surface"""
        try:
            heartbeat_request = HeartbeatRequest()
            heartbeat_request.ParseFromString(payload)
            
            if self.on_heartbeat_request:
                self.on_heartbeat_request()
            
            self.logger.debug("📥 Received heartbeat request")
            
        except Exception as e:
            self.logger.error(f"Heartbeat request parsing error: {e}")
    
    def _send_message(self, data: bytes) -> bool:
        """Send a message to surface station"""
        if not self.socket or self.state != ConnectionState.CONNECTED:
            return False
        
        try:
            frame = MessageFrame.create(data)
            self.socket.sendall(frame.to_bytes())
            return True
        except Exception as e:
            self.logger.error(f"Send message error: {e}")
            self._handle_connection_error()
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to surface station"""
        return self.state == ConnectionState.CONNECTED
    
    def get_connection_state(self) -> str:
        """Get current connection state"""
        return self.state.value