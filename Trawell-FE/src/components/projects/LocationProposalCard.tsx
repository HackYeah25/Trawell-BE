import { X, Star } from 'lucide-react';
import { Location } from '@/types';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface LocationProposalCardProps {
  location: Location;
  onDecision: (decision: 'reject' | 1 | 2 | 3) => void;
}

export function LocationProposalCard({ location, onDecision }: LocationProposalCardProps) {
  const isRejected = location.status === 'rejected';
  const isRated = location.status === 'rated';
  const isDisabled = isRejected || isRated;

  return (
    <Card
      className={cn(
        'overflow-hidden transition-all duration-300 animate-fade-in my-4 max-w-[460px] rounded-xl shadow-lg hover:shadow-xl border-0 bg-gradient-to-br from-white to-warm-sand/30',
        isRejected && 'opacity-40 grayscale border-2 border-muted',
        isRated && 'border-2 border-warm-turquoise shadow-lg ring-2 ring-warm-turquoise/30 bg-warm-turquoise/5',
        !isDisabled && 'hover:scale-[1.02]'
      )}
    >
      {/* Image */}
      <div className={cn(
        "relative h-32 sm:h-40 lg:h-48 overflow-hidden",
        isRejected && "after:absolute after:inset-0 after:bg-muted/60 after:content-['']"
      )}>
        {location.imageUrl ? (
          <img
            src={location.imageUrl}
            alt={location.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-warm-coral/20 to-warm-turquoise/20 flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-sunset flex items-center justify-center">
                <span className="text-white text-xl">🌍</span>
              </div>
              <p className="text-sm font-medium">Brak zdjęcia</p>
            </div>
          </div>
        )}
        {isRated && location.rating && (
          <Badge className="absolute top-3 right-3 bg-warm-turquoise text-white shadow-lg text-sm px-3 py-1.5 font-semibold z-10">
            {'★'.repeat(location.rating)}{'☆'.repeat(3 - location.rating)}
          </Badge>
        )}
        {isRejected && (
          <Badge className="absolute top-3 right-3 bg-muted/90 text-muted-foreground shadow-lg text-sm px-3 py-1.5 font-semibold z-10 border-2 border-border">
            ✕ Odrzucono
          </Badge>
        )}
      </div>

      {/* Content */}
      <div className={cn(
        "p-4 sm:p-5 space-y-3",
        isRated && "bg-warm-turquoise/5"
      )}>
        <div>
          <h3 className={cn(
            "font-semibold text-lg",
            isRejected && "line-through text-muted-foreground"
          )}>{location.name}</h3>
          <p className={cn(
            "text-sm text-muted-foreground",
            isRejected && "opacity-60"
          )}>{location.country}</p>
        </div>
        <p className={cn(
          "text-sm",
          isRejected && "text-muted-foreground"
        )}>{location.teaser}</p>

        {/* Bottom Bar */}
        <div className="grid grid-cols-4 gap-2 pt-3">
          <Button
            variant="outline"
            size="sm"
            disabled={isDisabled}
            onClick={() => onDecision('reject')}
            className={cn(
              'flex-col gap-1 h-auto py-3 rounded-lg border-2 hover:border-red-300 hover:bg-red-50 transition-all duration-200',
              isRejected && 'bg-red-100 border-red-300 text-red-700'
            )}
          >
            <X className="h-4 w-4" />
            <span className="text-xs hidden sm:inline font-medium">Odrzuć</span>
          </Button>

          {[1, 2, 3].map((stars) => (
            <Button
              key={stars}
              variant="outline"
              size="sm"
              disabled={isDisabled}
              onClick={() => onDecision(stars as 1 | 2 | 3)}
              className={cn(
                'flex-col gap-1 h-auto py-3 rounded-lg border-2 transition-all duration-200',
                'hover:border-warm-turquoise/50 hover:bg-warm-turquoise/5',
                isRated && location.rating === stars && 'bg-warm-turquoise/10 border-warm-turquoise text-warm-turquoise shadow-md'
              )}
            >
              <Star className={cn(
                'h-4 w-4',
                isRated && location.rating === stars && 'fill-warm-turquoise'
              )} />
            </Button>
          ))}
        </div>
      </div>
    </Card>
  );
}
