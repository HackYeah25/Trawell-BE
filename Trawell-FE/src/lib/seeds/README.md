# 🌱 Seed Data - Mock Users & Projects

This directory contains comprehensive mock data for development and testing, including **3 complete user profiles** with realistic conversations and shared projects.

---

## 👥 Seed Users

### 1. **Anna Kowalska** (`user-anna-001`)
- **Email:** anna@example.com
- **Persona:** Adrenaline Explorer - Górska Pasjonatka
- **Travel Style:** Explorer, high activity level
- **Preferences:** 
  - Mountains & trekking
  - Hostels/budget accommodations
  - Vegetarian
  - Culture-focused
- **Past Trips:** Nepal (Everest Base Camp), Patagonia, Iceland
- **Wishlist:** New Zealand, Norway, Alaska

### 2. **Tomasz Nowak** (`user-tomasz-002`)
- **Email:** tomasz@example.com
- **Persona:** Luxury Beach Relaxer - Smakosz Spokoju
- **Travel Style:** Relaxer, low activity level
- **Preferences:**
  - Beaches & all-inclusive resorts
  - Tropical climates
  - Foodie (no dietary restrictions)
  - Prefers minimal physical effort
- **Past Trips:** Maldives, Zanzibar, Bali
- **Wishlist:** Caribbean, Mauritius, Thailand

### 3. **Maria Wiśniewska** (`user-maria-003`)
- **Email:** maria@example.com
- **Persona:** Urban Culture Enthusiast - Miejska Esteta
- **Travel Style:** Mixed, medium activity level
- **Preferences:**
  - European cities & culture
  - Boutique hotels
  - Foodie (gluten-free)
  - Architecture & local cuisine
- **Past Trips:** Lisbon, Barcelona, Budapest
- **Wishlist:** Japan, Porto, Greece

---

## 🗂️ Shared Projects

### **Alpine Adventure 2025** (`ALPS2025`)
- **Participants:** Anna, Tomasz, Maria
- **Destination:** Dolomites, Italy (Cortina d'Ampezzo)
- **Status:** Planning phase - accommodation & dates confirmed
- **Budget:** ~2600 PLN/person (7 days)
- **Highlights:** Via ferratas for Anna, gondola rides for Tomasz, local cuisine for Maria
- **Messages:** 21 realistic group chat messages with debates about activities, budget, and compromises

### **Japan Dream Trip** (`JPNDREAM`)
- **Participants:** Anna, Maria
- **Route:** Tokyo → Kyoto → Hakone → Takayama
- **Status:** Active - Tokyo trip created with attractions
- **Duration:** 14 days
- **Highlights:** Culture (Maria), hiking in Japanese Alps (Anna), onsen, ramen tour
- **Messages:** 13 messages planning the route + separate Tokyo trip chat
- **Trips:**
  - **Tokyo** - 5 days with attractions (Sensō-ji, teamLab Borderless, Tsukiji Market)

### **Caribbean Escape** (`CARIBBEAN`)
- **Participants:** Tomasz (solo)
- **Status:** Early planning - seeking all-inclusive options
- **Highlights:** Beach relaxation, luxury resorts, minimal activities

---

## 📁 File Structure

```
src/lib/seeds/
├── README.md                           # This file
├── users.json                          # 3 complete user profiles with preferences
├── shared-projects.json                # Shared projects metadata
├── conversations/
│   ├── project-alpine-2025.json       # 21 group messages (Anna, Tomasz, Maria)
│   ├── project-japan-dream.json       # 13 planning messages (Anna, Maria)
│   └── trip-tokyo.json                # 13 trip-specific messages with attractions
└── index.ts                            # TypeScript exports
```

---

## 🔧 Usage in Development

### Switch Active User (Dev Mode)
```javascript
// In browser console:
window.__switchUser('user-anna-001')    // Anna Kowalska
window.__switchUser('user-tomasz-002')  // Tomasz Nowak
window.__switchUser('user-maria-003')   // Maria Wiśniewska
```

### Import Seed Data
```typescript
import { seedUsers, seedProjects } from '@/lib/seeds';

// Get specific user
const anna = seedUsers.find(u => u.id === 'user-anna-001');

// Get shared projects
const alpineProject = seedProjects.find(p => p.shareCode === 'ALPS2025');
```

---

## 🎭 Conversation Highlights

### Alpine Adventure (Group Chat)
- **Conflict & Resolution:** Anna wants extreme activities, Tomasz prefers relaxation, Maria mediates
- **Budget Comparison:** Switzerland vs. Dolomites analysis
- **Compromise:** Via ferratas for Anna + gondola rides for Tomasz + local culture for Maria

### Japan Dream Trip
- **Collaborative Planning:** Anna and Maria with shared interests in culture + nature
- **Detailed Itinerary:** Tokyo → Kyoto → Hakone → Takayama (14 days)
- **Attractions:** Accepted attractions in Tokyo trip (Sensō-ji, teamLab, Tsukiji Market)

---

## 🧪 Testing Scenarios

### Group Dynamics
- **Alpine Adventure:** Test multi-user conversations with different preferences
- **Japan Dream:** Test two-person planning with shared interests

### User Personas
- **Anna:** High-energy explorer → Test activity-heavy suggestions
- **Tomasz:** Luxury relaxer → Test comfort-focused recommendations
- **Maria:** Culture enthusiast → Test urban/foodie suggestions

### Share Codes
```
ALPS2025    → Alpine Adventure 2025
JPNDREAM    → Japan Dream Trip  
CARIBBEAN   → Caribbean Escape
```

---

## 📊 Data Statistics

- **Total Users:** 3
- **Total Shared Projects:** 3
- **Total Messages:** 47 (21 + 13 + 13)
- **Total Trips:** 1 (Tokyo)
- **Total Attractions:** 6 (in Tokyo trip)
- **Profile Completeness:** 88-95%

---

## 🚀 Future Enhancements

- [ ] Add more trips (Kyoto, Hakone, Takayama)
- [ ] Add attraction decisions (accept/reject) for Alpine project
- [ ] Add project location suggestions (Dolomites details)
- [ ] Add user avatars (different colors based on hash)
- [ ] Add timestamps across multiple weeks for realistic history
