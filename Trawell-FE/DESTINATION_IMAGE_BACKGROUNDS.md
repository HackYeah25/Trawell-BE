# Destination Image Backgrounds - Frontend Implementation

## Overview
Backend now provides destination photo URLs (`url` field) from Google Places API. These images should be used as gradient-overlayed backgrounds in three key locations.

## Backend Changes Completed ✅

### API Endpoints Updated
Both recommendation endpoints now include `url` field:

1. **GET `/brainstorm/recommendations`** - List of recommendations
2. **GET `/brainstorm/recommendations/{recommendation_id}`** - Single recommendation

Response includes:
```json
{
  "recommendation_id": "rec_xxx",
  "destination": {...},
  "url": "https://places.googleapis.com/v1/places/...",
  "flights": {...},
  "hotels": [...],
  "weather": {...}
}
```

## Frontend Implementation Required

### 1. 🎨 Planning Panel Background (TripView)

**Location:** `/app/trips/{tripId}` page  
**File:** `src/pages/TripView.tsx`  
**Component:** Main container

#### Design Specification:
- Full-width background image at top of planning panel
- Gradient overlay from top (dark) fading to transparent
- Header content overlaid on image (title, status, etc.)
- ~40-50vh height recommended

#### Implementation:

```tsx
// src/pages/TripView.tsx

export default function TripView() {
  const { tripId } = useParams<{ tripId: string }>();
  const { data: trip } = useTrip(tripId!);
  
  // Get image URL from trip data
  const destinationImageUrl = trip?.url || trip?.imageUrl;

  return (
    <AppShell>
      <div className="h-screen flex flex-col">
        {/* Hero Section with Background Image */}
        <div 
          className="relative h-[40vh] bg-cover bg-center"
          style={{
            backgroundImage: destinationImageUrl 
              ? `url(${destinationImageUrl})` 
              : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          }}
        >
          {/* Gradient Overlay - Dark to Transparent */}
          <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/40 to-transparent" />
          
          {/* Content over image */}
          <div className="relative z-10 h-full flex flex-col justify-end p-6 text-white">
            <div className="max-w-4xl mx-auto w-full">
              <h1 className="text-4xl font-bold mb-2">
                {trip?.title || 'Planning Your Trip'}
              </h1>
              <p className="text-lg text-white/90 mb-4">
                {trip?.destination}
              </p>
              
              {/* Status badges, dates, etc. */}
              <div className="flex gap-3 items-center">
                <Badge variant="secondary" className="bg-white/20 backdrop-blur-sm">
                  {trip?.status}
                </Badge>
                {trip?.dates && (
                  <span className="text-sm text-white/80">
                    {formatDateRange(trip.dates)}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Chat/Planning Content Below */}
        <div className="flex-1 overflow-hidden bg-white">
          {/* Your existing chat/planning UI */}
        </div>
      </div>
    </AppShell>
  );
}
```

#### Alternative: Blurred Background
```tsx
<div 
  className="relative h-[40vh]"
>
  {/* Blurred background layer */}
  <div 
    className="absolute inset-0 bg-cover bg-center filter blur-sm scale-105"
    style={{
      backgroundImage: destinationImageUrl 
        ? `url(${destinationImageUrl})` 
        : undefined
    }}
  />
  
  {/* Dark overlay */}
  <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/30 to-transparent" />
  
  {/* Content */}
  <div className="relative z-10 h-full p-6">
    {/* ... */}
  </div>
</div>
```

---

### 2. 📸 Trip Gallery Cards (TripGallery)

**Location:** `/app/trips` page  
**File:** `src/pages/TripGallery.tsx`  
**Component:** Trip cards in grid/list view

#### Design Specification:
- Card background shows destination image
- Gradient overlay for text readability
- Hover effect reveals more details
- Consistent card height (200-250px)

#### Current Issue:
Line 42 uses `rec.destination?.imageUrl` but should use `rec.url`

