import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";

/**
 * Learning Page
 *
 * Design: Dark Fintech Minimalism
 * - Educational resources and tutorials
 * - Trading guides and best practices
 * - Video courses and documentation
 */

export default function Learning() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col">
  <Navbar />

  <main className="flex flex-col justify-center items-center flex-grow px-4 sm:px-6 lg:px-8">
    <h1 className="text-4xl font-bold text-white mb-2 text-center">
      Coming Soon.....
    </h1>

        <p className="text-gray-400 mt-2 text-center">
          Learning resources, tutorials, and trading guides will be available here.
        </p>
      </main>

      {/* ================= FOOTER ================= */}
      <footer className="bg-slate-800 border-t border-slate-800 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-3 text-center">
          <p className="text-sm text-slate-400">
            © 2025 All rights reserved to AIFinverse.{" | "}
            <a href="/privacy-policy" className="text-cyan-400 hover:text-cyan-300 hover:underline ml-1">
              Privacy Policy
            </a>
            {" | "}
            <a href="/contact" className="text-cyan-400 hover:text-cyan-300 hover:underline ml-1">
              Contact Us
            </a>
            {" | "}
            <a
              href="https://aifinverse.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-cyan-400 hover:text-cyan-300 hover:underline ml-1"
            >
              Visit AIFinverse
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
