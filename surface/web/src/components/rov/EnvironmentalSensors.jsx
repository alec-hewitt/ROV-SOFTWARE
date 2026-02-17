import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Gauge, Waves, Thermometer } from "lucide-react";

export default function EnvironmentalSensors({ data }) {
  const { depth, pressure, temperature } = data;

  const sensors = [
    {
      icon: Waves,
      label: "Depth",
      value: depth !== null && depth !== undefined ? depth.toFixed(1) : "--",
      unit: "m",
      color: "text-blue-400",
      bgColor: "bg-blue-500/10"
    },
    {
      icon: Gauge,
      label: "Pressure",
      value: pressure !== null && pressure !== undefined ? pressure.toFixed(2) : "--",
      unit: "bar",
      color: "text-purple-400",
      bgColor: "bg-purple-500/10"
    },
    {
      icon: Thermometer,
      label: "Temperature",
      value: temperature !== null && temperature !== undefined ? temperature.toFixed(1) : "--",
      unit: "°C",
      color: "text-orange-400",
      bgColor: "bg-orange-500/10"
    }
  ];

  return (
    <Card className="bg-black/20 backdrop-blur-md border-cyan-500/20">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <Gauge className="w-5 h-5 text-cyan-400" />
          Environmental
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {sensors.map((sensor) => (
          <div key={sensor.label} className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${sensor.bgColor}`}>
              <sensor.icon className={`w-4 h-4 ${sensor.color}`} />
            </div>
            <div className="flex-1">
              <div className="text-sm text-blue-300">{sensor.label}</div>
              <div className="text-white font-mono font-bold">
                {sensor.value} <span className="text-xs font-normal">{sensor.unit}</span>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}