#### Implementation:

```tsx
// src/pages/TripGallery.tsx

export default function TripGallery() {
  // ... existing code ...

  // Combine trips and recommendations
  const allTrips = [
    ...(trips || []).map(trip => ({
      id: trip.id,
      title: trip.title,
      locationName: trip.locationName || trip.destination,
      imageUrl: trip.imageUrl || trip.url, // Support both fields
      createdAt: trip.createdAt,
      type: 'trip' as const,
      rating: undefined,
    })),
    ...(recommendations?.recommendations || []).map((rec: any) => ({
      id: rec.recommendation_id,
      title: rec.destination?.name || rec.destination?.city || 'Trip',
      locationName: rec.destination?.city || rec.destination?.name || 'Unknown',
      imageUrl: rec.url, // ✅ FIXED: Use rec.url instead of rec.destination?.imageUrl
      createdAt: rec.created_at,
      type: 'recommendation' as const,
      rating: rec.destination?.rating,
    })),
  ];

  // ... rest of component ...

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {filteredTrips.map((trip) => (
        <TripCard
          key={trip.id}
          trip={trip}
          onView={() => handleViewTrip(trip.id, trip.type)}
        />
      ))}
    </div>
  );
}
```

#### Trip Card Component:

```tsx
// src/components/trips/TripCard.tsx (new or update existing)

interface TripCardProps {
  trip: {
    id: string;
    title: string;
    locationName: string;
    imageUrl?: string;
    createdAt: string;
    rating?: number;
  };
  onView: () => void;
}

export function TripCard({ trip, onView }: TripCardProps) {
  return (
    <Card 
      className="group cursor-pointer overflow-hidden hover:shadow-xl transition-all duration-300"
      onClick={onView}
    >
      {/* Image Background with Gradient */}
      <div className="relative h-48 bg-gradient-to-br from-warm-coral/20 to-warm-turquoise/20">
        {trip.imageUrl ? (
          <>
            {/* Background Image */}
            <div 
              className="absolute inset-0 bg-cover bg-center transition-transform duration-300 group-hover:scale-105"
              style={{ backgroundImage: `url(${trip.imageUrl})` }}
            />
            
            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
          </>
        ) : (
          // Fallback gradient if no image
          <div className="absolute inset-0 bg-gradient-to-br from-warm-coral via-warm-sand to-warm-turquoise opacity-70" />
        )}

        {/* Content Overlay */}
        <div className="relative h-full flex flex-col justify-end p-4 text-white">
          <h3 className="text-xl font-bold mb-1 line-clamp-2">
            {trip.title}
          </h3>
          <p className="text-sm text-white/80 flex items-center gap-1">
            <MapPin className="h-3 w-3" />
            {trip.locationName}
          </p>
        </div>

        {/* Rating Badge (if available) */}
        {trip.rating && (
          <div className="absolute top-3 right-3 bg-black/60 backdrop-blur-sm rounded-full px-3 py-1 flex items-center gap-1">
            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm font-medium text-white">
              {trip.rating}
            </span>
          </div>
        )}
      </div>

      {/* Card Footer (optional additional info) */}
      <CardContent className="p-4">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>Created {formatDate(trip.createdAt)}</span>
          <ChevronRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
        </div>
      </CardContent>
    </Card>
  );
}
```

---

### 3. ⭐ Location Proposal Card (Brainstorm Rating)

**Location:** Brainstorm session when rating destinations  
**File:** `src/components/projects/LocationProposalCard.tsx`  
**Component:** Rating card with stars

#### Design Specification:
- Background image visible behind card content
- Gradient overlay for readability
- Stars and content remain visible
- Image doesn't interfere with interaction

#### Implementation:

