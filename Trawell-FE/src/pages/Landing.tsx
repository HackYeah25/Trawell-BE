import { useState } from 'react';
import { Plane, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { InstallButton } from '@/components/pwa/InstallButton';
import { AuthDialog } from '@/components/auth/AuthDialog';

export default function Landing() {
  const [showAuthDialog, setShowAuthDialog] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-warm flex flex-col">
      {/* Minimalist decorative landing */}
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="max-w-2xl mx-auto text-center space-y-8">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 rounded-3xl bg-white/20 backdrop-blur-sm flex items-center justify-center shadow-lg">
              <Plane className="w-10 h-10 text-white" />
            </div>
          </div>

          {/* Main heading with Pacifico */}
          <h1 className="text-5xl md:text-7xl font-pacifico text-white drop-shadow-lg">
            TraWell
          </h1>

          {/* Subheading */}
          <p className="text-xl md:text-2xl text-white/90 font-light">
            Your AI Travel Companion
          </p>

          {/* Decorative element */}
          <div className="flex items-center justify-center gap-2 text-white/80">
            <Sparkles className="w-5 h-5" />
            <span className="text-sm font-light">Plan, Discover, Explore</span>
            <Sparkles className="w-5 h-5" />
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-6">
            <Button
              size="lg"
              onClick={() => setShowAuthDialog(true)}
              className="bg-white text-primary hover:bg-white/90 font-medium text-lg px-8 shadow-xl hover:scale-105 transition-transform"
            >
              Start Planning
            </Button>
            <InstallButton 
              variant="outline" 
              size="lg"
              className="bg-white/10 backdrop-blur-sm text-white border-white/30 hover:bg-white/20 font-medium text-lg px-8"
            />
          </div>
        </div>
      </div>

      {/* Auth Dialog */}
      <AuthDialog open={showAuthDialog} onOpenChange={setShowAuthDialog} />
    </div>
  );
}
