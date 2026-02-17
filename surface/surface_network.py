#!/usr/bin/env python3
"""
Surface Network Server - Robust communication with ROV
Handles multiple connections, message framing, and automatic cleanup
"""

import socket
import struct
import time
import hashlib
import logging
import threading
from typing import Optional, Callable, Dict, Any, List
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
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ROVConnection:
    """Represents a connection to an ROV"""
    socket: socket.socket
    address: tuple
    state: ConnectionState
    last_heartbeat: float
    recv_buffer: bytes
    thread: Optional[threading.Thread]
    lock: threading.Lock


class SurfaceNetworkServer:
    """Robust surface network server with connection management"""
    
    def __init__(self, host_ip: str = "0.0.0.0", host_port: int = 65432):
        self.host_ip = host_ip
        self.host_port = host_port
        self.server_socket = None
        self.running = False
        
        # Connection management
        self.connections: Dict[str, ROVConnection] = {}
        self.connection_lock = threading.Lock()
        self.heartbeat_timeout = 5.0  # seconds
        self.cleanup_interval = 2.0  # seconds
        
        # Threading
        self.server_thread = None
        self.cleanup_thread = None
        
        # Callbacks
        self.on_heartbeat: Optional[Callable[[str, Heartbeat], None]] = None
        self.on_connection_change: Optional[Callable[[bool, str, tuple], None]] = None
        
        self.logger = logging.getLogger(__name__)
    
    def set_callbacks(self, 
                     on_heartbeat: Optional[Callable[[str, Heartbeat], None]] = None,
                     on_connection_change: Optional[Callable[[bool, str, tuple], None]] = None):
        """Set callback functions for different events"""
        self.on_heartbeat = on_heartbeat
        self.on_connection_change = on_connection_change
    
    def start(self) -> bool:
        """Start the surface network server"""
        if self.running:
            self.logger.warning("Server already running")
            return True
        
        try:
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host_ip, self.host_port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # 1 second timeout for accept
            
            self.running = True
            
            # Start threads
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            
            self.server_thread.start()
            self.cleanup_thread.start()
            
            self.logger.info(f"🚀 Surface server started on {self.host_ip}:{self.host_port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop the surface network server"""
        self.running = False
        
        # Close server socket first to stop accepting new connections
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        # Close all connections
        with self.connection_lock:
            for conn_id, connection in list(self.connections.items()):
                self._close_connection(conn_id)
        
        # Wait for threads with shorter timeout
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=0.5)
        
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=0.5)
        
        self.logger.info("🛑 Surface server stopped")
    
    def send_control_message(self, control_msg: ControlMessage) -> bool:
        """Send control message to all connected ROVs"""
        if not PROTOBUF_AVAILABLE:
            self.logger.error("Protobuf not available")
            return False
        
        try:
            # Wrap in network message
            network_msg = NetworkMessage()
            network_msg.type = NetworkMessage.CONTROL
            network_msg.payload = control_msg.SerializeToString()
            
            # Send to all connections
            success_count = 0
            with self.connection_lock:
                for conn_id, connection in list(self.connections.items()):
                    if self._send_to_connection(connection, network_msg.SerializeToString()):
                        success_count += 1
            
            self.logger.debug(f"📤 Sent control message to {success_count} ROVs")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to send control message: {e}")
            return False
    
    def send_heartbeat_request(self) -> bool:
        """Send heartbeat request to all connected ROVs"""
        if not PROTOBUF_AVAILABLE:
            self.logger.error("Protobuf not available")
            return False
        
        try:
            # Create heartbeat request
            heartbeat_request = HeartbeatRequest()
            heartbeat_request.request_heartbeat = True
            
            # Wrap in network message
            network_msg = NetworkMessage()
            network_msg.type = NetworkMessage.HEARTBEAT_REQUEST
            network_msg.payload = heartbeat_request.SerializeToString()
            
            # Send to all connections
            success_count = 0
            with self.connection_lock:
                for conn_id, connection in list(self.connections.items()):
                    if self._send_to_connection(connection, network_msg.SerializeToString()):
                        success_count += 1
            
            self.logger.debug(f"📤 Sent heartbeat request to {success_count} ROVs")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to send heartbeat request: {e}")
            return False
    
    def get_connection_count(self) -> int:
        """Get number of connected ROVs"""
        with self.connection_lock:
            return len(self.connections)
    
    def get_connection_info(self) -> List[Dict[str, Any]]:
        """Get information about all connections"""
        with self.connection_lock:
            connections = []
            for conn_id, connection in self.connections.items():
                connections.append({
                    'id': conn_id,
                    'address': connection.address,
                    'state': connection.state.value,
                    'last_heartbeat': connection.last_heartbeat,
                    'connected_time': time.time() - connection.last_heartbeat
                })
            return connections
    
    def _server_loop(self):
        """Main server loop - accepts new connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                self.logger.info(f"🔌 New ROV connection from {address}")
                
                # Create connection object
                conn_id = f"{address[0]}:{address[1]}"
                connection = ROVConnection(
                    socket=client_socket,
                    address=address,
                    state=ConnectionState.CONNECTED,
                    last_heartbeat=time.time(),
                    recv_buffer=b'',
                    thread=None,
                    lock=threading.Lock()
                )
                
                # Start connection handler thread
                connection.thread = threading.Thread(
                    target=self._handle_connection,
                    args=(conn_id, connection),
                    daemon=True
                )
                connection.thread.start()
                
                # Add to connections
                with self.connection_lock:
                    self.connections[conn_id] = connection
                
                if self.on_connection_change:
                    self.on_connection_change(True, conn_id, address)
                
            except socket.timeout:
                continue  # Normal timeout, continue
            except Exception as e:
                if self.running:  # Only log if we're supposed to be running
                    self.logger.error(f"Server loop error: {e}")
    
    def _handle_connection(self, conn_id: str, connection: ROVConnection):
        """Handle individual ROV connection"""
        try:
            while self.running and connection.state == ConnectionState.CONNECTED:
                try:
                    # Receive data
                    data = connection.socket.recv(4096)
                    if not data:
                        break  # Connection closed
                    
                    connection.last_heartbeat = time.time()
                    connection.recv_buffer += data
                    
                    # Process complete messages
                    while len(connection.recv_buffer) >= 8:
                        try:
                            # Parse frame header
                            msg_length, checksum = struct.unpack('>I4s', connection.recv_buffer[:8])
                            
                            # Check if we have complete message
                            if len(connection.recv_buffer) < 8 + msg_length:
                                break
                            
                            # Extract message data
                            message_data = connection.recv_buffer[8:8+msg_length]
                            
                            # Validate checksum
                            expected_checksum = hashlib.md5(message_data).digest()[:4]
                            if checksum != expected_checksum:
                                self.logger.error(f"Invalid checksum from {conn_id}")
                                connection.recv_buffer = connection.recv_buffer[8+msg_length:]
                                continue
                            
                            # Process the message
                            self._handle_message(conn_id, message_data)
                            
                            # Remove processed message from buffer
                            connection.recv_buffer = connection.recv_buffer[8+msg_length:]
                            
                        except struct.error as e:
                            self.logger.error(f"Message parsing error from {conn_id}: {e}")
                            connection.recv_buffer = b''
                            break
                
                except socket.timeout:
                    continue
                except Exception as e:
                    self.logger.error(f"Connection error for {conn_id}: {e}")
                    break
        
        except Exception as e:
            self.logger.error(f"Connection handler error for {conn_id}: {e}")
        
        finally:
            # Clean up connection
            self._close_connection(conn_id)
    
    def _handle_message(self, conn_id: str, message_data: bytes):
        """Handle incoming message from ROV"""
        if not PROTOBUF_AVAILABLE:
            self.logger.warning("Protobuf not available - cannot parse message")
            return
        
        try:
            network_msg = NetworkMessage()
            network_msg.ParseFromString(message_data)
            
            if network_msg.type == NetworkMessage.HEARTBEAT:
                self._handle_heartbeat(conn_id, network_msg.payload)
            else:
                self.logger.warning(f"Unknown message type from {conn_id}: {network_msg.type}")
                
        except Exception as e:
            self.logger.error(f"Message handling error from {conn_id}: {e}")
    
    def _handle_heartbeat(self, conn_id: str, payload: bytes):
        """Handle heartbeat message from ROV"""
        try:
            heartbeat = Heartbeat()
            heartbeat.ParseFromString(payload)
            
            if self.on_heartbeat:
                self.on_heartbeat(conn_id, heartbeat)
            
            self.logger.debug(f"💓 Heartbeat from {conn_id}: battery={heartbeat.battery_voltage}V")
            
        except Exception as e:
            self.logger.error(f"Heartbeat parsing error from {conn_id}: {e}")
    
    def _send_to_connection(self, connection: ROVConnection, data: bytes) -> bool:
        """Send data to a specific connection"""
        try:
            with connection.lock:
                # Create frame
                checksum = hashlib.md5(data).digest()[:4]
                frame = struct.pack('>I', len(data)) + checksum + data
                
                connection.socket.sendall(frame)
                return True
        except Exception as e:
            self.logger.error(f"Send error: {e}")
            return False
    
    def _close_connection(self, conn_id: str):
        """Close a specific connection"""
        with self.connection_lock:
            if conn_id in self.connections:
                connection = self.connections[conn_id]
                
                try:
                    connection.socket.close()
                except:
                    pass
                
                connection.state = ConnectionState.DISCONNECTED
                del self.connections[conn_id]
                
                self.logger.info(f"🔌 Closed connection {conn_id}")
                
                if self.on_connection_change:
                    self.on_connection_change(False, conn_id, connection.address)
    
    def _cleanup_loop(self):
        """Cleanup loop - removes stale connections"""
        while self.running:
            try:
                current_time = time.time()
                stale_connections = []
                
                with self.connection_lock:
                    for conn_id, connection in self.connections.items():
                        if current_time - connection.last_heartbeat > self.heartbeat_timeout:
                            stale_connections.append(conn_id)
                
                # Close stale connections
                for conn_id in stale_connections:
                    self.logger.warning(f"⏰ Closing stale connection {conn_id}")
                    self._close_connection(conn_id)
                
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
                time.sleep(self.cleanup_interval)


