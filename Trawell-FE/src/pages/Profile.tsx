import { AppShell } from '@/components/layout/AppShell';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowLeft, AlertCircle, Info } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useProfile } from '@/api/hooks/use-profile';
import { ProfileHeader } from '@/components/profile/ProfileHeader';
import { PersonaCard } from '@/components/profile/PersonaCard';
import { PreferencesGrid } from '@/components/profile/PreferencesGrid';
import { ConstraintsCard } from '@/components/profile/ConstraintsCard';
import { ExperienceTabs } from '@/components/profile/ExperienceTabs';

export default function Profile() {
  const navigate = useNavigate();
  const { data: profile, isLoading, error, refetch } = useProfile();

  // Loading state
  if (isLoading) {
    return (
      <AppShell>
        <div className="max-w-5xl mx-auto p-4 md:p-6 space-y-6">
          <Button variant="ghost" onClick={() => navigate('/app')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Projects
          </Button>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-6">
                <Skeleton className="h-24 w-24 rounded-full" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-8 w-48" />
                  <Skeleton className="h-4 w-64" />
                </div>
                <Skeleton className="h-24 w-24 rounded-full" />
              </div>
            </CardContent>
          </Card>

          {[1, 2, 3].map(i => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-40" />
                <Skeleton className="h-4 w-64" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-32 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </AppShell>
    );
  }

  // Error state
  if (error) {
    return (
      <AppShell>
        <div className="max-w-5xl mx-auto p-4 md:p-6 space-y-6">
          <Button variant="ghost" onClick={() => navigate('/app')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Projects
          </Button>

          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between">
              <span>Failed to load profile data. Please try again.</span>
              <Button variant="outline" size="sm" onClick={() => refetch()}>
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        </div>
      </AppShell>
    );
  }

  if (!profile) return null;

  const completenessPercent = Math.round(profile.completeness * 100);
  const needsImprovement = profile.completeness < 0.8;

  return (
    <AppShell>
      <div className="max-w-5xl mx-auto p-4 md:p-6 space-y-6">
        {/* Back button */}
        <Button
          variant="ghost"
          onClick={() => navigate('/app')}
          className="hover:bg-primary/10"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Projects
        </Button>

        {/* Profile Header */}
        <ProfileHeader
          name={profile.name || 'Traveler'}
          personaLabel={profile.insights?.personaLabel}
          completeness={profile.completeness}
          topTags={profile.insights?.topTags}
          updatedAt={profile.updatedAt}
        />

        {/* Completeness hint */}
        {needsImprovement && (
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              Your profile is {completenessPercent}% complete. Add more details to get better 
              personalized recommendations!
            </AlertDescription>
          </Alert>
        )}

        {/* Persona Summary */}
        <PersonaCard
          summaryMarkdown={profile.insights?.summaryMarkdown}
          onEdit={() => navigate('/onboarding')}
        />

        {/* Travel Preferences */}
        <PreferencesGrid preferences={profile.preferences} />

        {/* Constraints */}
        <ConstraintsCard constraints={profile.constraints} />

        {/* Experience & Wishlist */}
        <ExperienceTabs experience={profile.experience} />

        {/* Additional hints */}
        {needsImprovement && (
          <Card className="bg-muted/30">
            <CardHeader>
              <CardTitle className="text-lg">Boost Your Profile</CardTitle>
              <CardDescription>
                Add these details to improve recommendations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {!profile.preferences.traveler_type && (
                <p className="text-muted-foreground">• Define your traveler type</p>
              )}
              {!profile.experience.past_destinations?.length && (
                <p className="text-muted-foreground">• Add past destinations</p>
              )}
              {!profile.experience.wishlist_regions?.length && (
                <p className="text-muted-foreground">• Share your wishlist destinations</p>
              )}
              {!profile.constraints.dietary_restrictions?.length && 
               !profile.constraints.mobility_limitations?.length && (
                <p className="text-muted-foreground">• Specify any travel constraints</p>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
