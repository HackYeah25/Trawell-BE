import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { 
  Compass, 
  Activity, 
  Hotel, 
  Trees, 
  Building, 
  Waves, 
  Mountain, 
  Wallet, 
  Landmark, 
  UtensilsCrossed,
  HelpCircle
} from 'lucide-react';
import type { UserProfile } from '@/types/profile';

interface PreferencesGridProps {
  preferences: UserProfile['preferences'];
}

const preferenceConfig = {
  traveler_type: {
    icon: Compass,
    label: 'Traveler Type',
    values: {
      explorer: { label: 'Explorer', tooltip: 'Loves discovering new places and experiences' },
      relaxer: { label: 'Relaxer', tooltip: 'Prefers peaceful, laid-back vacations' },
      mixed: { label: 'Mixed', tooltip: 'Balances adventure with relaxation' }
    }
  },
  activity_level: {
    icon: Activity,
    label: 'Activity Level',
    values: {
      low: { label: 'Low', tooltip: 'Gentle pace, minimal physical demands' },
      medium: { label: 'Medium', tooltip: 'Moderate activities, balanced schedule' },
      high: { label: 'High', tooltip: 'Action-packed, physically demanding' }
    }
  },
  accommodation_style: {
    icon: Hotel,
    label: 'Accommodation',
    values: {
      all_inclusive: { label: 'All-Inclusive', tooltip: 'Full-service resorts with everything included' },
      boutique: { label: 'Boutique', tooltip: 'Unique, stylish, personalized hotels' },
      hostel: { label: 'Budget/Hostel', tooltip: 'Affordable, social accommodations' },
      mixed: { label: 'Mixed', tooltip: 'Varies by destination' }
    }
  },
  environment: {
    icon: Trees,
    label: 'Environment',
    values: {
      city: { label: 'City', tooltip: 'Urban exploration, culture, nightlife' },
      nature: { label: 'Nature', tooltip: 'Forests, parks, wildlife' },
      beach: { label: 'Beach', tooltip: 'Coastal, water activities' },
      mountains: { label: 'Mountains', tooltip: 'Alpine, hiking, scenic views' },
      mixed: { label: 'Mixed', tooltip: 'Variety of settings' }
    },
    icons: {
      city: Building,
      nature: Trees,
      beach: Waves,
      mountains: Mountain,
      mixed: Trees
    }
  },
  budget_sensitivity: {
    icon: Wallet,
    label: 'Budget Sensitivity',
    values: {
      low: { label: 'Low', tooltip: 'Price is not a major concern' },
      medium: { label: 'Medium', tooltip: 'Balance value and quality' },
      high: { label: 'High', tooltip: 'Very price-conscious' }
    }
  },
  culture_interest: {
    icon: Landmark,
    label: 'Cultural Interest',
    values: {
      low: { label: 'Low', tooltip: 'Minimal focus on museums, history' },
      medium: { label: 'Medium', tooltip: 'Some cultural activities' },
      high: { label: 'High', tooltip: 'Deep dive into local culture' }
    }
  },
  food_importance: {
    icon: UtensilsCrossed,
    label: 'Food Importance',
    values: {
      low: { label: 'Low', tooltip: 'Food is functional' },
      medium: { label: 'Medium', tooltip: 'Enjoy good meals' },
      high: { label: 'High', tooltip: 'Culinary experiences are essential' }
    }
  }
};

export function PreferencesGrid({ preferences }: PreferencesGridProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Travel Preferences</CardTitle>
        <CardDescription>Your ideal travel style and priorities</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(preferenceConfig).map(([key, config]) => {
            const value = preferences[key as keyof typeof preferences] as string;
            const valueConfig = value ? config.values[value as keyof typeof config.values] : null;
            
            // Special handling for environment icons
            let Icon = config.icon;
            if (key === 'environment' && value && 'icons' in config) {
              const envIcons = config.icons as Record<string, typeof Trees>;
              Icon = envIcons[value] || config.icon;
            }

            return (
              <TooltipProvider key={key}>
                <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50 border border-border">
                  <div className="w-10 h-10 rounded-lg bg-gradient-sunset flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-primary-foreground" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-muted-foreground mb-1">
                      {config.label}
                    </p>
                    {value && valueConfig ? (
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <div className="flex items-center gap-1 cursor-help">
                            <Badge variant="secondary" className="text-xs">
                              {valueConfig.label}
                            </Badge>
                            <HelpCircle className="w-3 h-3 text-muted-foreground" />
                          </div>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p className="text-xs">{valueConfig.tooltip}</p>
                        </TooltipContent>
                      </Tooltip>
                    ) : (
                      <p className="text-xs text-muted-foreground italic">Not set</p>
                    )}
                  </div>
                </div>
              </TooltipProvider>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
