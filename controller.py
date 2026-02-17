# controller.py: A clean, protobuf-focused thruster management system
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ThrusterCommand:
    """Represents a single thruster command"""
    id: int
    velocity: float  # -1.0 to 1.0
    enabled: bool
    
    def __post_init__(self):
        """Validate thruster command data"""
        if not isinstance(self.id, int) or self.id < 0 or self.id > 5:
            raise ValueError(f"Invalid thruster ID: {self.id}. Must be 0-5")
        
        if not isinstance(self.velocity, (int, float)) or self.velocity < -1.0 or self.velocity > 1.0:
            raise ValueError(f"Invalid velocity: {self.velocity}. Must be -1.0 to 1.0")
        
        if not isinstance(self.enabled, bool):
            raise ValueError(f"Invalid enabled value: {self.enabled}. Must be boolean")


class ThrusterManager:
    """Manages thruster operations with clean protobuf integration"""
    
    def __init__(self, thrusters: List):
        """
        Initialize thruster manager
        
        Args:
            thrusters: List of thruster objects (Revolver instances)
        """
        self.logger = logging.getLogger(__name__)
        self.thrusters = thrusters
        self.current_commands: Dict[int, ThrusterCommand] = {}
        
        # Initialize with all thrusters disabled
        for i in range(len(thrusters)):
            self.current_commands[i] = ThrusterCommand(
                id=i, 
                velocity=0.0, 
                enabled=False
            )
    
    def process_protobuf_commands(self, thruster_commands: List[Dict[str, Any]]) -> bool:
        """
        Process thruster commands from protobuf message
        
        Args:
            thruster_commands: List of thruster command dicts from protobuf
            
        Returns:
            bool: True if all commands processed successfully
        """
        try:
            self.logger.debug(f"🔄 Processing {len(thruster_commands)} thruster commands")
            
            # Update current commands
            for cmd_dict in thruster_commands:
                try:
                    cmd = ThrusterCommand(
                        id=int(cmd_dict['id']),
                        velocity=float(cmd_dict['velocity']),
                        enabled=bool(cmd_dict['enabled'])
                    )
                    self.current_commands[cmd.id] = cmd
                    self.logger.debug(f"✅ Thruster {cmd.id}: velocity={cmd.velocity}, enabled={cmd.enabled}")
                    
                except (ValueError, KeyError) as e:
                    self.logger.error(f"❌ Invalid thruster command {cmd_dict}: {e}")
                    return False
            
            # Execute all commands
            return self._execute_commands()
            
        except Exception as e:
            self.logger.error(f"❌ Exception processing thruster commands: {e}")
            return False
    
    def _execute_commands(self) -> bool:
        """Execute all current thruster commands"""
        try:
            for thruster_id, command in self.current_commands.items():
                if thruster_id >= len(self.thrusters):
                    self.logger.error(f"❌ Thruster {thruster_id} not found")
                    continue
                
                thruster = self.thrusters[thruster_id]
                
                # Handle enable/disable
                if command.enabled:
                    if not thruster.motor_enabled:
                        thruster.enable_motor()
                        self.logger.debug(f"🔧 Enabled thruster {thruster_id}")
                else:
                    if thruster.motor_enabled:
                        thruster.disable_motor()
                        self.logger.debug(f"🔧 Disabled thruster {thruster_id}")
                
                # Handle velocity (only if enabled)
                if command.enabled and command.velocity != 0:
                    success = thruster.command_speed(command.velocity)
                    if success:
                        self.logger.debug(f"⚡ Thruster {thruster_id} set to velocity {command.velocity}")
                    else:
                        self.logger.warning(f"⚠️ Failed to set thruster {thruster_id} velocity")
                elif command.enabled and command.velocity == 0:
                    # Stop the thruster
                    thruster.command_speed(0.0)
                    self.logger.debug(f"⏹️ Thruster {thruster_id} stopped")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Exception executing thruster commands: {e}")
            return False
    
    def get_thruster_status(self) -> List[Dict[str, Any]]:
        """Get current status of all thrusters for heartbeat"""
        status_list = []
        
        for thruster_id, command in self.current_commands.items():
            if thruster_id < len(self.thrusters):
                thruster = self.thrusters[thruster_id]
                status_list.append({
                    'id': thruster_id,
                    'velocity': command.velocity,
                    'enabled': command.enabled,
                    'current': 0.0,  # TODO: Add actual current reading
                    'temperature': 0.0  # TODO: Add actual temperature reading
                })
        
        return status_list
    
    def emergency_stop(self):
        """Emergency stop all thrusters"""
        self.logger.warning("🚨 EMERGENCY STOP - Disabling all thrusters")
        
        for thruster_id in range(len(self.thrusters)):
            self.current_commands[thruster_id] = ThrusterCommand(
                id=thruster_id,
                velocity=0.0,
                enabled=False
            )
        
        self._execute_commands()
        self.logger.info("✅ Emergency stop completed")
    
    def get_status_summary(self) -> str:
        """Get human-readable status summary"""
        active_count = sum(1 for cmd in self.current_commands.values() if cmd.enabled)
        total_count = len(self.current_commands)
        
        return f"Thrusters: {active_count}/{total_count} active"
