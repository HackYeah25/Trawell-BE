import { Bot } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

interface ChatMessageSkeletonProps {
  width?: '60%' | '65%' | '75%' | '85%' | '90%';
}

export function ChatMessageSkeleton({ width = '75%' }: ChatMessageSkeletonProps) {
  return (
    <div className="flex gap-3 mb-6 animate-fade-in">
      {/* Avatar skeleton */}
      <div className="flex-shrink-0">
        <div className="w-6 h-6 sm:w-8 sm:h-8 rounded-full bg-gradient-sunset flex items-center justify-center shadow-sm opacity-50">
          <Bot className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
        </div>
      </div>

      {/* Message bubble skeleton */}
      <div className="flex-1 min-w-0" style={{ maxWidth: width }}>
        <div className="rounded-2xl px-4 py-3 bg-card border border-warm-coral/20 shadow-sm space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
          <Skeleton className="h-4 w-3/5" />
        </div>
      </div>
    </div>
  );
}
