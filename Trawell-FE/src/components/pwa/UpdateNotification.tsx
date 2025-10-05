import { useEffect } from 'react';
import { toast } from 'sonner';
import { usePWAUpdate } from '@/hooks/use-pwa-update';
import { RefreshCw } from 'lucide-react';

export function UpdateNotification() {
  const { needsUpdate, updateAndReload } = usePWAUpdate();

  useEffect(() => {
    if (needsUpdate) {
      toast.success('New version available!', {
        description: 'Click to reload and get the latest features',
        duration: 10000,
        action: {
          label: 'Reload',
          onClick: updateAndReload,
        },
        icon: <RefreshCw className="w-4 h-4" />,
      });
    }
  }, [needsUpdate, updateAndReload]);

  return null;
}
