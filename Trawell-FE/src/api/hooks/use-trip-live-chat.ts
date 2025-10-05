import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { ChatMessage } from '@/types';

export function useTripLiveMessages(tripId: string) {
  return useQuery<ChatMessage[]>({
    queryKey: ['trip-live-messages', tripId],
    queryFn: () => apiClient.get(`/trips/${tripId}/live/messages`),
    enabled: !!tripId,
  });
}

export function useSendLiveMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ tripId, text }: { tripId: string; text: string }) => {
      return apiClient.post(`/trips/${tripId}/live/messages`, { text });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['trip-live-messages', variables.tripId] });
    },
  });
}
