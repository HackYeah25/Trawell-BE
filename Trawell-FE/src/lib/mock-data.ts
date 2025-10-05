import type {
  User,
  OnboardingQuestion,
  Project,
  Trip,
  ChatMessage,
  Location,
  Attraction,
  TripSummary,
} from '@/types';
import { 
  seedUsers, 
  seedProjects, 
  seedConversations, 
  seedTripConversations,
  seedAttractions,
  seedTrips,
  getSeedUserById,
  getSeedProjectsForUser 
} from './seeds';

// Get current user from storage
function getCurrentUserId(): string {
  const storedUser = localStorage.getItem('travelai_user');
  if (storedUser) {
    try {
      const user = JSON.parse(storedUser);
      return user.id;
    } catch {
      return 'user-anna-001';
    }
  }
  return 'user-anna-001';
}

// User data - dynamically from seed
export let mockUser: User = (() => {
  const userId = getCurrentUserId();
  const seedUser = getSeedUserById(userId);
  return seedUser || seedUsers[0];
})();

// Initial project questions (asked when starting a new project)
export const initialProjectQuestions: ChatMessage[] = [
  {
    id: 'pq1',
    role: 'assistant',
    markdown: 'Witaj! Zacznijmy planowanie Twojej podróży. Dokąd chciałbyś pojechać?',
    createdAt: new Date().toISOString(),
  },
  {
    id: 'pq2',
    role: 'assistant',
    markdown: 'Jaki jest Twój budżet na tę podróż?',
    createdAt: new Date().toISOString(),
  },
  {
    id: 'pq3',
    role: 'assistant',
    markdown: 'Jakie masz preferencje dotyczące zakwaterowania i transportu?',
    createdAt: new Date().toISOString(),
  },
];

// Onboarding questions
export const onboardingQuestions: OnboardingQuestion[] = [
  {
    id: 'q1',
    markdownQuestion:
      '**Pytanie 1/4:** Jaki rodzaj podróży Cię interesuje?\n\n(Przykład: relaks na plaży, eksploracja miast, aktywność w górach, etc.)',
  },
  {
    id: 'q2',
    markdownQuestion:
      '**Pytanie 2/4:** Jaki masz budżet na tę podróż?\n\n(Przykład: ekonomiczny, średni, premium)',
  },
  {
    id: 'q3',
    markdownQuestion:
      '**Pytanie 3/4:** Kiedy planujesz wyjazd?\n\n(Przykład: lato 2025, zima 2025, elastycznie)',
  },
  {
    id: 'q4',
    markdownQuestion:
      '**Pytanie 4/4:** Z kim podróżujesz?\n\n(Przykład: sam/sama, para, rodzina z dziećmi, grupa przyjaciół)',
  },
];

// Post-attraction questions
export const postAttractionQuestions: OnboardingQuestion[] = [
  {
    id: 'pq1',
    markdownQuestion:
      '**Pytanie 1/3:** Czy posiadasz wszystkie wymagane szczepienia do tej destynacji?\n\n(Przykład: tak/nie/nie wiem)',
  },
  {
    id: 'pq2',
    markdownQuestion:
      '**Pytanie 2/3:** Czy potrzebujesz wizy do tego kraju?\n\n(Przykład: tak/nie/nie sprawdzałem)',
  },
  {
    id: 'pq3',
    markdownQuestion:
      '**Pytanie 3/3:** Czy masz już ubezpieczenie podróżne?\n\n(Przykład: tak/nie/planuję wykupić)',
  },
];

// Projects and trips - only shared projects from seed data
export const mockProjects: Project[] = (() => {
  const userId = getCurrentUserId();
  const userProjects = getSeedProjectsForUser(userId);
  
  return userProjects;
})();

export const mockTrips: Trip[] = (() => {
  // Get trips from seed data only
  const userTrips = seedTrips.filter(trip => {
    const project = seedProjects.find(p => p.id === trip.projectId);
    return project?.participants.includes(getCurrentUserId());
  });
  
  return userTrips;
})();

export const mockProjectMessages: Record<string, ChatMessage[]> = (() => {
  const messages: Record<string, ChatMessage[]> = {};
  
  // Only seed conversations (shared projects)
  Object.entries(seedConversations).forEach(([projectId, msgs]) => {
    messages[projectId] = msgs;
  });
  
  return messages;
})();

