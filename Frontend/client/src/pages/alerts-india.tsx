import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { useLocation } from "wouter";

const ALERT_TYPES = [
  "Momentum",
  "Breakout / Breakdown",
  "Reversal",
  "Buy the Dip",
  "Chart Patterns",
];

export default function AlertsIndia() {
  const [selected, setSelected] = useState<string[]>([]);
  const [, setLocation] = useLocation();

  useEffect(() => {
    const saved = localStorage.getItem("alertPreferencesIndia");
    if (saved) setSelected(JSON.parse(saved));
  }, []);

  const toggle = (type: string) => {
    setSelected((prev) =>
      prev.includes(type)
        ? prev.filter((t) => t !== type)
        : [...prev, type]
    );
  };

  const save = () => {
    localStorage.setItem(
      "alertPreferencesIndia",
      JSON.stringify(selected)
    );
    setLocation("/live-alerts-india");
  };

  return (
    <div className="pt-24 px-6 max-w-xl mx-auto text-white">
      <h1 className="text-2xl font-bold mb-4">
        🇮🇳 India Alert Preferences
      </h1>

      {ALERT_TYPES.map((type) => (
        <label key={type} className="flex items-center gap-2 mb-3">
          <input
            type="checkbox"
            checked={selected.includes(type)}
            onChange={() => toggle(type)}
          />
          {type}
        </label>
      ))}

      <Button onClick={save} className="w-full mt-6 bg-cyan-600">
        Save
      </Button>
    </div>
  );
}
