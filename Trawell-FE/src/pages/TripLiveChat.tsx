import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, Radio } from 'lucide-react';
import { AppShell } from '@/components/layout/AppShell';
import { ChatThread } from '@/components/chat/ChatThread';
import { Composer } from '@/components/chat/Composer';
import { Button } from '@/components/ui/button';
import { useTrip } from '@/api/hooks/use-trips';
import { saveChatHistory, loadChatHistory } from '@/lib/chat-storage';
import { useChatPagination } from '@/hooks/use-chat-pagination';
import type { ChatMessage } from '@/types';

const INITIAL_MESSAGE: ChatMessage = {
  id: 'live-welcome',
  role: 'assistant',
  markdown: 'Hi! I\'m your real-time travel assistant. I\'m here to help you during your trip with immediate, practical advice.\n\nAsk me anything:\n- Restaurant recommendations nearby\n- Transportation and directions\n- What to do right now\n- Emergency help\n- Local tips and insights',
  createdAt: new Date().toISOString(),
};

export default function TripLiveChat() {
  const { tripId } = useParams<{ tripId: string }>();
  const navigate = useNavigate();
  const [localMessages, setLocalMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);

  const { data: trip } = useTrip(tripId!);

  // Pagination for chat messages
  const {
    displayedMessages,
    hasMore,
    isLoadingMore,
    loadMore,
    remainingCount,
  } = useChatPagination({
    allMessages: localMessages,
    pageSize: 10,
  });

  // Load chat history from localStorage or initialize with welcome message
  useEffect(() => {
    if (tripId) {
      const stored = loadChatHistory(`trip-live-${tripId}`);
      if (stored && stored.length > 0) {
        setLocalMessages(stored);
      } else {
        setLocalMessages([INITIAL_MESSAGE]);
      }
    }
  }, [tripId]);

  // Save to localStorage on every message change
  useEffect(() => {
    if (tripId && localMessages.length > 0) {
      saveChatHistory(`trip-live-${tripId}`, localMessages);
    }
  }, [tripId, localMessages]);

  const handleSendMessage = async (text: string) => {
    if (!tripId) return;

    const tempMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      markdown: text,
      createdAt: new Date().toISOString(),
      status: 'sending',
    };

    setLocalMessages((prev) => [...prev, tempMessage]);
    setIsSending(true);

    try {
      // Mock API call with delay
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Update with successful message
      setLocalMessages((prev) =>
        prev.map((m) => (m.id === tempMessage.id ? { ...m, status: undefined } : m))
      );

      // Add AI response
      const aiResponse: ChatMessage = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        markdown: generateLiveResponse(text),
        createdAt: new Date().toISOString(),
      };

      setTimeout(() => {
        setLocalMessages((prev) => [...prev, aiResponse]);
        setIsSending(false);
      }, 500);
    } catch (error) {
      console.error('Error sending message:', error);
      setLocalMessages((prev) =>
        prev.map((m) => (m.id === tempMessage.id ? { ...m, status: 'error' } : m))
      );
      setIsSending(false);
    }
  };

  const generateLiveResponse = (userMessage: string): string => {
    const lower = userMessage.toLowerCase();
    
    if (lower.includes('hungry') || lower.includes('food') || lower.includes('restaurant') || lower.includes('eat')) {
      return 'Based on your current location, here are some great nearby options:\n\n**Quick & Close:**\n- **Ramen Ichiban** (2 min walk) - Quick service, authentic tonkotsu ramen\n- **Sushi Express** (5 min walk) - Fresh sushi, counter seating\n\n**Sit-down:**\n- **Sakura Garden** (8 min walk) - Traditional kaiseki, reservations recommended\n\nAll are open now! Would you like directions to any of these?';
    }
    
    if (lower.includes('transport') || lower.includes('metro') || lower.includes('taxi') || lower.includes('bus')) {
      return 'Transportation Options:\n\n**Metro:** Nearest station is 3 minutes away (Exit B). Trains run every 5 minutes.\n\n**Taxi:** Available at the stand 100m to your left. Estimated wait: 2-3 minutes.\n\n**Bus:** Route 24 stops across the street, arrives in 7 minutes.\n\nWhere would you like to go?';
    }
    
    if (lower.includes('emergency') || lower.includes('help') || lower.includes('doctor') || lower.includes('hospital')) {
      return '**Emergency Assistance:**\n\n**Police:** 110 (English support available)\n**Ambulance/Fire:** 119\n\n**Nearest Hospital:** City Medical Center\n- 1.2 km away (5 min by taxi)\n- 24/7 Emergency Room\n- English-speaking staff\n\n**Your Embassy:** +XX-XXXX-XXXX\n\nDo you need immediate assistance?';
    }
    
    if (lower.includes('what to do') || lower.includes('recommend') || lower.includes('see') || lower.includes('visit')) {
      return '**Right Now:**\n\nBased on the time and your location, I recommend:\n\n1. **Temple Garden** (10 min walk) - Beautiful at sunset, free entry\n2. **Local Market** (5 min walk) - Open until 8 PM, great for souvenirs\n3. **Observation Deck** (15 min walk) - Best city views, open until 10 PM\n\nWhat interests you most?';
    }

    return 'I\'m here to help! Could you tell me more about what you need? I can assist with:\n- Finding restaurants or food nearby\n- Transportation and directions\n- Things to do right now\n- Emergency assistance\n- Local tips and recommendations';
  };

  if (!tripId || !trip) {
    return (
      <AppShell>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Loader2 className="w-8 h-8 animate-spin text-warm-coral" />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="h-[calc(100vh-4rem)] flex flex-col">
        {/* Header */}
        <div className="border-b border-warm-coral/20 bg-card/80 backdrop-blur-md p-4 flex-shrink-0">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate(`/app/trips/${tripId}`)}
                className="hover:bg-warm-coral/10"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h1 className="text-xl md:text-2xl font-pacifico bg-gradient-sunset bg-clip-text text-transparent truncate">
                    {trip.title}
                  </h1>
                  <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-red-500/10 border border-red-500/20">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                    <Radio className="w-3 h-3 text-red-600" />
                    <span className="text-xs font-semibold text-red-600">Live</span>
                  </div>
                </div>
                <p className="text-xs md:text-sm text-muted-foreground mt-1">
                  Real-time Travel Assistant
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Chat and Composer Container */}
        <div className="flex-1 flex flex-col min-h-0">
          {/* Chat Thread */}
          <div className="flex-1 overflow-y-auto h-0 pb-6">
            <ChatThread
              messages={displayedMessages}
              isLoading={isSending}
              hasMore={hasMore}
              isLoadingMore={isLoadingMore}
              onLoadMore={loadMore}
              remainingCount={remainingCount}
            />
          </div>

          {/* Composer */}
          <Composer
            onSend={handleSendMessage}
            disabled={isSending}
            placeholder="Ask me anything about your trip..."
          />
        </div>
      </div>
    </AppShell>
  );
}
