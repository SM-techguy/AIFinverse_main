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
   <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Navbar />

     <main className="flex-1 flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 bg-black">
        <h1 className="text-4xl font-bold text-white mb-2 text-center">
          Coming Soon.....
        </h1>
        <p className="text-gray-400 mt-2 text-center">
          Earn commissions by referring traders to our platform.
        </p>
      </main>

      {/* PRIVACY POLICY FOOTER */}
      <footer className="py-3 bg-slate-800 text-center text-sm text-slate-400">
        <p>
          © 2025 copyrights reserved to AIFinverse.{" "}
          <a
            href="/privacy-policy"
            className="text-cyan-400 hover:underline"
          >
            Privacy Policy
          </a>
        </p>
      </footer>
    </div>
  );
}

