// hooks/usePremiumInterceptor.ts
import { useEffect } from "react";
import { useLocation } from "wouter";

const PREMIUM_PATHS = [
  '/live-alerts-us',
  '/live-alerts-india',
  '/alerts-us',
  '/alerts-india'
];

export function usePremiumInterceptor() {
  const [, setLocation] = useLocation();

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      
      const link = target.closest('a') || target.closest('button');
      if (!link) return;
      
      let destination = '';
      
      if (link.tagName === 'A') {
        destination = (link as HTMLAnchorElement).getAttribute('href') || '';
      } else if (link.tagName === 'BUTTON') {
        const dataHref = link.getAttribute('data-href');
        if (dataHref) destination = dataHref;
        
        const text = link.textContent?.toLowerCase() || '';
        if (text.includes('live alerts') || text.includes('premium')) {
          const market = text.includes('us') ? 'us' : 'india';
          destination = `/live-alerts-${market}`;
        }
      }
      
      const isPremiumPath = PREMIUM_PATHS.some(path => 
        destination.includes(path)
      );
      
      if (isPremiumPath) {
        // Only block if not logged in
        const isLoggedIn = !!localStorage.getItem("authToken");
        
        if (!isLoggedIn) {
          e.preventDefault();
          e.stopPropagation();
          sessionStorage.setItem('redirectAfterLogin', destination);
          sessionStorage.setItem('premiumFeatureAttempted', 'true');
          setLocation("/login");
        } else {
          
          // Now, if they are logged in, we let them proceed to the destination
          setLocation(destination);
        }
      }
    };

    document.addEventListener('click', handleClick, true);
    
    return () => {
      document.removeEventListener('click', handleClick, true);
    };
  }, [setLocation]);
}