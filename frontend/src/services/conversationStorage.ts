/**
 * Conversation Storage Service
 * Manages conversation_id persistence in localStorage
 */

const CONVERSATION_ID_KEY = 'chat_conversation_id';

/**
 * Get the stored conversation ID from localStorage
 * @returns The conversation ID if it exists, null otherwise
 */
export const getConversationId = (): string | null => {
  if (typeof window === 'undefined') {
    // Server-side rendering - no localStorage available
    return null;
  }

  try {
    return localStorage.getItem(CONVERSATION_ID_KEY);
  } catch (error) {
    console.error('Failed to read conversation ID from localStorage:', error);
    return null;
  }
};

/**
 * Store a conversation ID in localStorage
 * @param conversationId - The conversation ID to store
 */
export const setConversationId = (conversationId: string): void => {
  if (typeof window === 'undefined') {
    // Server-side rendering - no localStorage available
    return;
  }

  try {
    localStorage.setItem(CONVERSATION_ID_KEY, conversationId);
  } catch (error) {
    console.error('Failed to save conversation ID to localStorage:', error);
  }
};

/**
 * Clear the stored conversation ID from localStorage
 */
export const clearConversationId = (): void => {
  if (typeof window === 'undefined') {
    // Server-side rendering - no localStorage available
    return;
  }

  try {
    localStorage.removeItem(CONVERSATION_ID_KEY);
  } catch (error) {
    console.error('Failed to clear conversation ID from localStorage:', error);
  }
};

/**
 * Check if a conversation ID is stored
 * @returns True if a conversation ID exists, false otherwise
 */
export const hasConversationId = (): boolean => {
  return getConversationId() !== null;
};
