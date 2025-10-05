import { useEffect, useRef, memo } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatMessageSkeleton } from './ChatMessageSkeleton';
import { LocationProposalCard } from '@/components/projects/LocationProposalCard';
import { AttractionProposalCard } from '@/components/trips/AttractionProposalCard';
import { Loader2, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { ChatMessage as ChatMessageType } from '@/types';
import { cn } from '@/lib/utils';

interface ChatThreadProps {
  messages: ChatMessageType[];
  isLoading?: boolean;
  onQuickReply?: (payload: unknown) => void;
  onRetryMessage?: (messageId: string) => void;
  onLocationDecision?: (locationId: string, decision: 'reject' | 1 | 2 | 3) => void;
  onAttractionDecision?: (attractionId: string, decision: 'reject' | 1 | 2 | 3) => void;
  onViewTrip?: (tripId: string) => void;
  className?: string;
  hasMore?: boolean;
  isLoadingMore?: boolean;
  onLoadMore?: () => void;
  remainingCount?: number;
}

export const ChatThread = memo(function ChatThread({
  messages,
  isLoading = false,
  onQuickReply,
  onRetryMessage,
  onLocationDecision,
  onAttractionDecision,
  onViewTrip,
  className,
  hasMore = false,
  isLoadingMore = false,
  onLoadMore,
  remainingCount = 0,
}: ChatThreadProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const previousMessagesLength = useRef(messages.length);
  const hasScrolledToBottom = useRef(false);
  const isUserScrolling = useRef(false);
  const scrollTimeout = useRef<NodeJS.Timeout | null>(null);

  // Initial scroll to bottom on mount
  useEffect(() => {
    if (!hasScrolledToBottom.current && messages.length > 0) {
      // Use a longer delay to ensure the container is properly rendered
      const timeoutId = setTimeout(() => {
        if (scrollContainerRef.current) {
          scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
          hasScrolledToBottom.current = true;
        }
      }, 100);
      
      return () => clearTimeout(timeoutId);
    }
  }, [messages.length]);

  // Handle user scroll detection
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      isUserScrolling.current = true;
      
      // Clear existing timeout
      if (scrollTimeout.current) {
        clearTimeout(scrollTimeout.current);
      }
      
      // Set timeout to detect when user stops scrolling
      scrollTimeout.current = setTimeout(() => {
        isUserScrolling.current = false;
        
        // Check if user is near bottom (within 100px)
        const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100;
        hasScrolledToBottom.current = isNearBottom;
      }, 150);
    };

    container.addEventListener('scroll', handleScroll);
    return () => {
      container.removeEventListener('scroll', handleScroll);
      if (scrollTimeout.current) {
        clearTimeout(scrollTimeout.current);
      }
    };
  }, []);

  // Auto-scroll to bottom for NEW messages
  useEffect(() => {
    // Only scroll if messages increased (new message added, not loaded)
    const isNewMessage = messages.length > previousMessagesLength.current && !isLoadingMore;
    
    if (isNewMessage && !isUserScrolling.current) {
      // Use requestAnimationFrame for smoother scrolling
      requestAnimationFrame(() => {
        if (scrollContainerRef.current) {
          scrollContainerRef.current.scrollTo({
            top: scrollContainerRef.current.scrollHeight,
            behavior: 'smooth'
          });
        }
      });
      
      previousMessagesLength.current = messages.length;
    }
    
    previousMessagesLength.current = messages.length;
  }, [messages, isLoadingMore]);

  return (
    <div 
      className={cn('h-full flex flex-col', className)}
      role="log"
      aria-live="polite"
      aria-label="Chat messages"
    >
      <div ref={scrollContainerRef} className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto">{/* Set to max-w-4xl (896px) for desktop width */}
        {/* Load More Button */}
        {hasMore && !isLoadingMore && (
          <div className="flex justify-center mb-6 animate-fade-in">
            <Button
              variant="ghost"
              size="sm"
              onClick={onLoadMore}
              className="text-muted-foreground hover:text-foreground hover:bg-warm-coral/10"
            >
              <ChevronUp className="w-4 h-4 mr-2" />
              Load more ({remainingCount} older message{remainingCount !== 1 ? 's' : ''})
            </Button>
          </div>
        )}

        {/* Loading Skeletons */}
        {isLoadingMore && (
          <div className="space-y-0">
            <ChatMessageSkeleton width="75%" />
            <ChatMessageSkeleton width="85%" />
            <ChatMessageSkeleton width="65%" />
          </div>
        )}

        {/* Messages */}
        {messages.map((message, index) => {
          // Determine if this is a historical message (loaded via pagination)
          const isHistoricalMessage = hasMore || isLoadingMore || index < messages.length - 10;
          
          return (
            <div key={message.id} className="space-y-3">
              <ChatMessage
                message={message}
                onQuickReply={onQuickReply}
                onRetry={
                  message.status === 'error'
                    ? () => onRetryMessage?.(message.id)
                    : undefined
                }
                onViewTrip={onViewTrip}
                disableAnimation={isHistoricalMessage}
              />
            
            {message.locationProposal && (
              <div className="max-w-[600px] mx-auto">
                <LocationProposalCard
                  location={message.locationProposal}
                  onDecision={(decision) => onLocationDecision?.(message.locationProposal!.id, decision)}
                />
              </div>
            )}
            
            {message.attractionProposal && (
              <div className="max-w-[600px] mx-auto">
                <AttractionProposalCard
                  attraction={message.attractionProposal}
                  onDecision={(decision) => onAttractionDecision?.(message.attractionProposal!.id, decision)}
                />
              </div>
            )}
            </div>
          );
        })}

        {/* Typing Indicator - Only for new messages */}
        {isLoading && (
          <div
            className="flex gap-3 mb-4 animate-slide-in-left"
            aria-label="Assistant is typing"
          >
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-sunset flex items-center justify-center shadow-sm">
              <Loader2 className="w-4 h-4 text-white animate-spin" />
            </div>
            <div className="bg-card border border-warm-coral/20 rounded-2xl px-4 py-3 shadow-sm">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-warm-coral/50 rounded-full animate-pulse-glow" />
                <span
                  className="w-2 h-2 bg-warm-coral/50 rounded-full animate-pulse-glow"
                  style={{ animationDelay: '0.2s' }}
                />
                <span
                  className="w-2 h-2 bg-warm-coral/50 rounded-full animate-pulse-glow"
                  style={{ animationDelay: '0.4s' }}
                />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} className="h-1 sm:h-2 md:h-3" />
        </div>
      </div>
    </div>
  );
});
