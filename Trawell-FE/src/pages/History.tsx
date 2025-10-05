import { useNavigate } from 'react-router-dom';
import { Plus, FolderKanban, Calendar, ChevronRight, Palmtree, Users as UsersIcon, MapPin, Grid3X3 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useUser } from '@/api/hooks/use-user';
import { AppShell } from '@/components/layout/AppShell';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useCreateProject, useJoinProject, useProjects } from '@/api/hooks/use-projects';
import { useBrainstormSessions, useCreateBrainstormSession } from '@/api/hooks/use-brainstorm';
import { useProjectTrips } from '@/api/hooks/use-trips';
import { useBrainstormTrips } from '@/api/hooks/use-brainstorm';
import { Skeleton } from '@/components/ui/skeleton';
import { useState } from 'react';
import { ProjectTypeDialog } from '@/components/projects/ProjectTypeDialog';
import { AdventureTrips } from '@/components/adventures/AdventureTrips';
import { useToast } from '@/hooks/use-custom-toast';

export default function History() {
  const navigate = useNavigate();
  const { data: user } = useUser();
  const toast = useToast();
  const { data: brainstormSessions, isLoading: brainstormLoading } = useBrainstormSessions();
  const { data: projects, isLoading: projectsLoading } = useProjects();
  const createProjectMutation = useCreateProject();
  const createBrainstormMutation = useCreateBrainstormSession();
  const joinProjectMutation = useJoinProject();
  const [showProjectTypeDialog, setShowProjectTypeDialog] = useState(false);
  const [expandedAdventures, setExpandedAdventures] = useState<Set<string>>(new Set());

  const handleSelectProjectType = (isShared: boolean) => {
    setShowProjectTypeDialog(false);

    if (isShared) {
      // Use old project system for shared adventures
      createProjectMutation.mutate(
        { title: 'New Project', isShared },
        {
          onSuccess: (result) => {
            if (result.shareCode) {
              toast.success('Projekt utworzony!', `Kod udostępniania: ${result.shareCode}`);
            } else {
              toast.success('Projekt utworzony!', 'Przechodzisz do nowego projektu');
            }
            navigate(`/app/projects/${result.id}`);
          },
        }
      );
    } else {
      // Use new brainstorm system for solo adventures
      createBrainstormMutation.mutate(undefined, {
        onSuccess: (result) => {
          toast.success('Nowa sesja!', 'Rozpoczynasz nową przygodę');
          navigate(`/app/brainstorm/${result.session_id}`);
        },
        onError: () => {
          toast.error('Błąd tworzenia', 'Nie udało się utworzyć sesji');
        },
      });
    }
  };

  const handleJoinProject = (shareCode: string) => {
    joinProjectMutation.mutate(
      { shareCode },
      {
        onSuccess: () => {
          setShowProjectTypeDialog(false);
          toast.success('Dołączono do przygody!', 'Przygoda została dodana do Twojej listy');
        },
        onError: () => {
          toast.error('Nieprawidłowy kod', 'Sprawdź kod i spróbuj ponownie');
        },
      }
    );
  };

  const toggleAdventureExpansion = (adventureId: string) => {
    setExpandedAdventures(prev => {
      const newSet = new Set(prev);
      if (newSet.has(adventureId)) {
        newSet.delete(adventureId);
      } else {
        newSet.add(adventureId);
      }
      return newSet;
    });
  };

  // Component to show trip count indicator
  const TripCountIndicator = ({ adventureId, adventureType }: { adventureId: string; adventureType: 'project' | 'brainstorm' }) => {
    const { data: projectTrips } = useProjectTrips(adventureType === 'project' ? adventureId : '');
    const { data: brainstormTrips } = useBrainstormTrips(adventureType === 'brainstorm' ? adventureId : '');
    
    const tripCount = adventureType === 'project' ? (projectTrips?.length || 0) : (brainstormTrips?.length || 0);
    
    if (tripCount === 0) return null;
    
    return (
      <div className="flex items-center gap-1 text-xs text-warm-coral ml-2">
        <MapPin className="w-3 h-3" />
        <span>{tripCount}</span>
      </div>
    );
  };

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto p-4 md:p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between gap-2 py-2">
          <h1 className="text-3xl font-pacifico bg-gradient-sunset bg-clip-text text-transparent leading-normal pb-2">Your Adventures</h1>
          <div className="flex gap-2">
            <Button 
              onClick={() => navigate('/app/gallery')}
              variant="outline"
              size="sm"
              className="sm:px-4"
            >
              <Grid3X3 className="w-4 h-4 sm:mr-2" />
              <span className="hidden sm:inline">All Trips</span>
            </Button>
            <Button 
              onClick={() => setShowProjectTypeDialog(true)}
              disabled={createProjectMutation.isPending}
              size="sm"
              className="bg-gradient-sunset hover:opacity-90 text-white shadow-warm border-0 sm:px-4"
            >
              <Plus className="w-4 h-4 sm:mr-2" />
              <span className="hidden sm:inline">New Adventure</span>
            </Button>
          </div>
        </div>

        {/* Combined list of projects and brainstorm sessions */}
        {(brainstormLoading || projectsLoading) ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-20" />
            ))}
          </div>
        ) : (!brainstormSessions || brainstormSessions.length === 0) && (!projects || projects.length === 0) ? (
          <Card className="p-12 text-center border-dashed border-warm-coral/30 bg-gradient-to-br from-warm-coral/5 to-warm-turquoise/5">
            <div className="w-20 h-20 rounded-full bg-gradient-sunset flex items-center justify-center mb-4 mx-auto shadow-warm">
              <Palmtree className="w-10 h-10 text-white" />
            </div>
            <p className="text-muted-foreground mb-4">You don't have any adventures yet</p>
            <Button
              onClick={() => setShowProjectTypeDialog(true)}
              disabled={createBrainstormMutation.isPending}
              className="bg-gradient-sunset hover:opacity-90 text-white shadow-warm border-0"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Adventure
            </Button>
          </Card>
        ) : (
          <div className="space-y-6">
            {/* Projects (shared adventures) */}
            {projects && projects.map((project) => {
              const isShared = project.isShared;
              const isExpanded = expandedAdventures.has(project.id);

              return (
                <div key={project.id} className="mb-6">
                  <Card
                    className={cn(
                      "border-warm-coral/20 bg-card/80 backdrop-blur-sm cursor-pointer hover:bg-warm-coral/5 transition-colors shadow-sm",
                      isShared && "border-warm-turquoise/40 bg-warm-turquoise/5"
                    )}
                    onClick={() => navigate(`/app/projects/${project.id}`)}
                  >
                    <div className="p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1">
                        <div className={cn(
                          "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 shadow-warm",
                          isShared
                            ? "bg-gradient-to-br from-warm-turquoise to-warm-turquoise/80"
                            : "bg-gradient-sunset"
                        )}>
                          {isShared ? (
                            <UsersIcon className="w-5 h-5 text-white" />
                          ) : (
                            <FolderKanban className="w-5 h-5 text-white" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-1">
                            <h3 className="font-semibold truncate sm:max-w-none max-w-[150px]">{project.title}</h3>
                            <TripCountIndicator adventureId={project.id} adventureType="project" />
                          </div>
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(project.createdAt).toLocaleDateString('en-US')}
                            {project.lastMessagePreview && (
                              <>
                                <span className="mx-1">•</span>
                                <span>Project</span>
                              </>
                            )}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {isShared && (
                          <Badge variant="secondary" className="text-xs hidden sm:inline-flex">
                            Shared
                          </Badge>
                        )}
                        <ChevronRight className="w-5 h-5 text-muted-foreground" />
                      </div>
                    </div>
                  </Card>
                  
                  {/* Trips list */}
                  <AdventureTrips
                    adventureId={project.id}
                    adventureType="project"
                    isExpanded={isExpanded}
                    onToggle={() => toggleAdventureExpansion(project.id)}
                  />
                </div>
              );
            })}

            {/* Brainstorm Sessions (solo adventures) */}
            {brainstormSessions && brainstormSessions.map((session) => {
              const isShared = session.isShared;
              const isExpanded = expandedAdventures.has(session.id);

              return (
                <div key={session.id} className="mb-6">
                  <Card
                    className={cn(
                      "border-warm-coral/20 bg-card/80 backdrop-blur-sm cursor-pointer hover:bg-warm-coral/5 transition-colors shadow-sm",
                      isShared && "border-warm-turquoise/40 bg-warm-turquoise/5"
                    )}
                    onClick={() => navigate(`/app/brainstorm/${session.id}`)}
                  >
                    <div className="p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1">
                        <div className={cn(
                          "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 shadow-warm",
                          isShared
                            ? "bg-gradient-to-br from-warm-turquoise to-warm-turquoise/80"
                            : "bg-gradient-sunset"
                        )}>
                          {isShared ? (
                            <UsersIcon className="w-5 h-5 text-white" />
                          ) : (
                            <FolderKanban className="w-5 h-5 text-white" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-1">
                            <h3 className="font-semibold truncate sm:max-w-none max-w-[150px]">{session.title}</h3>
                            <TripCountIndicator adventureId={session.id} adventureType="brainstorm" />
                          </div>
                          <p className="text-xs text-muted-foreground flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(session.createdAt).toLocaleDateString('en-US')}
                            <span className="mx-1">•</span>
                            {session.messageCount} {session.messageCount === 1 ? 'message' : 'messages'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {isShared && (
                          <Badge variant="secondary" className="text-xs hidden sm:inline-flex">
                            Shared
                          </Badge>
                        )}
                        <ChevronRight className="w-5 h-5 text-muted-foreground" />
                      </div>
                    </div>
                  </Card>
                  
                  {/* Trips list */}
                  <AdventureTrips
                    adventureId={session.id}
                    adventureType="brainstorm"
                    isExpanded={isExpanded}
                    onToggle={() => toggleAdventureExpansion(session.id)}
                  />
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Dialogs */}
      <ProjectTypeDialog
        open={showProjectTypeDialog}
        onOpenChange={setShowProjectTypeDialog}
        onSelectType={handleSelectProjectType}
        onJoinProject={handleJoinProject}
        isJoining={joinProjectMutation.isPending}
      />
    </AppShell>
  );
}