export const mockTripMessages: Record<string, ChatMessage[]> = (() => {
  const messages: Record<string, ChatMessage[]> = {
    'trip-iguana-bcn': [
    {
      id: 'iguana-msg-1',
      role: 'assistant',
      markdown: '🌟 **Welcome to Barcelona Summer Adventure!**\n\nI\'m here to help you plan an amazing trip to Barcelona. I\'ve analyzed the city and prepared some fantastic attractions for you to explore.',
      createdAt: new Date('2025-01-09T10:00:00').toISOString(),
    },
    {
      id: 'iguana-msg-2',
      role: 'user',
      userName: 'Sarah Mitchell',
      markdown: 'Hi everyone! I\'m so excited about this trip! I\'ve always wanted to see the Sagrada Familia.',
      createdAt: new Date('2025-01-09T10:15:00').toISOString(),
    },
    {
      id: 'iguana-msg-3',
      role: 'user',
      userName: 'Mark Johnson',
      markdown: 'Same here! The architecture in Barcelona is incredible. I think we should definitely include Park Güell too.',
      createdAt: new Date('2025-01-09T10:20:00').toISOString(),
    },
    {
      id: 'iguana-msg-4',
      role: 'user',
      userName: 'Emma Rodriguez',
      markdown: 'Count me in! I love the food there. Can we add some time for tapas bars on Las Ramblas?',
      createdAt: new Date('2025-01-09T10:25:00').toISOString(),
    },
    {
      id: 'iguana-msg-5',
      role: 'assistant',
      markdown: 'Great enthusiasm! I\'ve added all those attractions to your itinerary. Barcelona is perfect for mixing culture, food, and beach time.',
      createdAt: new Date('2025-01-09T10:30:00').toISOString(),
    },
    {
      id: 'iguana-msg-6',
      role: 'user',
      userName: 'Sarah Mitchell',
      markdown: 'Perfect! How many days do you think we need?',
      createdAt: new Date('2025-01-09T11:00:00').toISOString(),
    },
    {
      id: 'iguana-msg-7',
      role: 'assistant',
      markdown: 'I\'d recommend **4-5 days** to enjoy Barcelona without rushing. This gives you time for major attractions, beach relaxation, and discovering hidden gems.',
      createdAt: new Date('2025-01-09T11:05:00').toISOString(),
    },
    {
      id: 'iguana-msg-8',
      role: 'user',
      userName: 'Mark Johnson',
      markdown: 'Sounds good! I can take Friday off, so we could do Thursday to Monday. What do you all think?',
      createdAt: new Date('2025-01-09T11:15:00').toISOString(),
    },
    {
      id: 'iguana-msg-9',
      role: 'user',
      userName: 'Emma Rodriguez',
      markdown: 'Works for me! And we should definitely spend one afternoon at the beach. Barceloneta is supposed to be amazing.',
      createdAt: new Date('2025-01-09T11:20:00').toISOString(),
    },
    {
      id: 'iguana-msg-10',
      role: 'user',
      userName: 'Sarah Mitchell',
      markdown: 'Love it! Beach day is a must. I\'m also interested in the Gothic Quarter for some history.',
      createdAt: new Date('2025-01-09T11:30:00').toISOString(),
    },
    {
      id: 'iguana-msg-11',
      role: 'assistant',
      markdown: 'Excellent planning! I\'ve accepted Sagrada Familia, Park Güell, Las Ramblas, and Beach Day in your itinerary. The Gothic Quarter is included in the Las Ramblas area - perfect for an afternoon stroll.',
      createdAt: new Date('2025-01-09T11:35:00').toISOString(),
    },
  ],
  };
  
  // Merge with seed trip conversations
  Object.entries(seedTripConversations).forEach(([tripId, msgs]) => {
    messages[tripId] = msgs;
  });
  
  return messages;
})();

