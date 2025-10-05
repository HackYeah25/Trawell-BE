import { useQuery } from '@tanstack/react-query';

export interface User {
  id: string;
  email: string;
  name: string;
  onboardingCompleted: boolean;
}

function getUserFromStorage(): User | null {
  const storedUser = localStorage.getItem('travelai_user');
  if (storedUser) {
    try {
      return JSON.parse(storedUser);
    } catch {
      return null;
    }
  }
  return null;
}

export function useUser() {
  return useQuery({
    queryKey: ['user'],
    queryFn: getUserFromStorage,
    staleTime: Infinity,
  });
}

