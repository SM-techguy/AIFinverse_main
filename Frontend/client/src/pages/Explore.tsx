// pages/Explore.tsx
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { 
  Home, 
  Phone, 
  Info, 
  BarChart3, 
  BookOpen, 
  Shield, 
  Users,
  AlertCircle,
  Zap,
  Globe
} from "lucide-react";

export default function Explore() {
  const [, setLocation] = useLocation();

  const freeFeatures = [
    {
      icon: <Home className="w-8 h-8 text-cyan-400" />,
      title: "Home",
      description: "Access your personalized dashboard and overview",
      path: "/home",
      color: "from-cyan-500/10 to-blue-500/10",
      status: "PUBLIC"
    },
    {
      icon: <Zap className="w-8 h-8 text-teal-400" />,
      title: "Market Insights",
      description: "Subscribe to market updates and insights",
      path: "/newsletter",
      color: "from-teal-500/10 to-cyan-500/10",
      status: "PUBLIC"
    },
    {
      icon: <Globe className="w-8 h-8 text-blue-400" />,
      title: "About Us",
      description: "Learn about our mission and team",
      path: "/about",
      color: "from-blue-500/10 to-indigo-500/10",
      status: "PUBLIC"
    },
    {
      icon: <Phone className="w-8 h-8 text-red-400" />,
      title: "Contact Us",
      description: "Get in touch with our support team",
      path: "/contact",
      color: "from-red-500/10 to-pink-500/10",
      status: "PUBLIC"
    },
  ];

  const premiumFeatures = [
    {
      title: "Live Alerts (US Market)",
      description: "Real-time alerts for NYSE, NASDAQ, and US indices",
      path: "/live-alerts-us",
      icon: "🇺🇸",
      details: [
        "Real-time price alerts",
        "Breaking news notifications",
        "Institutional activity tracking",
        "Pre-market & after-hours alerts"
      ]
    },
    {
      title: "Live Alerts (India Market)", 
      description: "Real-time alerts for NSE, BSE, and Indian indices",
      path: "/live-alerts-india",
      icon: "🇮🇳",
      details: [
        "FII/DII activity tracking",
        "Sector-wise movement alerts",
        "Delivery volume alerts",
        "Breakout & breakdown signals"
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-950 text-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute top-0 left-0 right-0 h-96 bg-gradient-to-b from-cyan-500/5 to-transparent"></div>
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 py-16">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 mb-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500/20 to-blue-500/20 flex items-center justify-center">
                <Globe className="w-6 h-6 text-cyan-400" />
              </div>
              <h1 className="text-4xl md:text-5xl font-bold">
                Explore AIFinverse
              </h1>
            </div>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-6">
              Discover powerful market intelligence tools. Access free features instantly, 
              upgrade anytime for premium alerts.
            </p>

            {/* ⭐⭐⭐ ADDED TWO BUTTONS HERE ⭐⭐⭐ */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Button
                onClick={() => setLocation("/login")}
                className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 px-6 py-3"
              >
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                  Login
                </span>
              </Button>
              
              <Button
                onClick={() => setLocation("/register")}
                variant="outline"
                className="border-cyan-500 text-cyan-400 hover:bg-cyan-500/10 px-6 py-3"
              >
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                  </svg>
                  Start Free Account
                </span>
              </Button>
            </div>
            {/* ⭐⭐⭐ END OF ADDED BUTTONS ⭐⭐⭐ */}

            <div className="flex flex-wrap gap-2 justify-center">
              <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                No Login Required
              </span>
              <span className="px-3 py-1 bg-cyan-500/20 text-cyan-400 rounded-full text-sm">
                Free Access
              </span>
              <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full text-sm">
                Instant Exploration
              </span>
            </div>
          </div>

          {/* Public Features Grid */}
          <div className="mb-20">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-3xl font-bold mb-2">
                  Free Features
                </h2>
                <p className="text-gray-400">
                  Access these features without registration
                </p>
              </div>
              <div className="text-sm text-green-400 font-medium">
                4 Features Available
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {freeFeatures.map((feature, index) => (
                <div
                  key={index}
                  className={`group bg-gradient-to-br ${feature.color} border border-slate-700 rounded-2xl p-6 hover:border-slate-600 transition-all duration-300 hover:-translate-y-1 cursor-pointer relative overflow-hidden`}
                  onClick={() => setLocation(feature.path)}
                >
                  {/* Status Badge */}
                  <div className="absolute top-4 right-4">
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium">
                      {feature.status}
                    </span>
                  </div>
                  
                  {/* Icon */}
                  <div className="mb-4 transform group-hover:scale-110 transition-transform duration-300">
                    {feature.icon}
                  </div>
                  
                  {/* Content */}
                  <h3 className="text-xl font-bold mb-2 group-hover:text-cyan-300 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400 text-sm mb-4">
                    {feature.description}
                  </p>
                  
                  {/* Action */}
                  <div className="flex items-center justify-between">
                    <span className="text-cyan-400 text-sm font-medium group-hover:translate-x-2 transition-transform">
                      Explore →
                    </span>
                    <div className="w-2 h-2 bg-cyan-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Premium Features Section */}
          <div className="mb-20">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">
                Premium Features
              </h2>
              <p className="text-gray-400 max-w-2xl mx-auto">
                Unlock real-time market intelligence with our premium subscription
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              {premiumFeatures.map((feature, index) => (
                <div
                  key={index}
                  className="bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-cyan-500/20 rounded-2xl p-8 relative overflow-hidden group hover:border-cyan-500/40 transition-all duration-300"
                >
                  {/* Premium Badge */}
                  <div className="absolute -top-3 -right-3">
                    <div className="relative">
                      <div className="w-24 h-24 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-full"></div>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-2xl">{feature.icon}</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Lock Icon */}
                  <div className="absolute top-4 left-4 opacity-20 group-hover:opacity-100 transition-opacity">
                    <AlertCircle className="w-6 h-6 text-cyan-400" />
                  </div>
                  
                  {/* Content */}
                  <div className="mb-6">
                    <h3 className="text-2xl font-bold mb-3 text-cyan-300">
                      {feature.title}
                    </h3>
                    <p className="text-gray-300 mb-6">
                      {feature.description}
                    </p>
                    
                    {/* Feature Details */}
                    <div className="space-y-3">
                      {feature.details.map((detail, idx) => (
                        <div key={idx} className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-cyan-500 rounded-full"></div>
                          <span className="text-sm text-gray-400">{detail}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Action Button */}
                  <Button
                    onClick={() => {
                      const isLoggedIn = localStorage.getItem("authToken");
                      if (isLoggedIn) {
                        setLocation("/upgrade");
                      } else {
                        sessionStorage.setItem('redirectAfterLogin', feature.path);
                        sessionStorage.setItem('premiumFeatureAttempted', 'true');
                        setLocation("/login");
                      }
                    }}
                    className="w-full bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/30 hover:text-white group-hover:from-cyan-500 group-hover:to-blue-500 transition-all"
                  >
                    <AlertCircle className="w-4 h-4 mr-2" />
                    Unlock Feature
                  </Button>
                </div>
              ))}
            </div>
            
            {/* Premium Stats */}
            <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-2xl mx-auto">
              <div className="text-center p-6 bg-slate-800/30 rounded-xl">
                <div className="text-3xl font-bold text-cyan-400 mb-2">Real-time</div>
                <div className="text-gray-400">Live Market Data</div>
              </div>
              <div className="text-center p-6 bg-slate-800/30 rounded-xl">
                <div className="text-3xl font-bold text-cyan-400 mb-2">24/7</div>
                <div className="text-gray-400">Alerts & Monitoring</div>
              </div>
              <div className="text-center p-6 bg-slate-800/30 rounded-xl">
                <div className="text-3xl font-bold text-cyan-400 mb-2">2 Markets</div>
                <div className="text-gray-400">US & India Coverage</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}