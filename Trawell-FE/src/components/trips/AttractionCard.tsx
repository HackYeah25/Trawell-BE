import { memo } from 'react';
import { Check, X, MapPin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Attraction } from '@/types';
import { cn } from '@/lib/utils';

interface AttractionCardProps {
  attraction: Attraction;
  onDecision: (attractionId: string, decision: 'accept' | 'reject') => void;
  disabled?: boolean;
}

export const AttractionCard = memo(function AttractionCard({
  attraction,
  onDecision,
  disabled = false,
}: AttractionCardProps) {
  return (
    <Card
      className={cn(
        'overflow-hidden transition-all',
        attraction.status === 'rated' && attraction.rating && attraction.rating >= 2 && 'border-success bg-success/5',
        attraction.status === 'rejected' && 'opacity-50'
      )}
    >
      {attraction.imageUrl && (
        <div className="relative w-full h-40 sm:h-48 overflow-hidden">
          <img 
            src={attraction.imageUrl} 
            alt={attraction.title}
            className="w-full h-full object-cover"
          />
          {attraction.category && (
            <Badge 
              variant="secondary" 
              className="absolute top-2 right-2 bg-background/80 backdrop-blur-sm"
            >
              {attraction.category}
            </Badge>
          )}
        </div>
      )}
      
      <CardHeader className="pb-3">
        <div className="flex flex-col gap-3">
          <div className="flex items-start gap-2">
            <MapPin className="w-4 h-4 text-warm-coral mt-1 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <CardTitle className="text-base break-words">{attraction.title}</CardTitle>
              {!attraction.imageUrl && attraction.category && (
                <Badge variant="secondary" className="mt-2">
                  {attraction.category}
                </Badge>
              )}
            </div>
          </div>

          <CardDescription className="text-sm break-words">
            {attraction.description}
          </CardDescription>

          {attraction.status !== 'pending' ? (
            <Badge
              variant={attraction.status === 'rated' && attraction.rating ? 'default' : 'secondary'}
              className={cn(
                'w-fit',
                attraction.status === 'rated' && attraction.rating && 'bg-success text-success-foreground'
              )}
            >
              {attraction.status === 'rated' && attraction.rating ? (
                <>
                  <Check className="w-3 h-3 mr-1" />
                  Rated {attraction.rating}★
                </>
              ) : (
                <>
                  <X className="w-3 h-3 mr-1" />
                  Rejected
                </>
              )}
            </Badge>
          ) : (
            <div className="flex flex-col sm:flex-row gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => onDecision(attraction.id, 'accept')}
                disabled={disabled}
                className="bg-warm-turquoise/10 border-warm-turquoise text-warm-turquoise hover:bg-warm-turquoise hover:text-white hover:border-warm-turquoise transition-colors w-full sm:w-auto"
              >
                <Check className="w-4 h-4 mr-1" />
                Accept
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => onDecision(attraction.id, 'reject')}
                disabled={disabled}
                className="hover:bg-warm-coral/10 w-full sm:w-auto"
              >
                <X className="w-4 h-4 mr-1" />
                Reject
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
    </Card>
  );
});
