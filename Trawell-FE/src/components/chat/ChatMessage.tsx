import { memo, useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { ChatMessage as ChatMessageType } from '@/types';
import { cn } from '@/lib/utils';
import { TripCard } from '@/components/trips/TripCard';

interface ChatMessageProps {
  message: ChatMessageType;
  onQuickReply?: (payload: unknown) => void;
  onRetry?: () => void;
  disableAnimation?: boolean;
  onViewTrip?: (tripId: string) => void;
}

export const ChatMessage = memo(function ChatMessage({
  message,
  onQuickReply,
  onRetry,
  disableAnimation = false,
  onViewTrip,
}: ChatMessageProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [shouldAnimate, setShouldAnimate] = useState(false);

  const getAvatarColor = (name?: string) => {
    if (!name) return 'bg-warm-turquoise';
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const colors = [
      'bg-gradient-to-br from-warm-coral to-warm-coral/80',
      'bg-gradient-to-br from-warm-turquoise to-warm-turquoise/80',
      'bg-gradient-to-br from-purple-500 to-purple-600',
      'bg-gradient-to-br from-blue-500 to-blue-600',
      'bg-gradient-to-br from-green-500 to-green-600',
      'bg-gradient-to-br from-amber-500 to-amber-600',
    ];
    return colors[hash % colors.length];
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };
  
  // Track if this is a new message that should be animated
  useEffect(() => {
    if (message.role === 'assistant' && message.markdown && !disableAnimation) {
      // Only animate truly new messages (not system messages or pre-loaded ones)
      const isNewMessage = !message.id.startsWith('initial-') && 
                          !message.id.startsWith('iguana-') && 
                          !message.id.startsWith('welcome') &&
                          !message.id.startsWith('shared-');
      setShouldAnimate(isNewMessage);
    } else {
      setShouldAnimate(false);
    }
  }, [message.id, message.role, message.markdown, disableAnimation]);
  
  // Simple message display - no typing animation to avoid flickering
  useEffect(() => {
    setDisplayedText(message.markdown || '');
    setIsTyping(false);
  }, [message.markdown]);

  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  const isOtherUser = isUser && message.userName; // Message from another user in group chat
  const isCurrentUser = isUser && !message.userName; // Message from current user

  return (
    <div
      className={cn(
        'flex mb-6',
        isCurrentUser ? 'justify-end' : 'justify-start'
      )}
      role="article"
      aria-label={`${message.role} message`}
    >
        <div 
          className={cn(
            'flex flex-col gap-1 w-full',
            isCurrentUser ? 'items-end max-w-[85%] sm:max-w-xl md:max-w-2xl' : 'max-w-[85%] sm:max-w-xl md:max-w-2xl'
          )}
        >
        {/* Avatar + Username ABOVE bubble for other users */}
        {isOtherUser && (
          <div className="flex items-center gap-2 ml-1">
            <div
              className={cn(
                'w-6 h-6 sm:w-8 sm:h-8 rounded-full flex items-center justify-center shadow-sm text-white text-xs font-semibold',
                getAvatarColor(message.userName)
              )}
              aria-hidden="true"
            >
              {getInitials(message.userName!)}
            </div>
            <p className="text-xs font-medium text-muted-foreground">
              {message.userName}
            </p>
          </div>
        )}

        {/* Message bubble with avatar for non-group messages */}
        <div 
          className={cn(
            'flex gap-3 w-full',
            isCurrentUser && 'flex-row-reverse'
          )}
        >
          {/* Avatar for current user and assistant */}
          {!isOtherUser && (
            <div className="flex-shrink-0">
              <div
                className={cn(
                  'w-6 h-6 sm:w-8 sm:h-8 rounded-full flex items-center justify-center shadow-sm',
                  isUser
                    ? 'bg-warm-turquoise'
                    : 'bg-gradient-sunset'
                )}
                aria-hidden="true"
              >
                {isUser ? (
                  <User className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                ) : (
                  <Bot className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                )}
              </div>
            </div>
          )}

          {/* Message content */}
          <div className="flex-1 min-w-0">
            <div
              className={cn(
                'rounded-2xl px-4 py-3 shadow-sm',
                isCurrentUser
                  ? 'bg-gradient-sunset text-white shadow-warm'
                  : isOtherUser
                  ? 'bg-white text-foreground border border-warm-coral/20 shadow-sm'
                  : 'bg-card text-card-foreground border border-warm-coral/20'
              )}
              data-is-typing={isTyping ? 'true' : 'false'}
            >
          {message.markdown && (
            <div className="prose prose-sm max-w-none dark:prose-invert prose-p:my-0 prose-ul:my-0 prose-ol:my-0">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {displayedText}
              </ReactMarkdown>
              {isTyping && (
                <span className="inline-block w-1 h-4 ml-1 bg-warm-coral animate-pulse align-middle" />
              )}
            </div>
          )}

          {message.status === 'error' && (
            <div className="flex items-center gap-2 mt-2 text-destructive">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">Failed to send message</span>
              {onRetry && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onRetry}
                  className="ml-auto hover:bg-warm-coral/10"
                >
                  Try again
                </Button>
              )}
            </div>
          )}

          {/* Trip Card */}
          {message.tripCreated && (
            <div className="mt-3">
              <TripCard
                trip={{
                  id: message.tripCreated.tripId,
                  title: message.tripCreated.title,
                  locationName: message.tripCreated.locationName,
                  createdAt: message.tripCreated.createdAt,
                }}
                onViewTrip={onViewTrip}
              />
            </div>
          )}
        </div>

        {message.quickReplies && message.quickReplies.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2" role="group" aria-label="Quick replies">
            {message.quickReplies.map((reply) => (
              <Button
                key={reply.id}
                variant="outline"
                size="sm"
                onClick={() => onQuickReply?.(reply.payload)}
                className="bg-card hover:bg-warm-coral/10 border-warm-coral/20"
              >
                {reply.label}
              </Button>
            ))}
          </div>
        )}

            {message.uiHints?.map((hint, index) => (
              <div key={index} className="mt-2">
                {hint.type === 'choices' && (
                  <div className="flex flex-col gap-2">
                    {hint.options.map((option) => (
                      <Button
                        key={option.value}
                        variant="outline"
                        size="sm"
                        onClick={() => onQuickReply?.(option.value)}
                        className="justify-start bg-card hover:bg-warm-coral/10 border-warm-coral/20"
                      >
                        {option.label}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
});
