import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Power } from "lucide-react";

export default function MasterControls({ enabled, onToggle }) {
  return (
    <Card className="bg-black/20 backdrop-blur-md border-cyan-500/20">
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <div className="text-sm text-blue-300 font-medium">MASTER</div>
          <Button
            onClick={onToggle}
            size="sm"
            variant={enabled ? "default" : "outline"}
            className={`transition-all duration-300 ${
              enabled 
                ? "bg-green-500 hover:bg-green-600 text-white shadow-lg shadow-green-500/25" 
                : "bg-red-500/20 border-red-500/40 text-red-300 hover:bg-red-500/30"
            }`}
          >
            <Power className="w-4 h-4 mr-2" />
            {enabled ? "ENABLED" : "DISABLED"}
          </Button>
          
          {enabled && (
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          )}
        </div>
      </CardContent>
    </Card>
  );
}