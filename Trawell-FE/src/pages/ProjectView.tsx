
import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, Sparkles, Edit2, Check, X } from 'lucide-react';
import { AppShell } from '@/components/layout/AppShell';
import { ChatThread } from '@/components/chat/ChatThread';
import { Composer } from '@/components/chat/Composer';
import { CreateTripModal } from '@/components/projects/CreateTripModal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

import { useProject, useProjectMessages, useProjectLocationSuggestions, useCreateTripFromLocation, useSendProjectMessage } from '@/api/hooks/use-projects';
import { useBrainstormSession, useBrainstormWebSocket, useCreateRecommendation, type LocationProposal } from '@/api/hooks/use-brainstorm';
import { useTrips } from '@/api/hooks/use-trips';
import { useChatPagination } from '@/hooks/use-chat-pagination';
import { LocationProposalCard } from '@/components/projects/LocationProposalCard';
import type { ChatMessage, Location } from '@/types';
import { useToast } from '@/hooks/use-custom-toast';

export default function ProjectView() {
  const { projectId, sessionId } = useParams<{ projectId?: string; sessionId?: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const streamingMessageIdRef = useRef<string | null>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  
  // Location proposals state
  const [locationProposals, setLocationProposals] = useState<LocationProposal[]>([]);
  
  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // Trip creation modal state
  const [showCreateTripModal, setShowCreateTripModal] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);

  // Use sessionId for brainstorm routes, projectId for project routes
  const actualId = sessionId || projectId;
  const isProject = !!projectId;
  const isBrainstorm = !!sessionId;
  
  // Use appropriate hooks based on route type
  const { data: brainstormSession, isLoading: brainstormLoading, error: brainstormError } = useBrainstormSession(isBrainstorm ? actualId : null);
  const { data: project, isLoading: projectLoading, error: projectError } = useProject(isProject ? actualId! : '');
  const { data: projectMessagesData } = useProjectMessages(isProject ? actualId! : '');
  
  // Use the appropriate data source
  const session = isBrainstorm ? brainstormSession : project;
  const sessionLoading = isBrainstorm ? brainstormLoading : projectLoading;
  const sessionError = isBrainstorm ? brainstormError : projectError;
  
  const { data: locationSuggestions } = useProjectLocationSuggestions(actualId!);
  const { data: trips } = useTrips();
  const createTripMutation = useCreateTripFromLocation();
  const sendProjectMessageMutation = useSendProjectMessage();
  const createRecommendationMutation = useCreateRecommendation();

  // Pagination for chat messages
  const {
    displayedMessages,
    hasMore,
    isLoadingMore,
    loadMore,
    remainingCount,
  } = useChatPagination({
    allMessages: messages,
    pageSize: 10,
  });

  // Auto-scroll to bottom function
  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  };

  // Load messages from session data (only on initial load)
  const hasLoadedInitialMessages = useRef(false);
  useEffect(() => {
    if (isBrainstorm && brainstormSession?.messages && !hasLoadedInitialMessages.current) {
      // Brainstorm session messages
      const chatMessages: ChatMessage[] = brainstormSession.messages.map((msg: any, idx) => {
        const baseMessage: ChatMessage = {
          id: `msg-${idx}`,
          role: msg.role,
          markdown: msg.content,
          createdAt: msg.timestamp,
        };
        
        // Check if message has trip_created metadata
        if (msg.metadata && msg.metadata.type === 'trip_created') {
          baseMessage.tripCreated = {
            tripId: msg.metadata.tripId,
            title: msg.metadata.title,
            locationName: msg.metadata.locationName,
            createdAt: msg.timestamp,
          };
        }
        
        return baseMessage;
      });
      setMessages(chatMessages);
      hasLoadedInitialMessages.current = true;
      console.log('Loaded initial brainstorm messages:', chatMessages.length);
    } else if (isProject && projectMessagesData?.pages && !hasLoadedInitialMessages.current) {
      // Project messages from infinite query
      const allMessages = projectMessagesData.pages.flatMap(page => page.messages);
      setMessages(allMessages);
      hasLoadedInitialMessages.current = true;
      console.log('Loaded initial project messages:', allMessages.length);
    }
  }, [brainstormSession, projectMessagesData, isBrainstorm, isProject]);

  // Reset the loaded flag when session ID changes
  useEffect(() => {
    hasLoadedInitialMessages.current = false;
  }, [actualId]);

  // Auto-scroll when messages change
  useEffect(() => {
    // Small delay to ensure DOM has updated
    const timeoutId = setTimeout(() => {
      scrollToBottom();
    }, 100);
    
    return () => clearTimeout(timeoutId);
  }, [messages, currentStreamingMessage]);

  // WebSocket handlers - wrapped in useCallback to prevent reconnections
  const handleMessage = useCallback((wsMessage: { content?: string; role?: string }) => {
    if (wsMessage.content && wsMessage.role === 'assistant') {
      // Debug: log raw response
      console.log('📜 RAW MESSAGE FROM BACKEND:', wsMessage.content);
      
      // Clear streaming message and add final message
      const newMessage: ChatMessage = {
        id: streamingMessageIdRef.current || `ws-${Date.now()}`,
        role: 'assistant',
        markdown: wsMessage.content,
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, newMessage]);
      setCurrentStreamingMessage('');
      streamingMessageIdRef.current = null;
      setIsSending(false);
    }
  }, []);

  const handleToken = useCallback((token: string) => {
    if (!streamingMessageIdRef.current) {
      streamingMessageIdRef.current = `streaming-${Date.now()}`;
    }
    setCurrentStreamingMessage((prev) => prev + token);
  }, []);

  const handleThinking = useCallback(() => {
    console.log('Agent is thinking...');
  }, []);

  const handleComplete = useCallback(() => {
    // Note: We don't finalize here because the backend sends a final 'message' event
    // after all tokens are sent, which already contains the complete message
    setIsSending(false);
  }, []);

  const handleError = useCallback((error: string) => {
    console.error('Brainstorm error:', error);
    toast.error('Błąd połączenia', error);
    setIsSending(false);
  }, [toast]);

  const handleLocations = useCallback((locations: LocationProposal[]) => {
    console.log('Received location proposals:', locations);
    setLocationProposals(locations);
    toast.success('Nowe propozycje!', `${locations.length} destynacj${locations.length > 1 ? 'i' : 'a'} do sprawdzenia`);
  }, [toast]);

  const { sendMessage: sendWSMessage } = useBrainstormWebSocket({
    sessionId: isBrainstorm ? actualId : null,
    onMessage: handleMessage,
    onToken: handleToken,
    onThinking: handleThinking,
    onComplete: handleComplete,
    onError: handleError,
    onLocations: handleLocations,
  });

  const handleLocationProposalDecision = useCallback((decision: 'reject' | 1 | 2 | 3, locationId?: string) => {
    if (!locationId || !actualId) return;
    
    // Update location proposal status
    setLocationProposals((prev) =>
      prev.map((loc) => {
        if (loc.id === locationId) {
          return {
            ...loc,
            rating: decision === 'reject' ? null : decision,
            status: decision === 'reject' ? 'rejected' : 'rated',
          };
        }
        return loc;
      })
    );

    console.log(`Location ${locationId} decision: ${decision}`);

    // If rated with stars, handle based on session type
    if (decision !== 'reject') {
      const location = locationProposals.find(l => l.id === locationId);
      
      if (isBrainstorm && location) {
        // For brainstorm sessions, create recommendation and navigate to trip view
         createRecommendationMutation.mutate(
           {
             sessionId: actualId,
             locationData: {
               ...location,
               rating: decision,
             },
           },
           {
             onSuccess: (response) => {
               toast.success(`🎉 Trip to ${location.name} created!`);
               console.log('Created recommendation:', response.recommendation_id);
               
               // Add trip creation message to chat
               const tripMessage: ChatMessage = {
                 id: `trip-created-${Date.now()}`,
                 role: 'assistant',
                 markdown: `🎉 **Trip Created!**\n\nYour trip to **${location.name}** has been created successfully! You can now start planning your adventure.`,
                 createdAt: new Date().toISOString(),
                 tripCreated: {
                   tripId: response.recommendation_id,
                   title: `Trip to ${location.name}`,
                   locationName: location.name,
                   createdAt: new Date().toISOString(),
                 },
               };
               
               setMessages((prev) => [...prev, tripMessage]);
               
               // Navigate to trip view with the recommendation ID
               navigate(`/app/trips/${response.recommendation_id}`);
             },
             onError: (error) => {
               console.error('Error creating recommendation:', error);
               toast.error('Failed to create trip. Please try again.');
             },
           }
         );
      } else if (location) {
        // For project sessions, show trip creation modal
        setSelectedLocation(location);
        setShowCreateTripModal(true);
      }
    }
  }, [locationProposals, actualId, isBrainstorm, createRecommendationMutation, navigate, toast]);

  const handleQuickReply = (payload: unknown) => {
    if (typeof payload === 'string') {
      // Find location by ID in location proposals or messages
      const location = locationProposals.find(l => l.id === payload) || 
                     messages.find(msg => msg.locationProposal?.id === payload)?.locationProposal;
      
      if (location) {
        if (isBrainstorm) {
          // For brainstorm sessions, create recommendation directly
           createRecommendationMutation.mutate(
             {
               sessionId: actualId!,
               locationData: {
                 ...location,
                 rating: 3, // Default to 3 stars for quick reply
               },
             },
             {
               onSuccess: (response) => {
                 toast.success(`🎉 Trip to ${location.name} created!`);
                 
                 // Add trip creation message to chat
                 const tripMessage: ChatMessage = {
                   id: `trip-created-${Date.now()}`,
                   role: 'assistant',
                   markdown: `🎉 **Trip Created!**\n\nYour trip to **${location.name}** has been created successfully! You can now start planning your adventure.`,
                   createdAt: new Date().toISOString(),
                   tripCreated: {
                     tripId: response.recommendation_id,
                     title: `Trip to ${location.name}`,
                     locationName: location.name,
                     createdAt: new Date().toISOString(),
                   },
                 };
                 
                 setMessages((prev) => [...prev, tripMessage]);
                 
                 navigate(`/app/trips/${response.recommendation_id}`);
               },
               onError: (error) => {
                 console.error('Error creating recommendation:', error);
                 toast.error('Failed to create trip. Please try again.');
               },
             }
           );
        } else {
          // For project sessions, show modal
          setSelectedLocation(location);
          setShowCreateTripModal(true);
        }
      }
    }
  };

  const handleCreateTrip = async (tripData: { title: string; startDate?: string; endDate?: string }) => {
    if (!actualId || !selectedLocation || createTripMutation.isPending) return;

    try {
      const result = await createTripMutation.mutateAsync({
        projectId: actualId,
        selectedLocationId: selectedLocation.id,
      });

      // Add trip creation message to chat
      const tripMessage: ChatMessage = {
        id: `trip-created-${Date.now()}`,
        role: 'assistant',
        markdown: `🎉 **Trip Created!**\n\nYour trip to **${selectedLocation.name}** has been created successfully! You can now start planning your adventure.`,
        createdAt: new Date().toISOString(),
        tripCreated: {
          tripId: result.tripId,
          title: tripData.title,
          locationName: selectedLocation.name,
          createdAt: new Date().toISOString(),
        },
      };
      
      setMessages((prev) => [...prev, tripMessage]);

      // Close modal and navigate to trip
      setShowCreateTripModal(false);
      setSelectedLocation(null);
      navigate(`/app/trips/${result.tripId}`);
      
      toast.success('Podróż utworzona!', 'Przechodzisz do nowej podróży');
    } catch (error) {
      console.error('Error creating trip:', error);
      toast.error('Błąd tworzenia podróży', 'Spróbuj ponownie za chwilę');
    }
  };

  const handleCloseCreateTripModal = () => {
    setShowCreateTripModal(false);
    setSelectedLocation(null);
  };

  const handleSendMessage = async (text: string) => {
    if (!actualId) {
      toast.error('Błąd sesji', 'Brak identyfikatora sesji');
      return;
    }

    setIsSending(true);
    setCurrentStreamingMessage('');
    streamingMessageIdRef.current = null;

    // Send via appropriate method based on type
    if (isBrainstorm) {
      // Send via WebSocket for brainstorm sessions
      sendWSMessage(text);
    } else if (isProject) {
      // Send via API for projects
      sendProjectMessageMutation.mutate(
        { projectId: actualId, text },
        {
          onSuccess: (newMessages) => {
            // Update messages with response (API returns both user and assistant messages)
            setMessages((prev) => [...prev, ...newMessages]);
            setIsSending(false);
          },
          onError: (error) => {
            console.error('Error sending project message:', error);
            toast.error('Błąd wysyłania', 'Nie udało się wysłać wiadomości');
            setIsSending(false);
          },
        }
      );
    }

    // Every 3 user messages, add a location proposal
    const userMessageCount = messages.filter(m => m.role === 'user').length;
    if (locationSuggestions && userMessageCount % 3 === 0) {
      const unusedLocations = locationSuggestions.filter(loc => 
        !messages.some(msg => msg.locationProposal?.id === loc.id)
      );

      if (unusedLocations.length > 0) {
        const nextLocation = unusedLocations[0];
        const proposalMessage: ChatMessage = {
          id: `loc-proposal-${Date.now()}`,
          role: 'assistant',
          markdown: 'Mam dla Ciebie propozycję destynacji! 🌍',
          locationProposal: { ...nextLocation, status: 'pending' },
          createdAt: new Date().toISOString(),
        };

        setTimeout(() => {
          setMessages((prev) => [...prev, proposalMessage]);
        }, 1500);
      }
    }
  };

  // Edit handlers
  const handleEditClick = () => {
    setEditedTitle(session?.title || '');
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedTitle('');
  };

  const handleSaveEdit = async () => {
    if (!editedTitle.trim() || !actualId) return;
    
    setIsSaving(true);
    
    try {
      // Mock API call to backend
      console.log('Saving project name:', {
        projectId: actualId,
        newTitle: editedTitle.trim()
      });
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Update local state (in real app, this would come from API response)
      // For now, we'll just update the UI optimistically
      setIsEditing(false);
      setEditedTitle('');
      toast.success('Nazwa zaktualizowana!', 'Projekt został zapisany');
      
    } catch (error) {
      console.error('Error saving project name:', error);
      toast.error('Błąd zapisywania', 'Nie udało się zapisać nazwy');
    } finally {
      setIsSaving(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSaveEdit();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  if (sessionLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-warm-coral/5 via-warm-turquoise/5 to-warm-sand">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-sunset flex items-center justify-center shadow-warm">
            <Sparkles className="w-8 h-8 text-white animate-pulse" />
          </div>
          <Loader2 className="w-8 h-8 mx-auto animate-spin text-warm-coral" />
          <p className="mt-4 text-muted-foreground">Loading your brainstorm session...</p>
        </div>
      </div>
    );
  }

  if (sessionError || !session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-warm-coral/5 via-warm-turquoise/5 to-warm-sand">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-red-500/20 flex items-center justify-center">
            <span className="text-2xl">❌</span>
          </div>
          <p className="text-muted-foreground mb-4">
            Failed to load {isProject ? 'project' : 'brainstorm session'}
          </p>
          <p className="text-xs text-muted-foreground mb-4">
            Session ID: {actualId} | Error: {sessionError?.message || 'Unknown error'}
          </p>
          <Button onClick={() => navigate('/app')} variant="outline">
            Back to History
          </Button>
        </div>
      </div>
    );
  }

  // Combine messages with streaming message
  const displayMessages = [...messages];
  if (currentStreamingMessage && streamingMessageIdRef.current) {
    displayMessages.push({
      id: streamingMessageIdRef.current,
      role: 'assistant',
      markdown: currentStreamingMessage,
      createdAt: new Date().toISOString(),
    });
  }

  return (
    <AppShell>
      <div className="h-screen flex flex-col">
        {/* Fixed Header */}
        <div className="flex-shrink-0 p-4 border-b border-warm-coral/20 bg-card/80 backdrop-blur-md sticky top-0 z-[60]">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate('/app')}
                className="flex-shrink-0"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div className="w-10 h-10 rounded-xl bg-gradient-sunset flex items-center justify-center shadow-warm flex-shrink-0">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                {isEditing ? (
                  <div className="flex items-center gap-2">
                    <Input
                      value={editedTitle}
                      onChange={(e) => setEditedTitle(e.target.value)}
                      onKeyDown={handleKeyDown}
                      className="text-xl font-pacifico bg-transparent border-warm-coral/30 focus:border-warm-coral/60 h-8 px-2"
                      placeholder="Enter project name..."
                      autoFocus
                    />
                    <div className="flex items-center gap-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={handleSaveEdit}
                        disabled={isSaving || !editedTitle.trim()}
                        className="h-8 w-8 p-0 hover:bg-green-100"
                      >
                        <Check className="w-4 h-4 text-green-600" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={handleCancelEdit}
                        disabled={isSaving}
                        className="h-8 w-8 p-0 hover:bg-red-100"
                      >
                        <X className="w-4 h-4 text-red-600" />
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 group">
                    <h1 className="text-xl font-pacifico bg-gradient-sunset bg-clip-text text-transparent truncate">
                      {session.title}
                    </h1>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={handleEditClick}
                      className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-warm-coral/10"
                    >
                      <Edit2 className="w-4 h-4 text-warm-coral" />
                    </Button>
                  </div>
                )}
                <p className="text-xs text-muted-foreground">
                  {isProject ? 'Shared project' : 'Solo brainstorm session'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Scrollable Chat Area */}
        <div 
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto min-h-0"
        >
          <div className="max-w-4xl mx-auto p-4 space-y-4">
            <ChatThread
              messages={displayMessages}
              isLoading={isSending}
              onQuickReply={handleQuickReply}
              onViewTrip={(tripId) => navigate(`/app/trips/${tripId}`)}
              hasMore={hasMore}
              isLoadingMore={isLoadingMore}
              onLoadMore={loadMore}
              remainingCount={remainingCount}
            />
            
            {/* Location Proposals */}
            {locationProposals.length > 0 && (
              <div className="space-y-3 pb-8">
                <div className="flex items-center gap-2">
                  <div className="h-px flex-1 bg-warm-coral/20"></div>
                  <p className="text-sm text-warm-coral font-medium">✨ Destination Proposals</p>
                  <div className="h-px flex-1 bg-warm-coral/20"></div>
                </div>
                {locationProposals.map((location) => (
                  <LocationProposalCard
                    key={location.id}
                    location={location}
                    onDecision={(decision) => handleLocationProposalDecision(decision, location.id)}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Fixed Composer */}
        <div className="flex-shrink-0 border-t border-warm-coral/20 bg-card/80 backdrop-blur-md sticky bottom-0 z-10">
          <div className="max-w-4xl mx-auto p-4">
            <Composer onSend={handleSendMessage} disabled={isSending} />
          </div>
        </div>
      </div>

      {/* Create Trip Modal */}
      {selectedLocation && (
        <CreateTripModal
          isOpen={showCreateTripModal}
          onClose={handleCloseCreateTripModal}
          location={selectedLocation}
          onCreateTrip={handleCreateTrip}
          isLoading={createTripMutation.isPending}
        />
      )}
    </AppShell>
  );
}