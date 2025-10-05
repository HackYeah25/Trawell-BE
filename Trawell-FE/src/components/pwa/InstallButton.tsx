import { Download, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { usePWAInstall } from '@/hooks/use-pwa-install';
import { useState } from 'react';

interface InstallButtonProps {
  variant?: 'default' | 'outline' | 'secondary';
  size?: 'default' | 'sm' | 'lg';
  className?: string;
}

export function InstallButton({ variant = 'default', size = 'default', className }: InstallButtonProps) {
  const { isInstallable, isInstalled, installPWA } = usePWAInstall();
  const [isInstalling, setIsInstalling] = useState(false);

  const handleInstall = async () => {
    setIsInstalling(true);
    await installPWA();
    setIsInstalling(false);
  };

  if (isInstalled) {
    return (
      <Button variant="outline" size={size} className={className} disabled>
        <Check className="w-4 h-4 mr-2" />
        Installed
      </Button>
    );
  }

  if (!isInstallable) {
    return null;
  }

  return (
    <Button
      variant={variant}
      size={size}
      className={className}
      onClick={handleInstall}
      disabled={isInstalling}
    >
      <Download className="w-4 h-4 mr-2" />
      {isInstalling ? 'Installing...' : 'Install App'}
    </Button>
  );
}
