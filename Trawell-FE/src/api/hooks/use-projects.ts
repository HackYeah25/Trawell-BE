import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { Project, ChatMessage, Location } from '@/types';

export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => apiClient.get<Project[]>('/projects'),
  });
}

export function useProject(projectId: string) {
  return useQuery({
    queryKey: ['project', projectId],
    queryFn: () => apiClient.get<Project>(`/projects/${projectId}`),
    enabled: !!projectId,
  });
}

export function useProjectMessages(projectId: string) {
  return useInfiniteQuery({
    queryKey: ['project', projectId, 'messages'],
    queryFn: ({ pageParam = null }) => {
      const params = pageParam ? `?cursor=${pageParam}` : '';
      return apiClient.get<{ messages: ChatMessage[]; nextCursor: string | null }>(
        `/projects/${projectId}/messages${params}`
      );
    },
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    initialPageParam: null,
    enabled: !!projectId,
  });
}

export function useSendProjectMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { projectId: string; text: string }) =>
      apiClient.post<ChatMessage[]>(
        `/projects/${data.projectId}/messages`,
        { text: data.text }
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['project', variables.projectId, 'messages'],
      });
    },
  });
}

export function useProjectLocationSuggestions(projectId: string) {
  return useQuery({
    queryKey: ['project', projectId, 'locations', 'suggestions'],
    queryFn: () =>
      apiClient.get<Location[]>(`/projects/${projectId}/locations/suggestions`),
    enabled: !!projectId,
  });
}

export function useCreateTripFromLocation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { projectId: string; selectedLocationId: string }) =>
      apiClient.post<{ tripId: string }>(
        `/projects/${data.projectId}/locations`,
        { selectedLocationId: data.selectedLocationId }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trips'] });
    },
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { title?: string; seedFromOnboarding?: boolean; isShared?: boolean }) =>
      apiClient.post<{ id: string; shareCode?: string }>('/projects', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useJoinProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { shareCode: string }) =>
      apiClient.post<{ projectId: string }>('/projects/join', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useProjectParticipants(projectId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['project', projectId, 'participants'],
    queryFn: () => apiClient.get<any[]>(`/projects/${projectId}/participants`),
    enabled: !!projectId && enabled,
  });
}
