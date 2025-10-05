import { MapPin, Calendar, Star, ArrowRight } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { TripCard as TripCardType } from '@/types';

interface TripCardProps {
  trip: TripCardType;
  onViewTrip?: (tripId: string) => void;
  className?: string;
}

export const TripCard = ({ trip, onViewTrip, className }: TripCardProps) => {
  const handleViewTrip = () => {
    if (onViewTrip) {
      onViewTrip(trip.id);
    }
  };

  return (
    <Card className={cn(
      "p-4 bg-gradient-to-r from-warm-coral/5 to-warm-turquoise/5 border-warm-coral/20 hover:border-warm-coral/40 transition-colors",
      className
    )}>
      <div className="flex items-start gap-3">
        {/* Trip Image */}
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

        {/* Trip Info */}
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
            
            {/* Rating */}
            {trip.rating && (
              <Badge className="bg-warm-turquoise/10 text-warm-turquoise border-warm-turquoise/20">
                <Star className="w-3 h-3 mr-1" />
                {trip.rating}
              </Badge>
            )}
          </div>

          {/* Action Button */}
          <div className="mt-3">
            <Button
              onClick={handleViewTrip}
              size="sm"
              className="bg-gradient-sunset hover:opacity-90 text-white shadow-warm border-0"
            >
              View Trip
              <ArrowRight className="w-3 h-3 ml-1" />
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
};
