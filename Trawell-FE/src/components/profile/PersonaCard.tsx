import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { User, Settings } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface PersonaCardProps {
  summaryMarkdown?: string;
  onEdit?: () => void;
}

export function PersonaCard({ summaryMarkdown, onEdit }: PersonaCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5 text-primary" />
              Your Travel Persona
            </CardTitle>
            <CardDescription>AI-generated summary of your travel style</CardDescription>
          </div>
          {onEdit && (
            <Button
              variant="outline"
              size="sm"
              onClick={onEdit}
              className="border-primary/20 hover:bg-primary/10"
            >
              <Settings className="w-4 h-4 mr-2" />
              Edit
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {summaryMarkdown ? (
          <div className="prose prose-sm max-w-none text-foreground">
            <ReactMarkdown>{summaryMarkdown}</ReactMarkdown>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground italic">
            Complete your profile to generate a personalized travel persona
          </p>
        )}
      </CardContent>
    </Card>
  );
}
