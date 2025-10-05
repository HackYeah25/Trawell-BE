export type TravelerType = 'explorer' | 'relaxer' | 'mixed';
export type ActivityLevel = 'low' | 'medium' | 'high';
export type AccommodationStyle = 'all_inclusive' | 'boutique' | 'hostel' | 'mixed';
export type EnvironmentPref = 'city' | 'nature' | 'beach' | 'mountains' | 'mixed';
export type BudgetSensitivity = 'low' | 'medium' | 'high';
export type Level = 'low' | 'medium' | 'high';
export type ClimatePref = 'hot_tropical' | 'mild_temperate' | 'cool_cold' | 'no_preference';

export interface PastDestination {
  name: string;
  highlight?: string;
}

export interface UserProfile {
  id: string;
  name?: string;
  onboardingCompleted: boolean;
  completeness: number; // 0..1
  preferences: {
    traveler_type?: TravelerType;
    activity_level?: ActivityLevel;
    accommodation_style?: AccommodationStyle;
    environment?: EnvironmentPref;
    budget_sensitivity?: BudgetSensitivity;
    culture_interest?: Level;
    food_importance?: Level;
  };
  constraints: {
    dietary_restrictions?: string[];
    mobility_limitations?: string[];
    climate_preferences?: ClimatePref[];
    language_preferences?: string[];
  };
  experience: {
    past_destinations?: PastDestination[];
    wishlist_regions?: string[];
  };
  insights?: {
    personaLabel?: string;
    summaryMarkdown?: string;
    topTags?: string[];
  };
  updatedAt?: string;
}
