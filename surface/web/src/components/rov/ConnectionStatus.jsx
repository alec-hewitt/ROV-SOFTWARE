import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Wifi, WifiOff, Activity } from "lucide-react";

export default function ConnectionStatus({ connection }) {
  const { isConnected, signalStrength, latency } = connection;

  return (
    <Card className="bg-black/20 backdrop-blur-md border-cyan-500/20">
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            {isConnected ? (
              <Wifi className="w-6 h-6 text-cyan-400" />
            ) : (
              <WifiOff className="w-6 h-6 text-red-400" />
            )}
            {isConnected && (
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />
            )}
          </div>
          
          <div>
            <div className="flex items-center gap-2">
              <Badge 
                variant={isConnected ? "default" : "destructive"}
                className={isConnected ? "bg-green-500/20 text-green-300 border-green-500/30" : ""}
              >
                {isConnected ? "CONNECTED" : "OFFLINE"}
              </Badge>
            </div>
            
            {isConnected && (
              <div className="flex items-center gap-4 mt-2 text-sm text-blue-300">
                <span>Signal: {signalStrength}%</span>
                <span className="flex items-center gap-1">
                  <Activity className="w-3 h-3" />
                  {latency}ms
                </span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}