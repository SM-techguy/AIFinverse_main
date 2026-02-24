import { useState } from "react";
import Navbar from "@/components/Navbar";
import PageWrapper from "@/components/PageWrapper";
import { ArrowLeft } from "lucide-react";
import { useLocation } from "wouter";

const PrivacyPolicy = () => {
  const [, navigate] = useLocation();

  const handleBack = () => {
    // First try to go back in browser history
    if (window.history.length > 1) {
      window.history.back();
    } else {
      // If no history (direct access or new tab), go to home
      navigate("/");
    }
  };

  return (
    <PageWrapper>
      <div className="min-h-screen bg-gradient-to-br from-slate-950/95 via-blue-950/80 to-slate-950/95 bg-[url('/images/login.png')] bg-cover bg-center bg-fixed bg-blend-darken">
        <Navbar />

        <main className="pt-20 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
          {/* Back Button */}
          <div className="mb-6">
            <button
              onClick={handleBack}
              className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-cyan-400 font-medium transition-all duration-200"
            >
              <ArrowLeft size={18} />
              Back
            </button>
          </div>

          {/* Privacy Policy Content */}
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl backdrop-blur-sm p-6 sm:p-8">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-white mb-3">
                Privacy Policy
              </h1>
            </div>

            <div className="space-y-8 text-slate-300">
              {/* Main Content - Exact as provided */}
              <section className="leading-relaxed">
                <p className="mb-4">
                  AIFinverse is committed to protecting your privacy and handling your information responsibly. We may collect personal information that you voluntarily provide, such as your name, email address, contact details, account information, and any documents, images, videos, or other content you upload while using our AI-powered services.
                </p>
                
                <p className="mb-4">
                  We also automatically collect limited technical and usage data, including IP address, device type, browser information, access logs, and interaction data, to improve performance, security, and user experience. Your information is used solely to operate, maintain, enhance, and support the AIFinverse platform, respond to inquiries or demo requests, deliver AI-based processing and analytics, and comply with legal obligations.
                </p>
                
                <p className="mb-4">
                  We do not sell your personal data and only share information with trusted third-party service providers (such as cloud infrastructure, analytics, or communication tools) under strict confidentiality and data-protection requirements, or when required by law.
                </p>
                
                <p className="mb-4">
                  We implement reasonable administrative, technical, and organizational safeguards to protect your data, retain it only as long as necessary for legitimate business or legal purposes, and provide users the right to request access, correction, or deletion of their personal information.
                </p>
                
                <p className="mb-4">
                  By accessing or using the AIFinverse website, you acknowledge and consent to the data practices described in this Privacy Policy.
                </p>
              </section>
            </div>
          </div>

          {/* Footer */}
          <footer className="mt-12 py-6 text-center">
            <p className="text-sm text-slate-500">
              © 2025 AIFinverse. All rights reserved.
            </p>
          </footer>
        </main>
      </div>
    </PageWrapper>
  );
};

export default PrivacyPolicy;