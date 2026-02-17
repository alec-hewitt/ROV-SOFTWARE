# ROV Software Utils

## Surface Station Script

The `surface_station.py` script allows you to communicate with the ROV from your laptop (surface station).

### Prerequisites

1. **Generate protobuf files** (run from project root):
   ```bash
   ./generate_protobuf.sh
   ```

2. **Install Python dependencies**:
   ```bash
   pip install protobuf
   ```

### Usage Examples

#### Monitor ROV Heartbeat
```bash
# Monitor heartbeat for 60 seconds (default)
python utils/surface_station.py --rov-ip 192.168.1.12

# Monitor for 2 minutes
python utils/surface_station.py --rov-ip 192.168.1.12 --duration 120

# Use custom ROV IP
python utils/surface_station.py --rov-ip 10.0.0.100
```

#### Send Control Commands
```bash
# Enable ROV run mode
python utils/surface_station.py --rov-ip 192.168.1.12 --command control --run

# Control specific thruster (ID 0, velocity 0.5, enabled)
python utils/surface_station.py --rov-ip 192.168.1.12 --command control --thruster 0 0.5 1

# Multiple thrusters
python utils/surface_station.py --rov-ip 192.168.1.12 --command control --run --thruster 0 0.3 1 --thruster 1 -0.2 1
```

### Command Line Options

- `--rov-ip`: ROV IP address (default: 192.168.1.12)
- `--rov-port`: ROV port (default: 65432)
- `--command`: Command to execute (`monitor` or `control`)
- `--duration`: Monitoring duration in seconds (default: 60)
- `--run`: Enable ROV run mode
- `--thruster`: Thruster command (ID VELOCITY ENABLED)

### Message Format

The script uses Protocol Buffers for efficient communication:

- **Heartbeat Messages**: ROV status, battery, temperature, thruster status
- **Control Messages**: Run mode, thruster commands, lights, camera control

### Troubleshooting

1. **"Protobuf classes not available"**: Run `./generate_protobuf.sh` first
2. **Connection failed**: Check ROV IP address and network connectivity
3. **No heartbeat received**: Ensure ROV is running and listening on the correct port
