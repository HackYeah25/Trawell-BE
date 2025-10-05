import { useState } from 'react';
import { Copy, Check, Users } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import type { ProjectParticipant } from '@/types';

interface ShareCodeDisplayProps {
  shareCode: string;
  participants?: ProjectParticipant[];
}

export function ShareCodeDisplay({ shareCode, participants = [] }: ShareCodeDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Users className="w-5 h-5 text-blue-600" />
          Shared Project
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Share Code */}
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">Share this code:</p>
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-background border border-warm-coral/20 rounded-lg p-3 text-center">
              <code className="text-2xl font-mono font-bold tracking-wider bg-gradient-sunset bg-clip-text text-transparent">
                {shareCode}
              </code>
            </div>
            <Button
              size="icon"
              variant="outline"
              onClick={handleCopy}
              className="flex-shrink-0"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Participants */}
        {participants.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground flex items-center gap-2">
              Participants
              <Badge variant="secondary" className="ml-auto">
                {participants.length}
              </Badge>
            </p>
            <div className="flex flex-wrap gap-2">
              {participants.map((participant) => (
                <div
                  key={participant.id}
                  className="flex items-center gap-2 bg-background border border-warm-coral/20 rounded-full pl-1 pr-3 py-1"
                >
                  <Avatar className="w-6 h-6">
                    <AvatarFallback className="text-xs bg-gradient-sunset text-white">
                      {getInitials(participant.userName)}
                    </AvatarFallback>
                  </Avatar>
                  <span className="text-sm">{participant.userName}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
