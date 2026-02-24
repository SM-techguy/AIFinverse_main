import { useLocation } from "wouter";
import { X, Lock, Star, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface PremiumLockModalProps {
  isOpen: boolean;
  onClose: () => void;
  featureName: string;
  featureDescription: string;
  alertType?: "india" | "us"; // 👈 NEW
}

export default function PremiumLockModal({
  isOpen,
  onClose,
  featureName,
  featureDescription,
  alertType = "india",
}: PremiumLockModalProps) {
  const [, setLocation] = useLocation();

  if (!isOpen) return null;

  /* -------------------------------
     Helpers
  --------------------------------*/
  const redirectToAlert = () => {
    sessionStorage.setItem("intendedAlert", alertType);
    onClose();
    setLocation(
      alertType === "us"
        ? "/live-alerts-us"
        : "/live-alerts-india"
    );
  };

  const handleLogin = () => {
    sessionStorage.setItem("premiumFeatureAttempted", "true");
    sessionStorage.setItem("premiumFeatureName", featureName);
    sessionStorage.setItem("intendedAlert", alertType);
    onClose();
    setLocation("/login");
  };

  const handleRegister = () => {
    sessionStorage.setItem("premiumFeatureAttempted", "true");
    sessionStorage.setItem("premiumFeatureName", featureName);
    sessionStorage.setItem("intendedAlert", alertType);
    onClose();
    setLocation("/register");
  };

  const premiumFeatures = [
    "Live Alerts for US & Indian Markets",
    "Real-time Market Intelligence",
    "Advanced Analytics Dashboard",
    "Custom Alert Configurations",
    "Priority Customer Support",
    "Historical Data Analysis",
  ];

  /* -------------------------------
     UI
  --------------------------------*/
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="relative w-full max-w-4xl mx-4">
        <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl border border-slate-700 shadow-2xl overflow-hidden">

          {/* Header */}
          <div className="p-6 border-b border-slate-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-cyan-500/20 flex items-center justify-center">
                  <Lock className="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">
                    Premium Feature Locked
                  </h2>
                  <p className="text-slate-400">
                    Upgrade to access {featureName}
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-slate-800 rounded-full"
              >
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-2">

            {/* Left */}
            <div className="p-8 border-r border-slate-700">
              <h3 className="text-xl font-bold text-white mb-3">
                {featureName}
              </h3>
              <p className="text-slate-300 mb-6">
                {featureDescription}
              </p>

              <h4 className="text-lg font-semibold text-white mb-4">
                What you’ll get:
              </h4>

              <div className="space-y-3 mb-8">
                {premiumFeatures.map((feature, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-cyan-400" />
                    <span className="text-slate-300">{feature}</span>
                  </div>
                ))}
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={handleLogin}
                  className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-500"
                >
                  Log In
                </Button>
                <Button
                  onClick={handleRegister}
                  variant="outline"
                  className="flex-1 border-cyan-500 text-cyan-400"
                >
                  Register
                </Button>
              </div>
            </div>

            {/* Right */}
            <div className="p-8">
              <div className="mb-6">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/20 border border-cyan-500/30 mb-4">
                  <Star className="w-4 h-4 text-cyan-400" />
                  <span className="text-sm text-cyan-300">
                    MOST POPULAR
                  </span>
                </div>

                <h3 className="text-2xl font-bold text-white mb-2">
                  Premium Plan
                </h3>
                <div className="flex items-baseline gap-2 mb-4">
                  <span className="text-4xl font-bold text-white">$29</span>
                  <span className="text-slate-400">/month</span>
                </div>
                <p className="text-slate-400">
                  Full access to all premium features
                </p>
              </div>

              <div className="space-y-4">
                
                <Button
                  onClick={redirectToAlert}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 py-3 text-lg font-semibold"
                >
                  Continue to Alerts
                </Button>

                <Button
                  onClick={onClose}
                  variant="ghost"
                  className="w-full text-slate-400 hover:text-white"
                >
                  Continue with Free Features
                </Button>
              </div>

              <div className="mt-8 pt-6 border-t border-slate-700">
                <p className="text-sm text-slate-500 text-center">
                  Upgrade anytime — no commitment
                </p>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
