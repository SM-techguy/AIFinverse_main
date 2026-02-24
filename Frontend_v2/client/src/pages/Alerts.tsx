import React, { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";

type Preferences = {
  market: "India" | "US" | "Both";
  alerts: string[];
  plan: string;
};

export default function Alerts() {
  const [preferences, setPreferences] = useState<Preferences | null>(null);
  const [selectedAlerts, setSelectedAlerts] = useState<string[]>([]);

  useEffect(() => {
    const prefs = localStorage.getItem("userPreferences");
    if (prefs) {
      const parsed: Preferences = JSON.parse(prefs);
      setPreferences(parsed);
      setSelectedAlerts(parsed.alerts || []);
    }
  }, []);

  const alertOptions = ["Price Alerts", "Signal Alerts", "News Alerts"];

  const handleSave = () => {
    if (!preferences) return;
    const updatedPrefs = { ...preferences, alerts: selectedAlerts };
    localStorage.setItem("userPreferences", JSON.stringify(updatedPrefs));
    alert("Preferences saved! (Telegram integration coming soon)");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Navbar />

      <main className="pt-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-10">
          <h1 className="text-4xl font-bold text-white mb-2">Alerts</h1>
          <p className="text-gray-400">
            Real-time notifications for market movements and trades
          </p>
        </header>

        {/* Active Alerts */}
        <section className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-white mb-6">
            Active Alerts
          </h2>

          <div className="space-y-4">
            {preferences?.alerts?.length ? (
              preferences.alerts.map((alert, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg border border-slate-600/50 hover:border-cyan-500/50 transition"
                >
                  <div>
                    <p className="text-white font-medium">{alert}</p>
                    <p className="text-sm text-gray-400">
                      Market: {preferences.market}
                    </p>
                  </div>
                  <span className="text-sm text-gray-400">
                    {i * 5 + 2} min ago
                  </span>
                </div>
              ))
            ) : (
              <p className="text-gray-400">No active alerts</p>
            )}
          </div>
        </section>

        {/* Alert Preferences */}
        <section className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-white mb-6">
            Alert Preferences
          </h2>

          <div className="space-y-4">
            {alertOptions.map((option) => (
              <label
                key={option}
                className="flex items-center p-4 bg-slate-700/30 rounded-lg border border-slate-600/50 cursor-pointer hover:border-cyan-500/50"
              >
                <input
                  type="checkbox"
                  className="accent-cyan-500"
                  checked={selectedAlerts.includes(option)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedAlerts([...selectedAlerts, option]);
                    } else {
                      setSelectedAlerts(
                        selectedAlerts.filter((a) => a !== option)
                      );
                    }
                  }}
                />
                <span className="ml-3 text-white">{option}</span>
              </label>
            ))}
          </div>

          <Button
            className="mt-6 bg-cyan-500 hover:bg-cyan-600 text-black font-semibold"
            onClick={handleSave}
          >
            Save Preferences
          </Button>
        </section>
      </main>
    </div>
  );
}
