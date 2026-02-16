const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 border-t border-slate-800">
      <div className="max-w-7xl mx-auto px-6 py-3 text-center">

        <p className="text-xs text-slate-400 mb-1 leading-tight">
          © 2025 All rights reserved to AIFinverse.
        </p>

        <div className="flex justify-center gap-5 text-xs leading-tight flex-wrap">
          <a href="/privacy-policy" className="text-cyan-400 hover:text-cyan-300">
            Privacy Policy
          </a>
          <a href="/terms" className="text-cyan-400 hover:text-cyan-300">
            Terms of Service
          </a>
          <a href="/contact" className="text-cyan-400 hover:text-cyan-300">
            Contact Us
          </a>
          <a
            href="https://aifinverse.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-cyan-400 hover:text-cyan-300"
          >
            Visit AIFinverse
          </a>
        </div>

      </div>
    </footer>
  );
};

export default Footer;
