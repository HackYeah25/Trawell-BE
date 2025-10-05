# TravelAI - Travel Planning App MVP

Modern web application for trip planning with AI assistant, chat, and project management.

## 🚀 Features

### ✅ One-time Onboarding
- Chat with 4 questions about travel preferences
- Automatic creation of first project
- Intelligent answer validation with clarification option

### ✅ Travel Projects
- Chat-first interface for refining requirements
- Location proposals from AI
- Creating multiple trips from one project

### ✅ Detailed Trips
- Interactive chat for specific location
- Attractions panel with accept/reject options
- Comprehensive summary (weather, safety, budget, transport, etc.)

### ✅ Responsive Design
- Mobile-first approach
- Ocean/sunset gradient theme
- Smooth animations and transitions
- Dark mode ready

### ✅ Accessibility
- WCAG 2.2 AA compliance
- Aria-live for chat
- Focus states and keyboard navigation
- Screen reader friendly

## 🛠️ Technology Stack

- **React 18** + **TypeScript** + **Vite**
- **React Router** - routing
- **TanStack Query (React Query)** - data fetching & caching
- **Zustand** - lightweight UI state
- **Tailwind CSS** - styling with custom design system
- **shadcn/ui** + **Radix UI** - accessible components
- **react-markdown** + **remark-gfm** - markdown rendering
- **MSW (Mock Service Worker)** - mock backend for development

## 📦 Installation and Running

```bash
# Install dependencies
npm install

# Run dev server (with mock backend)
npm run dev

# Production build
npm run build

# Preview build
npm run preview
```

The app will be available at: http://localhost:8080

## 🎨 Design System

### Colors
- **Primary (Ocean Blue):** HSL(210, 85%, 42%) - main brand color
- **Accent (Coral/Sunset):** HSL(16, 85%, 60%) - accents and CTA
- **Success:** HSL(142, 71%, 45%) - positive actions
- **Gradients:** ocean, sunset, sky - for hero sections and cards

### Components
All styles are defined in the design system (`index.css` + `tailwind.config.ts`).
**Never** use ad-hoc classes like `text-white` or `bg-blue-500`.

## 📁 Project Structure

```
src/
├── api/
│   └── hooks/          # React Query hooks for API
├── components/
│   ├── ui/             # shadcn/ui components
│   ├── chat/           # ChatThread, ChatMessage, Composer
│   ├── trips/          # AttractionsPanel, SummaryCard
│   └── layout/         # AppShell, Navigation
├── pages/
│   ├── Onboarding.tsx  # 4 onboarding questions
│   ├── History.tsx     # List of projects and trips
│   ├── ProjectView.tsx # Project chat + locations
│   └── TripView.tsx    # Trip chat + attractions + summary
├── mocks/
│   ├── handlers.ts     # MSW request handlers
│   └── browser.ts      # MSW setup
├── store/
│   └── ui-store.ts     # Zustand store for UI state
├── types/
│   └── index.ts        # TypeScript types
└── lib/
    ├── api-client.ts   # Fetch wrapper with error handling
    └── utils.ts        # Utilities (cn, etc.)
```

## 🔌 Integration with Real Backend

1. **Set environment variable:**
   ```bash
   VITE_API_URL=https://your-backend.com/api
   ```

2. **Disable MSW in production:**
   Mock Service Worker is automatically disabled in production builds.

3. **API Contract:**
   Backend must implement endpoints described in `src/mocks/handlers.ts`:
   - GET/PATCH `/me`
   - GET `/onboarding/questions`
   - POST `/onboarding/answer`, `/onboarding/complete`
   - CRUD for `/projects` and `/trips`
   - Attractions and summaries

## 🛠️ Developer Mode

For faster development and testing, the application includes a developer mode that provides a skip button in the onboarding process:

### **Enable Developer Mode:**
```javascript
// In browser console:
localStorage.setItem('TRAWELL_DEV_MODE', 'true');
// Refresh the page - Skip button will appear in onboarding header
```

### **Disable Developer Mode:**
```javascript
// In browser console:
localStorage.removeItem('TRAWELL_DEV_MODE');
// or
localStorage.setItem('TRAWELL_DEV_MODE', 'false');
```

### **Features in Developer Mode:**
- ✅ **Skip button visible** - Shows "Skip" button in onboarding header
- ✅ **Manual skip** - Click "Skip" to bypass profiling questions
- ✅ **Direct access to app** - Goes straight to project creation
- ✅ **Production safe** - Only works when explicitly enabled

### **Production Behavior:**
- ❌ No skip button visible to users
- ✅ Normal onboarding flow for all users

## 🧪 Acceptance Tests (Checklist)

- [x] New user lands on onboarding after login
- [x] 4 questions with clarification option
- [x] Automatic project creation after completion
- [x] Creating trips from proposed locations
- [x] Accept/reject attractions with optimistic updates
- [x] Display summary cards in 10 categories
- [x] Mobile/desktop responsiveness
- [x] Keyboard and screen reader accessibility

## 🌍 i18n (Future)

Application is ready for internationalization:
- All texts are in variables (easy to extract)
- Structure supports translations
- MVP: English language version

## 📝 Notes

- **Error Handling:** All API calls have retry (2x), error states, and toasts
- **Loading States:** Skeletons, spinners, optimistic updates
- **Accessibility:** Aria-labels, focus management, semantic HTML
- **Performance:** React Query caching, lazy loading, code splitting ready

## 🌱 Mock Data & Seed Users

The application contains **3 complete user profiles** for testing group conversations:

### User Accounts

**1. Anna Kowalska** (Mountain Explorer)
- **Email:** anna@example.com
- **Password:** password123
- **Profile:** Adventure seeker, loves trekking and mountains
- **Preferences:** High activity, hostels, vegetarian
- **Past trips:** Nepal Himalayas, Patagonia, Iceland

**2. Tomasz Nowak** (Beach Relaxer)
- **Email:** tomasz@example.com
- **Password:** password123
- **Profile:** Luxury beach vacationer, loves relaxation
- **Preferences:** Low activity, all-inclusive, foodie
- **Past trips:** Maldives, Zanzibar, Bali

**3. Maria Wiśniewska** (Culture Enthusiast)
- **Email:** maria@example.com
- **Password:** password123
- **Profile:** Urban explorer, architecture and food lover
- **Preferences:** Medium activity, boutique hotels, gluten-free
- **Past trips:** Lisbon, Barcelona, Budapest

### Shared Projects

- **Alpine Adventure 2025** - Share code: `ALPS2025` (All 3 users)
- **Japan Dream Trip** - Share code: `JPNDREAM` (Anna & Maria)
- **Caribbean Escape** - Share code: `CARIBBEAN` (Tomasz only)

### Change User (Dev Mode)

```js
window.__switchUser('user-anna-001')   // Anna
window.__switchUser('user-tomasz-002') // Tomasz  
window.__switchUser('user-maria-003')  // Maria
```

📁 Details: `src/lib/seeds/README.md`

## 🎯 Roadmap

- [ ] Integration with real AI backend
- [ ] Export trips to PDF
- [ ] Share trips with other users
- [ ] Calendar and bookings
- [ ] Interactive map
- [ ] Multi-language support

---

**Author:** Generated by Lovable AI  
**License:** MIT  
**Contact:** Add your contact details
