import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';
import type { OnboardingQuestion, OnboardingAnswerResponse } from '@/types';

export function useProfileStatus() {
  return useQuery({
    queryKey: ['profiling', 'status'],
    queryFn: async () => {
      const response = await apiClient.get<{
        has_completed_profiling: boolean;
        should_skip_onboarding: boolean;
        profile_completeness: number;
        last_session_id?: string | null;
        user_id?: string | null;
        completed_at?: string;
      }>('/profiling/status');
      return response;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useResetProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.delete('/profiling/profile/reset'),
    onSuccess: () => {
      // Invalidate profile status to refetch
      queryClient.invalidateQueries({ queryKey: ['profiling', 'status'] });
    },
  });
}

export function useOnboardingQuestions() {
  return useQuery({
    queryKey: ['profiling', 'questions'],
    queryFn: async () => {
      const response = await apiClient.get<OnboardingQuestion[]>('/profiling/questions');
      return response;
    },
    staleTime: Infinity, // Questions don't change
  });
}

export function useStartProfiling() {
  return useMutation({
    mutationFn: (userId?: string) =>
      apiClient.post<{
        session: { session_id: string };
        first_message: string;
        websocket_url: string;
      }>('/profiling/start', { user_id: userId }),
  });
}

export interface WSMessage {
  type: 'message' | 'token' | 'progress' | 'validation' | 'complete' | 'thinking';
  conversation_id: string;
  role?: 'user' | 'assistant';
  content?: string;
  token?: string;
  current_question?: number;
  total_questions?: number;
  completeness?: number;
  current_question_id?: string;
  question_id?: string;
  status?: 'insufficient' | 'sufficient' | 'complete';
  feedback?: string;
  profile_id?: string;
  message?: string;
}

interface UseProfilingWebSocketOptions {
  sessionId: string | null;
  onMessage?: (message: WSMessage) => void;
  onToken?: (token: string) => void;
  onProgress?: (progress: {
    current: number;
    total: number;
    completeness: number;
  }) => void;
  onValidation?: (validation: {
    questionId: string;
    status: string;
    feedback?: string;
  }) => void;
  onComplete?: (data: { profileId: string; completeness: number }) => void;
  onThinking?: () => void;
}

export function useProfilingWebSocket({
  sessionId,
  onMessage,
  onToken,
  onProgress,
  onValidation,
  onComplete,
  onThinking,
}: UseProfilingWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // Store callbacks in refs to avoid reconnections
  const handlersRef = useRef({ onMessage, onToken, onProgress, onValidation, onComplete, onThinking });

  useEffect(() => {
    handlersRef.current = { onMessage, onToken, onProgress, onValidation, onComplete, onThinking };
  }, [onMessage, onToken, onProgress, onValidation, onComplete, onThinking]);

  const connect = useCallback(() => {
    console.log('connect() called, sessionId:', sessionId);

    if (!sessionId) {
      console.warn('No sessionId, skipping WebSocket connection');
      return;
    }

    // Don't create new connection if one already exists and is open
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected, skipping');
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.hostname}:8000/api/profiling/ws/${sessionId}`;

    console.log('Creating new WebSocket connection to:', wsUrl);
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data: WSMessage = JSON.parse(event.data);
      const handlers = handlersRef.current;

      // Debug log (skip tokens to avoid spam)
      if (data.type !== 'profiling_token') {
        console.log('WS message:', data.type, data);
      }

      switch (data.type) {
        case 'profiling_message':
        case 'message':
          handlers.onMessage?.(data);
          break;
        case 'profiling_token':
        case 'token':
          if (data.token) handlers.onToken?.(data.token);
          break;
        case 'profiling_progress':
        case 'progress':
          if (
            data.current_question !== undefined &&
            data.total_questions !== undefined &&
            data.completeness !== undefined
          ) {
            handlers.onProgress?.({
              current: data.current_question,
              total: data.total_questions,
              completeness: data.completeness,
            });
          }
          break;
        case 'profiling_validation':
        case 'validation':
          if (data.question_id && data.status) {
            handlers.onValidation?.({
              questionId: data.question_id,
              status: data.status,
              feedback: data.feedback,
            });
          }
          break;
        case 'profiling_complete':
        case 'complete':
          if (data.profile_id !== undefined && data.completeness !== undefined) {
            handlers.onComplete?.({
              profileId: data.profile_id,
              completeness: data.completeness,
            });
          }
          break;
        case 'profiling_thinking':
        case 'thinking':
          handlers.onThinking?.();
          break;
        default:
          console.warn('Unknown WS message type:', data.type);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = (event) => {
      console.log('WebSocket disconnected', event.code, event.reason);
      wsRef.current = null;
      // Only auto-reconnect on unexpected disconnects (not 1000 normal closure or 1008 session not found)
      if (event.code !== 1000 && event.code !== 1008) {
        console.log('Will attempt reconnect in 3 seconds...');
        reconnectTimeoutRef.current = window.setTimeout(() => connect(), 3000);
      }
    };

    wsRef.current = ws;
  }, [sessionId]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendAnswer = useCallback((answer: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('Sending answer via WebSocket:', answer);
      wsRef.current.send(
        JSON.stringify({
          type: 'user_answer',
          answer,
        })
      );
    } else {
      console.error('WebSocket not ready. State:', wsRef.current?.readyState);
    }
  }, []);

  useEffect(() => {
    console.log('useEffect triggered, sessionId:', sessionId);
    if (sessionId) {
      connect();
    }
    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]); // Only re-run when sessionId changes, not when connect/disconnect change

  return { sendAnswer, disconnect };
}

export function useAnswerQuestion() {
  return useMutation({
    mutationFn: (data: { questionId: string; answerText: string }) =>
      apiClient.post<OnboardingAnswerResponse>('/onboarding/answer', data),
  });
}

export function useCompleteOnboarding() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { createInitialProject: boolean }) =>
      apiClient.post<{ projectId: string }>('/onboarding/complete', data),
    onSuccess: () => {
      // Update user's onboarding status in localStorage
      const storedUser = localStorage.getItem('travelai_user');
      if (storedUser) {
        const user = JSON.parse(storedUser);
        user.onboardingCompleted = true;
        localStorage.setItem('travelai_user', JSON.stringify(user));
      }

      // Invalidate cache to trigger re-render
      queryClient.invalidateQueries({ queryKey: ['user'] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}
