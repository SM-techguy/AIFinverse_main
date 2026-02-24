import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";

export default function Landing() {
  const [, setLocation] = useLocation();

  const handleLoginClick = () => {
    setLocation("/home");
  };

  return (
    <div className="w-full min-h-screen flex flex-col bg-slate-900">

      {/* ================= HERO SECTION ================= */}
      <section className="relative h-screen w-full overflow-hidden flex-shrink-0">

        {/* BACKGROUND IMAGE */}
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{ backgroundImage: "url('/images/landing.jpg')" }}
        >
          {/* DARK OVERLAY */}
          <div className="absolute inset-0 bg-gradient-to-br from-slate-900/90 via-slate-800/85 to-slate-900/90" />

          {/* SUBTLE GLOWS */}
          <div className="absolute top-0 left-0 right-0 h-1/3 bg-gradient-to-b from-cyan-500/10 to-transparent" />
          <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-blue-500/10 to-transparent" />
        </div>

        {/* LOGO */}
        <div className="absolute top-6 left-6 z-20">
          <div className="relative">
            <img
              src="/images/icon.png"
              alt="Logo"
              className="w-36 h-36 md:w-60 md:h-60 object-contain drop-shadow-2xl hover:scale-105 transition-all duration-300"
            />
            <div className="absolute inset-0 bg-cyan-500/10 blur-xl -z-10 rounded-full" />
          </div>
        </div>

        {/* CONTENT */}
        <div className="relative z-10 h-full flex items-center justify-center px-6 md:px-16">
          <div className="max-w-xl text-center">

            <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
              AI Market{" "}
              <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                Intelligence
              </span>{" "}
              Platform
            </h1>

            <p className="text-xl md:text-2xl text-gray-300 mb-12">
              Smarter insights.{" "}
              <span className="text-cyan-300 font-medium">
                Confident decisions.
              </span>
            </p>

            {/* CTA BUTTON */}
            <div className="relative inline-block group">
              <div className="absolute -inset-4 bg-gradient-to-r from-cyan-500/30 via-blue-500/30 to-cyan-500/30 blur-xl rounded-3xl opacity-0 group-hover:opacity-70 transition-all duration-500 animate-pulse-slow" />

              <Button
                onClick={handleLoginClick}
                className="relative bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold text-lg px-12 py-7 rounded-2xl shadow-2xl transition-all duration-300 hover:scale-105"
              >
                <span className="flex items-center gap-3">
                  Get Started
                  <span className="group-hover:translate-x-2 transition-transform duration-300">
                    →
                  </span>
                </span>
              </Button>
            </div>

          </div>
        </div>
      </section>

      {/* ================= FOOTER ================= */}
      <footer className="bg-slate-900 border-t border-slate-800 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-3 text-center">
          <p className="text-sm text-slate-400">
            © 2025 All rights reserved to AIFinverse.{" | "}
            <a href="/privacy-policy" className="text-cyan-400 hover:text-cyan-300 hover:underline ml-1">
              Privacy Policy
            </a>
          </p>
        </div>
      </footer>

      {/* ================= ANIMATIONS ================= */}
      <style>{`
        @keyframes pulse-slow {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.7; }
        }
        .animate-pulse-slow {
          animation: pulse-slow 2s ease-in-out infinite;
        }
      `}</style>

    </div>
  );
}
