import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { MapPin, Heart, Sparkles } from 'lucide-react';
import type { UserProfile } from '@/types/profile';

interface ExperienceTabsProps {
  experience: UserProfile['experience'];
}

export function ExperienceTabs({ experience }: ExperienceTabsProps) {
  const pastDestinations = experience.past_destinations || [];
  const wishlist = experience.wishlist_regions || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Travel Experience</CardTitle>
        <CardDescription>Places you've been and want to visit</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="past" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="past" className="flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              Past Destinations
            </TabsTrigger>
            <TabsTrigger value="wishlist" className="flex items-center gap-2">
              <Heart className="w-4 h-4" />
              Wishlist
            </TabsTrigger>
          </TabsList>

          <TabsContent value="past" className="mt-4 space-y-3">
            {pastDestinations.length > 0 ? (
              pastDestinations.map((dest, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-gradient-to-r from-primary/5 to-accent/5 border border-primary/10 hover:border-primary/30 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-sunset flex items-center justify-center flex-shrink-0">
                      <MapPin className="w-5 h-5 text-primary-foreground" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-foreground">{dest.name}</h4>
                      {dest.highlight && (
                        <p className="text-sm text-muted-foreground mt-1 flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          {dest.highlight}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <MapPin className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm italic">No past destinations added yet</p>
                <p className="text-xs mt-1">Share your travel history to get better recommendations</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="wishlist" className="mt-4">
            {wishlist.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {wishlist.map((region, i) => (
                  <Badge
                    key={i}
                    variant="outline"
                    className="px-3 py-2 text-sm bg-gradient-to-r from-accent/10 to-primary/10 border-accent/20 hover:from-accent/20 hover:to-primary/20 transition-colors cursor-pointer"
                  >
                    <Heart className="w-3 h-3 mr-1 fill-current" />
                    {region}
                  </Badge>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Heart className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm italic">No wishlist destinations yet</p>
                <p className="text-xs mt-1">Add places you dream of visiting</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
