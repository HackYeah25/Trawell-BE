/**
 * Planning hooks - WebSocket and API calls for trip planning
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
const TEST_USER_ID = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';

export interface PlanningWSMessage {
  type: 'message' | 'token' | 'thinking' | 'complete' | 'error' | 'trip_updated' | 'photos' | 'pong';
  recommendation_id?: string;
  content?: string;
  token?: string;
  message?: string;
  updates?: Array<{
    field: string;
    value: any;
    currency?: string;
  }>;
  photos?: Array<{
    query: string;
    caption: string;
    url: string;
  }>;
}

export interface UsePlanningWebSocketOptions {
  recommendationId: string;
  onMessage?: (content: string) => void;
  onToken?: (token: string) => void;
  onThinking?: () => void;
  onComplete?: (content: string) => void;
  onError?: (error: string) => void;
  onTripUpdated?: (updates: any[]) => void;
  onPhotos?: (photos: Array<{ query: string; caption: string; url: string }>) => void;
}

/**
 * Hook for managing planning WebSocket connection
 */
export function usePlanningWebSocket(options: UsePlanningWebSocketOptions) {
  const {
    recommendationId,
    onMessage,
    onToken,
    onThinking,
    onComplete,
    onError,
    onTripUpdated,
    onPhotos,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const isConnectingRef = useRef(false);
  const recommendationIdRef = useRef(recommendationId);

  // Update ref when recommendationId changes
  useEffect(() => {
    recommendationIdRef.current = recommendationId;
  }, [recommendationId]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      console.log('Planning WS: Manually disconnecting...');
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsConnecting(false);
    isConnectingRef.current = false;
  }, []);

  const connect = useCallback(() => {
    const recId = recommendationIdRef.current;

    if (!recId) {
      console.warn('Planning WS: No recommendation ID provided, skipping connection');
      return;
    }

    if (isConnectingRef.current) {
      console.log('Planning WS: Already connecting, skipping...');
      return;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('Planning WS: Already connected');
      return;
    }

    console.log(`Planning WS: Connecting to recommendation ${recId}...`);
    isConnectingRef.current = true;
    setIsConnecting(true);

    try {
      const ws = new WebSocket(
        `${WS_BASE_URL}/api/planning/ws/${recId}?user_id=${TEST_USER_ID}`
      );

      ws.onopen = () => {
        console.log('Planning WS: Connection established');
        setIsConnected(true);
        setIsConnecting(false);
        isConnectingRef.current = false;
      };

      ws.onmessage = (event) => {
        try {
          const wsMessage: PlanningWSMessage = JSON.parse(event.data);
          console.log('Planning WS message:', wsMessage.type, wsMessage);

          switch (wsMessage.type) {
            case 'message':
              if (wsMessage.content && onMessage) {
                onMessage(wsMessage.content);
              }
              break;

            case 'token':
              if (wsMessage.token && onToken) {
                onToken(wsMessage.token);
              }
              break;

            case 'thinking':
              if (onThinking) {
                onThinking();
              }
              break;

            case 'complete':
              if (wsMessage.content && onComplete) {
                onComplete(wsMessage.content);
              }
              break;

            case 'trip_updated':
              console.log('🔄 Trip updated with structured data:', wsMessage.updates);
              if (wsMessage.updates && onTripUpdated) {
                onTripUpdated(wsMessage.updates);
              }
              break;

            case 'photos':
              console.log('📸 Photos received:', wsMessage.photos);
              if (wsMessage.photos && onPhotos) {
                onPhotos(wsMessage.photos);
              }
              break;

            case 'error':
              console.error('Planning WS error:', wsMessage.message);
              if (wsMessage.message && onError) {
                onError(wsMessage.message);
              }
              break;

            case 'pong':
              // Heartbeat response
              break;

            default:
              console.warn('Unknown planning WS message type:', wsMessage.type);
          }
        } catch (error) {
          console.error('Planning WS: Error parsing message', error);
        }
      };

      ws.onerror = (error) => {
        console.error('Planning WS error:', error);
        setIsConnecting(false);
        isConnectingRef.current = false;
        if (onError) {
          onError('WebSocket connection error');
        }
      };

      ws.onclose = (event) => {
        console.log(`Planning WS disconnected: ${event.code} ${event.reason}`);
        setIsConnected(false);
        setIsConnecting(false);
        isConnectingRef.current = false;
        wsRef.current = null;

        // Don't reconnect on permanent errors
        if (event.code === 1008 || event.code === 1011) {
          console.log('Planning WS: Permanent error, not reconnecting');
          return;
        }

        // Auto-reconnect after a delay
        console.log('Planning WS: Will attempt reconnect in 3 seconds...');
        setTimeout(() => {
          if (!isConnectingRef.current) {
            connect();
          }
        }, 3000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Planning WS: Connection failed', error);
      setIsConnecting(false);
      isConnectingRef.current = false;
    }
  }, []); // Empty deps - uses refs for stable reference

  const sendMessage = useCallback(
    (content: string) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        console.log('Planning WS: Sending message:', content.substring(0, 50));
        wsRef.current.send(
          JSON.stringify({
            type: 'message',
            content,
          })
        );
      } else {
        console.error('Planning WS: Cannot send message, not connected');
      }
    },
    []
  );

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();

    // Heartbeat to keep connection alive
    const heartbeat = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // Every 30 seconds

    return () => {
      clearInterval(heartbeat);
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    isConnecting,
    sendMessage,
    connect,
    disconnect,
  };
}

/**
 * Mutation to refresh trip summary
 */
export function useRefreshTripSummary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (recommendationId: string) => {
      // This will be called when trip is updated
      // Invalidate relevant queries
      queryClient.invalidateQueries({
        queryKey: ['trip', recommendationId],
      });
      queryClient.invalidateQueries({
        queryKey: ['brainstorm', 'sessions'],
      });
    },
  });
}
