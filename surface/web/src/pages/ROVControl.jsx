
import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Power, 
  Wifi, 
  WifiOff, 
  Battery, 
  Thermometer,
  Gauge,
  Waves,
  Camera,
  Activity
} from "lucide-react";
import { rovClient } from "../api/rovClient";

import ConnectionStatus from "../components/rov/ConnectionStatus";
import PDBStatus from "../components/rov/PDBStatus";
import ThrusterPanel from "../components/rov/ThrusterPanel";
import EnvironmentalSensors from "../components/rov/EnvironmentalSensors";
import CameraFeed from "../components/rov/CameraFeed";
import PS5Controller from "../components/rov/PS5Controller";
import MasterControls from "../components/rov/MasterControls";
import AuxiliaryPanel from "../components/rov/AuxiliaryPanel";
import ThrusterControlModal from "../components/rov/ThrusterControlModal";

export default function ROVControl() {
  const [editingThruster, setEditingThruster] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Real data from backend
  const [rovData, setRovData] = useState({
    connection: {
      isConnected: false,
      signalStrength: null,
      latency: null
    },
    masterEnable: false,
    pdb: {
      isConnected: false,
      batteryVoltage: 0.0,
      soc: 0,
      mainSwitchEnabled: false,
      mainSwitchCurrent: 0.0,
      temperature: 0.0,
      switchChannels: []
    },
    thrusters: [],
    environmental: {
      depth: null,
      pressure: null,
      temperature: 0.0
    },
    auxiliary: {
      lights: {
        left: false,
        right: false,
      }
    },
    controller: {
      leftStick: { x: 0, y: 0 },
      rightStick: { x: 0, y: 0 },
      buttons: {
        cross: false,
        circle: false,
        square: false,
        triangle: false,
        l1: false,
        r1: false,
        l2: 0,
        r2: 0
      }
    }
  });

  // Fetch real data from backend
  useEffect(() => {
    document.title = "ROV Control Panel";

    const fetchData = async () => {
      try {
        const data = await rovClient.getROVData();
        setRovData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch ROV data:', err);
        setError('Failed to connect to ROV backend');
      }
    };

    // Initial fetch
    fetchData();
    setLoading(false);

    // Poll for updates every 1 second
    const interval = setInterval(fetchData, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleMasterToggle = async () => {
    const newState = !rovData.masterEnable;
    
    try {
      await rovClient.sendMasterEnable(newState);
      // Update local state optimistically
      setRovData(prev => ({
        ...prev,
        masterEnable: newState
      }));
    } catch (err) {
      console.error('Failed to toggle master enable:', err);
      setError('Failed to toggle master enable');
    }
  };

  const handleThrusterToggle = (thrusterId) => {
    setRovData(prev => ({
      ...prev,
      thrusters: prev.thrusters.map(t => 
        t.id === thrusterId ? { ...t, enabled: !t.enabled } : t
      )
    }));
  };

  const handleChannelToggle = (channelId) => {
    setRovData(prev => ({
      ...prev,
      pdb: {
        ...prev.pdb,
        switchChannels: prev.pdb.switchChannels.map(ch =>
          ch.id === channelId ? { ...ch, enabled: !ch.enabled } : ch
        )
      }
    }));
  };

  const handleLightToggle = (side) => {
    setRovData(prev => ({
      ...prev,
      auxiliary: {
        ...prev.auxiliary,
        lights: {
          ...prev.auxiliary.lights,
          [side]: !prev.auxiliary.lights[side]
        }
      }
    }))
  }

  const handleCommandVelocityChange = (thrusterId, newVelocity) => {
    setRovData(prev => ({
      ...prev,
      thrusters: prev.thrusters.map(t =>
        t.id === thrusterId ? { ...t, commandVelocity: newVelocity } : t
      )
    }));
    // In a real app, you would send this command to the backend here.
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading ROV Control Panel...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-red-400 text-xl">Error: {error}</div>
      </div>
    );
  }

  return (
    <>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4 overflow-auto">
        {/* Background effects */}
        <div className="fixed inset-0 bg-black/5 opacity-40" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }} />
        
        <div className="relative max-w-[100vw] mx-auto">
          {/* Header */}
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-6 gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-xl flex items-center justify-center">
                <Waves className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">ROV Command Panel</h1>
                <p className="text-blue-300">Underwater Vehicle Control Interface</p>
              </div>
            </div>
            
            <div className="flex gap-4">
              <ConnectionStatus connection={rovData.connection} />
              <MasterControls 
                enabled={rovData.masterEnable}
                onToggle={handleMasterToggle}
              />
            </div>
          </div>

          {/* Main Grid Layout */}
          <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
            {/* Left Panel - Status Monitors */}
            <div className="xl:col-span-3 space-y-4">
              <EnvironmentalSensors data={rovData.environmental} />
              <PDBStatus 
                data={rovData.pdb} 
                onChannelToggle={handleChannelToggle}
              />
            </div>

            {/* Center - Camera Feed */}
            <div className="xl:col-span-6">
              <CameraFeed />
            </div>

            {/* Right Panel - Thrusters & Controller */}
            <div className="xl:col-span-3 space-y-4">
              <ThrusterPanel 
                thrusters={rovData.thrusters}
                onThrusterToggle={handleThrusterToggle}
                masterEnabled={rovData.masterEnable}
                onOpenControl={(thruster) => setEditingThruster(thruster)}
              />
              <AuxiliaryPanel 
                lights={rovData.auxiliary.lights}
                onLightToggle={handleLightToggle}
              />
              <PS5Controller data={rovData.controller} />
            </div>
          </div>
        </div>
      </div>

      {editingThruster && (
        <ThrusterControlModal
          thruster={editingThruster}
          onClose={() => setEditingThruster(null)}
          onCommandVelocityChange={handleCommandVelocityChange}
        />
      )}
    </>
  );
}
