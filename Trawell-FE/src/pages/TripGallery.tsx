import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Grid, List, MapPin, Calendar, Star, Eye } from 'lucide-react';
import { AppShell } from '@/components/layout/AppShell';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { useTrips } from '@/api/hooks/use-trips';
import { useBrainstormSessions, useAllRecommendations } from '@/api/hooks/use-brainstorm';
import { toast } from 'sonner';

type ViewMode = 'grid' | 'list';

// Skeleton Components
const TripCardSkeleton = ({ viewMode }: { viewMode: ViewMode }) => {
  if (viewMode === 'grid') {
    return (
      <Card className="overflow-hidden">
        <Skeleton className="aspect-[4/3] w-full" />
        <div className="p-4 space-y-2">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-3 w-1/3" />
        </div>
      </Card>
    );
  }

  return (
    <Card className="flex items-center gap-4 p-4">
      <Skeleton className="w-16 h-16 rounded-lg flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-5 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-3 w-1/3" />
      </div>
      <Skeleton className="h-8 w-16" />
    </Card>
  );
};

const GallerySkeleton = ({ viewMode }: { viewMode: ViewMode }) => (
  <div className={cn(
    "mt-6",
    viewMode === 'grid' 
      ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      : "space-y-4"
  )}>
    {Array.from({ length: 8 }).map((_, i) => (
      <TripCardSkeleton key={i} viewMode={viewMode} />
    ))}
  </div>
);

