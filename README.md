# ROV Software

Underwater vehicle control software that communicates with a surface station over Ethernet and controls thrusters via I2C.

## Features

- **Thruster Control**: Manages 6 thrusters with individual speed and enable/disable control
- **Surface Communication**: TCP/IP communication with surface station laptop
- **Hardware Interface**: I2C communication with motor controllers and power distribution board
- **Health Monitoring**: Continuous health checks and heartbeat messages
- **Logging**: Comprehensive logging system for debugging and monitoring

## Hardware Requirements

- Raspberry Pi (3 or 4 recommended)
- I2C-enabled motor controllers
- Power distribution board
- Ethernet connection for surface communication

## Quick Start with Docker

### Prerequisites

1. **Install Docker on Raspberry Pi**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   # Log out and back in for group changes to take effect
   ```

2. **Install Docker Compose**:
   ```bash
   sudo apt-get update
   sudo apt-get install docker-compose
   ```

3. **Enable I2C on Raspberry Pi**:
   ```bash
   sudo raspi-config
   # Navigate to Interface Options > I2C > Enable
   sudo reboot
   ```

4. **Enable SSH on Raspberry Pi**:
   ```bash
   sudo raspi-config
   # Navigate to Interface Options > SSH > Enable
   ```

5. **Set up SSH keys for passwordless access**:
   ```bash
   ssh-keygen -t rsa -b 4096
   ssh-copy-id pi@192.168.1.12
   ```

### Initial Deployment

**One command from your laptop:**
```bash
./docker-update.sh
```

This script automatically:
1. ✅ Checks Pi connection
2. ✅ Sets up directory structure on Pi
3. ✅ Copies Docker configuration files
4. ✅ Builds Docker image on your laptop
5. ✅ Deploys to Pi

### Remote Updates from Laptop

Once deployed, you can update the software remotely from your laptop using Docker:

1. **Simple Docker Update** (build and deploy):
   ```bash
   ./docker-update.sh
   ```

2. **Registry-based Update** (for production):
   ```bash
   ./docker-registry-update.sh
   ```

3. **Manual Docker Commands**:
   ```bash
   # Build and save image
   docker build -t rov-software .
   docker save rov-software > rov-software.tar
   
   # Copy to Pi and deploy
   scp rov-software.tar pi@192.168.1.12:~/
   ssh pi@192.168.1.12 "docker load < ~/rov-software.tar && cd ROV-SOFTWARE && docker-compose up -d --force-recreate"
   ```

### Management Commands

From your laptop:
- **Update software**: `./docker-update.sh`
- **Check status**: `./manage-pi.sh status`
- **View logs**: `./manage-pi.sh logs`
- **Restart services**: `./manage-pi.sh restart`
- **Stop/Start services**: `./manage-pi.sh stop` / `./manage-pi.sh start`
- **Full management**: `./manage-pi.sh help`

## Manual Docker Commands

If you prefer to use Docker commands directly from your laptop:

```bash
# Build and save image
docker build -t rov-software .
docker save rov-software > rov-software.tar

# Copy to Pi and deploy
scp rov-software.tar pi@192.168.1.12:~/
ssh pi@192.168.1.12 "docker load < ~/rov-software.tar && cd ROV-SOFTWARE && docker-compose up -d --force-recreate"
```

## Configuration

### Pi Connection Configuration

Before using remote update scripts, configure your Pi connection details:

1. **Update the scripts directly**:
   - `docker-update.sh` (lines 6-8)
   - `docker-registry-update.sh` (lines 8-10)

2. **Key values to update**:
   - `PI_HOST`: Your Pi's IP address (currently 192.168.1.12)
   - `PI_USER`: Username on Pi (usually "pi")
   - `PI_PATH`: Path to ROV software on Pi

### Network Configuration

The software is configured to communicate with the surface station at `192.168.1.12:65432`. To change this:

1. Edit `Interfaces/Surface.py`
2. Update the `host_ip` and `host_port` in the `Surface` class
3. Rebuild and redeploy: `./deploy.sh deploy`

### I2C Configuration

The software uses I2C bus 1 by default. If you need to use a different bus:

1. Edit `rov.py` in the `initialize_interfaces()` method
2. Change `I2cBus(1)` to your desired bus number
3. Update the `docker-compose.yml` device mapping if needed
4. Rebuild and redeploy: `./docker-update.sh`

## Development

### Local Development

For development and testing:

1. **Create virtual environment**:
   ```bash
   python3 -m venv rov-venv
   source rov-venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Test locally**:
   ```bash
   python rov.py
   ```

3. **Deploy to Pi**:
   ```bash
   ./docker-update.sh
   ```

### Testing

The software includes basic error handling and logging. Check the `logging/` directory for log files.

## Troubleshooting

### Common Issues

1. **Permission Denied for I2C**:
   - Ensure the container has access to I2C devices
   - Check that I2C is enabled on the Raspberry Pi
   - Verify device mappings in `docker-compose.yml`

2. **Network Connection Issues**:
   - Verify the surface station IP address is correct
   - Check firewall settings
   - Ensure the port 65432 is accessible

3. **Container Won't Start**:
   - Check Docker logs: `docker-compose logs`
   - Verify all dependencies are installed
   - Check for port conflicts

### Debug Mode

To run with more verbose logging, modify the logging level in `rov.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Architecture

```
┌─────────────────┐    TCP/IP     ┌─────────────────┐
│   Surface       │◄─────────────►│   ROV Software  │
│   Station       │   Port 65432  │   (Docker)      │
│   (Laptop)      │               │                 │
└─────────────────┘               └─────────────────┘
                                              │
                                              │ I2C
                                              ▼
                                    ┌─────────────────┐
                                    │   Hardware      │
                                    │  - Thrusters    │
                                    │  - PDB          │
                                    └─────────────────┘
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in the `logging/` directory
3. Open an issue on the repository
