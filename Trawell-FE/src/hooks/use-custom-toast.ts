import { useCustomToast } from '@/components/ui/custom-toast';

export const useToast = () => {
  const { toast } = useCustomToast();
  return toast;
};
