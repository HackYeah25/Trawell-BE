import { Toaster } from "@/components/ui/toaster";
import { CustomToastContainer } from "@/components/ui/custom-toast";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useUser } from "./api/hooks/use-user";
import { UpdateNotification } from "./components/pwa/UpdateNotification";

import Landing from "./pages/Landing";
import Onboarding from "./pages/Onboarding";
import History from "./pages/History";
import Profile from "./pages/Profile";
import ProjectView from "./pages/ProjectView";
import TripView from "./pages/TripView";
import TripLiveChat from "./pages/TripLiveChat";
import TripGallery from "./pages/TripGallery";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 30000,
      refetchOnWindowFocus: false,
    },
  },
});

function AppRoutes() {
  const { data: user, isLoading } = useUser();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-warm">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center animate-pulse">
            <span className="text-2xl">✈️</span>
          </div>
          <p className="text-white/80">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to onboarding if not completed
  const needsOnboarding = user && !user.onboardingCompleted;

  return (
    <Routes>
      <Route path="/" element={user ? <Navigate to="/app" replace /> : <Landing />} />
      <Route
        path="/onboarding"
        element={
          !user ? (
            <Navigate to="/" replace />
          ) : needsOnboarding ? (
            <Onboarding />
          ) : (
            <Navigate to="/app" replace />
          )
        }
      />
      <Route
        path="/app"
        element={
          !user ? (
            <Navigate to="/" replace />
          ) : needsOnboarding ? (
            <Navigate to="/onboarding" replace />
          ) : (
            <History />
          )
        }
      />
      <Route
        path="/app/profile"
        element={user && !needsOnboarding ? <Profile /> : <Navigate to="/" replace />}
      />
      <Route
        path="/app/projects/:projectId"
        element={user && !needsOnboarding ? <ProjectView /> : <Navigate to="/" replace />}
      />
      <Route
        path="/app/brainstorm/:sessionId"
        element={user && !needsOnboarding ? <ProjectView /> : <Navigate to="/" replace />}
      />
      <Route
        path="/app/trips/:tripId"
        element={user && !needsOnboarding ? <TripView /> : <Navigate to="/" replace />}
      />
      <Route
        path="/app/trips/:tripId/live"
        element={user && !needsOnboarding ? <TripLiveChat /> : <Navigate to="/" replace />}
      />
      <Route
        path="/app/gallery"
        element={user && !needsOnboarding ? <TripGallery /> : <Navigate to="/" replace />}
      />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <UpdateNotification />
      <Toaster />
      <CustomToastContainer />
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