export const mockAttractions: Record<string, Attraction[]> = (() => {
  const attractions: Record<string, Attraction[]> = {
  'trip-iguana-bcn': [
    {
      id: 'attr-bcn-1',
      title: 'Sagrada Familia',
      description: "Gaudí's masterpiece - iconic unfinished basilica",
      category: 'Architecture',
      imageUrl: 'https://images.unsplash.com/photo-1583422409516-2895a77efded?w=600&q=80',
      rating: 3,
      status: 'rated',
    },
    {
      id: 'attr-bcn-2',
      title: 'Park Güell',
      description: 'Colorful mosaic park with stunning city views',
      category: 'Parks',
      imageUrl: 'https://images.unsplash.com/photo-1562883676-8c7feb83f09b?w=600&q=80',
      rating: 3,
      status: 'rated',
    },
    {
      id: 'attr-bcn-3',
      title: 'Las Ramblas',
      description: 'Famous tree-lined pedestrian street',
      category: 'Streets',
      imageUrl: 'https://images.unsplash.com/photo-1523531294919-4bcd7c65e216?w=600&q=80',
      rating: 2,
      status: 'rated',
    },
    {
      id: 'attr-bcn-4',
      title: 'Beach Day',
      description: 'Relax at Barceloneta Beach',
      category: 'Beach',
      imageUrl: 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=600&q=80',
      rating: 3,
      status: 'rated',
    },
  ],
  };
  
  // Merge with seed attractions
  Object.entries(seedAttractions).forEach(([tripId, attrs]) => {
    attractions[tripId] = attrs;
  });
  
  return attractions;
})();

// Special shared project (only accessible via ABC123 code)
export const specialSharedProject: Project = {
  id: 'shared-proj-abc123',
  title: 'Team Adventure - Alps Explorer',
  createdAt: new Date('2025-01-10').toISOString(),
  lastMessagePreview: 'Collaborative trip planning for the whole team',
  isShared: true,
  shareCode: 'ABC123',
  ownerId: 'other-user-123', // Not owned by current user
  hasLocationSuggestions: true, // Has location suggestions ready
};

// Special shared project with complete trip (accessible via IGUANA code)
export const iguanaSharedProject: Project = {
  id: 'shared-proj-iguana',
  title: 'Barcelona Group Trip 2025',
  createdAt: new Date('2025-01-08').toISOString(),
  lastMessagePreview: 'Group planning for Barcelona adventure',
  isShared: true,
  shareCode: 'iguana',
  ownerId: 'user-sarah-456',
};

export const iguanaTrip: Trip = {
  id: 'trip-iguana-bcn',
  projectId: 'shared-proj-iguana',
  locationId: 'loc-barcelona',
  locationName: 'Barcelona, Spain',
  title: 'Barcelona Summer Adventure',
  createdAt: new Date('2025-01-09').toISOString(),
};

export const iguanaLocation: Location = {
  id: 'loc-barcelona',
  name: 'Barcelona',
  country: 'Spain',
  teaser: 'Vibrant Mediterranean city with stunning architecture, beaches, and culture',
  imageUrl: 'https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800&q=80',
};

// Available locations
export const mockLocations: Location[] = [
  {
    id: 'loc1',
    name: 'Val Thorens',
    country: 'France',
    teaser: 'Highest ski resort in Europe with 600 km of slopes',
    imageUrl: 'https://images.unsplash.com/photo-1605540436563-5bca919ae766?w=800&q=80',
  },
  {
    id: 'loc2',
    name: 'Livigno',
    country: 'Italy',
    teaser: 'Duty-free zone in the Alps with excellent skiing conditions',
    imageUrl: 'https://images.unsplash.com/photo-1551524164-687a55dd1126?w=800&q=80',
  },
  {
    id: 'loc3',
    name: 'Sölden',
    country: 'Austria',
    teaser: 'Glacier skiing all season long, famous from Bond movies',
    imageUrl: 'https://images.unsplash.com/photo-1609137144813-7d9921338f24?w=800&q=80',
  },
];

