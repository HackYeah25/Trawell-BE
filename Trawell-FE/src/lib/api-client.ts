import type { 
  User, 
  OnboardingQuestion, 
  OnboardingAnswerResponse,
  Project,
  Trip,
  ChatMessage,
  Location,
  Attraction,
  TripSummary,
} from '@/types';
import {
  mockUser,
  updateMockUser,
  onboardingQuestions,
  mockProjects,
  mockTrips,
  mockProjectMessages,
  mockTripMessages,
  mockAttractions,
  mockLocations,
  getTripSummary,
  specialSharedProject,
  iguanaSharedProject,
  iguanaTrip,
  iguanaLocation,
} from './mock-data';
import { getSeedConversation, getSeedTripConversation, getSeedAttractions } from './seeds';

// Simulate network delay
async function mockDelay(ms: number = 300): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, ms));
}

// Simulate API response
async function mockFetch<T>(data: T, delay: number = 300): Promise<T> {
  await mockDelay(delay);
  return data;
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// API Client implementation with real backend
const API_BASE_URL = 'http://localhost:8000/api';

export const apiClient = {
  // User endpoints
  get: async <T>(endpoint: string): Promise<T> => {
    // User
    if (endpoint === '/me') {
      return mockFetch(mockUser as T);
    }

    // Onboarding questions - use real backend
    if (endpoint === '/profiling/questions') {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    // Profiling status - use real backend
    if (endpoint === '/profiling/status') {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    // Brainstorm sessions - use real backend
    if (endpoint === '/brainstorm/sessions') {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    // Single brainstorm session
    if (endpoint.match(/^\/brainstorm\/sessions\/[^/]+$/)) {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    // Brainstorm session recommendations
    if (endpoint.match(/^\/brainstorm\/sessions\/[^/]+\/recommendations$/)) {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    // Single recommendation by ID (for trip view)
    if (endpoint.match(/^\/brainstorm\/recommendations\/[^/]+$/)) {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    // Projects list
    if (endpoint === '/projects') {
      return mockFetch(mockProjects as T);
    }

    // Single project
    if (endpoint.match(/^\/projects\/[^/]+$/)) {
      const projectId = endpoint.split('/')[2];
      const project = mockProjects.find((p) => p.id === projectId);
      if (!project) throw new ApiError('Project not found', 404);
      return mockFetch(project as T);
    }

    // Project messages
    if (endpoint.match(/^\/projects\/[^/]+\/messages$/)) {
      const projectId = endpoint.split('/')[2];
      const messages = mockProjectMessages[projectId] || [];
      return mockFetch({ messages, nextCursor: null } as T);
    }

    // Project location suggestions
    if (endpoint.match(/^\/projects\/[^/]+\/locations\/suggestions$/)) {
      const projectId = endpoint.split('/')[2];
      
      // Return locations for projects that have suggestions
      const project = mockProjects.find(p => p.id === projectId);
      if (project?.hasLocationSuggestions || 
          projectId === 'shared-proj-abc123') {
        const allLocations = [...mockLocations, iguanaLocation];
        return mockFetch(allLocations as T, 400);
      }
      
      return mockFetch([] as T, 400);
    }

    // Project participants
    if (endpoint.match(/^\/projects\/[^/]+\/participants$/)) {
      const projectId = endpoint.split('/')[2];
      
      if (projectId === 'shared-proj-iguana') {
        return mockFetch([
          {
            id: 'participant-1',
            projectId,
            userId: 'user-sarah-456',
            userName: 'Sarah Mitchell',
            joinedAt: new Date('2025-01-08T09:00:00').toISOString(),
          },
          {
            id: 'participant-2',
            projectId,
            userId: 'user-mark-789',
            userName: 'Mark Johnson',
            joinedAt: new Date('2025-01-08T09:30:00').toISOString(),
          },
          {
            id: 'participant-3',
            projectId,
            userId: 'user-emma-321',
            userName: 'Emma Rodriguez',
            joinedAt: new Date('2025-01-08T10:00:00').toISOString(),
          },
        ] as T);
      }
      
      if (projectId === 'shared-proj-abc123') {
        return mockFetch([
          {
            id: 'participant-abc-1',
            projectId,
            userId: 'other-user-123',
            userName: 'Alex Thompson',
            joinedAt: new Date('2025-01-10T08:00:00').toISOString(),
          },
        ] as T);
      }
      
      return mockFetch([] as T);
    }

    // Project trips
    if (endpoint.match(/^\/projects\/[^/]+\/trips$/)) {
      const projectId = endpoint.split('/')[2];
      const projectTrips = mockTrips.filter(trip => trip.projectId === projectId);
      return mockFetch(projectTrips as T);
    }

    // Brainstorm session trips (recommendations)
    if (endpoint.match(/^\/brainstorm\/sessions\/[^/]+\/recommendations$/)) {
      const sessionId = endpoint.split('/')[3];
      // Mock some recommendations for demo
      const mockRecommendations = [
        {
          recommendation_id: `rec-${sessionId}-1`,
          destination: {
            name: 'Tokyo, Japan',
            city: 'Tokyo',
            imageUrl: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400',
            rating: 4.5
          },
          created_at: new Date().toISOString(),
          status: 'active'
        },
        {
          recommendation_id: `rec-${sessionId}-2`,
          destination: {
            name: 'Barcelona, Spain',
            city: 'Barcelona',
            imageUrl: 'https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=400',
            rating: 4.2
          },
          created_at: new Date().toISOString(),
          status: 'active'
        }
      ];
      return mockFetch({ recommendations: mockRecommendations } as T);
    }

    // Trips list - use real backend
    if (endpoint === '/trips') {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    // Single trip
    if (endpoint.match(/^\/trips\/[^/]+$/)) {
      const tripId = endpoint.split('/')[2];
      const trip = mockTrips.find((t) => t.id === tripId);
      if (!trip) throw new ApiError('Trip not found', 404);
      return mockFetch(trip as T);
    }

    // Trip messages
    if (endpoint.match(/^\/trips\/[^/]+\/messages$/)) {
      const tripId = endpoint.split('/')[2];
      const messages = mockTripMessages[tripId] || [];
      return mockFetch({ messages, nextCursor: null } as T);
    }

    // Trip attractions
    if (endpoint.match(/^\/trips\/[^/]+\/attractions$/)) {
      const tripId = endpoint.split('/')[2];
      return mockFetch((mockAttractions[tripId] || []) as T);
    }

    // Trip summary
    if (endpoint.match(/^\/trips\/[^/]+\/summary$/)) {
      const tripId = endpoint.split('/')[2];
      const tripAttractions = mockAttractions[tripId] || [];
      return mockFetch(getTripSummary(tripAttractions) as T, 500);
    }

    throw new ApiError(`Unknown endpoint: ${endpoint}`, 404);
  },

  patch: async <T>(endpoint: string, data?: unknown): Promise<T> => {
    // Update user
    if (endpoint === '/me') {
      const updates = data as Partial<User>;
      updateMockUser(updates);
      return mockFetch(mockUser as T);
    }

    // Update project
    if (endpoint.match(/^\/projects\/[^/]+$/)) {
      await mockDelay(300);
      const projectId = endpoint.split('/')[2];
      const project = mockProjects.find((p) => p.id === projectId);
      if (!project) throw new ApiError('Project not found', 404);
      
      const updates = data as Partial<Project>;
      Object.assign(project, updates);
      return mockFetch(project as T);
    }

    // Update trip
    if (endpoint.match(/^\/trips\/[^/]+$/)) {
      await mockDelay(300);
      const tripId = endpoint.split('/')[2];
      const trip = mockTrips.find((t) => t.id === tripId);
      if (!trip) throw new ApiError('Trip not found', 404);
      
      const updates = data as Partial<Trip>;
      Object.assign(trip, updates);
      return mockFetch(trip as T);
    }

    throw new ApiError(`Unknown endpoint: ${endpoint}`, 404);
  },

  post: async <T>(endpoint: string, data?: unknown): Promise<T> => {
    // Start profiling session - use real backend
    if (endpoint === '/profiling/start') {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    // Create brainstorm session - use real backend
    if (endpoint === '/brainstorm/sessions') {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    // Create recommendation from brainstorm session - use real backend
    if (endpoint.match(/^\/brainstorm\/sessions\/[^/]+\/recommendations$/)) {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    // Answer onboarding question
    if (endpoint === '/onboarding/answer') {
      await mockDelay(500);
      const body = data as { questionId: string; answerText: string };
      
      // Simple validation
      if (body.answerText.length < 3) {
        return {
          status: 'needs_clarification',
          followupMarkdown:
            'Czy mógłbyś/mogłabyś podać więcej szczegółów? Pomoże mi to lepiej dobrać oferty.',
        } as T;
      }

      return { status: 'ok' } as T;
    }

    // Complete onboarding
    if (endpoint === '/onboarding/complete') {
      await mockDelay(800);

      const newProject: Project = {
        id: `proj-${Date.now()}`,
        title: 'Moja wymarzona podróż',
        createdAt: new Date().toISOString(),
        lastMessagePreview: 'Rozpocznijmy planowanie...',
      };

      mockProjects.push(newProject);

      mockProjectMessages[newProject.id] = [
        {
          id: 'm1',
          role: 'assistant',
          markdown:
            '🎉 Świetnie! Na podstawie Twoich odpowiedzi przygotowałem kilka propozycji.\n\nCzy chciałbyś zobaczyć sugerowane lokalizacje?',
          createdAt: new Date().toISOString(),
        },
      ];

      return { projectId: newProject.id } as T;
    }

    // Create new project
    if (endpoint === '/projects') {
      await mockDelay(400);
      const body = data as { title?: string; isShared?: boolean };

      const newProject: Project = {
        id: `proj-${Date.now()}`,
        title: body.title || 'New Project',
        createdAt: new Date().toISOString(),
        isShared: body.isShared || false,
      };

      if (body.isShared) {
        const { generateShareCode } = await import('./utils');
        newProject.shareCode = generateShareCode();
      }

      mockProjects.push(newProject);
      mockProjectMessages[newProject.id] = [];

      return { id: newProject.id, shareCode: newProject.shareCode } as T;
    }

    // Join shared project
    if (endpoint === '/projects/join') {
      await mockDelay(600);
      const body = data as { shareCode: string };

      // Check for special shared project code
      if (body.shareCode.toUpperCase() === 'ABC123') {
        // Add the special shared project if not already added
        const existingProject = mockProjects.find(p => p.id === specialSharedProject.id);
        if (!existingProject) {
          mockProjects.push({ ...specialSharedProject });
          mockProjectMessages[specialSharedProject.id] = [
            {
              id: 'shared-msg-1',
              role: 'assistant',
              markdown: '👥 Welcome to the **Team Adventure**!\n\nThis is a collaborative project. You can see and contribute to the planning.',
              createdAt: new Date().toISOString(),
            },
          ];
        }
        return { projectId: specialSharedProject.id } as T;
      }

      // Check for iguana shared project code
      if (body.shareCode.toLowerCase() === 'iguana') {
        const existingProject = mockProjects.find(p => p.id === iguanaSharedProject.id);
        if (!existingProject) {
          mockProjects.push({ ...iguanaSharedProject });
          mockTrips.push({ ...iguanaTrip });
          
          // Add project messages from seed data
          mockProjectMessages[iguanaSharedProject.id] = getSeedConversation('proj-krakow-iguana');
          
          // Multi-user conversation from seed data
          mockTripMessages[iguanaTrip.id] = getSeedTripConversation('trip-iguana-bcn');
          
          // Attractions for Krakow trip from seed data
          mockAttractions[iguanaTrip.id] = getSeedAttractions('trip-iguana-bcn');
          
          mockProjectMessages[iguanaSharedProject.id] = getSeedConversation('proj-krakow-iguana');
        }
        return { projectId: iguanaSharedProject.id } as T;
      }

      const project = mockProjects.find((p) => p.shareCode === body.shareCode);
      if (!project) {
        throw new ApiError('Project not found with that share code', 404);
      }

      // In a real app, this would add the user to the project participants
      return { projectId: project.id } as T;
    }

    // Send project message
    if (endpoint.match(/^\/projects\/[^/]+\/messages$/)) {
      await mockDelay(800);
      const projectId = endpoint.split('/')[2];
      const body = data as { text: string };

      const userMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'user',
        markdown: body.text,
        createdAt: new Date().toISOString(),
      };

      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        markdown:
          'Rozumiem! Oto kilka propozycji lokalizacji, które mogą Cię zainteresować. Możesz utworzyć podróż dla każdej z nich.',
        createdAt: new Date().toISOString(),
      };

      if (!mockProjectMessages[projectId]) {
        mockProjectMessages[projectId] = [];
      }

      mockProjectMessages[projectId].push(userMessage, assistantMessage);

      return [userMessage, assistantMessage] as T;
    }

    // Create trip from location
    if (endpoint.match(/^\/projects\/[^/]+\/locations$/)) {
      await mockDelay(600);
      const body = data as { selectedLocationId: string };

      const location = mockLocations.find((l) => l.id === body.selectedLocationId);
      if (!location) throw new ApiError('Location not found', 404);

      const newTrip: Trip = {
        id: `trip-${Date.now()}`,
        projectId: 'proj-1',
        locationId: location.id,
        locationName: `${location.name}, ${location.country}`,
        title: `Podróż do ${location.name}`,
        createdAt: new Date().toISOString(),
      };

      mockTrips.push(newTrip);
      mockTripMessages[newTrip.id] = [
        {
          id: 'tm1',
          role: 'assistant',
          markdown: `Witaj w planowaniu podróży do **${location.name}**! 🎿\n\nOpowiedz mi więcej o swoich oczekiwaniach, a ja przygotuję listę atrakcji.`,
          createdAt: new Date().toISOString(),
        },
      ];

      // Add mock attractions
      mockAttractions[newTrip.id] = [
        {
          id: 'attr1',
          title: 'Przejazd kolejką gondolową',
          description: 'Spektakularne widoki na Alpy podczas przejazdu nowoczesną kolejką',
          category: 'Transport',
          imageUrl: 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600&q=80',
        },
        {
          id: 'attr2',
          title: 'Szkoła narciarska (2 dni)',
          description: 'Profesjonalne kursy dla początkujących i zaawansowanych',
          category: 'Aktywności',
          imageUrl: 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=600&q=80',
        },
        {
          id: 'attr3',
          title: 'Wieczór przy ognisku',
          description: 'Tradycyjne spotkanie z lokalnymi potrawami i muzyką',
          category: 'Rozrywka',
          imageUrl: 'https://images.unsplash.com/photo-1519861531473-9200262188bf?w=600&q=80',
        },
      ];

      return { tripId: newTrip.id } as T;
    }

    // Send trip message
    if (endpoint.match(/^\/trips\/[^/]+\/messages$/)) {
      await mockDelay(800);
      const tripId = endpoint.split('/')[2];
      const body = data as { text: string };

      const userMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'user',
        markdown: body.text,
        createdAt: new Date().toISOString(),
      };

      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        markdown:
          'Świetnie! Sprawdź zakładkę **Atrakcje** - przygotowałem dla Ciebie propozycje. Zaakceptuj te, które Cię interesują.',
        createdAt: new Date().toISOString(),
      };

      if (!mockTripMessages[tripId]) {
        mockTripMessages[tripId] = [];
      }

      mockTripMessages[tripId].push(userMessage, assistantMessage);

      return [userMessage, assistantMessage] as T;
    }

    // Attraction decision
    if (endpoint.match(/^\/trips\/[^/]+\/attractions\/[^/]+\/decision$/)) {
      await mockDelay(400);
      const tripId = endpoint.split('/')[2];
      const attractionId = endpoint.split('/')[4];
      const body = data as { rating: 1 | 2 | 3 | null };

      // Update attraction rating in mock data
      if (mockAttractions[tripId]) {
        const attraction = mockAttractions[tripId].find((a) => a.id === attractionId);
        if (attraction) {
          attraction.rating = body.rating;
          attraction.status = body.rating ? 'rated' : 'rejected';
        }
      }

      // Check if all attractions have been rated
      const allDecided = mockAttractions[tripId]?.every((a) => a.status === 'rated' || a.status === 'rejected');
      
      if (allDecided && mockTripMessages[tripId]) {
        // Add post-attraction questions after all decisions are made
        const { postAttractionQuestions } = await import('./mock-data');
        
        mockTripMessages[tripId].push({
          id: `msg-${Date.now()}`,
          role: 'assistant',
          markdown: postAttractionQuestions[0].markdownQuestion,
          createdAt: new Date().toISOString(),
        });
      }

      return { status: 'ok' } as T;
    }

    throw new ApiError(`Unknown endpoint: ${endpoint}`, 404);
  },

  put: async <T>(endpoint: string, data?: unknown): Promise<T> => {
    throw new ApiError(`PUT not implemented: ${endpoint}`, 404);
  },

  delete: async <T>(endpoint: string): Promise<T> => {
    // Delete brainstorm session
    if (endpoint.match(/^\/brainstorm\/sessions\/[^/]+$/)) {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    // Delete profiling profile/reset
    if (endpoint === '/profiling/profile/reset') {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new ApiError(`HTTP ${response.status}`, response.status);
      }
      return response.json();
    }

    throw new ApiError(`DELETE not implemented: ${endpoint}`, 404);
  },
};

export { ApiError };
