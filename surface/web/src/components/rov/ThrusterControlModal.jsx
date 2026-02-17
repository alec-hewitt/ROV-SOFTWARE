import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { Fan, Zap } from "lucide-react";

export default function ThrusterControlModal({ thruster, onClose, onCommandVelocityChange }) {
  const [commandValue, setCommandValue] = useState(thruster.commandVelocity * 10); // Scale to -100 to 100

  useEffect(() => {
    setCommandValue(thruster.commandVelocity * 10);
  }, [thruster]);

  const handleSliderChange = (value) => {
    setCommandValue(value[0]);
  };

  const handleInputChange = (e) => {
    const value = parseFloat(e.target.value);
    if (!isNaN(value)) {
      setCommandValue(Math.max(-100, Math.min(100, value)));
    }
  };
  
  const handleApply = () => {
    onCommandVelocityChange(thruster.id, commandValue / 10);
  };
  
  const handleApplyAndClose = () => {
    handleApply();
    onClose();
  };

  const handleZeroOut = () => {
    setCommandValue(0);
    onCommandVelocityChange(thruster.id, 0);
  }

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md bg-slate-900/80 backdrop-blur-xl border-cyan-500/30 text-white">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Fan className="w-5 h-5 text-cyan-400" />
            Manual Control: {thruster.name}
          </DialogTitle>
        </DialogHeader>
        <div className="py-6 space-y-6">
          <div className="text-center">
            <p className="text-blue-300 text-sm">Command Velocity (%)</p>
            <p className="text-5xl font-mono font-bold text-white">
              {commandValue !== null && commandValue !== undefined ? commandValue.toFixed(0) : "--"}
            </p>
          </div>
          <Slider
            value={[commandValue]}
            onValueChange={handleSliderChange}
            min={-100}
            max={100}
            step={1}
            className="w-full"
          />
          <div className="flex items-center gap-2">
            <Input
              type="number"
              value={commandValue !== null && commandValue !== undefined ? commandValue.toFixed(0) : "0"}
              onChange={handleInputChange}
              min={-100}
              max={100}
              className="bg-slate-800 border-slate-700 text-white font-mono text-center"
            />
            <Button variant="outline" onClick={handleZeroOut} className="bg-yellow-500/20 border-yellow-500/40 text-yellow-300 hover:bg-yellow-500/30">
              <Zap className="w-4 h-4 mr-2" /> Zero
            </Button>
          </div>
        </div>
        <DialogFooter className="gap-2 sm:justify-end">
          <Button type="button" variant="secondary" onClick={onClose}>
            Close
          </Button>
          <Button type="button" onClick={handleApply} className="bg-blue-500 hover:bg-blue-600">
            Apply
          </Button>
          <Button type="button" onClick={handleApplyAndClose} className="bg-green-500 hover:bg-green-600">
            Apply & Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}