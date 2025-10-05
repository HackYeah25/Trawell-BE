import { memo } from 'react';
import { MapPin } from 'lucide-react';
import { AttractionCard } from './AttractionCard';
import type { Attraction } from '@/types';

interface AttractionsPanelProps {
  attractions: Attraction[];
  onDecision: (attractionId: string, decision: 'accept' | 'reject') => void;
  disabled?: boolean;
}

export const AttractionsPanel = memo(function AttractionsPanel({
  attractions,
  onDecision,
  disabled = false,
}: AttractionsPanelProps) {
  // Only show attractions without ratings
  const pendingAttractions = attractions.filter(a => a.status === 'pending');

  if (pendingAttractions.length === 0) {
    return null;
  }

  return (
    <div className="border-t border-warm-coral/20 bg-gradient-to-br from-warm-sand/30 to-warm-turquoise/5 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-2 mb-4">
          <MapPin className="w-5 h-5 text-warm-coral" />
          <h3 className="font-semibold text-lg">Suggested Attractions</h3>
        </div>

        <div className="space-y-3">
          {pendingAttractions.map((attraction) => (
            <AttractionCard
              key={attraction.id}
              attraction={attraction}
              onDecision={onDecision}
              disabled={disabled}
            />
          ))}
        </div>
      </div>
    </div>
  );
});
