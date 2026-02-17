
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Gamepad2 } from "lucide-react";

export default function PS5Controller({ data }) {
  const { leftStick, rightStick, buttons } = data;

  const ButtonIndicator = ({ active, label, className = "" }) => (
    <div className={`relative ${className}`}>
      <div 
        className={`w-8 h-8 rounded-full border-2 transition-all duration-150 ${
          active 
            ? "bg-cyan-400 border-cyan-400 shadow-lg shadow-cyan-400/50" 
            : "border-gray-600 bg-gray-800"
        }`}
      />
      <span className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 text-xs text-blue-300">
        {label}
      </span>
    </div>
  );

  const ShoulderButtonIndicator = ({ active, label, isLarge = false }) => (
    <div className="relative">
      <div 
        className={`${isLarge ? 'w-12 h-8' : 'w-10 h-6'} rounded-md border-2 transition-all duration-150 ${
          active 
            ? "bg-cyan-400 border-cyan-400 shadow-lg shadow-cyan-400/50" 
            : "border-gray-600 bg-gray-800"
        }`}
      />
      <span className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 text-xs text-blue-300">
        {label}
      </span>
    </div>
  );

  const StickIndicator = ({ x, y, label }) => (
    <div className="relative">
      <div className="w-16 h-16 border-2 border-gray-600 rounded-full bg-gray-800 relative">
        <div 
          className="absolute w-4 h-4 bg-cyan-400 rounded-full shadow-lg shadow-cyan-400/50 transition-all duration-100"
          style={{
            left: `${((x + 1) / 2) * 48 + 8}px`,
            top: `${((y + 1) / 2) * 48 + 8}px`,
            transform: 'translate(-50%, -50%)'
          }}
        />
      </div>
      <span className="block text-xs text-blue-300 mt-2 text-center">{label}</span>
    </div>
  );

  // TriggerIndicator component is removed as per the outline for shoulder button rendering

  return (
    <Card className="bg-black/20 backdrop-blur-md border-cyan-500/20">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <Gamepad2 className="w-5 h-5 text-cyan-400" />
          Controller Input
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6 space-y-6">
        {/* Shoulder buttons */}
        <div className="flex justify-between items-start px-4">
          <div className="space-y-3 flex flex-col items-center">
            <ShoulderButtonIndicator active={buttons.l1} label="L1" />
            <ShoulderButtonIndicator active={buttons.l2 > 0} label="L2" isLarge={true} />
          </div>
          <div className="space-y-3 flex flex-col items-center">
            <ShoulderButtonIndicator active={buttons.r1} label="R1" />
            <ShoulderButtonIndicator active={buttons.r2 > 0} label="R2" isLarge={true} />
          </div>
        </div>

        {/* Analog sticks */}
        <div className="flex justify-between">
          <StickIndicator x={leftStick.x} y={leftStick.y} label="Left Stick" />
          <StickIndicator x={rightStick.x} y={rightStick.y} label="Right Stick" />
        </div>
        
        {/* Face buttons */}
        <div className="relative">
          <div className="text-xs text-blue-300 mb-3 text-center">Face Buttons</div>
          <div className="grid grid-cols-3 gap-2 w-24 mx-auto">
            <div></div>
            <ButtonIndicator active={buttons.triangle} label="△" />
            <div></div>
            <ButtonIndicator active={buttons.square} label="□" />
            <div></div>
            <ButtonIndicator active={buttons.circle} label="○" />
            <div></div>
            <ButtonIndicator active={buttons.cross} label="✕" />
            <div></div>
          </div>
        </div>

        {/* Input values display */}
        <div className="bg-slate-800/30 rounded p-3">
          <div className="text-xs text-blue-300 mb-2">Raw Values</div>
          <div className="grid grid-cols-2 gap-2 text-xs font-mono text-white">
            <div>LS: ({leftStick.x !== null && leftStick.x !== undefined ? leftStick.x.toFixed(2) : "--"}, {leftStick.y !== null && leftStick.y !== undefined ? leftStick.y.toFixed(2) : "--"})</div>
            <div>RS: ({rightStick.x !== null && rightStick.x !== undefined ? rightStick.x.toFixed(2) : "--"}, {rightStick.y !== null && rightStick.y !== undefined ? rightStick.y.toFixed(2) : "--"})</div>
            <div>L2: {buttons.l2 !== null && buttons.l2 !== undefined ? buttons.l2.toFixed(2) : "--"}</div>
            <div>R2: {buttons.r2 !== null && buttons.r2 !== undefined ? buttons.r2.toFixed(2) : "--"}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
