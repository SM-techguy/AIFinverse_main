import { Button } from "@/components/ui/button";
import { useLocation } from "wouter";
import { useState } from "react";
import { api } from "@/services/api";
import { CheckCircle, Eye, EyeOff } from "lucide-react";

export default function Login() {
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false);
  const [userName, setUserName] = useState("");

  const validateForm = () => {
    setError(""); // Clear previous errors
    
    if (!email.trim() || !password.trim()) {
      setError("Please fill in all fields");
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email address");
      return false;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return false;
    }

    return true;
  };

  // Updated handleLogin function to match backend response
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setShowWelcome(false);
    setError("");

    try {
      console.log("🔄 Starting login process...");
      
      const response = await api.post("/login", {
        email: email.trim().toLowerCase(), // ✅ Backend expects lowercase
        password,
      });

      const data = response.data;
      console.log("✅ Login API response:", data);

      if (response.status === 200 && data.message === "Login successful") {
        // ✅ Get user data from backend response
        const userId = data.user_id;
        const userEmail = data.email;
        const profile = data.profile || {};
        const preferences = data.preferences || {};
        
        if (!userId) {
          throw new Error("No user_id received from server");
        }
        
        // ✅ All registered users get premium access
        const userPlan = "premium";
        
        // ✅ Extract username from profile data
        let extractedUserName = email.split('@')[0];
        if (profile.first_name) {
          extractedUserName = profile.first_name;
          if (profile.last_name) {
            extractedUserName += ` ${profile.last_name}`;
          }
        } else if (data.first_name) {
          extractedUserName = data.first_name;
          if (data.last_name) {
            extractedUserName += ` ${data.last_name}`;
          }
        }

        // ✅ STORE ALL USER DATA IN LOCALSTORAGE
        localStorage.setItem("authToken", data.token || `token_${userId}_${Date.now()}`);
        localStorage.setItem("userId", userId);
        localStorage.setItem("userEmail", userEmail);
        localStorage.setItem("userPlan", userPlan);
        localStorage.setItem("userName", extractedUserName);
        localStorage.setItem("userCountry", profile.country || "");
        
        // ✅ Store market preferences
        localStorage.setItem("marketPreferences", JSON.stringify(preferences));
        
        // ✅ Store active markets and strategies
        const activeMarkets = [];
        const activeStrategies = [];
        
        // Check India market
        if (preferences.India?.is_active) {
          activeMarkets.push("India");
          activeStrategies.push(...(preferences.India.strategies || []));
        }
        
        // Check US market
        if (preferences.US?.is_active) {
          activeMarkets.push("US");
          activeStrategies.push(...(preferences.US.strategies || []));
        }
        
        localStorage.setItem("activeMarkets", JSON.stringify(activeMarkets));
        localStorage.setItem("activeStrategies", JSON.stringify(activeStrategies));
        
        // ✅ Store COMPLETE userProfile
        const userProfile = {
          userId: userId,
          user_id: userId,
          id: userId,
          email: userEmail,
          firstName: profile.first_name || extractedUserName,
          lastName: profile.last_name || "",
          country: profile.country || "",
          plan: userPlan,
          marketPreferences: preferences,
          telegram: data.telegram || {},
          selectedMarket: activeMarkets[0] || "India",
          selectedStrategies: activeStrategies,
          token: data.token || userId
        };
        localStorage.setItem("userProfile", JSON.stringify(userProfile));
        
        // ✅ Set fresh login flag
        localStorage.removeItem("freshRegistration");
        localStorage.setItem("isLoggedIn", "true");
        localStorage.setItem("lastLogin", new Date().toISOString());
        
        // ✅ Store user data in sessionStorage
        const userData = {
          userId: userId,
          email: userEmail,
          name: extractedUserName,
          firstName: profile.first_name,
          lastName: profile.last_name,
          country: profile.country,
          plan: userPlan,
          loginTime: new Date().toISOString(),
          marketPreferences: preferences
        };
        sessionStorage.setItem("userData", JSON.stringify(userData));

        setUserName(extractedUserName);
        
        // Show welcome message
        setShowWelcome(true);
        setIsLoading(false);
        
        console.log("✅ Login successful - Data stored:", {
          userId: userId,
          email: userEmail,
          name: extractedUserName,
          country: profile.country,
          preferences: preferences
        });
        
        // Redirect after delay
        setTimeout(() => {
          console.log("🚀 Redirecting to /home...");
          setLocation("/home");
        }, 2000);
        
      } else {
        const errorMsg = data.message || "Login failed. Please check your credentials.";
        setError(errorMsg);
        setIsLoading(false);
      }
    } catch (err: any) {
      console.error("❌ Login error:", err);

      let errorMessage = "An unexpected error occurred";
      
      if (err.response) {
        // Handle specific HTTP status codes
        switch (err.response.status) {
          case 400:
            errorMessage = "Invalid request. Please check your input.";
            break;
          case 401:
            errorMessage = "Invalid email or password.";
            break;
          case 403:
            errorMessage = "Account disabled or access denied.";
            break;
          case 404:
            errorMessage = "User not found.";
            break;
          case 422:
            errorMessage = "Validation error. Please check your input.";
            break;
          case 429:
            errorMessage = "Too many attempts. Please try again later.";
            break;
          case 500:
            errorMessage = "Server error. Please try again later.";
            break;
          default:
            errorMessage = err.response.data?.message || `Error: ${err.response.status}`;
        }
      } else if (err.request) {
        errorMessage = "Network error. Please check your connection.";
      } else {
        errorMessage = err.message || "An error occurred during login.";
      }
      
      setError(errorMessage);
      setIsLoading(false);
    }
  };

  // Helper function to get user preferences from localStorage
  const getUserPreferences = () => {
    try {
      const stored = localStorage.getItem("marketPreferences");
      return stored ? JSON.parse(stored) : { India: { is_active: false, strategies: [] }, US: { is_active: false, strategies: [] } };
    } catch {
      return { India: { is_active: false, strategies: [] }, US: { is_active: false, strategies: [] } };
    }
  };

  return (
    <div className="min-h-screen flex flex-col">

      {/* TOP NAVBAR: Integrated Icon and Beta Badge */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-transparent">
        <div className="max-w-7xl mx-auto pl-2 pr-4 sm:pl-4 sm:pr-6 lg:pl-6 lg:pr-8">
          <div className="flex items-center h-16">
            {/* Big Icon */}
            <img 
              src="/images/icon.png" 
              alt="AI Finverse Icon" 
              className="h-40 w-40 object-contain cursor-pointer"
              onClick={() => setLocation("/")}
            />
            
            {/* Beta Badge */}
            <div className="relative">
              <span className="px-2 py-1 text-xs font-bold bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-md shadow-lg">
                BETA
              </span>
              <div className="absolute inset-0 bg-cyan-500/20 blur-sm rounded-md -z-10"></div>
            </div>
          </div>
        </div>
      </nav>

      {/* Background */}
      <div
        className="flex-1 flex items-center justify-center relative bg-cover bg-center"
        style={{ backgroundImage: "url('/images/login.png')" }}
      >
        <div className="absolute inset-0 bg-slate-900/70 z-0" />

        {/* Welcome Animation */}
        {showWelcome && (
          <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/90 backdrop-blur-sm">
            <div className="w-full max-w-md bg-transparent border border-cyan-500/40 rounded-2xl p-8 shadow-2xl">
              <div className="text-center">
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center animate-bounce">
                  <CheckCircle className="w-10 h-10 text-white" />
                </div>
                
                <h1 className="text-3xl font-bold text-white mb-3">
                  Welcome Back!
                </h1>
                
                <div className="mb-6">
                  <p className="text-xl text-cyan-300 font-medium">
                    Good to see you again,
                  </p>
                  <p className="text-2xl font-bold text-white mt-2">
                    {userName}!
                  </p>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-center gap-2 text-slate-300">
                    <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                    <span className="ml-2">Redirecting to home...</span>
                  </div>
                  
                  <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 w-full rounded-full animate-progress"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Login Card */}
        <div className="w-full max-w-md z-30">
          <div className="bg-transparent border border-slate-500/40 rounded-xl p-6 sm:p-8 shadow-2xl">
            <div className="text-center mb-8">
              <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2">
                Welcome Back
              </h1>
              <p className="text-gray-300 text-sm">
                Sign in to your account
              </p>
            </div>

            <form onSubmit={handleLogin} className="space-y-5">
              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleLogin(e)}
                  placeholder="you@example.com"
                  className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30 transition-all"
                  autoComplete="email"
                  disabled={isLoading}
                />
              </div>

              {/* Password with show/hide */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleLogin(e)}
                    placeholder="••••••••"
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/30 pr-12 transition-all"
                    autoComplete="current-password"
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-300"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={isLoading}
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 text-sm animate-fade-in">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-cyan-500 hover:bg-cyan-600 text-black font-semibold py-3 rounded-lg disabled:opacity-50 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Signing in...
                  </span>
                ) : (
                  "Sign In"
                )}
              </Button>
            </form>

            {/* Forgot Password */}
            <div className="mt-4 text-center">
              <button
                type="button"
                onClick={() => setLocation("/forgot-password")}
                className="text-sm text-cyan-400 hover:text-cyan-300 hover:underline transition-colors"
                disabled={isLoading}
              >
                Forgot your password?
              </button>
            </div>

            {/* Register */}
            <div className="mt-6 text-center text-sm text-gray-400">
              <p>
                Don&apos;t have an account?{" "}
                <span
                  onClick={() => !isLoading && setLocation("/register")}
                  className={`${isLoading ? 'text-gray-500 cursor-not-allowed' : 'text-cyan-400 hover:text-cyan-300 cursor-pointer'} font-medium`}
                >
                  Sign up
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-3 text-center">
          <p className="text-sm text-slate-400">
            © 2025 All rights reserved to AIFinverse.{" | "}
            <a
              href="/privacy-policy"
              className="text-cyan-400 hover:text-cyan-300 hover:underline ml-1"
            >
              Privacy Policy
            </a>
          </p>
        </div>
      </footer>

      {/* Animation styles */}
      <style>{`
        @keyframes progress {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(0%); }
        }
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-progress {
          animation: progress 2s ease-in-out;
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}