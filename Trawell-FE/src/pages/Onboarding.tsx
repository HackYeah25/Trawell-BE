import { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plane, Loader2, SkipForward } from 'lucide-react';
import { ChatThread } from '@/components/chat/ChatThread';
import { Composer } from '@/components/chat/Composer';
import { Button } from '@/components/ui/button';
import {
  useOnboardingQuestions,
  useStartProfiling,
  useProfilingWebSocket,
  useCompleteOnboarding,
  useProfileStatus,
} from '@/api/hooks/use-onboarding';
import type { ChatMessage } from '@/types';

export default function Onboarding() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [isThinking, setIsThinking] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const streamingMessageIdRef = useRef<string | null>(null);

  const { data: profileStatus, isLoading: profileStatusLoading } = useProfileStatus();
  const { data: questions, isLoading: questionsLoading } = useOnboardingQuestions();
  const startProfilingMutation = useStartProfiling();
  const completeMutation = useCompleteOnboarding();

  const handleSkipOnboarding = useCallback(async () => {
    try {
      // Complete onboarding without answering questions
      const result = await completeMutation.mutateAsync({
        createInitialProject: true,
      });

      // Redirect to dashboard instead of specific project
      navigate('/app');
    } catch (error) {
      console.error('Error skipping onboarding:', error);
    }
  }, [completeMutation, navigate]);

  // Check if user already has profile - skip onboarding
  useEffect(() => {
    if (profileStatus && profileStatus.should_skip_onboarding) {
      console.log('User already has complete profile, redirecting to app...');
      navigate('/app/brainstorm');
    }
  }, [profileStatus, navigate]);

  // Note: Auto-skip removed to prevent interference with normal onboarding flow
  // Developers can use the Skip button in the header when needed

  // Handle successful session creation using mutation.data instead of onSuccess callback
  useEffect(() => {
    if (startProfilingMutation.isSuccess && startProfilingMutation.data && !sessionId) {
      console.log('Setting up session from mutation data:', startProfilingMutation.data);
      setSessionId(startProfilingMutation.data.session.session_id);
      setTotalQuestions(questions?.length || 0);

      // Add welcome message
      const welcomeMessage: ChatMessage = {
        id: 'welcome',
        role: 'system',
        markdown: startProfilingMutation.data.first_message,
        createdAt: new Date().toISOString(),
      };
      setMessages([welcomeMessage]);
    }
  }, [startProfilingMutation.isSuccess, startProfilingMutation.data, sessionId, questions?.length]);

  // WebSocket handlers
  const { sendAnswer } = useProfilingWebSocket({
    sessionId,
    onMessage: (message) => {
      if (message.role === 'assistant' && message.content) {
        const assistantMessage: ChatMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          markdown: message.content,
          createdAt: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
        setCurrentStreamingMessage('');
        streamingMessageIdRef.current = null;
      }
    },
    onToken: (token) => {
      setCurrentStreamingMessage((prev) => prev + token);
      if (!streamingMessageIdRef.current) {
        streamingMessageIdRef.current = `streaming-${Date.now()}`;
      }
    },
    onProgress: (progress) => {
      setCurrentQuestion(progress.current);
      setTotalQuestions(progress.total);
    },
    onValidation: (validation) => {
      console.log('Validation:', validation);
    },
    onComplete: async (data) => {
      console.log('Profiling complete:', data);
      // Complete onboarding
      const result = await completeMutation.mutateAsync({
        createInitialProject: true,
      });
      navigate(`/app/projects/${result.projectId}`);
    },
    onThinking: () => {
      setIsThinking(true);
      setTimeout(() => setIsThinking(false), 500);
    },
  });

  // Start profiling session (only once, and only if user doesn't have profile)
  useEffect(() => {
    console.log('Start session check - sessionId:', sessionId, 'isPending:', startProfilingMutation.isPending, 'isSuccess:', startProfilingMutation.isSuccess);

    // Don't start if user already has profile or profile is still loading
    if (profileStatusLoading || profileStatus?.should_skip_onboarding) {
      return;
    }

    if (!sessionId && !startProfilingMutation.isPending && !startProfilingMutation.isSuccess) {
      console.log('Calling mutate to create session...');
      startProfilingMutation.mutate(undefined);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, startProfilingMutation.isPending, startProfilingMutation.isSuccess, profileStatus, profileStatusLoading]);

  const handleSendMessage = async (text: string) => {
    if (!sessionId) {
      console.error('Cannot send message: no session ID');
      return;
    }

    console.log('Sending answer:', text);

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      markdown: text,
      createdAt: new Date().toISOString(),
      status: 'sent',
    };

    setMessages((prev) => [...prev, userMessage]);

    // Send via WebSocket
    sendAnswer(text);
  };

  const handleStartAdventure = async () => {
    try {
      // Complete onboarding - this will update localStorage and invalidate cache
      const result = await completeMutation.mutateAsync({
        createInitialProject: true,
      });

      // Redirect to first project
      navigate(`/app/projects/${result.projectId}`);
    } catch (error) {
      console.error('Error completing onboarding:', error);
    }
  };

  if (profileStatusLoading || questionsLoading || startProfilingMutation.isPending) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-warm-coral/5 via-warm-turquoise/5 to-warm-sand">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-sunset flex items-center justify-center shadow-warm">
            <Plane className="w-8 h-8 text-white animate-pulse" />
          </div>
          <Loader2 className="w-8 h-8 mx-auto animate-spin text-warm-coral" />
          <p className="mt-4 text-muted-foreground">
            {profileStatusLoading ? 'Checking your profile...' : 'Preparing your travel profile...'}
          </p>
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
    <div className="h-screen flex flex-col bg-gradient-to-br from-warm-coral/5 via-warm-turquoise/5 to-warm-sand">
      {/* Fixed Header */}
      <div className="flex-shrink-0 p-6 border-b border-warm-coral/20 bg-card/80 backdrop-blur-md">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-sunset flex items-center justify-center shadow-warm">
                <Plane className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-pacifico bg-gradient-sunset bg-clip-text text-transparent">
                  Let's Plan Your Trip
                </h1>
                <p className="text-sm text-muted-foreground">
                  Question {Math.min(currentQuestion, totalQuestions)} of {totalQuestions}
                </p>
              </div>
            </div>
            
            {/* Skip Button - Only visible in dev mode */}
            {localStorage.getItem('TRAWELL_DEV_MODE') === 'true' && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSkipOnboarding}
                disabled={completeMutation.isPending}
                className="text-muted-foreground hover:text-foreground hover:bg-warm-coral/10"
              >
                <SkipForward className="w-4 h-4 mr-2" />
                Skip
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Scrollable Chat Area */}
      <div className="flex-1 overflow-hidden">
        <ChatThread
          messages={displayMessages}
          isLoading={isThinking || completeMutation.isPending}
          className="h-full"
          onQuickReply={handleStartAdventure}
        />
      </div>

      {/* Fixed Footer */}
      <div className="flex-shrink-0 border-t border-warm-coral/20 bg-card/80 backdrop-blur-md">
        <div className="max-w-4xl mx-auto">
          <Composer
            onSend={handleSendMessage}
            disabled={isThinking || completeMutation.isPending || !sessionId}
            placeholder="Your answer..."
            disableMobileFixed={true}
          />
        </div>
      </div>
    </div>
  );
}