// Trip summary template
export const getTripSummary = (attractions?: Attraction[]): TripSummary => {
  const ratedAttractions = attractions?.filter(a => a.status === 'rated' && a.rating && a.rating >= 2) || [];
  
  return {
    sections: [
      {
        category: 'Key Info',
        title: '⚠️ Most Important Information',
        markdown: `**Remember these things:**

✅ **Passport valid for at least 6 months**
✅ **Travel insurance mandatory**
✅ **Vaccinations: none required**
✅ **Visa: not required (up to 90 days)**

🚨 **Emergency numbers:**
- Emergency: 112
- Embassy: +81 3-5562-1100`,
        important: true,
        tags: ['Essential', 'Must-know'],
      },
      {
        category: 'Weather',
        title: 'Weather in March',
        markdown: `**Weather conditions:**

🌸 **Cherry blossom season (Sakura)**
- Temperature: 12-18°C (54-64°F)
- Precipitation: moderate (umbrella useful)
- Sunrise: 5:45 AM, Sunset: 5:50 PM
- Best month for sightseeing!

**What to pack:**
- Light jacket
- Layered clothing
- Umbrella`,
        tags: ['Spring', 'Sakura', 'Perfect temperature'],
      },
      {
        category: 'Flights',
        title: 'Flight Connections',
        markdown: `**Flight options:**

✈️ **1. LOT Polish Airlines** (recommended)
- Warsaw → Tokyo (Narita)
- Direct: ~11h
- Price: $650-850 round trip

✈️ **2. Turkish Airlines**
- With layover in Istanbul
- Total time: ~15h
- Price: $500-650

✈️ **3. Lufthansa**
- With layover in Frankfurt
- Total time: ~14h
- Price: $580-750

🎫 **Pro tip:** Book 2-3 months in advance for best prices`,
        tags: ['Direct flight available', 'Book early'],
      },
      {
        category: 'Hotels',
        title: 'Recommended Accommodations',
        markdown: `**Hotel options:**

🏨 **Budget ($35-60/night):**
- Capsule hotels (unique experience!)
- Hostels in Shinjuku/Shibuya
- Airbnb in residential areas

🏨 **Mid-range ($70-120/night):**
- Hotel Gracery Shinjuku (Godzilla view!)
- Cross Hotel Osaka
- Richmond Hotel Asakusa

🏨 **Luxury ($140+/night):**
- Park Hyatt Tokyo (Lost in Translation!)
- Aman Tokyo
- The Peninsula Tokyo

💡 **Tip:** Choose hotel near metro station - key to comfortable sightseeing!`,
        tags: ['Variety', 'Metro access important'],
      },
      {
        category: 'Dates',
        title: 'Best Travel Dates',
        markdown: `**Travel calendar:**

🌸 **March-April** (recommended!)
- Sakura season
- Perfect weather: 12-20°C (54-68°F)
- Higher tourist traffic
- Book in advance!

🍂 **October-November**
- Colorful fall (Momiji)
- Pleasant weather: 15-22°C (59-72°F)
- Less crowded than Sakura season

❄️ **December-February**
- Skiing in Japanese Alps
- Christmas illuminations
- Warm onsen (hot springs)

🔥 **Avoid:** July-August (hot and humid, rainy season)`,
        tags: ['Sakura season', 'Fall foliage'],
      },
      {
        category: 'Location',
        title: 'Tokyo - Capital of Japan',
        markdown: `**About the city:**

📍 **Location:** Eastern Japan, on Tokyo Bay
🏙️ **Population:** ~14 million (38 million in metro area!)
🗼 **Must-see districts:**
- **Shibuya** - famous crossing, youth fashion
- **Shinjuku** - neon lights, nightlife
- **Asakusa** - traditional district, temples
- **Harajuku** - fashion, kawaii culture
- **Ginza** - luxury shopping

⏰ **Time zone:** UTC+9 (7h ahead of GMT)`,
        tags: ['Megacity', 'Safe', 'Modern + Traditional'],
      },
      {
        category: 'Description',
        title: 'What to Expect',
        markdown: `**Tokyo is:**

🎌 **Contrast of tradition and modernity**
- Ancient temples next to skyscrapers
- Traditional tea gardens and futuristic robot cafes

🍱 **Culinary paradise**
- Most Michelin-starred restaurants in the world
- Street food: ramen, sushi, takoyaki
- Konbini (24/7 stores) with delicious food

🚄 **Perfect infrastructure**
- Metro NEVER late
- Everything ultra-clean
- High safety

🎭 **Unique experiences**
- Karaoke boxes
- Onsen (hot springs)
- Anime & manga cafes
- Gaming centers`,
      },
      {
        category: 'Transport',
        title: 'Getting Around Tokyo',
        markdown: `**Transportation system:**

🎫 **Suica Card / Pasmo** (must-have!)
- City card for metro/buses/trains
- Purchase at airport: 1000-2000 ¥
- Refill at vending machines

🚇 **Metro:**
- 13 metro lines + 10 JR lines
- Rush hours: 7:30-9:30 AM, 5:30-7:30 PM
- Google Maps ALWAYS shows best route

🚅 **JR Pass** (for longer stays)
- Unlimited JR rides for 7/14/21 days
- Worth it if planning trips outside Tokyo
- Price: ~$280 for 7 days

🚕 **Taxi:**
- Expensive! (start: ~$2.70, per km: ~$0.90)
- Use only as last resort

💡 **Pro tip:** Download offline maps in Google Maps!`,
        tags: ['Suica essential', 'Metro best option'],
      },
      {
        category: 'Budget',
        title: 'Estimated Budget (7 days)',
        markdown: `**Costs per person:**

✈️ **Flight:** $650-850
🏨 **Accommodation:** $350-700 (depending on category)
🍜 **Food:**
- Budget: $16-23/day
- Mid: $28-46/day
- Premium: $58+/day

🎫 **Attractions & transport:** $115-185
🛍️ **Shopping & souvenirs:** $70-230

**💰 TOTAL: $1,280-2,100**

💡 **How to save:**
- Eat at convenience stores (konbini)
- Free attractions: temples, parks, districts
- Happy hours at restaurants (lunch sets!)`,
        tags: ['Mid-range budget', 'Savings tips'],
      },
      {
        category: 'Packing',
        title: 'Packing List',
        markdown: `**Essential items:**

📱 **Electronics:**
- ☑️ Powerbank (long sightseeing days!)
- ☑️ Adapter (Japanese plugs: Type A/B)
- ☑️ Pocket WiFi or SIM card

👕 **Clothing (March):**
- ☑️ Light jacket/windbreaker
- ☑️ Sweaters/hoodies (layers!)
- ☑️ Comfortable walking shoes
- ☑️ Compact umbrella

💊 **Health:**
- ☑️ Basic medications (headache, stomach)
- ☑️ Vitamins
- ☑️ Insurance (copy!)

🎒 **Useful:**
- ☑️ Small bag/backpack for the day
- ☑️ Reusable water bottle
- ☑️ Powerbank
- ☑️ Cash (many places don't take cards!)

❌ **DON'T bring:**
- Large suitcase (metros have stairs!)
- Too many clothes (you'll shop there!)`,
      },
      {
        category: 'Documents',
        title: 'Required Documents',
        markdown: `**What you must have:**

✅ **Passport:**
- Validity: minimum 6 months from departure date
- Minimum 2 blank pages

✅ **Travel insurance:**
- Mandatory!
- Coverage min. $30,000
- Copy of policy on phone + printout

✅ **Boarding pass:**
- Online check-in 24h before flight
- Save on phone (Google/Apple Wallet)

✅ **Reservations:**
- Hotel confirmation (printout/PDF)
- Return ticket (may be checked at border!)

📱 **On phone:**
- Passport photo
- Reservation confirmations
- Emergency numbers
- Offline maps

💡 **Pro tip:** Make copies of everything and email to yourself!`,
        important: true,
      },
      {
        category: 'Checklist',
        title: 'Pre-flight Checklist',
        markdown: `**3 months before:**
- ☑️ Book flights
- ☑️ Book hotel
- ☑️ Check passport validity

**1 month before:**
- ☑️ Get travel insurance
- ☑️ Order Pocket WiFi/SIM card
- ☑️ Book attraction tickets (TeamLab!)
- ☑️ Exchange some money to JPY

**1 week before:**
- ☑️ Online check-in
- ☑️ Download offline maps
- ☑️ Install apps: Google Translate, Google Maps, Suica
- ☑️ Check weather forecast

**Day before:**
- ☑️ Pack luggage (max 23kg!)
- ☑️ Charge all devices
- ☑️ Print confirmations
- ☑️ Notify bank of travel

**At airport:**
- ☑️ Passport + ticket
- ☑️ Cash JPY (minimum 10,000¥)
- ☑️ Suica card (buy at Narita airport!)`,
      },
      ...(ratedAttractions.length > 0 ? [{
        category: 'Attractions' as const,
        title: '⭐ Accepted Attractions',
        markdown: ratedAttractions
          .map(a => {
            const stars = '⭐'.repeat(a.rating || 0);
            const imgTag = a.imageUrl ? `\n![${a.title}](${a.imageUrl})` : '';
            return `### ${a.title} ${stars}\n${a.description}${a.category ? ` *(${a.category})*` : ''}${imgTag}`;
          })
          .join('\n\n---\n\n'),
        tags: ['Personalized', 'Your picks'],
      }] : []),
    ],
  };
};

// Helper function to update user
export function updateMockUser(updates: Partial<User>) {
  mockUser = { ...mockUser, ...updates };
}
