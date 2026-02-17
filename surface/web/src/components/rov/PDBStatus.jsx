
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Battery, Power, Thermometer, Zap } from "lucide-react";

export default function PDBStatus({ data, onChannelToggle }) {
  const { isConnected, batteryVoltage, soc, mainSwitchEnabled, mainSwitchCurrent, temperature, switchChannels } = data;

  const getSoCColor = (percentage) => {
    if (percentage > 50) return "bg-green-500";
    if (percentage > 20) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <Card className="bg-black/20 backdrop-blur-md border-cyan-500/20">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <Battery className="w-5 h-5 text-cyan-400" />
          Power Distribution
          <Badge variant={isConnected ? "default" : "destructive"} className="ml-auto">
            {isConnected ? "ONLINE" : "OFFLINE"}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Battery SoC */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-xs text-blue-300">
            <span>Battery SoC</span>
            <span className="text-white font-mono font-bold">{soc !== null && soc !== undefined ? soc.toFixed(0) : "--"}%</span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${getSoCColor(soc)}`}
              style={{ width: `${soc}%` }}
            />
          </div>
        </div>

        {/* Main Power Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-blue-500/10 p-3 rounded-lg">
            <div className="text-xs text-blue-300">Battery</div>
            <div className="text-white font-mono font-bold">{batteryVoltage !== null && batteryVoltage !== undefined ? batteryVoltage.toFixed(1) : "--"}V</div>
          </div>
          <div className="bg-green-500/10 p-3 rounded-lg">
            <div className="text-xs text-green-300">Main Current</div>
            <div className="text-white font-mono font-bold">{mainSwitchCurrent !== null && mainSwitchCurrent !== undefined ? mainSwitchCurrent.toFixed(1) : "--"}A</div>
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Power className="w-4 h-4 text-yellow-400" />
            <span className="text-sm text-blue-300">Main Switch</span>
          </div>
          <Badge variant={mainSwitchEnabled ? "default" : "secondary"}>
            {mainSwitchEnabled ? "ON" : "OFF"}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          <Thermometer className="w-4 h-4 text-orange-400" />
          <span className="text-sm text-blue-300">Temperature</span>
          <span className="text-white font-mono ml-auto">{temperature !== null && temperature !== undefined ? temperature.toFixed(1) : "--"}°C</span>
        </div>

        {/* Switch Channels */}
        <div>
          <h4 className="text-sm text-blue-300 mb-2 flex items-center gap-1">
            <Zap className="w-3 h-3" />
            Switch Channels
          </h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {switchChannels.map((channel) => (
              <div key={channel.id} className="flex items-center gap-2 p-2 bg-slate-800/30 rounded border border-slate-700/50">
                <Button
                  onClick={() => onChannelToggle(channel.id)}
                  size="sm"
                  variant={channel.enabled ? "default" : "outline"}
                  className={`w-12 h-8 text-xs ${
                    channel.enabled
                      ? "bg-green-500 hover:bg-green-600"
                      : "bg-red-500/20 border-red-500/40 text-red-300"
                  }`}
                >
                  CH{channel.id}
                </Button>
                <div className="flex-1 text-xs">
                  <div className="text-white font-mono">{channel.voltage !== null && channel.voltage !== undefined ? channel.voltage.toFixed(1) : "--"}V</div>
                  <div className="text-blue-300">{channel.current !== null && channel.current !== undefined ? channel.current.toFixed(1) : "--"}A</div>
                </div>
                <div className={`w-2 h-2 rounded-full ${
                  channel.enabled ? "bg-green-400" : "bg-red-400"
                }`} />
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
