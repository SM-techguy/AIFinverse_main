import React from "react";
import Navbar from "@/components/Navbar";

const Signals = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Navbar />

      <main className="flex items-center justify-center min-h-screen px-4">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">
            Coming Soon.....
          </h1>
          <p className="text-gray-400 max-w-md mx-auto">
            Trading signals and alert subscriptions will be available here shortly.
          </p>
        </div>
      </main>
    </div>
  );
};

export default Signals;
