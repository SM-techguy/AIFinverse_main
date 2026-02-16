import React, { useState } from "react";
import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { 
  MessageCircle, 
  ExternalLink, 
  QrCode, 
  ArrowLeft
} from "lucide-react";
import { useLocation } from "wouter";

type Step = "ask-installed" | "show-link";

export default function TelegramIntegration() {
  const [step, setStep] = useState<Step>("ask-installed");
  const [, setLocation] = useLocation();

  // Always go back to Live Alerts India page
  const handleGoBack = () => {
    if (step === "show-link") {
      setStep("ask-installed");
    } else {
      setLocation("/live-alerts-india"); // <- Updated route
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 flex flex-col font-sans">
      <Navbar />

      <main className="flex-grow flex items-center justify-center p-4 sm:p-6 pt-24">
        <Card className="w-full max-w-md bg-slate-900/50 border-slate-800 backdrop-blur-md shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-300">
          <CardContent className="p-6 sm:p-8">
            
            {/* Header */}
            <div className="flex flex-col items-center text-center mb-8">
              <div className="w-16 h-16 bg-cyan-500/10 rounded-full flex items-center justify-center mb-4">
                <MessageCircle className="w-8 h-8 text-cyan-400" />
              </div>
              <h1 className="text-2xl font-bold text-white">Telegram Integration</h1>
              <p className="text-slate-400 text-sm mt-1">
                Connect with us on Telegram
              </p>
            </div>

            {/* Step 1: Ask if installed */}
            {step === "ask-installed" && (
              <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
                <div className="text-center">
                  <p className="text-slate-300 font-medium">
                    Do you have Telegram installed on your device?
                  </p>
                </div>

                <div className="flex flex-col sm:flex-row gap-3">
                  <Button 
                    onClick={() => setStep("show-link")}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-6 rounded-xl shadow-lg shadow-green-900/20"
                  >
                    Yes, I have Telegram
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => window.open("https://telegram.org/", "_blank")}
                    className="flex-1 border-slate-700 hover:bg-slate-800 text-slate-300 py-6 rounded-xl"
                  >
                    No, I don't
                  </Button>
                </div>
              </div>
            )}

            {/* Step 2: Show link and QR */}
            {step === "show-link" && (
              <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
                <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-center">
                  <p className="text-slate-300 text-sm leading-relaxed">
                    Your Telegram link is ready! Click the button below or scan the QR code.
                  </p>
                </div>

                <Button 
                  onClick={() => window.open("https://t.me/Finversemsbot", "_blank")}
                  className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-6 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-green-900/20"
                >
                  <ExternalLink className="w-5 h-5" />
                  Open in Telegram
                </Button>

                <div className="space-y-4">
                  <div className="flex items-center justify-center gap-2 text-slate-400 text-sm font-medium">
                    <QrCode className="w-4 h-4" />
                    Scan QR Code
                  </div>
                  
                  <div className="bg-white p-4 rounded-2xl w-48 h-48 mx-auto shadow-xl">
                    {/* Placeholder for QR Code */}
                    <img 
                      src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://t.me/my_live_alerts_bot" 
                      alt="Telegram QR Code"
                      className="w-full h-full"
                    />
                  </div>
                  
                  <p className="text-center text-slate-500 text-xs">
                    Scan with your phone's camera to open in Telegram
                  </p>
                </div>
              </div>
            )}

            {/* Footer / Back Button */}
            <div className="mt-8 pt-6 border-t border-slate-800/50">
              <Button 
                variant="ghost" 
                onClick={handleGoBack}
                className="w-full text-slate-400 hover:text-white hover:bg-slate-800/50 flex items-center justify-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Go Back
              </Button>
            </div>

          </CardContent>
        </Card>
      </main>
    </div>
  );
}