export default function TripGallery() {
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const { data: trips, isLoading: tripsLoading } = useTrips();
  const { data: recommendations, isLoading: recommendationsLoading } = useAllRecommendations();
  
  // Debug logging
  console.log('Trips data:', trips);
  console.log('Recommendations data:', recommendations);
  
  // Combine trips and recommendations
  const allTrips = [
    ...(trips || []).map(trip => ({
      id: trip.id,
      title: trip.title,
      locationName: trip.locationName || trip.destination,
      imageUrl: trip.imageUrl,
      createdAt: trip.createdAt,
      type: 'trip' as const,
      rating: undefined,
    })),
    ...(recommendations?.recommendations || []).map((rec: any) => ({
      id: rec.recommendation_id,
      title: rec.destination?.name || rec.destination?.city || 'Trip',
      locationName: rec.destination?.city || rec.destination?.name || 'Unknown',
      imageUrl: rec.url, // ✅ Use rec.url from Google Places API
      createdAt: rec.created_at,
      type: 'recommendation' as const,
      rating: rec.destination?.rating,
    })),
  ];

  const filteredTrips = allTrips.filter(trip =>
    trip.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    trip.locationName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleViewTrip = (tripId: string, type: 'trip' | 'recommendation') => {
    if (type === 'recommendation') {
      navigate(`/app/trips/${tripId}`);
    } else {
      navigate(`/app/trips/${tripId}`);
    }
  };

  const handleBackToPlanning = (sessionId?: string) => {
    if (sessionId) {
      navigate(`/app/brainstorm/${sessionId}`);
    } else {
      navigate('/app');
    }
  };

  if (tripsLoading || recommendationsLoading) {
    return (
      <AppShell>
        <div className="min-h-screen bg-gradient-to-br from-warm-coral/5 via-warm-turquoise/5 to-warm-sand">
          {/* Header Skeleton */}
          <div className="sticky top-0 z-50 bg-card/80 backdrop-blur-md border-b border-warm-coral/20">
            <div className="max-w-6xl mx-auto p-4">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <Skeleton className="w-10 h-10 rounded-lg" />
                  <Skeleton className="w-10 h-10 rounded-xl" />
                  <div>
                    <Skeleton className="h-8 w-32 mb-2" />
                    <Skeleton className="h-4 w-20" />
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Skeleton className="h-10 w-64" />
                  <Skeleton className="h-10 w-20" />
                </div>
              </div>
            </div>
          </div>

          {/* Content Skeleton */}
          <div className="max-w-6xl mx-auto p-4">
            <GallerySkeleton viewMode={viewMode} />
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="min-h-screen bg-gradient-to-br from-warm-coral/5 via-warm-turquoise/5 to-warm-sand">
        {/* Header */}
        <div className="sticky top-0 z-50 bg-card/80 backdrop-blur-md border-b border-warm-coral/20">
          <div className="max-w-6xl mx-auto p-4">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => navigate('/app')}
                  className="flex-shrink-0"
                >
                  <ArrowLeft className="w-5 h-5" />
                </Button>
                <div className="w-10 h-10 rounded-xl bg-gradient-sunset flex items-center justify-center shadow-warm flex-shrink-0">
                  <MapPin className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-pacifico bg-gradient-sunset bg-clip-text text-transparent">
                    Trip Gallery
                  </h1>
                  <p className="text-sm text-muted-foreground">
                    {filteredTrips.length} trip{filteredTrips.length !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {/* Search */}
                <Input
                  placeholder="Search trips..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64 border-warm-coral/20 focus:border-warm-coral/60"
                />

                {/* View Mode Toggle */}
                <div className="flex border border-warm-coral/20 rounded-lg overflow-hidden">
                  <Button
                    variant={viewMode === 'grid' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('grid')}
                    className={cn(
                      "rounded-none border-0",
                      viewMode === 'grid' 
                        ? "bg-gradient-sunset text-white shadow-warm" 
                        : "hover:bg-warm-coral/10"
                    )}
                  >
                    <Grid className="w-4 h-4" />
                  </Button>
                  <Button
                    variant={viewMode === 'list' ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setViewMode('list')}
                    className={cn(
                      "rounded-none border-0",
                      viewMode === 'list' 
                        ? "bg-gradient-sunset text-white shadow-warm" 
                        : "hover:bg-warm-coral/10"
                    )}
                  >
                    <List className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-6xl mx-auto p-4">
          {filteredTrips.length === 0 ? (
            <div className="text-center py-16">
              <div className="w-20 h-20 rounded-full bg-gradient-sunset flex items-center justify-center mb-4 mx-auto shadow-warm">
                <MapPin className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-2">No trips found</h3>
              <p className="text-muted-foreground mb-6">
                {searchQuery ? 'Try adjusting your search terms' : 'Start planning your first adventure!'}
              </p>
              <Button
                onClick={() => navigate('/app')}
                className="bg-gradient-sunset hover:opacity-90 text-white shadow-warm border-0"
              >
                <MapPin className="w-4 h-4 mr-2" />
                Start Planning
              </Button>
            </div>
          ) : (
            <div className={cn(
              "mt-6",
              viewMode === 'grid' 
                ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
                : "space-y-4"
            )}>
              {filteredTrips.map((trip) => (
                <Card
                  key={trip.id}
                  className={cn(
                    "group cursor-pointer transition-all duration-300 hover:shadow-lg hover:scale-105",
                    viewMode === 'grid' 
                      ? "overflow-hidden" 
                      : "flex items-center gap-4 p-4"
                  )}
                  onClick={() => handleViewTrip(trip.id, trip.type)}
                >
                  {viewMode === 'grid' ? (
                    <>
                      {/* Grid View - Photo-centric */}
                      <div className="aspect-[4/3] relative overflow-hidden">
                        {trip.imageUrl ? (
                          <img
                            src={trip.imageUrl}
                            alt={trip.title}
                            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                          />
                        ) : (
                          <div className="w-full h-full bg-gradient-to-br from-warm-coral/20 to-warm-turquoise/20 flex items-center justify-center">
                            <MapPin className="w-12 h-12 text-warm-coral" />
                          </div>
                        )}
                        
                        {/* Overlay */}
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300 flex items-center justify-center">
                          <Button
                            size="sm"
                            className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-white/90 text-black hover:bg-white"
                          >
                            <Eye className="w-4 h-4 mr-2" />
                            View Trip
                          </Button>
                        </div>

                        {/* Rating Badge */}
                        {trip.rating && (
                          <div className="absolute top-3 right-3">
                            <Badge className="bg-warm-turquoise/90 text-white border-0">
                              <Star className="w-3 h-3 mr-1" />
                              {trip.rating}
                            </Badge>
                          </div>
                        )}
                      </div>

                      {/* Trip Info */}
                      <div className="p-4">
                        <h3 className="font-semibold text-lg truncate mb-1">{trip.title}</h3>
                        <p className="text-sm text-muted-foreground flex items-center gap-1 mb-2">
                          <MapPin className="w-3 h-3" />
                          {trip.locationName}
                        </p>
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(trip.createdAt).toLocaleDateString('en-US')}
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      {/* List View */}
                      <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-warm-coral/20 to-warm-turquoise/20 flex items-center justify-center flex-shrink-0 overflow-hidden">
                        {trip.imageUrl ? (
                          <img
                            src={trip.imageUrl}
                            alt={trip.title}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <MapPin className="w-8 h-8 text-warm-coral" />
                        )}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-lg truncate">{trip.title}</h3>
                            <p className="text-sm text-muted-foreground flex items-center gap-1">
                              <MapPin className="w-3 h-3" />
                              {trip.locationName}
                            </p>
                            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                              <Calendar className="w-3 h-3" />
                              {new Date(trip.createdAt).toLocaleDateString('en-US')}
                            </p>
                          </div>
                          
                          {trip.rating && (
                            <Badge className="bg-warm-turquoise/10 text-warm-turquoise border-warm-turquoise/20">
                              <Star className="w-3 h-3 mr-1" />
                              {trip.rating}
                            </Badge>
                          )}
                        </div>
                      </div>

                      <Button
                        size="sm"
                        className="bg-gradient-sunset hover:opacity-90 text-white shadow-warm border-0"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        View
                      </Button>
                    </>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
