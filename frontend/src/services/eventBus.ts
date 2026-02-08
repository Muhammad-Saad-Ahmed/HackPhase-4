/**
 * Event Bus for Component Communication
 * Enables chat and todo list to sync without tight coupling
 */

type EventCallback = (data?: any) => void;

class EventBus {
  private events: Map<string, Set<EventCallback>> = new Map();

  /**
   * Subscribe to an event
   */
  on(event: string, callback: EventCallback): () => void {
    if (!this.events.has(event)) {
      this.events.set(event, new Set());
    }
    this.events.get(event)!.add(callback);

    // Return unsubscribe function
    return () => this.off(event, callback);
  }

  /**
   * Unsubscribe from an event
   */
  off(event: string, callback: EventCallback): void {
    const callbacks = this.events.get(event);
    if (callbacks) {
      callbacks.delete(callback);
    }
  }

  /**
   * Emit an event
   */
  emit(event: string, data?: any): void {
    const callbacks = this.events.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  /**
   * Clear all event listeners
   */
  clear(): void {
    this.events.clear();
  }
}

// Export singleton instance
export const eventBus = new EventBus();

// Event types
export const EVENTS = {
  TASK_CREATED: 'task:created',
  TASK_UPDATED: 'task:updated',
  TASK_COMPLETED: 'task:completed',
  TASK_DELETED: 'task:deleted',
  TASKS_REFRESH: 'tasks:refresh',
  CHAT_TOOL_EXECUTED: 'chat:tool_executed',
} as const;
