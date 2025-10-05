import { useState, useMemo, useCallback } from 'react';
import type { ChatMessage } from '@/types';

interface UseChatPaginationOptions {
  allMessages: ChatMessage[];
  pageSize?: number;
}

interface UseChatPaginationReturn {
  displayedMessages: ChatMessage[];
  hasMore: boolean;
  isLoadingMore: boolean;
  loadMore: () => void;
  remainingCount: number;
  reset: () => void;
}

export function useChatPagination({
  allMessages,
  pageSize = 10,
}: UseChatPaginationOptions): UseChatPaginationReturn {
  const [displayedCount, setDisplayedCount] = useState(pageSize);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  const displayedMessages = useMemo(() => {
    // Always show the last N messages (most recent ones)
    const startIndex = Math.max(0, allMessages.length - displayedCount);
    return allMessages.slice(startIndex);
  }, [allMessages, displayedCount]);

  const remainingCount = useMemo(() => {
    return Math.max(0, allMessages.length - displayedCount);
  }, [allMessages.length, displayedCount]);

  const hasMore = remainingCount > 0;

  const loadMore = useCallback(() => {
    if (isLoadingMore || !hasMore) return;

    setIsLoadingMore(true);

    // Simulate loading delay for smooth skeleton display
    setTimeout(() => {
      setDisplayedCount((prev) => Math.min(prev + pageSize, allMessages.length));
      setIsLoadingMore(false);
    }, 400);
  }, [isLoadingMore, hasMore, pageSize, allMessages.length]);

  const reset = useCallback(() => {
    setDisplayedCount(pageSize);
    setIsLoadingMore(false);
  }, [pageSize]);

  return {
    displayedMessages,
    hasMore,
    isLoadingMore,
    loadMore,
    remainingCount,
    reset,
  };
}
