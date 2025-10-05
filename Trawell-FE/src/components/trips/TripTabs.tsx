import { MessageSquare, ClipboardList } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface TripTabsProps {
  activeTab: 'chat' | 'summary';
  onTabChange: (tab: 'chat' | 'summary') => void;
  chatContent: React.ReactNode;
  summaryContent: React.ReactNode;
}

export function TripTabs({ activeTab, onTabChange, chatContent, summaryContent }: TripTabsProps) {
  return (
    <Tabs value={activeTab} onValueChange={(v) => onTabChange(v as 'chat' | 'summary')} className="flex-1 flex flex-col min-h-0">
      <TabsList className="grid w-full max-w-4xl mx-auto grid-cols-2 flex-shrink-0">
        <TabsTrigger value="chat" className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4" />
          <span>Chat</span>
        </TabsTrigger>
        <TabsTrigger value="summary" className="flex items-center gap-2">
          <ClipboardList className="h-4 w-4" />
          <span>Summary</span>
        </TabsTrigger>
      </TabsList>

      {activeTab === 'chat' && <TabsContent value="chat" className="flex-1 flex flex-col mt-0 min-h-0">
        {chatContent}
      </TabsContent>  }

      {activeTab === 'summary' && <TabsContent value="summary" className="flex-1 mt-0 overflow-y-auto p-4 min-h-0">
        {summaryContent}
      </TabsContent>}
    </Tabs>
  );
}
