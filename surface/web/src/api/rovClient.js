// Simple API client for ROV backend
const API_BASE_URL = 'http://localhost:3000/api';

class ROVClient {
  async getROVData() {
    try {
      const response = await fetch(`${API_BASE_URL}/rov-data`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch ROV data:', error);
      throw error;
    }
  }

  async getStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/status`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to fetch status:', error);
      throw error;
    }
  }

  async sendControl(controlData) {
    try {
      const response = await fetch(`${API_BASE_URL}/control`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(controlData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to send control command:', error);
      throw error;
    }
  }

  async sendMasterEnable(enabled) {
    return this.sendControl({ masterEnable: enabled });
  }

  async sendThrusterCommand(thrusterId, velocity, enabled) {
    return this.sendControl({
      thrusters: [{
        id: thrusterId,
        velocity: velocity,
        enabled: enabled
      }]
    });
  }
}

export const rovClient = new ROVClient();
