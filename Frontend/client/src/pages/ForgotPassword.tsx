import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";
import { api } from "@/services/api";

export default function ForgotPassword() {
  const [, setLocation] = useLocation();

  const [step, setStep] = useState<1 | 2>(1);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [message, setMessage] = useState("");

  // STEP 1: Send OTP
  const handleSendOtp = async () => {
    setLoading(true);
    setMessage("");

    try {
      await api.post("/forgot-password", { email });
      setStep(2);
      setMessage("OTP sent to your email.");
    } catch (err: any) {
      setMessage(
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        "Failed to send OTP"
      );
    } finally {
      setLoading(false);
    }
  };

  // STEP 2: Verify OTP
  const handleVerifyOtp = async () => {
    setLoading(true);
    setMessage("");

    try {
      await api.post("/verify-otp", { email, otp });
      setMessage("OTP verified. Please check your email for the reset link.");

      // Optional redirect
      setTimeout(() => setLocation("/login"), 3000);
    } catch (err: any) {
      setMessage(
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        "Invalid or expired OTP"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setLoading(true);
    setMessage("");

    try {
      await api.post("/forgot-password", { email });
      setMessage("New OTP sent.");
    } catch {
      setMessage("Failed to resend OTP.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 px-4">
      <div className="w-full max-w-md bg-slate-800/60 rounded-2xl border border-slate-700 p-8">
        <h1 className="text-2xl font-bold text-white text-center mb-6">
          Forgot Password
        </h1>

        {message && (
          <p className={`text-center text-sm mb-4 ${
            message.includes("OTP") || message.includes("verified")
              ? "text-green-400"
              : "text-red-400"
          }`}>
            {message}
          </p>
        )}

        {step === 1 && (
          <>
            <input
              type="email"
              placeholder="Enter your email"
              className="w-full mb-4 px-4 py-3 rounded-lg bg-slate-900 border border-slate-700 text-white"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            />

            <Button
              onClick={handleSendOtp}
              disabled={loading || !email}
              className="w-full bg-cyan-500"
            >
              {loading ? "Sending..." : "Send OTP"}
            </Button>
          </>
        )}

        {step === 2 && (
          <>
            <input
              type="text"
              placeholder="Enter OTP"
              maxLength={6}
              className="w-full mb-4 px-4 py-3 text-center text-xl tracking-widest rounded-lg bg-slate-900 border border-slate-700 text-white"
              value={otp}
              onChange={(e) =>
                setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
              }
              disabled={loading}
            />

            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => setStep(1)}
                className="flex-1"
                disabled={loading}
              >
                Back
              </Button>

              <Button
                onClick={handleVerifyOtp}
                disabled={loading || otp.length !== 6}
                className="flex-1 bg-cyan-500"
              >
                Verify OTP
              </Button>
            </div>

            <button
              onClick={handleResendOtp}
              className="mt-4 text-sm text-cyan-400 hover:underline"
              disabled={loading}
            >
              Resend OTP
            </button>
          </>
        )}

        <button
          onClick={() => setLocation("/login")}
          className="mt-6 text-sm text-cyan-400 hover:underline block mx-auto"
        >
          Back to Login
        </button>
      </div>
    </div>
  );
}
