import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { CompletenessRing } from './CompletenessRing';
import { formatDistanceToNow } from 'date-fns';

interface ProfileHeaderProps {
  name: string;
  personaLabel?: string;
  completeness: number;
  topTags?: string[];
  updatedAt?: string;
}

export function ProfileHeader({ 
  name, 
  personaLabel, 
  completeness, 
  topTags = [],
  updatedAt 
}: ProfileHeaderProps) {
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const relativeTime = updatedAt 
    ? formatDistanceToNow(new Date(updatedAt), { addSuffix: true })
    : null;

  return (
    <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-accent/5">
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
          {/* Avatar */}
          <Avatar className="h-24 w-24 border-4 border-primary/20">
            <AvatarFallback className="bg-gradient-sunset text-primary-foreground text-3xl font-bold">
              {getInitials(name)}
            </AvatarFallback>
          </Avatar>

          {/* Info */}
          <div className="flex-1 text-center md:text-left space-y-3">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-sunset bg-clip-text text-transparent">
                {name}
              </h1>
              {personaLabel && (
                <p className="text-muted-foreground mt-1">{personaLabel}</p>
              )}
            </div>

            {/* Tags */}
            {topTags.length > 0 && (
              <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                {topTags.map((tag, i) => (
                  <Badge 
                    key={i}
                    variant="secondary"
                    className="bg-primary/10 text-primary border-primary/20 hover:bg-primary/20 transition-colors cursor-pointer"
                  >
                    #{tag}
                  </Badge>
                ))}
              </div>
            )}

            {/* Updated timestamp */}
            {relativeTime && (
              <p className="text-xs text-muted-foreground">
                Last updated {relativeTime}
              </p>
            )}
          </div>

          {/* Completeness Ring */}
          <div className="flex flex-col items-center gap-2">
            <CompletenessRing completeness={completeness} />
            <p className="text-sm font-medium text-muted-foreground">Profile Completeness</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
