import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { X, ExternalLink, CheckCircle, Bot, Mail, AlertCircle, Info } from "lucide-react";

interface TelegramSubscriptionModalProps {
  isOpen: boolean;
  onClose: () => void;
  market: "us" | "india";
}

export default function TelegramSubscriptionModal({ 
  isOpen, 
  onClose, 
  market = "us" 
}: TelegramSubscriptionModalProps) {
  const [email, setEmail] = useState("");
  const [step, setStep] = useState<"email" | "generate" | "success">("email");
  const [error, setError] = useState("");

  // Based on backend code analysis
  const botConfig = {
    us: {
      botUsername: "AIFinverseUSBot",
      botLink: "https://t.me/AIFinverseUSBot",
      title: "US Market Alerts",
      color: "from-blue-500 to-cyan-600",
      icon: "🇺🇸",
      borderColor: "border-blue-500/30",
    },
    india: {
      botUsername: "AIFinverseIndiaBot",
      botLink: "https://t.me/AIFinverseIndiaBot",
      title: "India Market Alerts",
      color: "from-orange-500 to-yellow-600",
      icon: "🇮🇳",
      borderColor: "border-orange-500/30",
    },
  };

  const config = botConfig[market] || botConfig.us;

  // Handle email verification
  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email address");
      return;
    }

    // Check if email matches registered email
    const savedEmail = localStorage.getItem("userEmail") || 
                       localStorage.getItem("registeredEmail") ||
                       localStorage.getItem("userProfileEmail");

    if (savedEmail && savedEmail.toLowerCase() !== email.toLowerCase()) {
      setError("Email doesn't match your registered account");
      return;
    }

    // Move to next step
    setStep("generate");
    
    // Store email for future reference
    if (!savedEmail) {
      localStorage.setItem("userEmail", email);
    }
  };

  // Generate Telegram URL with start parameter
  const generateTelegramUrl = () => {
    const userEmail = email || localStorage.getItem("userEmail") || "";
    
    // Create start parameter format: email_timestamp
    const startParam = userEmail 
      ? `start=${encodeURIComponent(userEmail)}_${Date.now()}`
      : "start";
    
    return `${config.botLink}?${startParam}`;
  };

  // Handle Telegram confirmation
  const handleTelegramConfirmation = () => {
    setStep("success");
    
    // Store subscription info
    const subscriptionData = {
      market: market,
      bot: config.botUsername,
      email: email || localStorage.getItem("userEmail"),
      subscribedAt: new Date().toISOString(),
      chatId: "pending", // Will be updated via webhook
    };
    
    localStorage.setItem(`telegramSubscription_${market}`, JSON.stringify(subscriptionData));
  };

  // Close modal
  const handleClose = () => {
    setEmail("");
    setStep("email");
    setError("");
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className={`bg-slate-900 border ${config.borderColor} rounded-2xl w-full max-w-md shadow-2xl`}>
        {/* Header */}
        <div className="p-6 border-b border-slate-700 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 bg-gradient-to-br ${config.color} rounded-lg flex items-center justify-center`}>
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-white">
                {config.icon} {config.title}
              </h3>
              <p className="text-sm text-slate-400">@{config.botUsername}</p>
            </div>
          </div>
          <button 
            onClick={handleClose} 
            className="p-2 hover:bg-slate-800 rounded-lg transition"
          >
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {/* Step 1: Email Input */}
        {step === "email" && (
          <form onSubmit={handleEmailSubmit} className="p-6">
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Enter your registered email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full p-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            
            {error && (
              <div className="mb-4 p-3 bg-red-900/30 border border-red-700/50 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-400" />
                  <p className="text-red-400 text-sm">{error}</p>
                </div>
              </div>
            )}
            
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <Info className="w-4 h-4 text-blue-400" />
                <h4 className="text-sm font-medium text-slate-300">How it works:</h4>
              </div>
              <ul className="text-xs text-slate-400 space-y-2">
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5"></span>
                  <span>Enter the email you used during registration</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5"></span>
                  <span>Get Telegram bot link with your email encoded</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5"></span>
                  <span>Click "Start" in Telegram to save chat ID to S3</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-1.5"></span>
                  <span>Receive real-time alerts based on your preferences</span>
                </li>
              </ul>
            </div>
            
            <Button 
              type="submit"
              className={`w-full bg-gradient-to-r ${config.color} text-white font-semibold hover:opacity-90`}
            >
              Generate Telegram Link
            </Button>
          </form>
        )}

        {/* Step 2: Telegram Link */}
        {step === "generate" && (
          <div className="p-6">
            <div className="text-center mb-6">
              <div className={`w-16 h-16 mx-auto mb-4 bg-gradient-to-br ${config.color} rounded-2xl flex items-center justify-center`}>
                <Bot className="w-8 h-8 text-white" />
              </div>
              <h4 className="font-bold text-lg text-white mb-2">
                Your Telegram Link is Ready!
              </h4>
              <p className="text-sm text-slate-400">
                Click the link below and press <span className="font-bold text-green-400">Start</span> in Telegram
              </p>
            </div>
            
            <a
              href={generateTelegramUrl()}
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 bg-slate-800/50 border border-slate-700 rounded-xl hover:bg-slate-800 mb-6 transition-all hover:border-blue-500 group"
              onClick={() => {
                // Note: Backend will capture chat_id via webhook when user clicks /start
                setTimeout(() => {
                  // Allow user to confirm after clicking
                }, 1000);
              }}
            >
              <div className="flex items-center justify-center gap-2 text-blue-400">
                <ExternalLink className="w-4 h-4" />
                <span className="font-medium">Open Telegram Bot</span>
              </div>
              <p className="text-xs text-slate-500 text-center mt-2">
                @{config.botUsername}
              </p>
            </a>
            
            <div className="space-y-3">
              <Button
                onClick={handleTelegramConfirmation}
                className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white"
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                I've clicked "Start" in Telegram
              </Button>
              
              <Button
                onClick={() => setStep("email")}
                variant="outline"
                className="w-full border-slate-700 text-slate-400 hover:text-white"
              >
                Back to Email
              </Button>
            </div>
            
            <div className="mt-6 p-4 bg-slate-800/30 rounded-lg border border-slate-700">
              <p className="text-sm font-medium text-slate-300 mb-2">Important:</p>
              <ul className="text-xs text-slate-400 space-y-1">
                <li>• The bot will automatically save your chat ID to S3</li>
                <li>• Alerts are sent based on your market preferences</li>
                <li>• Make sure you've selected alert types in your dashboard</li>
                <li>• You'll receive a welcome message in Telegram</li>
              </ul>
            </div>
          </div>
        )}

        {/* Step 3: Success */}
        {step === "success" && (
          <div className="p-6 text-center">
            <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-full border border-green-500/30 flex items-center justify-center">
              <CheckCircle className="w-10 h-10 text-green-400" />
            </div>
            
            <h4 className="font-bold text-xl text-white mb-2">
              Successfully Connected! 🎉
            </h4>
            
            <p className="text-sm text-slate-300 mb-2">
              Your Telegram is now linked to {config.title}
            </p>
            
            <p className="text-xs text-slate-400 mb-6">
              Chat ID will be saved automatically via webhook
            </p>
            
            <div className="mb-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
              <p className="text-sm font-medium text-slate-300 mb-1">
                Next Steps:
              </p>
              <ul className="text-xs text-slate-400 space-y-1">
                <li>• Check your selected alert types are active</li>
                <li>• You'll receive alerts in Telegram real-time</li>
                <li>• Manage preferences from your dashboard</li>
              </ul>
            </div>
            
            <Button
              onClick={handleClose}
              className={`w-full bg-gradient-to-r ${config.color} text-white font-semibold hover:opacity-90`}
            >
              Done
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}