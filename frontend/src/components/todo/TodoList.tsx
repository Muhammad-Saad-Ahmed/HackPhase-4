'use client';

/**
 * TodoList Component
 * Displays a list of todo items with filtering
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  getTasks,
  createTask,
  updateTask,
  completeTask,
  deleteTask,
  Task,
} from '../../services/taskApi';
import { TodoItem } from './TodoItem';
import { AddTodoForm } from './AddTodoForm';
import { eventBus, EVENTS } from '../../services/eventBus';

type FilterType = 'all' | 'pending' | 'completed';

export const TodoList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState<FilterType>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncIndicator, setSyncIndicator] = useState<string | null>(null);

  // Fetch tasks from API
  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getTasks(filter);
      setTasks(data);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      setError('Failed to load tasks. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  // Load tasks on mount and when filter changes
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Listen for chat events to refresh tasks
  useEffect(() => {
    const unsubscribe = eventBus.on(EVENTS.TASKS_REFRESH, () => {
      setSyncIndicator('Syncing with chat...');
      fetchTasks();
      // Auto-dismiss sync indicator
      setTimeout(() => setSyncIndicator(null), 2000);
    });

    return () => unsubscribe();
  }, [fetchTasks]);

  // Auto-dismiss error after 4 seconds
  useEffect(() => {
    if (!error) return;
    const t = setTimeout(() => setError(null), 4000);
    return () => clearTimeout(t);
  }, [error]);

  // Handle adding a new task
  const handleAddTask = async (title: string, description: string) => {
    try {
      await createTask({ title, description: description || undefined });
      await fetchTasks(); // Reload the list
    } catch (err) {
      console.error('Failed to create task:', err);
      setError('Failed to create task. Please try again.');
      throw err;
    }
  };

  // Handle completing a task
  const handleCompleteTask = async (taskId: number) => {
    try {
      await completeTask(taskId);
      await fetchTasks(); // Reload the list
    } catch (err) {
      console.error('Failed to complete task:', err);
      setError('Failed to complete task. Please try again.');
      throw err;
    }
  };

  // Handle deleting a task
  const handleDeleteTask = async (taskId: number) => {
    try {
      await deleteTask(taskId);
      // Remove from local state immediately for better UX
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      console.error('Failed to delete task:', err);
      setError('Failed to delete task. Please try again.');
      // Reload to sync state if delete failed
      await fetchTasks();
      throw err;
    }
  };

  // Handle editing a task
  const handleEditTask = async (taskId: number, title: string, description: string) => {
    try {
      await updateTask(taskId, {
        title: title || undefined,
        description: description || undefined,
      });
      await fetchTasks(); // Reload the list
    } catch (err) {
      console.error('Failed to update task:', err);
      setError('Failed to update task. Please try again.');
      throw err;
    }
  };

  const pendingCount = tasks.filter((t) => t.status === 'pending').length;
  const completedCount = tasks.filter((t) => t.status === 'completed').length;

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ margin: '0 0 8px 0', fontSize: '32px', fontWeight: 700 }}>
          My Tasks
        </h1>
        <p style={{ margin: 0, color: '#6c757d', fontSize: '14px' }}>
          {pendingCount} pending · {completedCount} completed
        </p>
      </div>

      {/* Sync Indicator from Chat */}
      {syncIndicator && (
        <div
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '10px 16px',
            borderRadius: '8px',
            marginBottom: '16px',
            fontSize: '13px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: '0 2px 8px rgba(102,126,234,0.3)',
          }}
        >
          <span style={{ fontSize: '16px', animation: 'spin 1s linear infinite' }}>⚡</span>
          {syncIndicator}
        </div>
      )}

      {/* Add Task Form */}
      <AddTodoForm onAdd={handleAddTask} />

      {/* Filter Tabs */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '20px',
          borderBottom: '2px solid #e0e0e0',
          paddingBottom: '8px',
        }}
      >
        {(['all', 'pending', 'completed'] as FilterType[]).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '8px 16px',
              background: filter === f ? '#007bff' : 'transparent',
              color: filter === f ? 'white' : '#6c757d',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 600,
              textTransform: 'capitalize',
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Error Message */}
      {error && (
        <div
          style={{
            background: '#f8d7da',
            color: '#721c24',
            padding: '12px 16px',
            borderRadius: '4px',
            marginBottom: '16px',
            border: '1px solid #f5c6cb',
          }}
        >
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6c757d' }}>
          Loading tasks...
        </div>
      )}

      {/* Empty State */}
      {!isLoading && tasks.length === 0 && (
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📝</div>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '20px', fontWeight: 600 }}>
            No tasks found
          </h3>
          <p style={{ margin: 0, color: '#6c757d', fontSize: '14px' }}>
            {filter === 'all'
              ? 'Add your first task above to get started!'
              : `No ${filter} tasks. Try changing the filter.`}
          </p>
        </div>
      )}

      {/* Task List */}
      {!isLoading && tasks.length > 0 && (
        <div>
          {tasks.map((task) => (
            <TodoItem
              key={task.id}
              task={task}
              onComplete={handleCompleteTask}
              onDelete={handleDeleteTask}
              onEdit={handleEditTask}
            />
          ))}
        </div>
      )}

      {/* Animation styles */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
