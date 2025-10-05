import { useState } from 'react';
import { UserPlus } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface JoinProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onJoin: (shareCode: string) => void;
  isLoading?: boolean;
}

export function JoinProjectDialog({
  open,
  onOpenChange,
  onJoin,
  isLoading,
}: JoinProjectDialogProps) {
  const [shareCode, setShareCode] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (shareCode.trim()) {
      onJoin(shareCode.trim().toUpperCase());
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-2xl font-pacifico bg-gradient-sunset bg-clip-text text-transparent flex items-center gap-2">
            <UserPlus className="w-6 h-6 text-warm-coral" />
            Join Shared Adventure
          </DialogTitle>
          <DialogDescription>
            Enter the share code to join an existing adventure
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="shareCode">Share Code</Label>
              <Input
                id="shareCode"
                value={shareCode}
                onChange={(e) => setShareCode(e.target.value.toUpperCase())}
                placeholder="ABC123"
                maxLength={6}
                className="text-center text-lg font-mono tracking-wider"
                autoFocus
              />
              <p className="text-xs text-muted-foreground">
                Ask the adventure owner for the 6-character code
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!shareCode.trim() || isLoading}
              className="bg-gradient-sunset hover:opacity-90 text-white shadow-warm border-0"
            >
              {isLoading ? 'Joining...' : 'Join Adventure'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
