// components/ProtectedRoute.tsx
import { useEffect } from "react";
import { useLocation } from "wouter";

interface Props {
  children: React.ReactNode;
  requirePremium?: boolean;
}

export default function ProtectedRoute({
  children,
  requirePremium = false
}: Props) {
  const [, setLocation] = useLocation();

  const isLoggedIn = !!localStorage.getItem("authToken");
  const hasPremium = localStorage.getItem("userPlan") === "premium";

  useEffect(() => {
    if (!isLoggedIn) {
      setLocation("/login");
      return;
    }
  }, [isLoggedIn, hasPremium, requirePremium, setLocation]);

  if (!isLoggedIn) return null;
  if (requirePremium && !hasPremium) return null;

  return <>{children}</>;
}
