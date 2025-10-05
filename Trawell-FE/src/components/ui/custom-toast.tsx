import { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface CustomToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  description?: string;
  duration?: number;
  onClose: (id: string) => void;
}

const toastIcons = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertCircle,
  info: Info,
};

const toastStyles = {
  success: {
    container: 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200 shadow-green-100',
    icon: 'text-green-600',
    title: 'text-green-900',
    description: 'text-green-700',
  },
  error: {
    container: 'bg-gradient-to-r from-red-50 to-rose-50 border-red-200 shadow-red-100',
    icon: 'text-red-600',
    title: 'text-red-900',
    description: 'text-red-700',
  },
  warning: {
    container: 'bg-gradient-to-r from-amber-50 to-yellow-50 border-amber-200 shadow-amber-100',
    icon: 'text-amber-600',
    title: 'text-amber-900',
    description: 'text-amber-700',
  },
  info: {
    container: 'bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200 shadow-blue-100',
    icon: 'text-blue-600',
    title: 'text-blue-900',
    description: 'text-blue-700',
  },
};

export const CustomToast = ({ id, type, title, description, duration = 5000, onClose }: CustomToastProps) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);
  const Icon = toastIcons[type];
  const styles = toastStyles[type];

  useEffect(() => {
    // Animate in
    const timer = setTimeout(() => setIsVisible(true), 10);
    
    // Auto close
    if (duration > 0) {
      const autoCloseTimer = setTimeout(() => {
        handleClose();
      }, duration);
      
      return () => {
        clearTimeout(timer);
        clearTimeout(autoCloseTimer);
      };
    }
    
    return () => clearTimeout(timer);
  }, [duration]);

  const handleClose = () => {
    setIsLeaving(true);
    setTimeout(() => {
      onClose(id);
    }, 300);
  };

  return (
    <div
      className={cn(
        'relative max-w-sm w-full rounded-xl border-2 shadow-lg backdrop-blur-sm transition-all duration-300 ease-out transform',
        styles.container,
        isVisible && !isLeaving ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0',
        isLeaving && 'translate-x-full opacity-0'
      )}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <Icon className={cn('w-5 h-5', styles.icon)} />
          </div>
          
          <div className="flex-1 min-w-0">
            {title && (
              <p className={cn('text-sm font-semibold leading-5', styles.title)}>
                {title}
              </p>
            )}
            {description && (
              <p className={cn('text-sm mt-1 leading-5', styles.description)}>
                {description}
              </p>
            )}
          </div>
          
          <button
            onClick={handleClose}
            className={cn(
              'flex-shrink-0 p-1 rounded-lg transition-colors hover:bg-black/5',
              styles.icon
            )}
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

// Toast Manager
interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  description?: string;
  duration?: number;
}

class ToastManager {
  private toasts: Toast[] = [];
  private listeners: ((toasts: Toast[]) => void)[] = [];

  subscribe(listener: (toasts: Toast[]) => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notify() {
    this.listeners.forEach(listener => listener([...this.toasts]));
  }

  add(toast: Omit<Toast, 'id'>) {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = { ...toast, id };
    this.toasts.push(newToast);
    this.notify();
    return id;
  }

  remove(id: string) {
    this.toasts = this.toasts.filter(toast => toast.id !== id);
    this.notify();
  }

  clear() {
    this.toasts = [];
    this.notify();
  }
}

export const toastManager = new ToastManager();

// Hook for using toasts
export const useCustomToast = () => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const unsubscribe = toastManager.subscribe(setToasts);
    return unsubscribe;
  }, []);

  const toast = {
    success: (title: string, description?: string, duration?: number) => 
      toastManager.add({ type: 'success', title, description, duration }),
    error: (title: string, description?: string, duration?: number) => 
      toastManager.add({ type: 'error', title, description, duration }),
    warning: (title: string, description?: string, duration?: number) => 
      toastManager.add({ type: 'warning', title, description, duration }),
    info: (title: string, description?: string, duration?: number) => 
      toastManager.add({ type: 'info', title, description, duration }),
  };

  return { toasts, toast };
};

// Toast Container Component
export const CustomToastContainer = () => {
  const { toasts } = useCustomToast();

  return (
    <div className="fixed bottom-4 right-4 left-4 sm:left-auto sm:right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <CustomToast
          key={toast.id}
          {...toast}
          onClose={toastManager.remove}
        />
      ))}
    </div>
  );
};