```tsx
// src/components/projects/LocationProposalCard.tsx

interface LocationProposalCardProps {
  location: LocationProposal;
  onDecision: (decision: 'reject' | 1 | 2 | 3) => void;
}

export function LocationProposalCard({ location, onDecision }: LocationProposalCardProps) {
  const isRated = location.status === 'rated' && location.rating;
  const isRejected = location.status === 'rejected';
  const isDisabled = isRated || isRejected;

  return (
    <Card className="relative overflow-hidden group">
      {/* Background Image Layer */}
      {location.imageUrl && (
        <>
          <div 
            className="absolute inset-0 bg-cover bg-center opacity-20 transition-opacity group-hover:opacity-30"
            style={{ 
              backgroundImage: `url(${location.imageUrl})`,
              filter: 'blur(3px)' // Subtle blur so text is readable
            }}
          />
          
          {/* Gradient Overlay for Readability */}
          <div className="absolute inset-0 bg-gradient-to-b from-white/95 via-white/90 to-white/95" />
        </>
      )}

      {/* Content - Always on top */}
      <div className="relative z-10">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <CardTitle className="text-xl mb-2">{location.name}</CardTitle>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span>{location.country}</span>
              </div>
            </div>

            {/* Rating Badge */}
            {isRated && (
              <Badge 
                variant="secondary" 
                className="bg-warm-turquoise/10 text-warm-turquoise border-warm-turquoise/20"
              >
                {location.rating}★
              </Badge>
            )}
            {isRejected && (
              <Badge variant="secondary" className="bg-muted">
                Rejected
              </Badge>
            )}
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Description */}
          <p className="text-sm text-muted-foreground line-clamp-3">
            {location.description}
          </p>

          {/* Rating Buttons */}
          <div className="grid grid-cols-4 gap-2 pt-3">
            <Button
              variant="outline"
              size="sm"
              disabled={isDisabled}
              onClick={() => onDecision('reject')}
              className={cn(
                'flex-col gap-1 h-auto py-2 relative z-20',
                isRejected && 'bg-muted'
              )}
            >
              <X className="h-4 w-4" />
              <span className="text-xs hidden sm:inline">Odrzuć</span>
            </Button>

            {[1, 2, 3].map((stars) => (
              <Button
                key={stars}
                variant="outline"
                size="sm"
                disabled={isDisabled}
                onClick={() => onDecision(stars as 1 | 2 | 3)}
                className={cn(
                  'flex-col gap-1 h-auto py-2 relative z-20',
                  isRated && location.rating === stars && 
                  'bg-warm-turquoise/10 border-warm-turquoise text-warm-turquoise'
                )}
              >
                <Star className={cn(
                  'h-4 w-4',
                  isRated && location.rating === stars && 'fill-warm-turquoise'
                )} />
                <span className="text-xs hidden sm:inline">{stars}★</span>
              </Button>
            ))}
          </div>
        </CardContent>
      </div>
    </Card>
  );
}
```

#### Alternative: Side Image Layout
```tsx
<Card className="relative overflow-hidden">
  <div className="grid md:grid-cols-[200px_1fr] gap-0">
    {/* Left: Image */}
    <div className="relative h-48 md:h-auto">
      {location.imageUrl ? (
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${location.imageUrl})` }}
        />
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-warm-coral to-warm-turquoise opacity-30" />
      )}
    </div>

    {/* Right: Content */}
    <div className="p-4">
      <CardTitle>{location.name}</CardTitle>
      {/* ... rest of content ... */}
    </div>
  </div>
</Card>
```

---

## Data Flow

```
Backend API
    ↓
Fetches url from Google Places API
    ↓
Stores in destination_recommendations.url
    ↓
Returns in API responses:
  - /brainstorm/recommendations (list)
  - /brainstorm/recommendations/:id (single)
    ↓
Frontend receives url field
    ↓
Three implementations:
    ├─ TripView: Hero background with gradient
    ├─ TripGallery: Card backgrounds  
    └─ LocationProposalCard: Subtle background
