# Frontend Implementation Guide - Logistics Cards

## Overview
This guide provides instructions for implementing the logistics cards feature in the Trawell frontend. The backend now sends logistics data (flights, hotels, weather) via WebSocket that should be displayed as mini cards at the start of the planning conversation.

## Backend Changes Completed ✅
- ✅ Database migration with new columns
- ✅ WebSocket sends `logistics_data` message type
- ✅ Planning agent has logistics context
- ✅ Trip summary endpoint includes logistics

## Frontend Tasks Required

### 1. Update WebSocket Message Handler

**File to modify:** `src/api/hooks/use-brainstorm.ts` or equivalent planning hook

Add handler for new message type:

```typescript
// In your WebSocket message handler
switch (message.type) {
  // ... existing cases
  
  case 'logistics_data':
    handleLogisticsData(message.data);
    break;
}
```

### 2. Create Type Definitions

**File:** `src/types/logistics.ts` (new file)

```typescript
export interface FlightSegment {
  from: string;
  to: string;
  departureAt: string;
  arrivalAt: string;
  duration: string;
}

export interface FlightItinerary {
  totalDuration: string;
  segments: FlightSegment[];
}

export interface FlightLeg {
  price: string;
  currency: string;
  itinerary: FlightItinerary;
}

export interface Flights {
  outbound?: FlightLeg;
  return?: FlightLeg;
}

export interface Hotel {
  name: string;
  price: string;
  currency: string;
  checkInDate: string;
  checkOutDate: string;
}

export interface Weather {
  summary?: string;
  forecast?: any; // Define based on actual weather API response
}

export interface LogisticsData {
  url?: string;
  flights?: Flights;
  hotels?: Hotel[];
  weather?: Weather;
}
```

### 3. Create Logistics Card Components

#### A. Flight Card Component

**File:** `src/components/planning/FlightCard.tsx`

```typescript
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Plane } from 'lucide-react';
import { Flights } from '@/types/logistics';

interface FlightCardProps {
  flights: Flights;
}

export function FlightCard({ flights }: FlightCardProps) {
  const { outbound, return: returnFlight } = flights;
  
  if (!outbound) return null;

  return (
    <Card className="mb-4 border-blue-200 bg-blue-50">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Plane className="h-5 w-5 text-blue-600" />
          Flight Options
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Outbound Flight */}
          <div className="rounded-md bg-white p-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {outbound.itinerary.segments[0]?.from} → {outbound.itinerary.segments[outbound.itinerary.segments.length - 1]?.to}
                </p>
                <p className="text-xs text-gray-500">
                  {outbound.itinerary.totalDuration}
                </p>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-blue-600">
                  {outbound.price} {outbound.currency}
                </p>
                <p className="text-xs text-gray-500">Outbound</p>
              </div>
            </div>
          </div>

          {/* Return Flight */}
          {returnFlight && (
            <div className="rounded-md bg-white p-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {returnFlight.itinerary.segments[0]?.from} → {returnFlight.itinerary.segments[returnFlight.itinerary.segments.length - 1]?.to}
                  </p>
                  <p className="text-xs text-gray-500">
                    {returnFlight.itinerary.totalDuration}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-blue-600">
                    {returnFlight.price} {returnFlight.currency}
                  </p>
                  <p className="text-xs text-gray-500">Return</p>
                </div>
              </div>
            </div>
          )}

          {/* Total */}
          <div className="border-t pt-2">
            <div className="flex justify-between">
              <p className="text-sm font-medium">Total Flight Cost:</p>
              <p className="text-sm font-bold">
                {(parseFloat(outbound.price) + (returnFlight ? parseFloat(returnFlight.price) : 0)).toFixed(2)} {outbound.currency}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

#### B. Hotels Card Component

**File:** `src/components/planning/HotelsCard.tsx`

```typescript
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Hotel as HotelIcon } from 'lucide-react';
import { Hotel } from '@/types/logistics';

interface HotelsCardProps {
  hotels: Hotel[];
}

