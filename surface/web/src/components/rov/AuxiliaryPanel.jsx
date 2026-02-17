import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Lightbulb, LightbulbOff, Zap } from "lucide-react";

export default function AuxiliaryPanel({ lights, onLightToggle }) {
  const LightControl = ({ label, side, isOn }) => (
    <div className="flex items-center justify-between p-2 bg-slate-800/30 rounded-lg border border-slate-700/50">
      <div className="flex items-center gap-2">
        {isOn ? (
          <Lightbulb className="w-4 h-4 text-yellow-400" />
        ) : (
          <LightbulbOff className="w-4 h-4 text-gray-500" />
        )}
        <span className="text-sm text-blue-300">{label}</span>
      </div>
      <Button
        onClick={() => onLightToggle(side)}
        size="sm"
        variant={isOn ? "default" : "outline"}
        className={`w-16 transition-all duration-300 ${
          isOn
            ? "bg-yellow-500 hover:bg-yellow-600 text-white shadow-lg shadow-yellow-500/25"
            : "bg-gray-500/20 border-gray-500/40 text-gray-300 hover:bg-gray-500/30"
        }`}
      >
        {isOn ? "ON" : "OFF"}
      </Button>
    </div>
  );

  return (
    <Card className="bg-black/20 backdrop-blur-md border-cyan-500/20">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <Zap className="w-5 h-5 text-cyan-400" />
          Auxiliary
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <LightControl label="Left Light" side="left" isOn={lights.left} />
        <LightControl label="Right Light" side="right" isOn={lights.right} />
      </CardContent>
    </Card>
  );
}