// components/PremiumRouteGuard.tsx
import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { Lock, X, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface PremiumRouteGuardProps {
  children: React.ReactNode;
  featureName: string;
  featureDescription: string;
}

export default function PremiumRouteGuard({
  children,
  featureName,
  featureDescription,
}: PremiumRouteGuardProps) {
  const [, setLocation] = useLocation();
  const [isLocked, setIsLocked] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAccess = () => {
      const authToken = localStorage.getItem("authToken");
      
      // ⭐⭐ CHANGE: Check ONLY if user is logged in (not premium plan) ⭐⭐
      if (authToken) {
        setIsLocked(false); // All logged-in users can access
      } else {
        setIsLocked(true);
        // Show modal immediately if not logged in
        setShowModal(true);
      }
      
      setIsLoading(false);
    };

    checkAccess();
  }, []);

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto mb-4"></div>
          <p className="text-white">Loading...</p>
        </div>
      </div>
    );
  }

  // If locked, show login required screen
  if (isLocked) {
    return (
      <>
        {/* Lock Screen */}
        <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-950">
          <div className="flex flex-col items-center justify-center min-h-screen p-6">
            <div className="max-w-md w-full">
              {/* Logo */}
              <div className="text-center mb-8">
                <img
                  src="/images/icon.png"
                  alt="Logo"
                  className="w-20 h-20 object-contain mx-auto mb-4"
                />
                <h1 className="text-xl font-bold text-white">AI Market Intelligence</h1>
              </div>

              {/* Feature Card */}
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 p-8 shadow-2xl">
                {/* Lock Icon */}
                <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center">
                  <Lock className="w-8 h-8 text-cyan-400" />
                </div>
                
                {/* Feature Info */}
                <h2 className="text-2xl font-bold text-white mb-3 text-center">
                  {featureName}
                </h2>
                
                <p className="text-gray-400 mb-6 text-center text-sm">
                  {featureDescription}
                </p>
                
                {/* Status Badge */}
                <div className="mb-8 p-3 bg-slate-900/50 rounded-xl border border-cyan-500/30">
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse"></div>
                    <span className="text-cyan-400 font-medium text-sm">Login Required</span>
                  </div>
                  <p className="text-gray-500 text-xs text-center mt-1">
                    Sign in to access this feature
                  </p>
                </div>
                
                {/* Action Buttons */}
                <div className="space-y-3">
                  <Button
                    onClick={() => {
                      sessionStorage.setItem('redirectAfterLogin', window.location.pathname);
                      setLocation("/login");
                    }}
                    className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600"
                  >
                    Sign In to Access
                  </Button>
                  
                  <Button
                    onClick={() => setLocation("/register")}
                    variant="outline"
                    className="w-full border-cyan-500 text-cyan-400 hover:bg-cyan-500/10"
                  >
                    Create Free Account
                  </Button>
                  
                  <Button
                    onClick={() => window.history.back()}
                    variant="ghost"
                    className="w-full text-slate-300 hover:text-white"
                  >
                    ← Go Back
                  </Button>
                </div>
                
                {/* Already have account? */}
                <div className="mt-6 pt-6 border-t border-slate-700">
                  <p className="text-sm text-gray-500 text-center">
                    Already have an account?{" "}
                    <button
                      onClick={() => {
                        sessionStorage.setItem('redirectAfterLogin', window.location.pathname);
                        setLocation("/login");
                      }}
                      className="text-cyan-400 hover:text-cyan-300 underline"
                    >
                      Sign in here
                    </button>
                  </p>
                </div>
              </div>
              
              {/* Free Features Reminder */}
              <div className="mt-6 text-center">
                <p className="text-sm text-gray-500">
                  You can still access{" "}
                  <button
                    onClick={() => setLocation("/explore")}
                    className="text-cyan-400 hover:text-cyan-300 underline"
                  >
                    free features
                  </button>
                  {" "}without logging in
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Modal */}
        <PremiumLockModal
          isOpen={showModal}
          onClose={() => setShowModal(false)}
          featureName={featureName}
          featureDescription={featureDescription}
        />
      </>
    );
  }

  // User has access, render the original page
  return <>{children}</>;
}

// Keep your existing PremiumLockModal component as is
function PremiumLockModal({
  isOpen,
  onClose,
  featureName,
  featureDescription,
}: {
  isOpen: boolean;
  onClose: () => void;
  featureName: string;
  featureDescription: string;
}) {
  const [, setLocation] = useLocation();

  if (!isOpen) return null;

  const handleAction = (path: string) => {
    sessionStorage.setItem('redirectAfterLogin', window.location.pathname);
    onClose();
    setLocation(path);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-lg bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl border border-slate-700 shadow-2xl">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 p-2 hover:bg-slate-800 rounded-full transition-colors"
        >
          <X className="w-5 h-5 text-slate-400" />
        </button>

        {/* Header */}
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center">
              <Lock className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Access {featureName}</h2>
              <p className="text-sm text-slate-400">Login or register to continue</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Benefits */}
          <div className="mb-6">
            <h3 className="font-semibold text-white mb-3">Feature Benefits:</h3>
            <div className="space-y-2">
              {[
                "Real-time market alerts",
                "Advanced analytics",
                "Instant notifications",
                "Custom configurations"
              ].map((benefit, index) => (
                <div key={index} className="flex items-center gap-3">
                  <CheckCircle className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                  <span className="text-sm text-slate-300">{benefit}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <Button
              onClick={() => handleAction("/login")}
              className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600"
            >
              Log In to Continue
            </Button>
            
            <Button
              onClick={() => handleAction("/register")}
              variant="outline"
              className="w-full border-cyan-500 text-cyan-400 hover:bg-cyan-500/10"
            >
              Create Free Account
            </Button>
            
            <div className="text-center">
              <button
                onClick={onClose}
                className="text-sm text-slate-400 hover:text-white"
              >
                Explore free features instead
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-900/50 border-t border-slate-700 rounded-b-2xl">
          <p className="text-xs text-slate-500 text-center">
            All features are free for registered users
          </p>
        </div>
      </div>
    </div>
  );
}