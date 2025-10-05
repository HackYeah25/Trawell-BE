import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';

interface EditPreferencesDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  displayName: string;
  preferences: {
    type: string;
    budget: string;
    timing: string;
    companions: string;
  };
  interests: string[];
  destinations: string[];
  onSave: (data: {
    displayName?: string;
    preferences: {
      type: string;
      budget: string;
      timing: string;
      companions: string;
    };
    interests: string[];
    destinations: string[];
  }) => void;
}

export function EditPreferencesDialog({
  open,
  onOpenChange,
  displayName,
  preferences,
  interests,
  destinations,
  onSave,
}: EditPreferencesDialogProps) {
  const [editedDisplayName, setEditedDisplayName] = useState(displayName);
  const [editedPreferences, setEditedPreferences] = useState(preferences);
  const [editedInterests, setEditedInterests] = useState(interests);
  const [editedDestinations, setEditedDestinations] = useState(destinations);
  const [newInterest, setNewInterest] = useState('');
  const [newDestination, setNewDestination] = useState('');

  const handleSave = () => {
    onSave({
      displayName: editedDisplayName,
      preferences: editedPreferences,
      interests: editedInterests,
      destinations: editedDestinations,
    });
    onOpenChange(false);
  };

  const addInterest = () => {
    if (newInterest.trim()) {
      setEditedInterests([...editedInterests, newInterest.trim()]);
      setNewInterest('');
    }
  };

  const removeInterest = (index: number) => {
    setEditedInterests(editedInterests.filter((_, i) => i !== index));
  };

  const addDestination = () => {
    if (newDestination.trim()) {
      setEditedDestinations([...editedDestinations, newDestination.trim()]);
      setNewDestination('');
    }
  };

  const removeDestination = (index: number) => {
    setEditedDestinations(editedDestinations.filter((_, i) => i !== index));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Travel Preferences</DialogTitle>
          <DialogDescription>
            Update your travel style and preferences
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Display Name */}
          <div className="space-y-2">
            <Label htmlFor="displayName">Display Name</Label>
            <Input
              id="displayName"
              value={editedDisplayName}
              onChange={(e) => setEditedDisplayName(e.target.value)}
              placeholder="Enter your display name"
            />
          </div>

          {/* Travel Preferences */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg">Travel Preferences</h3>
            
            <div className="space-y-2">
              <Label htmlFor="type">Travel Type</Label>
              <Textarea
                id="type"
                value={editedPreferences.type}
                onChange={(e) =>
                  setEditedPreferences({ ...editedPreferences, type: e.target.value })
                }
                placeholder="e.g., Beach relaxation, city exploration"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="budget">Budget Range</Label>
              <Input
                id="budget"
                value={editedPreferences.budget}
                onChange={(e) =>
                  setEditedPreferences({ ...editedPreferences, budget: e.target.value })
                }
                placeholder="e.g., Medium, Luxury"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="timing">Preferred Timing</Label>
              <Input
                id="timing"
                value={editedPreferences.timing}
                onChange={(e) =>
                  setEditedPreferences({ ...editedPreferences, timing: e.target.value })
                }
                placeholder="e.g., Summer 2025"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="companions">Travel Companions</Label>
              <Input
                id="companions"
                value={editedPreferences.companions}
                onChange={(e) =>
                  setEditedPreferences({ ...editedPreferences, companions: e.target.value })
                }
                placeholder="e.g., Couple, Family, Solo"
              />
            </div>
          </div>

          {/* Interests */}
          <div className="space-y-3">
            <h3 className="font-semibold text-lg">Interests</h3>
            <div className="flex gap-2">
              <Input
                value={newInterest}
                onChange={(e) => setNewInterest(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addInterest()}
                placeholder="Add new interest"
              />
              <Button onClick={addInterest} variant="secondary">
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {editedInterests.map((interest, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="px-3 py-1.5 bg-warm-coral/10 border-warm-coral/20"
                >
                  {interest}
                  <button
                    onClick={() => removeInterest(index)}
                    className="ml-2 hover:text-destructive"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </div>

          {/* Destinations */}
          <div className="space-y-3">
            <h3 className="font-semibold text-lg">Favorite Destinations</h3>
            <div className="flex gap-2">
              <Input
                value={newDestination}
                onChange={(e) => setNewDestination(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addDestination()}
                placeholder="Add new destination"
              />
              <Button onClick={addDestination} variant="secondary">
                Add
              </Button>
            </div>
            <div className="space-y-2">
              {editedDestinations.map((destination, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 rounded-lg bg-warm-sand/10 border border-warm-sand/20"
                >
                  <span className="font-medium">{destination}</span>
                  <button
                    onClick={() => removeDestination(index)}
                    className="hover:text-destructive"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} className="bg-warm-coral hover:bg-warm-coral/90">
            Save Changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