export function HotelsCard({ hotels }: HotelsCardProps) {
  if (!hotels || hotels.length === 0) return null;

  // Show top 3 hotels
  const topHotels = hotels.slice(0, 3);

  return (
    <Card className="mb-4 border-purple-200 bg-purple-50">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <HotelIcon className="h-5 w-5 text-purple-600" />
          Accommodation Options
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {topHotels.map((hotel, index) => (
            <div 
              key={index}
              className="rounded-md bg-white p-3 hover:shadow-sm transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    {hotel.name}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {hotel.checkInDate} → {hotel.checkOutDate}
                  </p>
                </div>
                <div className="text-right ml-3">
                  <p className="text-base font-bold text-purple-600">
                    {hotel.price} {hotel.currency}
                  </p>
                  <p className="text-xs text-gray-500">Total</p>
                </div>
              </div>
            </div>
          ))}
          
          {hotels.length > 3 && (
            <p className="text-xs text-gray-500 text-center pt-2">
              +{hotels.length - 3} more options available
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

#### C. Weather Card Component

**File:** `src/components/planning/WeatherCard.tsx`

```typescript
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Cloud } from 'lucide-react';
import { Weather } from '@/types/logistics';

interface WeatherCardProps {
  weather: Weather;
  destination?: string;
}

export function WeatherCard({ weather, destination }: WeatherCardProps) {
  if (!weather || Object.keys(weather).length === 0) return null;

  return (
    <Card className="mb-4 border-amber-200 bg-amber-50">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Cloud className="h-5 w-5 text-amber-600" />
          Weather Forecast
          {destination && <span className="text-sm font-normal text-gray-600">for {destination}</span>}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md bg-white p-3">
          <p className="text-sm text-gray-700">
            {weather.summary || 'Weather information available for your planning.'}
          </p>
          {/* Add more weather details based on your weather API response structure */}
        </div>
      </CardContent>
    </Card>
  );
}
```

#### D. Container Component

**File:** `src/components/planning/LogisticsCards.tsx`

```typescript
import React from 'react';
import { FlightCard } from './FlightCard';
import { HotelsCard } from './HotelsCard';
import { WeatherCard } from './WeatherCard';
import { LogisticsData } from '@/types/logistics';

interface LogisticsCardsProps {
  logistics: LogisticsData;
  destinationName?: string;
}

export function LogisticsCards({ logistics, destinationName }: LogisticsCardsProps) {
  const { flights, hotels, weather } = logistics;

  // Don't render anything if no data
  if (!flights && !hotels && !weather) {
    return null;
  }

  return (
    <div className="space-y-4 my-6">
      <div className="flex items-center gap-2 mb-4">
        <div className="h-px flex-1 bg-gray-200" />
        <p className="text-sm text-gray-500 font-medium">Trip Details</p>
        <div className="h-px flex-1 bg-gray-200" />
      </div>
      
      {flights && <FlightCard flights={flights} />}
      {hotels && <HotelsCard hotels={hotels} />}
      {weather && <WeatherCard weather={weather} destination={destinationName} />}
    </div>
  );
}
```

### 4. Integrate into Planning Page

**File to modify:** `src/pages/ProjectView.tsx` or equivalent

```typescript
import { LogisticsCards } from '@/components/planning/LogisticsCards';
import { LogisticsData } from '@/types/logistics';

// Add to component state
const [logisticsData, setLogisticsData] = useState<LogisticsData | null>(null);

// In your WebSocket message handler
const handleWebSocketMessage = (message: any) => {
  switch (message.type) {
    case 'logistics_data':
      setLogisticsData(message.data);
      break;
    // ... other cases
  }
};

// In your render/return
return (
  <div>
    {/* Existing planning UI */}
    
    {/* Add logistics cards before chat messages */}
    {logisticsData && (
      <LogisticsCards 
        logistics={logisticsData}
        destinationName={recommendation?.destination?.name}
      />
    )}
    
    {/* Chat messages */}
    {messages.map(msg => ...)}
  </div>
);
```

### 5. Styling Recommendations

Use Tailwind classes for consistent styling:

```css
/* Card colors */
- Flights: blue-50, blue-200, blue-600
- Hotels: purple-50, purple-200, purple-600
- Weather: amber-50, amber-200, amber-600

/* Layout */
- Cards: mb-4 for spacing
- Content: p-3 rounded-md bg-white
- Hover: hover:shadow-sm transition-shadow
```

### 6. Responsive Design

Ensure cards work on mobile:

```typescript
// Use responsive Tailwind classes
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* On mobile: stack vertically */}
  {/* On tablet: 2 columns */}
  {/* On desktop: 3 columns (or keep stacked for better UX) */}
</div>
```

### 7. Loading States

Add loading states while waiting for logistics data:

```typescript
const [isLoadingLogistics, setIsLoadingLogistics] = useState(true);

// When logistics_data received
setLogisticsData(message.data);
setIsLoadingLogistics(false);

// In render
{isLoadingLogistics && (
  <div className="flex items-center justify-center py-8">
    <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
    <p className="ml-2 text-sm text-gray-500">Loading trip details...</p>
  </div>
)}
```

### 8. Error Handling

Handle missing or incomplete data gracefully:

```typescript
// Each card component should handle missing data
if (!data || Object.keys(data).length === 0) {
  return null; // Don't render empty cards
}

// For arrays
if (!hotels || hotels.length === 0) {
  return null;
}
```

### 9. Testing Checklist

- [ ] WebSocket receives `logistics_data` message
- [ ] Cards render with real data
- [ ] Cards handle missing data gracefully
- [ ] Cards are responsive on mobile/tablet/desktop
- [ ] Prices format correctly
- [ ] Dates display in user-friendly format
- [ ] Loading states work
- [ ] Cards appear before first AI message
- [ ] Multiple hotels display correctly
- [ ] Flight segments display route clearly

### 10. Optional Enhancements

Consider adding:
- Click to expand for more details
- Share button to copy logistics to clipboard
- Export to PDF/calendar
- Price comparison visualization
- Map view for hotels
- Calendar integration for flights
- Booking links (future)

## API Response Examples

### logistics_data Message
```json
{
  "type": "logistics_data",
  "recommendation_id": "rec_123",
  "data": {
    "url": "https://places.googleapis.com/...",
    "flights": {
      "outbound": {
        "price": "196.89",
        "currency": "EUR",
        "itinerary": {
          "totalDuration": "6h 3m",
          "segments": [
            {
              "from": "JFK",
              "to": "LAX",
              "departureAt": "2025-10-08T11:37:00",
              "arrivalAt": "2025-10-08T14:40:00",
              "duration": "6h 3m"
            }
          ]
        }
      },
      "return": {
        "price": "64.66",
        "currency": "EUR",
        "itinerary": {
          "totalDuration": "5h 38m",
          "segments": [
            {
              "from": "LAX",
              "to": "JFK",
              "departureAt": "2025-10-21T20:52:00",
              "arrivalAt": "2025-10-22T05:30:00",
              "duration": "5h 38m"
            }
          ]
        }
      }
    },
    "hotels": [
      {
        "name": "HOLIDAY INN EXP DOWNTOWN WEST",
        "price": "2825.07",
        "currency": "USD",
        "checkInDate": "2025-10-08",
        "checkOutDate": "2025-10-21"
      },
      {
        "name": "Courtyard by Marriott Los Angeles L.A. LIVE",
        "price": "3879.86",
        "currency": "USD",
        "checkInDate": "2025-10-08",
        "checkOutDate": "2025-10-21"
      }
    ],
    "weather": {
      "summary": "Sunny with temperatures 20-28°C"
    }
  }
}
```

## Questions or Issues?

1. Check backend docs:
   - `/Trawell-BE/docs/adr/add-logistics-data-to-planning.md`
   - `/LOGISTICS_INTEGRATION_SUMMARY.md`
   - `/Trawell-BE/docs/LOGISTICS_DATA_FLOW.md`

2. Verify WebSocket connection is working
3. Check browser console for message types
4. Test with different destinations

## Commit Message Template

```
feat(planning): Add logistics cards for flights, hotels, and weather

- Add LogisticsCards component with sub-components
- Update WebSocket handler for logistics_data message type
- Add TypeScript types for logistics data
- Implement responsive design for cards
- Add loading and error states

Implements frontend for logistics data integration as part of
trip planning enhancement. Backend changes completed in previous commit.
```
