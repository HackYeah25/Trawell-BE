import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Leaf, Accessibility, ThermometerSun, ThermometerSnowflake, Languages, Info } from 'lucide-react';
import type { UserProfile, ClimatePref } from '@/types/profile';

interface ConstraintsCardProps {
  constraints: UserProfile['constraints'];
}

const climateIcons: Record<ClimatePref, typeof ThermometerSun> = {
  hot_tropical: ThermometerSun,
  mild_temperate: ThermometerSun,
  cool_cold: ThermometerSnowflake,
  no_preference: ThermometerSun
};

const climateLabels: Record<ClimatePref, string> = {
  hot_tropical: 'Hot & Tropical',
  mild_temperate: 'Mild & Temperate',
  cool_cold: 'Cool & Cold',
  no_preference: 'No Preference'
};

export function ConstraintsCard({ constraints }: ConstraintsCardProps) {
  const hasConstraints = 
    (constraints.dietary_restrictions?.length ?? 0) > 0 ||
    (constraints.mobility_limitations?.length ?? 0) > 0 ||
    (constraints.climate_preferences?.length ?? 0) > 0 ||
    (constraints.language_preferences?.length ?? 0) > 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Constraints & Requirements</CardTitle>
        <CardDescription>Special needs and preferences</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Dietary Restrictions */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Leaf className="w-4 h-4 text-primary" />
            <h4 className="text-sm font-medium">Dietary Restrictions</h4>
          </div>
          {constraints.dietary_restrictions && constraints.dietary_restrictions.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {constraints.dietary_restrictions.map((item, i) => (
                <Badge key={i} variant="outline" className="bg-primary/5 border-primary/20">
                  {item}
                </Badge>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">No dietary restrictions</p>
          )}
        </div>

        {/* Mobility */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Accessibility className="w-4 h-4 text-primary" />
            <h4 className="text-sm font-medium">Mobility & Accessibility</h4>
          </div>
          {constraints.mobility_limitations && constraints.mobility_limitations.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {constraints.mobility_limitations.map((item, i) => (
                <Badge key={i} variant="outline" className="bg-accent/5 border-accent/20">
                  {item}
                </Badge>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">No mobility limitations</p>
          )}
        </div>

        {/* Climate */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <ThermometerSun className="w-4 h-4 text-primary" />
            <h4 className="text-sm font-medium">Climate Preferences</h4>
          </div>
          {constraints.climate_preferences && constraints.climate_preferences.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {constraints.climate_preferences.map((climate, i) => {
                const Icon = climateIcons[climate];
                return (
                  <Badge 
                    key={i} 
                    variant="outline" 
                    className="bg-primary/5 border-primary/20 flex items-center gap-1"
                  >
                    <Icon className="w-3 h-3" />
                    {climateLabels[climate]}
                  </Badge>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">No climate preferences</p>
          )}
        </div>

        {/* Language */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Languages className="w-4 h-4 text-primary" />
            <h4 className="text-sm font-medium">Language Preferences</h4>
          </div>
          {constraints.language_preferences && constraints.language_preferences.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {constraints.language_preferences.map((lang, i) => (
                <Badge key={i} variant="outline" className="bg-accent/5 border-accent/20">
                  {lang}
                </Badge>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">No language preferences</p>
          )}
        </div>

        {!hasConstraints && (
          <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-lg border border-dashed">
            <Info className="w-4 h-4 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">No special requirements specified</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
