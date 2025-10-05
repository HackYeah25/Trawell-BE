import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import type { Project, Trip } from '@/types';

export function useRenameProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { projectId: string; title: string }) =>
      apiClient.patch<Project>(`/projects/${data.projectId}`, { title: data.title }),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useRenameTrip() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { tripId: string; title: string }) =>
      apiClient.patch<Trip>(`/trips/${data.tripId}`, { title: data.title }),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['trip', variables.tripId] });
      queryClient.invalidateQueries({ queryKey: ['trips'] });
    },
  });
}
