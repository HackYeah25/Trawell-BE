import { useMutation, useQueryClient } from '@tanstack/react-query';
import { User } from './use-user';

interface LoginCredentials {
  email: string;
  password: string;
}

interface SignupCredentials {
  email: string;
  password: string;
  name: string;
}

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ email, password }: LoginCredentials) => {
      // Simulate login - in production this would be an API call
      const user: User = {
        id: Math.random().toString(36).substr(2, 9),
        email,
        name: email.split('@')[0],
        onboardingCompleted: false,
      };
      
      localStorage.setItem('travelai_user', JSON.stringify(user));
      return user;
    },
    onSuccess: (user) => {
      // Invalidate and refetch user query
      queryClient.setQueryData(['user'], user);
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });
}

export function useSignup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ email, password, name }: SignupCredentials) => {
      // Simulate signup - in production this would be an API call
      const user: User = {
        id: Math.random().toString(36).substr(2, 9),
        email,
        name,
        onboardingCompleted: false,
      };
      
      localStorage.setItem('travelai_user', JSON.stringify(user));
      return user;
    },
    onSuccess: (user) => {
      // Invalidate and refetch user query
      queryClient.setQueryData(['user'], user);
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      localStorage.removeItem('travelai_user');
    },
    onSuccess: () => {
      // Clear user query
      queryClient.setQueryData(['user'], null);
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });
}
