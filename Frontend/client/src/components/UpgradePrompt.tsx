import { useState } from "react";
import { useLocation } from "wouter";
import { Lock, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface UpgradePromptProps {
  featureName: string;
  alertType?: "india" | "us"; // 👈 NEW
}

export default function UpgradePrompt({
  featureName,
  alertType = "india",
}: UpgradePromptProps) {
  const [, setLocation] = useLocation();
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  const handleUpgradeClick = () => {
    // Remember which alert user wanted
    sessionStorage.setItem("intendedAlert", alertType);

    // Navigate to REAL protected route
    setLocation(
      alertType === "us"
        ? "/live-alerts-us"
        : "/live-alerts-india"
    );
  };

  return (
    <div className="fixed bottom-4 right-4 z-40 max-w-sm">
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-xl p-4 shadow-2xl">

        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center">
              <Lock className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h4 className="font-semibold text-white">
                Upgrade for {featureName}
              </h4>
              <p className="text-xs text-slate-400">
                Unlock premium features
              </p>
            </div>
          </div>

          <button
            onClick={() => setIsVisible(false)}
            className="p-1 hover:bg-slate-700 rounded"
          >
            <X className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button
            onClick={handleUpgradeClick}
            size="sm"
            className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600"
          >
            Continue to Alerts
          </Button>

          <Button
            onClick={() => setIsVisible(false)}
            size="sm"
            variant="outline"
            className="flex-1 border-slate-600 text-slate-400"
          >
            Later
          </Button>
        </div>
      </div>
    </div>
  );
}
