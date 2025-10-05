import { useEffect, useState } from 'react';
import { Workbox } from 'workbox-window';

export function usePWAUpdate() {
  const [needsUpdate, setNeedsUpdate] = useState(false);
  const [wb, setWb] = useState<Workbox | null>(null);

  useEffect(() => {
    if ('serviceWorker' in navigator) {
      const workbox = new Workbox('/sw.js');

      workbox.addEventListener('waiting', () => {
        setNeedsUpdate(true);
      });

      workbox.addEventListener('controlling', () => {
        window.location.reload();
      });

      workbox.register();
      setWb(workbox);
    }
  }, []);

  const updateAndReload = () => {
    if (wb) {
      wb.messageSkipWaiting();
    }
  };

  return {
    needsUpdate,
    updateAndReload,
  };
}
