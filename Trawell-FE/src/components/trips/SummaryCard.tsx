import { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Cloud,
  Shield,
  DollarSign,
  Plane,
  Users,
  FileText,
  Globe,
  Hotel,
  Utensils,
  MapPin,
  Calendar,
  Home,
  ShoppingBag,
  ListChecks,
  AlertCircle,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { TripSummarySection, SummaryCategory, Attraction } from '@/types';

const categoryIcons: Record<SummaryCategory, LucideIcon> = {
  'Pogoda': Cloud,
  'Weather': Cloud,
  'Bezpieczeństwo': Shield,
  'Safety': Shield,
  'Budżet/koszty': DollarSign,
  'Budget': DollarSign,
  'Transport/Dojezdność': Plane,
  'Transport': Plane,
  'Sezonowość/Tłok': Calendar,
  'Formalności': FileText,
  'Kultura/Obyczaje': Users,
  'Noclegi': Home,
  'Jedzenie': Utensils,
  'Atrakcje': MapPin,
  'Attractions': MapPin,
  'Hotele': Home,
  'Hotels': Home,
  'Loty': Plane,
  'Flights': Plane,
  'Terminy': Calendar,
  'Dates': Calendar,
  'Lokalizacja': MapPin,
  'Location': MapPin,
  'Opis': FileText,
  'Description': FileText,
  'Co zabrać': ShoppingBag,
  'Packing': ShoppingBag,
  'Dokumenty': FileText,
  'Documents': FileText,
  'Checklista': ListChecks,
  'Checklist': ListChecks,
  'Najważniejsze': AlertCircle,
  'Key Info': AlertCircle,
};

interface SummaryCardProps {
  section: TripSummarySection;
  attractions?: Attraction[];
}

export const SummaryCard = memo(function SummaryCard({ section, attractions }: SummaryCardProps) {
  const Icon = categoryIcons[section.category] || FileText;
  const isAttractionsSection = section.category === 'Attractions' || section.category === 'Atrakcje';
  const ratedAttractions = attractions?.filter(a => a.status === 'rated' && a.rating && a.rating >= 2) || [];

  return (
    <Card className="overflow-hidden transition-shadow hover:shadow-warm border-warm-coral/20">
      <CardHeader className="bg-gradient-to-r from-warm-coral/10 to-warm-turquoise/10 border-b border-warm-coral/20">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-sunset flex items-center justify-center flex-shrink-0 shadow-warm">
              <Icon className="w-5 h-5 text-white" />
            </div>
            <CardTitle className="text-lg">{section.title}</CardTitle>
          </div>
          {section.important && (
            <Badge variant="destructive" className="bg-warm-coral">
              Ważne!
            </Badge>
          )}
        </div>
        {section.tags && section.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {section.tags.map((tag, idx) => (
              <Badge key={idx} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </CardHeader>
      <CardContent className="p-6">
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              img: ({ src, alt }) => (
                <img
                  src={src}
                  alt={alt}
                  className="rounded-lg w-full h-48 object-cover my-4 shadow-md"
                />
              ),
              h3: ({ children }) => (
                <h3 className="text-lg font-semibold mt-4 mb-2 text-foreground">{children}</h3>
              ),
              ul: ({ children }) => (
                <ul className="list-disc list-inside space-y-1 my-2">{children}</ul>
              ),
              li: ({ children }) => (
                <li className="text-muted-foreground">{children}</li>
              ),
              p: ({ children }) => (
                <p className="text-muted-foreground my-2">{children}</p>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-foreground">{children}</strong>
              ),
              hr: () => (
                <hr className="my-4 border-warm-coral/20" />
              ),
            }}
          >
            {section.markdown}
          </ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  );
});
