import { useQuery } from '@tanstack/react-query';
import type { UserProfile } from '@/types/profile';
import { seedUsers, getSeedUserById } from '@/lib/seeds';

// Get current user from storage (defaults to Anna)
function getCurrentUserId(): string {
  const storedUser = localStorage.getItem('travelai_user');
  if (storedUser) {
    try {
      const user = JSON.parse(storedUser);
      return user.id;
    } catch {
      return 'user-anna-001'; // Default to Anna
    }
  }
  return 'user-anna-001';
}

// Get profile for current user
function getCurrentProfile(): UserProfile {
  const userId = getCurrentUserId();
  const seedUser = getSeedUserById(userId);
  return seedUser?.profile || seedUsers[0].profile; // Fallback to Anna
}

// Legacy mock data (kept for backward compatibility)
const mockProfile: UserProfile = {
  id: "u_123",
  name: "Anna Kowalska",
  onboardingCompleted: true,
  completeness: 0.92,
  preferences: {
    traveler_type: "mixed",
    activity_level: "medium",
    accommodation_style: "boutique",
    environment: "mountains",
    budget_sensitivity: "medium",
    culture_interest: "high",
    food_importance: "high"
  },
  constraints: {
    dietary_restrictions: ["vegetarian"],
    mobility_limitations: [],
    climate_preferences: ["mild_temperate", "cool_cold"],
    language_preferences: ["Prefer English-friendly"]
  },
  experience: {
    past_destinations: [
      { name: "Lisbon, Portugal", highlight: "Amazing climate and cuisine" },
      { name: "Sölden, Austria", highlight: "Stunning slopes and views" }
    ],
    wishlist_regions: ["Japan", "Patagonia", "Iceland"]
  },
  insights: {
    personaLabel: "Mountain aesthete with appetite for local cuisine",
    summaryMarkdown: "You prefer **medium-intensity** trips, prioritize **boutique accommodations** and **culinary experiences**. Budget matters, but **experiences** win.",
    topTags: ["mountains", "foodie", "boutique", "culture"]
  },
  updatedAt: new Date().toISOString()
};

async function fetchProfile(): Promise<UserProfile> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // TODO: Replace with actual API call
  // const response = await fetch('/api/profile');
  // return response.json();
  
  // Use seed data based on current user
  return getCurrentProfile();
}

export function useProfile() {
  const userId = getCurrentUserId();
  
  return useQuery({
    queryKey: ['profile', userId],
    queryFn: fetchProfile,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Dev helper: Switch user in development
if (typeof window !== 'undefined') {
  (window as any).__switchUser = (userId: string) => {
    const user = getSeedUserById(userId);
    if (user) {
      localStorage.setItem('travelai_user', JSON.stringify(user));
      window.location.reload();
      console.log(`✅ Switched to user: ${user.name} (${userId})`);
    } else {
      console.error(`❌ User ${userId} not found. Available: user-anna-001, user-tomasz-002, user-maria-003`);
    }
  };
  
  (window as any).__listUsers = () => {
    console.log('📋 Available seed users:');
    seedUsers.forEach(u => {
      console.log(`  - ${u.id}: ${u.name} (${u.email})`);
    });
  };
}
