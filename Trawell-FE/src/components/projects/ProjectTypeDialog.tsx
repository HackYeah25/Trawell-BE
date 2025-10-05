import { Lock, Users, UserPlus } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { useState } from 'react';

interface ProjectTypeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSelectType: (isShared: boolean) => void;
  onJoinProject?: (shareCode: string) => void;
  isJoining?: boolean;
}

export function ProjectTypeDialog({
  open,
  onOpenChange,
  onSelectType,
  onJoinProject,
  isJoining = false,
}: ProjectTypeDialogProps) {
  const [shareCode, setShareCode] = useState('');
  const [showJoinSection, setShowJoinSection] = useState(false);

  const handleJoinProject = () => {
    if (shareCode.trim() && onJoinProject) {
      onJoinProject(shareCode.trim());
      setShareCode('');
    }
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg max-w-[95vw] mx-4 sm:mx-0">
        <DialogHeader className="space-y-2">
          <DialogTitle className="text-xl sm:text-2xl font-pacifico bg-gradient-sunset bg-clip-text text-transparent">
            New Adventure
          </DialogTitle>
          <DialogDescription className="text-sm">
            Choose how you want to start your adventure
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-6">
          {/* Create New Adventures */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-muted-foreground">Create New</h3>
            
            <Button
              onClick={() => onSelectType(false)}
              variant="outline"
              className="w-full h-auto flex-col items-start p-4 sm:p-5 gap-3 hover:border-warm-coral hover:bg-warm-coral/5 transition-all duration-200 rounded-xl border-2"
            >
              <div className="flex items-center gap-3 w-full">
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-warm-sand/40 to-warm-coral/20 flex items-center justify-center flex-shrink-0 shadow-sm">
                  <Lock className="w-5 h-5 sm:w-6 sm:h-6 text-warm-coral" />
                </div>
                <div className="flex-1 text-left">
                  <div className="font-semibold text-base sm:text-lg">Private Adventure</div>
                  <div className="text-sm text-muted-foreground">Only you can access this adventure</div>
                </div>
              </div>
            </Button>

            <Button
              onClick={() => onSelectType(true)}
              variant="outline"
              className="w-full h-auto flex-col items-start p-4 sm:p-5 gap-3 hover:border-warm-turquoise hover:bg-warm-turquoise/5 transition-all duration-200 rounded-xl border-2"
            >
              <div className="flex items-center gap-3 w-full">
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-blue-100 to-warm-turquoise/20 flex items-center justify-center flex-shrink-0 shadow-sm">
                  <Users className="w-5 h-5 sm:w-6 sm:h-6 text-warm-turquoise" />
                </div>
                <div className="flex-1 text-left">
                  <div className="font-semibold text-base sm:text-lg">Shared Adventure</div>
                  <div className="text-sm text-muted-foreground">
                    Collaborate with others via share code
                  </div>
                </div>
              </div>
            </Button>
          </div>

          {/* Separator */}
          <div className="flex items-center gap-4 my-6">
            <Separator className="flex-1" />
            <span className="text-sm font-medium text-muted-foreground px-2">OR</span>
            <Separator className="flex-1" />
          </div>

          {/* Join Existing Adventure */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-muted-foreground">Join Existing</h3>
            
            {!showJoinSection ? (
              <Button
                onClick={() => setShowJoinSection(true)}
                variant="outline"
                className="w-full h-auto flex-col items-start p-4 sm:p-5 gap-3 hover:border-warm-turquoise hover:bg-warm-turquoise/5 transition-all duration-200 rounded-xl border-2"
              >
                <div className="flex items-center gap-3 w-full">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-warm-turquoise/20 to-warm-turquoise/10 flex items-center justify-center flex-shrink-0 shadow-sm">
                    <UserPlus className="w-5 h-5 sm:w-6 sm:h-6 text-warm-turquoise" />
                  </div>
                  <div className="flex-1 text-left">
                    <div className="font-semibold text-base sm:text-lg">Join Adventure</div>
                    <div className="text-sm text-muted-foreground">
                      Enter a share code to join an existing adventure
                    </div>
                  </div>
                </div>
              </Button>
            ) : (
              <div className="space-y-4 p-4 sm:p-5 border-2 border-warm-turquoise/20 rounded-xl bg-gradient-to-br from-warm-turquoise/5 to-warm-turquoise/10">
                <div className="text-base font-semibold text-warm-turquoise">Enter Share Code</div>
                <div className="flex flex-col sm:flex-row gap-3">
                  <Input
                    value={shareCode}
                    onChange={(e) => setShareCode(e.target.value)}
                    placeholder="Enter adventure code..."
                    className="flex-1 h-11 text-base"
                    onKeyDown={(e) => e.key === 'Enter' && handleJoinProject()}
                  />
                  <Button
                    onClick={handleJoinProject}
                    disabled={!shareCode.trim() || isJoining}
                    size="sm"
                    className="bg-warm-turquoise hover:bg-warm-turquoise/90 text-white h-11 px-6 font-medium"
                  >
                    {isJoining ? 'Joining...' : 'Join'}
                  </Button>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowJoinSection(false)}
                  className="text-sm text-muted-foreground hover:text-foreground self-start"
                >
                  ← Cancel
                </Button>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
