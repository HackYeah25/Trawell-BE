import { useState } from 'react';
import { MapPin, Calendar, Users, Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Location } from '@/types';
import { cn } from '@/lib/utils';

interface CreateTripModalProps {
  isOpen: boolean;
  onClose: () => void;
  location: Location;
  onCreateTrip: (tripData: { title: string; startDate?: string; endDate?: string }) => Promise<void>;
  isLoading?: boolean;
}

export const CreateTripModal = ({ 
  isOpen, 
  onClose, 
  location, 
  onCreateTrip, 
  isLoading = false 
}: CreateTripModalProps) => {
  const [tripTitle, setTripTitle] = useState(`Podróż do ${location.name}`);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const handleCreateTrip = async () => {
    if (!tripTitle.trim()) return;
    
    await onCreateTrip({
      title: tripTitle.trim(),
      startDate: startDate || undefined,
      endDate: endDate || undefined,
    });
  };

  const handleClose = () => {
    if (!isLoading) {
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-sunset flex items-center justify-center">
              <MapPin className="w-4 h-4 text-white" />
            </div>
            Utwórz podróż
          </DialogTitle>
          <DialogDescription>
            Stwórz nową podróż na podstawie wybranej lokalizacji
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Location Preview */}
          <Card className="p-4 bg-gradient-to-r from-warm-coral/5 to-warm-turquoise/5 border-warm-coral/20">
            <div className="flex items-start gap-3">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-warm-coral/20 to-warm-turquoise/20 flex items-center justify-center flex-shrink-0">
                {location.imageUrl ? (
                  <img
                    src={location.imageUrl}
                    alt={location.name}
                    className="w-full h-full object-cover rounded-lg"
                  />
                ) : (
                  <span className="text-xl">🌍</span>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-lg truncate">{location.name}</h3>
                <p className="text-sm text-muted-foreground">{location.country}</p>
                <p className="text-sm mt-1 line-clamp-2">{location.teaser}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge className="bg-warm-turquoise/10 text-warm-turquoise border-warm-turquoise/20">
                    {'★'.repeat(location.rating || 0)}{'☆'.repeat(3 - (location.rating || 0))}
                  </Badge>
                </div>
              </div>
            </div>
          </Card>

          {/* Trip Details Form */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="trip-title">Nazwa podróży</Label>
              <Input
                id="trip-title"
                value={tripTitle}
                onChange={(e) => setTripTitle(e.target.value)}
                placeholder="Wprowadź nazwę podróży..."
                disabled={isLoading}
                className="border-warm-coral/20 focus:border-warm-coral/60"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start-date" className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  Data rozpoczęcia
                </Label>
                <Input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  disabled={isLoading}
                  className="border-warm-coral/20 focus:border-warm-coral/60"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end-date" className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  Data zakończenia
                </Label>
                <Input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  disabled={isLoading}
                  className="border-warm-coral/20 focus:border-warm-coral/60"
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
              className="flex-1"
            >
              Anuluj
            </Button>
            <Button
              onClick={handleCreateTrip}
              disabled={isLoading || !tripTitle.trim()}
              className="flex-1 bg-gradient-sunset hover:opacity-90 text-white"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Tworzenie...
                </>
              ) : (
                <>
                  <Users className="w-4 h-4 mr-2" />
                  Utwórz podróż
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
