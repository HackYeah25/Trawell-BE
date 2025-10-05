import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { Trip, ChatMessage, Attraction, TripSummary } from '@/types';

export function useTrips() {
  return useQuery({
    queryKey: ['trips'],
    queryFn: () => apiClient.get<Trip[]>('/trips'),
  });
}

export function useProjectTrips(projectId: string) {
  return useQuery({
    queryKey: ['trips', 'project', projectId],
    queryFn: () => apiClient.get<Trip[]>(`/projects/${projectId}/trips`),
    enabled: !!projectId,
  });
}

export function useTrip(tripId: string) {
  return useQuery({
    queryKey: ['trip', tripId],
    queryFn: async () => {
      // Try to fetch as a recommendation first (from brainstorm)
      try {
        const recommendation = await apiClient.get<any>(`/brainstorm/recommendations/${tripId}`);
        // Transform recommendation to Trip format
        return {
          id: recommendation.recommendation_id,
          title: recommendation.destination.name || recommendation.destination.city,
          destination: recommendation.destination.city || recommendation.destination.name,
          status: recommendation.status,
          dates: null,
          participants: [],
          createdAt: recommendation.created_at,
          updatedAt: recommendation.updated_at,
          // Logistics data from new backend fields
          url: recommendation.url,
          imageUrl: recommendation.url, // Backwards compatibility
          flights: recommendation.flights,
          hotels: recommendation.hotels,
          weather: recommendation.weather,
          optimal_season: recommendation.optimal_season,
          estimated_budget: recommendation.estimated_budget,
          currency: recommendation.currency,
          highlights: recommendation.highlights,
        } as Trip;
      } catch (error) {
        // Fallback to regular trip endpoint (already returns new fields)
        return apiClient.get<Trip>(`/trips/${tripId}`);
      }
    },
    enabled: !!tripId,
  });
}

export function useTripMessages(tripId: string) {
  return useInfiniteQuery({
    queryKey: ['trip', tripId, 'messages'],
    queryFn: ({ pageParam = null }) => {
      const params = pageParam ? `?cursor=${pageParam}` : '';
      return apiClient.get<{ messages: ChatMessage[]; nextCursor: string | null }>(
        `/trips/${tripId}/messages${params}`
      );
    },
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    initialPageParam: null,
    enabled: !!tripId,
  });
}

export function useSendTripMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { tripId: string; text?: string; formPayload?: unknown }) =>
      apiClient.post<ChatMessage[]>(
        `/trips/${data.tripId}/messages`,
        data.text ? { text: data.text } : { formPayload: data.formPayload }
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['trip', variables.tripId, 'messages'],
      });
      queryClient.invalidateQueries({
        queryKey: ['trip', variables.tripId, 'attractions'],
      });
    },
  });
}

export function useTripAttractions(tripId: string) {
  return useQuery({
    queryKey: ['trip', tripId, 'attractions'],
    queryFn: () => apiClient.get<Attraction[]>(`/trips/${tripId}/attractions`),
    enabled: !!tripId,
  });
}

export function useAttractionDecision() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      tripId: string;
      attractionId: string;
      decision: 'accept' | 'reject';
    }) =>
      apiClient.post<{ status: string }>(
        `/trips/${data.tripId}/attractions/${data.attractionId}/decision`,
        { decision: data.decision }
      ),
    onMutate: async ({ tripId, attractionId, decision }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['trip', tripId, 'attractions'] });

      const previousAttractions = queryClient.getQueryData<Attraction[]>([
        'trip',
        tripId,
        'attractions',
      ]);

      if (previousAttractions) {
        queryClient.setQueryData<Attraction[]>(
          ['trip', tripId, 'attractions'],
          previousAttractions.map((attr) =>
            attr.id === attractionId
              ? { ...attr, decision: decision === 'accept' ? 'accepted' : 'rejected' }
              : attr
          )
        );
      }

      return { previousAttractions };
    },
    onError: (err, { tripId }, context) => {
      // Rollback on error
      if (context?.previousAttractions) {
        queryClient.setQueryData(
          ['trip', tripId, 'attractions'],
          context.previousAttractions
        );
      }
    },
    onSettled: (_, __, { tripId }) => {
      queryClient.invalidateQueries({ queryKey: ['trip', tripId, 'attractions'] });
    },
  });
}

export function useTripSummary(tripId: string) {
  return useQuery({
    queryKey: ['trip', tripId, 'summary'],
    queryFn: () => apiClient.get<TripSummary>(`/trips/${tripId}/summary`),
    enabled: !!tripId,
  });
}

export function useCreateTrip() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { projectId: string; locationId: string }) =>
      apiClient.post<{ id: string }>('/trips', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trips'] });
    },
  });
}
