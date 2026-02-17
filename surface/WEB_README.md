# ROV Web Interface

A modern React-based web interface for controlling and monitoring your ROV.

## Features

- **Real-time Data**: Live heartbeat data from ROV via WebSocket
- **Thruster Control**: Individual thruster control with velocity sliders
- **PDB Monitoring**: Power distribution board status and current readings
- **Environmental Sensors**: Temperature, depth, and pressure monitoring
- **Connection Status**: Real-time connection health monitoring
- **Responsive Design**: Works on desktop, tablet, and mobile

## Quick Start

### Option 1: Automatic Setup
```bash
cd surface
python run_web.py
```

This will:
1. Install npm dependencies
2. Build the React app
3. Install Python dependencies
4. Start the web server

### Option 2: Manual Setup

1. **Build React App**:
   ```bash
   cd surface/web
   npm install
   npm run build
   ```

2. **Install Python Dependencies**:
   ```bash
   cd surface
   pip install -r requirements.txt
   ```

3. **Start Web Server**:
   ```bash
   python web_server.py
   ```

4. **Open Browser**:
   Navigate to `http://localhost:3000`

## Architecture

- **Backend**: Python web server (`web_server.py`) that integrates with surface network
- **Frontend**: React app with modern UI components
- **Communication**: WebSocket for real-time data, REST API for controls
- **Data Flow**: ROV → Surface Network → Web Server → React UI

## Development

### Frontend Development
```bash
cd surface/web
npm run dev  # Starts Vite dev server on port 5173
```

### Backend Development
```bash
cd surface
python web_server.py  # Starts web server on port 3000
```

## API Endpoints

- `GET /api/status` - Server status
- `GET /api/rov-data` - Current ROV data
- `POST /api/control` - Send control commands
- `GET /ws` - WebSocket connection for real-time data

## Integration

The web server automatically:
- Connects to the surface network server
- Receives heartbeat data from ROV
- Broadcasts data to connected web clients
- Handles control commands from the web UI

No modifications needed to `surface_test.py` - the web server runs independently!
