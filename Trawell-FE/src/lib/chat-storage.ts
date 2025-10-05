import { ChatMessage } from '@/types';

const STORAGE_KEY_PREFIX = 'travelai_chat_';

export function saveChatHistory(entityId: string, messages: ChatMessage[]) {
  try {
    localStorage.setItem(
      `${STORAGE_KEY_PREFIX}${entityId}`,
      JSON.stringify(messages)
    );
  } catch (error) {
    console.error('Failed to save chat history:', error);
  }
}

export function loadChatHistory(entityId: string): ChatMessage[] | null {
  try {
    const stored = localStorage.getItem(`${STORAGE_KEY_PREFIX}${entityId}`);
    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error('Failed to load chat history:', error);
    return null;
  }
}

export function clearChatHistory(entityId: string) {
  try {
    localStorage.removeItem(`${STORAGE_KEY_PREFIX}${entityId}`);
  } catch (error) {
    console.error('Failed to clear chat history:', error);
  }
}
