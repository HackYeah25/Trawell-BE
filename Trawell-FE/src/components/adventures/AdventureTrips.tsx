import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronDown, ChevronRight, MapPin, Calendar, Star, Plane } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useProjectTrips } from '@/api/hooks/use-trips';
import { useBrainstormTrips } from '@/api/hooks/use-brainstorm';

interface AdventureTripsProps {
  adventureId: string;
  adventureType: 'project' | 'brainstorm';
  isExpanded: boolean;
  onToggle: () => void;
}

export function AdventureTrips({ 
  adventureId, 
  adventureType, 
  isExpanded, 
  onToggle 
}: AdventureTripsProps) {
  const navigate = useNavigate();
  const { data: projectTrips, isLoading: projectTripsLoading } = useProjectTrips(
    adventureType === 'project' ? adventureId : ''
  );
  const { data: brainstormTrips, isLoading: brainstormTripsLoading } = useBrainstormTrips(
    adventureType === 'brainstorm' ? adventureId : ''
  );

  const trips = adventureType === 'project' ? projectTrips : brainstormTrips;
  const isLoading = adventureType === 'project' ? projectTripsLoading : brainstormTripsLoading;
  const tripCount = trips?.length || 0;

  const handleTripClick = (trip: any) => {
    const tripId = trip.id || trip.recommendation_id;
    if (tripId) {
      navigate(`/app/trips/${tripId}`);
    }
  };

  if (isLoading) {
    return (
      <div className="ml-13 mt-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted/30 rounded-lg p-3">
          <div className="w-4 h-4 border-2 border-warm-coral/30 border-t-warm-coral rounded-full animate-spin" />
          Loading trips...
        </div>
      </div>
    );
  }

  if (tripCount === 0) {
    return (
      <div className="ml-13 mt-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted/30 rounded-lg p-3">
          <MapPin className="w-4 h-4" />
          No trips yet
        </div>
      </div>
    );
  }

  return (
    <div className="ml-13 mt-3">
      {/* Toggle button with better styling */}
      <Button
        variant="ghost"
        size="sm"
        onClick={onToggle}
        className="h-8 px-3 text-sm text-muted-foreground hover:text-foreground hover:bg-warm-coral/10 rounded-lg border border-warm-coral/20 bg-card/50"
      >
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 mr-2" />
        ) : (
          <ChevronRight className="w-4 h-4 mr-2" />
        )}
        <MapPin className="w-4 h-4 mr-1" />
        {tripCount} {tripCount === 1 ? 'trip' : 'trips'}
      </Button>

      {/* Trips list with better grouping */}
      {isExpanded && (
        <div className="mt-3 ml-4 border-l-2 border-warm-coral/20 pl-4 space-y-3">
          <div className="flex items-center justify-between mb-2">
            <div className="text-xs font-medium text-warm-coral uppercase tracking-wide">
              Your Adventures
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/app/gallery')}
              className="h-6 px-2 text-xs text-warm-coral hover:text-warm-coral/80 hover:bg-warm-coral/10"
            >
              View All
            </Button>
          </div>
          <div className="space-y-2">
            {trips?.map((trip: any, index: number) => (
              <Card
                key={trip.id || trip.recommendation_id}
                className="group p-4 border-warm-coral/15 bg-gradient-to-r from-warm-coral/3 to-warm-turquoise/3 hover:from-warm-coral/8 hover:to-warm-turquoise/8 hover:border-warm-coral/25 transition-all duration-200 cursor-pointer hover:shadow-sm"
                onClick={() => handleTripClick(trip)}
              >
                <div className="flex items-center gap-4">
                  {/* Trip icon with better styling */}
                  <div className="w-12 h-12 rounded-xl bg-gradient-sunset flex items-center justify-center flex-shrink-0 shadow-warm group-hover:scale-105 transition-transform">
                    <Plane className="w-6 h-6 text-white" />
                  </div>
                  
                  {/* Trip details */}
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-sm truncate mb-1">
                      {trip.title || trip.destination?.name || trip.destination?.city}
                    </h4>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        <span>
                          {trip.startDate ? 
                            new Date(trip.startDate).toLocaleDateString() : 
                            new Date(trip.created_at || trip.createdAt).toLocaleDateString()
                          }
                        </span>
                      </div>
                      {trip.destination?.rating && (
                        <div className="flex items-center gap-1">
                          <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                          <span>{trip.destination.rating}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Status badges */}
                  <div className="flex-shrink-0 flex flex-col gap-1">
                    {trip.status === 'active' && (
                      <Badge variant="secondary" className="text-xs w-fit">
                        Active
                      </Badge>
                    )}
                    {trip.startDate && trip.endDate && (
                      <Badge variant="outline" className="text-xs w-fit border-warm-coral/30 text-warm-coral">
                        Planned
                      </Badge>
                    )}
                    {!trip.status && !trip.startDate && (
                      <Badge variant="outline" className="text-xs w-fit border-warm-turquoise/30 text-warm-turquoise">
                        Idea
                      </Badge>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
