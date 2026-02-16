import { useState, useEffect } from "react";

/* =======================
   TYPES - SIMPLIFIED
======================= */
export interface UserPreferences {
  email: string;
  firstName: string;
  lastName: string;
  country: string;
  // NEW: Registration market selection
  registeredMarket: "India" | "US" | "Both" | null;
  // Market access - starts with only registered market
  selectedMarkets: string[];
  // Strategies per market
  marketPreferences: Record<string, string[]>;
}

/* =======================
   CONSTANTS
======================= */
export const ALERT_TYPES = [
  "Momentum",
  "Breakout / Breakdown",
  "Reversal",
  "Buy the Dip",
  "Chart Patterns",
];

export const MARKET_CONFIG = {
  india: { name: "India", flag: "🇮🇳", key: "alertPreferencesIndia" },
  us: { name: "US", flag: "🇺🇸", key: "alertPreferencesUS" },
} as const;

/* =======================
   HOOK - UPDATED FOR REGISTRATION LOCKING
======================= */
export const useUserPreferences = () => {
  const [preferences, setPreferences] = useState<UserPreferences>({
    email: "",
    firstName: "",
    lastName: "",
    country: "",
    registeredMarket: null,
    selectedMarkets: [], // EMPTY initially
    marketPreferences: {
      india: [],
      us: [],
    },
  });

  const [isLoading, setIsLoading] = useState(true);

  /* =======================
     LOAD FROM STORAGE
  ======================= */
  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = () => {
    setIsLoading(true);
    try {
      const raw = localStorage.getItem("userProfile");

      if (!raw) {
        // New user - no preferences yet
        const defaultPrefs: UserPreferences = {
          email: "",
          firstName: "",
          lastName: "",
          country: "",
          registeredMarket: null,
          selectedMarkets: [],
          marketPreferences: {
            india: [],
            us: [],
          },
        };
        localStorage.setItem("userProfile", JSON.stringify(defaultPrefs));
        setPreferences(defaultPrefs);
        return;
      }

      const parsed = JSON.parse(raw);

      // FIX: Handle migration from old format
      let selectedMarkets: string[] = [];
      
      // If user has registeredMarket, ONLY that market is selected initially
      if (parsed.registeredMarket) {
        switch(parsed.registeredMarket) {
          case "India":
            selectedMarkets = ["india"];
            break;
          case "US":
            selectedMarkets = ["us"];
            break;
          case "Both":
            selectedMarkets = ["india", "us"];
            break;
          default:
            selectedMarkets = parsed.selectedMarkets || [];
        }
      } else {
        // Fallback to whatever is saved
        selectedMarkets = parsed.selectedMarkets || [];
      }

      setPreferences({
        email: parsed.email || "",
        firstName: parsed.firstName || "",
        lastName: parsed.lastName || "",
        country: parsed.country || "",
        registeredMarket: parsed.registeredMarket || null,
        selectedMarkets,
        marketPreferences: parsed.marketPreferences || {
          india: parsed.strategies || [],
          us: [],
        },
      });
    } catch (err) {
      console.error("Failed to load preferences", err);
    } finally {
      setIsLoading(false);
    }
  };

  /* =======================
     MARKET ACCESS CONTROL
  ======================= */
  const hasMarketAccess = (marketId: string): boolean => {
    return preferences.selectedMarkets.includes(marketId);
  };

  const requireMarketAccess = (
    marketId: string,
    currentPath: string
  ): { 
    hasAccess: boolean;
    redirectTo?: string;
    marketName: string;
  } => {
    const hasAccess = hasMarketAccess(marketId);
    const marketName = MARKET_CONFIG[marketId]?.name || marketId;

    if (!hasAccess) {
      // Store where user was trying to go
      localStorage.setItem("lockedMarketRedirect", JSON.stringify({
        market: marketId,
        originalPath: currentPath,
        timestamp: Date.now()
      }));

      return {
        hasAccess: false,
        redirectTo: `/profile?tab=manage-markets&unlock=${marketId}`,
        marketName
      };
    }

    return { hasAccess: true, marketName };
  };

  /* =======================
     SAVE PREFERENCES (USED BY PROFILE)
  ======================= */
  const savePreferences = (updates: Partial<UserPreferences>) => {
    try {
      const current = localStorage.getItem("userProfile");
      const currentData = current ? JSON.parse(current) : {};
      
      const updated: UserPreferences = {
        ...currentData,
        ...updates,
        // Ensure marketPreferences exists
        marketPreferences: {
          ...(currentData.marketPreferences || { india: [], us: [] }),
          ...(updates.marketPreferences || {}),
        },
      };

      localStorage.setItem("userProfile", JSON.stringify(updated));
      setPreferences(updated);
      
      // Trigger storage event for other tabs
      window.dispatchEvent(new Event('storage'));
      
      return { success: true, data: updated };
    } catch (err) {
      console.error("Save failed", err);
      return { success: false, error: err };
    }
  };

  /* =======================
     UNLOCK MARKET (FROM PROFILE)
  ======================= */
  const unlockMarket = (marketId: string, strategies: string[] = []) => {
    if (hasMarketAccess(marketId)) {
      return { success: true, alreadyUnlocked: true };
    }

    const newSelectedMarkets = [...preferences.selectedMarkets, marketId];
    const newMarketPrefs = {
      ...preferences.marketPreferences,
      [marketId]: strategies
    };

    const result = savePreferences({
      selectedMarkets: newSelectedMarkets,
      marketPreferences: newMarketPrefs
    });

    return result;
  };

  /* =======================
     GET PENDING REDIRECT
  ======================= */
  const getPendingRedirect = () => {
    const data = localStorage.getItem("lockedMarketRedirect");
    return data ? JSON.parse(data) : null;
  };

  /* =======================
     CLEAR REDIRECT
  ======================= */
  const clearRedirect = () => {
    localStorage.removeItem("lockedMarketRedirect");
  };

  /* =======================
     AUTH & RESET
  ======================= */
  const isAuthenticated = (): boolean => {
    return !!preferences.email;
  };

  const clearPreferences = () => {
    localStorage.removeItem("userProfile");
    localStorage.removeItem("lockedMarketRedirect");
    setPreferences({
      email: "",
      firstName: "",
      lastName: "",
      country: "",
      registeredMarket: null,
      selectedMarkets: [],
      marketPreferences: {
        india: [],
        us: [],
      },
    });
  };

  /* =======================
     EXPORT
  ======================= */
  return {
    // State
    preferences,
    isLoading,
    
    // Constants
    alertTypes: ALERT_TYPES,
    MARKET_CONFIG,
    
    // Market Access
    hasMarketAccess,
    requireMarketAccess,
    unlockMarket,
    
    // Data
    getMarketStrategies: (marketId: string) => 
      preferences.marketPreferences[marketId] || [],
    
    updateMarketStrategies: (marketId: string, strategies: string[]) => {
      const updated = {
        ...preferences.marketPreferences,
        [marketId]: strategies
      };
      return savePreferences({ marketPreferences: updated });
    },
    
    // Core Operations
    savePreferences,
    clearPreferences,
    loadPreferences,
    isAuthenticated,
    
    // Redirect Helpers
    getPendingRedirect,
    clearRedirect,
  };
};