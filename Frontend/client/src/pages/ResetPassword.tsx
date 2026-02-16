import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { api } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Eye, EyeOff } from "lucide-react";


export default function ResetPassword() {
  const [, setLocation] = useLocation();
  const [token, setToken] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Extract token from URL: https://aifinverse.com/reset-password?token=UUID
    const params = new URLSearchParams(window.location.search);
    const tokenFromUrl = params.get("token");

    if (tokenFromUrl) {
      setToken(tokenFromUrl);
    } else {
      setMessage("❌ No reset token found. Please use the link sent to your email.");
    }
  }, []);

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setMessage("❌ Passwords do not match");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      // Body matches your Swagger: { token, new_password, confirm_password }
      await api.post("/reset-password", {
        token,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });

      setMessage("✅ Password reset successful! Redirecting to login...");
      setTimeout(() => setLocation("/login"), 2500);
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || "❌ Reset failed. The link may be expired.");
    } finally {
      setLoading(false);
    }
  };

  // IF NO TOKEN: Show "Invalid Link" UI
  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 px-4">
        <div className="w-full max-w-md bg-slate-800/60 rounded-2xl border border-slate-700 p-8 text-center">
          <p className="text-red-400 mb-6">{message}</p>
          <Button onClick={() => setLocation("/forgot-password")} className="bg-slate-700">
            Request New Link
          </Button>
        </div>
      </div>
    );
  }

  // IF TOKEN EXISTS: Show the Reset Form
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 px-4">
      <div className="w-full max-w-md bg-slate-800/60 rounded-2xl border border-slate-700 p-8 shadow-xl">
        <h1 className="text-2xl font-bold text-white text-center mb-6">Set New Password</h1>

        {message && (
          <div className={`text-center text-sm mb-4 p-3 rounded-lg ${
            message.includes("✅") ? "text-green-400 bg-green-900/20" : "text-red-400 bg-red-900/20"
          }`}>
            {message}
          </div>
        )}

        <form onSubmit={handleReset} className="space-y-4">
          <div className="relative">
            <input
              type={showPass ? "text" : "password"}
              placeholder="New Password"
              className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700 text-white outline-none focus:border-cyan-500"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
            <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-3 top-3.5 text-slate-500">
              {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          <input
            type={showPass ? "text" : "password"}
            placeholder="Confirm Password"
            className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700 text-white outline-none focus:border-cyan-500"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />

          <Button type="submit" disabled={loading} className="w-full bg-cyan-500 hover:bg-cyan-600">
            {loading ? "Resetting..." : "Update Password"}
          </Button>
        </form>
      </div>
    </div>
  );
}