```

## Image Optimization Best Practices

### 1. Lazy Loading
```tsx
<div 
  className="bg-cover bg-center"
  style={{ 
    backgroundImage: `url(${imageUrl})`,
    loading: 'lazy' // Browser hint
  }}
/>
```

### 2. Fallback Gradients
Always provide a fallback if image fails to load:
```tsx
style={{
  backgroundImage: imageUrl 
    ? `url(${imageUrl})` 
    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
}}
```

### 3. Loading State
```tsx
const [imageLoaded, setImageLoaded] = useState(false);
const [imageError, setImageError] = useState(false);

// Preload image
useEffect(() => {
  if (!imageUrl) return;
  
  const img = new Image();
  img.src = imageUrl;
  img.onload = () => setImageLoaded(true);
  img.onerror = () => setImageError(true);
}, [imageUrl]);

// Render
<div className={cn(
  "transition-opacity duration-300",
  imageLoaded ? "opacity-100" : "opacity-0"
)}>
  {/* Image background */}
</div>
```

## Responsive Considerations

### Mobile
- Smaller hero height: `h-[30vh]` instead of `h-[40vh]`
- Adjust gradient opacity for better text contrast
- Test on various screen sizes

### Tablet
- Balance between mobile and desktop
- Consider side-by-side layouts

### Desktop
- Full visual impact with larger images
- More subtle gradients possible

## Tailwind CSS Classes Reference

### Background Setup
```css
bg-cover          /* Image covers entire area */
bg-center         /* Image centered */
bg-no-repeat      /* No tiling */
bg-fixed          /* Parallax effect (optional) */
```

### Gradient Overlays
```css
/* Dark to transparent (top to bottom) */
bg-gradient-to-b from-black/70 via-black/40 to-transparent

/* Light overlay for readability */
bg-gradient-to-t from-white/95 to-white/80

/* Radial gradient */
bg-radial from-black/60 to-transparent
```

### Effects
```css
filter blur-sm    /* Blur background image */
scale-105         /* Slight zoom on hover */
opacity-30        /* Subtle background presence */
backdrop-blur-sm  /* Blur behind overlays */
```

## Testing Checklist

### TripView (Planning Panel)
- [ ] Image loads and displays correctly
- [ ] Gradient overlay provides text readability
- [ ] Hero section height appropriate
- [ ] Content overlay visible on all backgrounds
- [ ] Fallback gradient works when no image
- [ ] Responsive on mobile/tablet/desktop

### TripGallery
- [ ] All cards display images correctly
- [ ] Hover effects work smoothly
- [ ] Text readable on all image backgrounds
- [ ] Grid layout maintains consistency
- [ ] Loading states handled gracefully
- [ ] Click/navigation works

### LocationProposalCard
- [ ] Background image subtle, not distracting
- [ ] Content fully readable
- [ ] Stars/buttons clearly visible
- [ ] Interaction not affected by background
- [ ] Works with and without images

## Example URLs

Google Places API URLs look like:
```
https://places.googleapis.com/v1/places/ChIJN1t_tDeuEmsRUsoyG83frY4/photos/...
```

## Troubleshooting

### Image Not Showing
1. Check browser console for CORS errors
2. Verify URL is valid and accessible
3. Check if Google Places API returned URL
4. Ensure CSS syntax is correct

### Text Not Readable
1. Increase gradient opacity
2. Add text shadows: `text-shadow-lg`
3. Use backdrop-blur on text containers
4. Adjust gradient direction

### Performance Issues
1. Implement lazy loading
2. Use smaller image sizes if possible
3. Add loading skeletons
4. Optimize gradient calculations

## Future Enhancements

- [ ] Image caching strategy
- [ ] CDN integration for faster loading
- [ ] Progressive image loading (blur-up)
- [ ] Multiple image sizes (responsive images)
- [ ] Dominant color extraction for better fallbacks
- [ ] Animation on image load
