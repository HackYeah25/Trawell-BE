import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MapPin, Calendar, Loader2, Pencil, Check, X, Radio, ArrowLeft, Sparkles } from 'lucide-react';
import { AppShell } from '@/components/layout/AppShell';
import { ChatThread } from '@/components/chat/ChatThread';
import { Composer } from '@/components/chat/Composer';
import { TripTabs } from '@/components/trips/TripTabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useIsMobile } from '@/hooks/use-mobile';
import { useChatPagination } from '@/hooks/use-chat-pagination';
import {
  useTrip,
  useTripMessages,
  useSendTripMessage,
  useTripAttractions,
  useAttractionDecision,
  useTripSummary,
} from '@/api/hooks/use-trips';
import { usePlanningWebSocket } from '@/api/hooks/use-planning';
import { useRenameTrip } from '@/api/hooks/use-rename';
import { SummaryCard } from '@/components/trips/SummaryCard';
import { saveChatHistory, loadChatHistory } from '@/lib/chat-storage';
import type { ChatMessage } from '@/types';

export default function TripView() {
  const { tripId } = useParams<{ tripId: string }>();
  const navigate = useNavigate();
  const [localMessages, setLocalMessages] = useState<ChatMessage[]>([]);
  const [activeTab, setActiveTab] = useState<'chat' | 'summary'>('chat');
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState('');
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<string>('');
  const [isAIResponding, setIsAIResponding] = useState(false);
  const isMobile = useIsMobile();

  const { data: trip } = useTrip(tripId!);
  const { data: messagesData } = useTripMessages(tripId!);
  const { data: attractions } = useTripAttractions(tripId!);
  const { data: summary } = useTripSummary(tripId!);
  const sendMessageMutation = useSendTripMessage();
  const attractionDecisionMutation = useAttractionDecision();
  const renameMutation = useRenameTrip();

  // Planning WebSocket handlers
  const handlePlanningMessage = useCallback((content: string) => {
    console.log('Planning message received:', content);
    // This won't be called for streaming - we use tokens instead
  }, []);

  const handlePlanningToken = useCallback((token: string) => {
    setCurrentStreamingMessage((prev) => prev + token);
  }, []);

  const handlePlanningThinking = useCallback(() => {
    console.log('Planning agent is thinking...');
    setIsAIResponding(true);
    setCurrentStreamingMessage('');
  }, []);

  // Store pending photos that arrived before the message
  const pendingPhotosRef = useRef<Array<{ query: string; caption: string; url: string }>>([]);

  const handlePlanningComplete = useCallback((content: string) => {
    console.log('Planning response complete');
    setIsAIResponding(false);

    // Add complete AI message to chat, including any pending photos
    const aiMessage: ChatMessage = {
      id: `ai-${Date.now()}`,
      role: 'assistant',
      markdown: content,
      createdAt: new Date().toISOString(),
      photos: pendingPhotosRef.current.length > 0 ? pendingPhotosRef.current : undefined,
    };

    setLocalMessages((prev) => [...prev, aiMessage]);
    setCurrentStreamingMessage('');

    // Clear pending photos after using them
    pendingPhotosRef.current = [];
  }, []);

  const handlePlanningError = useCallback((error: string) => {
    console.error('Planning error:', error);
    setIsAIResponding(false);
    setCurrentStreamingMessage('');
    pendingPhotosRef.current = [];
  }, []);

  const handleTripUpdated = useCallback((updates: any[]) => {
    console.log('Trip updated with structured data:', updates);
    // TODO: Update UI to reflect new trip data (budget, dates, etc.)
  }, []);

  const handlePhotos = useCallback((photos: Array<{ query: string; caption: string; url: string }>) => {
    console.log('📸 Photos received (storing for next message):', photos);

    // Store photos to be attached when the complete message arrives
    pendingPhotosRef.current = photos;
  }, []);

  // Initialize Planning WebSocket
  const { isConnected, sendMessage: sendWSMessage } = usePlanningWebSocket({
    recommendationId: tripId || '',
    onMessage: handlePlanningMessage,
    onToken: handlePlanningToken,
    onThinking: handlePlanningThinking,
    onComplete: handlePlanningComplete,
    onError: handlePlanningError,
    onTripUpdated: handleTripUpdated,
    onPhotos: handlePhotos,
  });

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
      const stored = loadChatHistory(`trip-${tripId}`);
      if (stored && stored.length > 0) {
        setLocalMessages(stored);
      } else {
        // Initialize with welcome message
        const welcomeMessage: ChatMessage = {
          id: 'welcome',
          role: 'assistant',
          markdown: `Welcome to trip planning! 🌟 I'll help you create the perfect plan. Tell me what you're looking for?`,
          createdAt: new Date().toISOString(),
        };
        setLocalMessages([welcomeMessage]);
      }
    }
  }, [tripId]);

  // Save to localStorage on every message change
  useEffect(() => {
    if (tripId && localMessages.length > 0) {
      saveChatHistory(`trip-${tripId}`, localMessages);
    }
  }, [tripId, localMessages]);

  const handleSaveTitle = async () => {
    if (!tripId || !editedTitle.trim()) {
      setIsEditingTitle(false);
      return;
    }

    try {
      await renameMutation.mutateAsync({
        tripId,
        title: editedTitle.trim(),
      });
      setIsEditingTitle(false);
    } catch (error) {
      console.error('Error renaming trip:', error);
    }
  };

  const handleCancelEdit = () => {
    setIsEditingTitle(false);
    setEditedTitle(trip?.title || '');
  };

  const handleSendMessage = useCallback((text: string) => {
    if (!tripId || !isConnected) {
      console.warn('Cannot send message: no tripId or WebSocket not connected');
      return;
    }

    // Add user message to local state immediately
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      markdown: text,
      createdAt: new Date().toISOString(),
    };

    setLocalMessages((prev) => [...prev, userMessage]);

    // Send via WebSocket
    sendWSMessage(text);
  }, [tripId, isConnected, sendWSMessage]);

  const handleAttractionDecision = (attractionId: string, decision: 'reject' | 1 | 2 | 3) => {
    setLocalMessages((prev) =>
      prev.map((msg) => {
        if (msg.attractionProposal?.id === attractionId) {
          return {
            ...msg,
            attractionProposal: {
              ...msg.attractionProposal,
              rating: decision === 'reject' ? null : decision,
              status: decision === 'reject' ? 'rejected' : 'rated',
            },
          };
        }
        return msg;
      })
    );

    // Mock API call
    console.log(`Attraction ${attractionId} decision: ${decision}`);

    // Add AI acknowledgment
    const acknowledgment = decision === 'reject' 
      ? 'Rozumiem, poszukam innych opcji. 👍'
      : `Świetnie! Oceniłeś to na ${decision} gwiazdki. ⭐`;

    setTimeout(() => {
      const ackMessage: ChatMessage = {
        id: `ack-${Date.now()}`,
        role: 'assistant',
        markdown: acknowledgment,
        createdAt: new Date().toISOString(),
      };
      setLocalMessages((prev) => [...prev, ackMessage]);
    }, 600);
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
      <div className="h-screen flex flex-col">
        {/* Header - Fixed */}
        <div className="flex-shrink-0 p-4 border-b border-warm-coral/20 bg-card/80 backdrop-blur-md sticky top-0 z-[60]">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-3 mb-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate('/app')}
                className="flex-shrink-0"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div className="w-8 h-8 rounded-lg bg-gradient-sunset flex items-center justify-center shadow-warm flex-shrink-0">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="font-pacifico text-lg bg-gradient-sunset bg-clip-text text-transparent leading-tight">
                  {trip?.title || 'Trip Details'}
                </h3>
                <p className="text-xs text-muted-foreground">
                  {trip?.locationName || 'Your amazing journey'}
                </p>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <MapPin className="w-3 h-3 md:w-4 md:h-4 text-warm-coral" />
                {trip.locationName}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3 md:w-4 md:h-4" />
                {trip.startDate && trip.endDate 
                  ? `${new Date(trip.startDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${new Date(trip.endDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
                  : new Date(trip.createdAt).toLocaleDateString('en-US')
                }
              </span>
              {trip.startDate && trip.endDate && (() => {
                const now = new Date();
                const start = new Date(trip.startDate);
                const end = new Date(trip.endDate);
                start.setDate(start.getDate() - 2);
                end.setDate(end.getDate() + 2);
                return now >= start && now <= end;
              })() && (
                <>
                  <span>•</span>
                  <button
                    onClick={() => navigate(`/app/trips/${tripId}/live`)}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-500/10 border border-red-500/20 hover:bg-red-500/20 transition-colors group"
                  >
                    <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                    <Radio className="w-3.5 h-3.5 text-red-600 group-hover:scale-110 transition-transform" />
                    <span className="text-xs font-semibold text-red-600">Live Assistant</span>
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Tabs and Content - Flex container */}
        <div className="flex-1 flex flex-col min-h-0">
          <TripTabs
            activeTab={activeTab}
            onTabChange={setActiveTab}
            chatContent={
              <div className="flex-1 flex flex-col min-h-0">
                {/* Chat Thread - Scrollable */}
                <div className="flex-1 overflow-y-auto pb-6">
                  <ChatThread
                    messages={displayedMessages}
                    isLoading={isAIResponding}
                    onAttractionDecision={handleAttractionDecision}
                    hasMore={hasMore}
                    isLoadingMore={isLoadingMore}
                    onLoadMore={loadMore}
                    remainingCount={remainingCount}
                  />
                </div>
              </div>
            }
            summaryContent={
              summary ? (
                <div className="max-w-4xl mx-auto space-y-6 pb-6 min-h-full">
                  {summary.sections.map((section, index) => (
                    <SummaryCard
                      key={index}
                      section={section}
                      attractions={attractions}
                    />
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center space-y-2">
                    <Loader2 className="w-8 h-8 animate-spin text-warm-coral mx-auto" />
                    <p className="text-muted-foreground">Generating summary...</p>
                  </div>
                </div>
              )
            }
          />
        </div>

        {/* Fixed Composer - Only for chat tab */}
        {activeTab === 'chat' && (
          <div className="flex-shrink-0 border-t border-warm-coral/20 bg-card/80 backdrop-blur-md sticky bottom-0 z-10">
            <div className="max-w-4xl mx-auto p-4">
              <Composer
                onSend={handleSendMessage}
                disabled={isAIResponding || !isConnected}
                placeholder={isConnected ? "Opisz swoje preferencje..." : "Łączenie..."}
              />
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
