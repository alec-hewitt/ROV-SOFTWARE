import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Fan, Edit } from "lucide-react";

export default function ThrusterPanel({ thrusters, onThrusterToggle, masterEnabled, onOpenControl }) {
  return (
    <Card className="bg-black/20 backdrop-blur-md border-cyan-500/20">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <Fan className="w-5 h-5 text-cyan-400" />
          Thrusters
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {thrusters.map((thruster) => (
          <div
            key={thruster.id}
            className="p-2 bg-slate-800/30 rounded-lg border border-slate-700/50 flex items-center gap-2 group cursor-pointer hover:bg-slate-700/50 transition-colors"
            onClick={() => onOpenControl(thruster)}
          >
            <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
              thruster.isConnected ? "bg-green-400" : "bg-red-400"
            }`} />
            <span className="text-white font-medium text-sm w-8">{thruster.name}</span>
            
            <div className="flex-1 grid grid-cols-2 gap-2 text-xs text-center">
              <div>
                <div className="text-blue-300">Vel</div>
                <div className="text-white font-mono font-bold">{thruster.velocity !== null && thruster.velocity !== undefined ? thruster.velocity.toFixed(1) : "--"}</div>
              </div>
              <div>
                <div className="text-purple-300">Cur</div>
                <div className="text-white font-mono font-bold">{thruster.current !== null && thruster.current !== undefined ? thruster.current.toFixed(1) : "--"}</div>
              </div>
            </div>

            <Button
              onClick={(e) => { e.stopPropagation(); onThrusterToggle(thruster.id); }}
              disabled={!masterEnabled}
              size="sm"
              variant={thruster.enabled ? "default" : "outline"}
              className={`w-12 h-7 text-xs transition-all z-10 ${
                thruster.enabled && masterEnabled
                  ? "bg-green-500 hover:bg-green-600 shadow-lg shadow-green-500/20" 
                  : "bg-red-500/20 border-red-500/40 text-red-300"
              }`}
            >
              {thruster.enabled ? "ON" : "OFF"}
            </Button>
            <Edit className="w-4 h-4 text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}