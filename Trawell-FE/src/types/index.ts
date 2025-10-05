export type ID = string;

export type Role = 'system' | 'assistant' | 'user';

export interface FormField {
  id: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'checkbox' | 'date' | 'number';
  required?: boolean;
  options?: { value: string; label: string }[];
  placeholder?: string;
}

export interface ChoiceOption {
  value: string;
  label: string;
}

export interface QuickReply {
  id: ID;
  label: string;
  payload?: unknown;
}

export type UIHint =
  | { type: 'form'; fields: FormField[] }
  | { type: 'choices'; options: ChoiceOption[] };

export interface ChatMessage {
  id: ID;
  role: Role;
  markdown?: string;
  createdAt: string;
  quickReplies?: QuickReply[];
  uiHints?: UIHint[];
  status?: 'sending' | 'sent' | 'error';
  userName?: string;
  userAvatar?: string;
  locationProposal?: Location;
  attractionProposal?: Attraction;
  tripCreated?: {
    tripId: string;
    title: string;
    locationName: string;
    createdAt: string;
  };
  photos?: Array<{
    query: string;
    caption: string;
    url: string;
  }>;
}

export interface User {
  id: ID;
  name: string;
  email?: string;
  onboardingCompleted: boolean;
}

export interface OnboardingQuestion {
  id: ID;
  markdownQuestion: string;
}

export interface OnboardingAnswerResponse {
  status: 'ok' | 'needs_clarification';
  followupMarkdown?: string;
}

export interface Project {
  id: ID;
  title: string;
  createdAt: string;
  lastMessagePreview?: string;
  updatedAt?: string;
  isShared?: boolean;
  shareCode?: string;
  ownerId?: string; // Owner's user ID (for shared projects not owned by current user)
  hasLocationSuggestions?: boolean; // Whether project has location suggestions ready
}

export interface ProjectParticipant {
  id: ID;
  projectId: ID;
  userId: ID;
  userName: string;
  joinedAt: string;
}

export interface Location {
  id: ID;
  name: string;
  country: string;
  teaser: string;
  imageUrl?: string;
  rating?: 1 | 2 | 3 | null;
  status?: 'pending' | 'rejected' | 'rated';
}

export interface Trip {
  id: ID;
  projectId?: ID;
  locationId?: ID;
  locationName: string;
  title: string;
  destination?: string;
  createdAt: string;
  lastMessagePreview?: string;
  updatedAt?: string;
  startDate?: string; // Trip start date
  endDate?: string; // Trip end date
  status?: string;
  rating?: number;
  // Images
  imageUrl?: string; // Legacy field
  url?: string; // Google Places photo URL
  // Logistics data
  flights?: {
    outbound?: {
      price: string;
      currency: string;
      itinerary: {
        totalDuration: string;
        segments: Array<{
          from: string;
          to: string;
          departureAt: string;
          arrivalAt: string;
          duration: string;
        }>;
      };
    };
    return?: {
      price: string;
      currency: string;
      itinerary: {
        totalDuration: string;
        segments: Array<{
          from: string;
          to: string;
          departureAt: string;
          arrivalAt: string;
          duration: string;
        }>;
      };
    };
  };
  hotels?: Array<{
    name: string;
    price: string;
    currency: string;
    checkInDate: string;
    checkOutDate: string;
  }>;
  weather?: any; // Weather forecast data structure
  // Trip details
  optimal_season?: string;
  estimated_budget?: number;
  currency?: string;
  highlights?: string[];
  // Additional fields
  dates?: any;
  participants?: any[];
}

export interface Attraction {
  id: ID;
  title: string;
  description: string;
  imageUrl?: string;
  category?: string;
  rating?: 1 | 2 | 3 | null;
  status?: 'pending' | 'rejected' | 'rated';
}

export type SummaryCategory =
  | 'Pogoda'
  | 'Weather'
  | 'Hotele'
  | 'Hotels'
  | 'Loty'
  | 'Flights'
  | 'Atrakcje'
  | 'Attractions'
  | 'Terminy'
  | 'Dates'
  | 'Lokalizacja'
  | 'Location'
  | 'Opis'
  | 'Description'
  | 'Co zabrać'
  | 'Packing'
  | 'Dokumenty'
  | 'Documents'
  | 'Checklista'
  | 'Checklist'
  | 'Najważniejsze'
  | 'Key Info'
  | 'Bezpieczeństwo'
  | 'Safety'
  | 'Budżet/koszty'
  | 'Budget'
  | 'Transport/Dojezdność'
  | 'Transport'
  | 'Sezonowość/Tłok'
  | 'Formalności'
  | 'Kultura/Obyczaje'
  | 'Noclegi'
  | 'Jedzenie';

export interface TripSummarySection {
  category: SummaryCategory;
  title: string;
  markdown: string;
  important?: boolean;
  tags?: string[];
}

export interface TripSummary {
  sections: TripSummarySection[];
}

export interface TripCard {
  id: string;
  title: string;
  locationName: string;
  imageUrl?: string; // Legacy field
  url?: string; // Google Places photo URL
  createdAt: string;
  rating?: 1 | 2 | 3;
}

// Seed data types
export interface SeedUser extends User {
  profile: import('@/types/profile').UserProfile;
}

export interface SeedProject extends Project {
  participants: string[]; // User IDs
}

export interface SeedConversation {
  projectId: string;
  messages: ChatMessage[];
}

export interface SeedTrip {
  tripId: string;
  messages: ChatMessage[];
  attractions: Attraction[];
}
