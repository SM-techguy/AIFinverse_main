import React, { useState, useEffect } from 'react';
import { Bot, CheckCircle, Clock, AlertCircle, Wifi, WifiOff } from 'lucide-react';

interface TelegramSubscriptionStatusProps {
  market: 'us' | 'india';
}

export default function TelegramSubscriptionStatus({ market }: TelegramSubscriptionStatusProps) {
  const [subscription, setSubscription] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkSubscriptionStatus();
  }, [market]);

  const checkSubscriptionStatus = () => {
    const savedSubscription = localStorage.getItem(`telegramSubscription_${market}`);
    if (savedSubscription) {
      try {
        setSubscription(JSON.parse(savedSubscription));
      } catch (error) {
        console.error('Error parsing subscription data:', error);
      }
    }
    setIsLoading(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <Clock className="w-4 h-4 animate-spin" />
        <span>Checking status...</span>
      </div>
    );
  }

  if (!subscription) {
    return (
      <div className="flex items-center gap-2 text-sm text-amber-400">
        <AlertCircle className="w-4 h-4" />
        <span>Not subscribed</span>
      </div>
    );
  }

  // Check if subscription is recent (within 24 hours)
  const isRecent = subscription.subscribedAt && 
    (Date.now() - new Date(subscription.subscribedAt).getTime()) < 24 * 60 * 60 * 1000;

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2 text-sm">
        {isRecent ? (
          <div className="flex items-center gap-2 text-green-400">
            <Wifi className="w-4 h-4" />
            <span>Connected</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-blue-400">
            <CheckCircle className="w-4 h-4" />
            <span>Subscribed</span>
          </div>
        )}
      </div>
      
      <div className="text-xs text-slate-400">
        <div className="truncate max-w-[200px]" title={subscription.email}>
          {subscription.email}
        </div>
        <div className="flex items-center justify-between mt-1">
          <span>@{subscription.bot}</span>
          <span className="text-slate-500">
            {new Date(subscription.subscribedAt).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
}