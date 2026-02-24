// hooks/useFeatureInterceptor.ts
import { useEffect } from "react";
import { useLocation } from "wouter";

const PREMIUM_FEATURES = [
  "/live-alerts-india",
  "/live-alerts-us",
  "/alerts-india",
  "/alerts-us"
];

export function useFeatureInterceptor() {
  const [, setLocation] = useLocation();

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const link = target.closest('a');
      
      if (link) {
        const href = link.getAttribute('href');
        
        // Check if it's a premium feature link
        if (href && PREMIUM_FEATURES.some(path => href.startsWith(path))) {
          e.preventDefault();
          
          const isLoggedIn = !!localStorage.getItem("authToken");
          // Even if they don't have premium, we will let them through now
          const hasPremium = localStorage.getItem("userPlan") === "premium";
          
          if (!isLoggedIn) {
            sessionStorage.setItem('redirectAfterLogin', href);
            sessionStorage.setItem('premiumFeatureAttempted', 'true');
            setLocation("/login");
          } else {
            
            // ALLOWED: Go directly to the link regardless of premium status
            setLocation(href);
          }
        }
      }
    };

    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [setLocation]);
}