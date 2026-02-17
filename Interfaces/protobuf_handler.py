import logging
import time
from typing import Optional, Dict, Any
import struct

# Import the generated protobuf classes from root directory
import sys
import os

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from rov_messages_pb2 import (
    Heartbeat, ThrusterStatus, ControlMessage, 
    ThrusterCommand, NetworkMessage
)


class ProtobufHandler:
    """Handles protobuf message serialization/deserialization for ROV communication"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        if not all([Heartbeat, ThrusterStatus, ControlMessage, ThrusterCommand, NetworkMessage]):
            self.logger.warning("Protobuf classes not available - using fallback JSON mode")
    
    def parse_control_message(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Parse incoming control message from surface"""
        if len(data) >= 4:
            # Remove length prefix and parse
            msg_length = struct.unpack('>I', data[:4])[0]
            if len(data) >= 4 + msg_length:
                network_msg = NetworkMessage()
                network_msg.ParseFromString(data[4:4+msg_length])
                return network_msg
            else:
                self.logger.warning(f"Incomplete message: expected {msg_length} bytes, got {len(data)-4}")
                return None
        return None
    

