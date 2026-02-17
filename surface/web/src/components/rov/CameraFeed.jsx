import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Camera, Video, VideoOff, Maximize, Settings } from "lucide-react";

export default function CameraFeed() {
  const [isRecording, setIsRecording] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  return (
    <Card className="bg-black/20 backdrop-blur-md border-cyan-500/20 h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Camera className="w-5 h-5 text-cyan-400" />
            Main Camera Feed
            <Badge variant="default" className="bg-green-500/20 text-green-300 border-green-500/30">
              LIVE
            </Badge>
          </CardTitle>
          
          <div className="flex gap-2">
            <Button
              onClick={() => setIsRecording(!isRecording)}
              size="sm"
              variant={isRecording ? "default" : "outline"}
              className={isRecording ? "bg-red-500 hover:bg-red-600" : ""}
            >
              {isRecording ? <VideoOff className="w-4 h-4" /> : <Video className="w-4 h-4" />}
            </Button>
            <Button size="sm" variant="outline">
              <Settings className="w-4 h-4" />
            </Button>
            <Button size="sm" variant="outline">
              <Maximize className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <div className="relative aspect-video bg-gradient-to-br from-slate-800 to-blue-900 rounded-lg mx-4 mb-4 overflow-hidden">
          {/* Placeholder for camera feed */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <Camera className="w-16 h-16 text-cyan-400/50 mx-auto mb-4" />
              <p className="text-blue-300/70">Camera Feed Will Display Here</p>
              <p className="text-xs text-blue-400/50 mt-2">Awaiting video stream...</p>
            </div>
          </div>
          
          {/* Overlay UI */}
          <div className="absolute inset-0">
            {/* Recording indicator */}
            {isRecording && (
              <div className="absolute top-4 left-4 flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                <span className="text-white text-sm font-medium">REC</span>
              </div>
            )}
            
            {/* Crosshairs */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="relative">
                <div className="w-8 h-8 border-2 border-cyan-400/50 rounded-full" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-1 h-1 bg-cyan-400 rounded-full" />
                </div>
              </div>
            </div>
            
            {/* Bottom overlay with info */}
            <div className="absolute bottom-4 left-4 right-4 flex justify-between text-sm">
              <div className="bg-black/50 backdrop-blur-sm rounded px-2 py-1 text-white">
                1920x1080 • 30 FPS
              </div>
              <div className="bg-black/50 backdrop-blur-sm rounded px-2 py-1 text-white">
                00:00:00
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}