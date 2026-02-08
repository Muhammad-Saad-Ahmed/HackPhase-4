'use client';

/**
 * AddTodoForm Component
 * Form for adding new todo items
 */
import React, { useState } from 'react';

interface AddTodoFormProps {
  onAdd: (title: string, description: string) => Promise<void>;
}

export const AddTodoForm: React.FC<AddTodoFormProps> = ({ onAdd }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      return;
    }

    setIsLoading(true);
    try {
      await onAdd(title.trim(), description.trim());
      setTitle('');
      setDescription('');
    } catch (error) {
      console.error('Failed to add task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '24px' }}>
      <div
        style={{
          background: '#fff',
          borderRadius: '8px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        }}
      >
        <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600 }}>
          Add New Task
        </h3>

        <div style={{ marginBottom: '12px' }}>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Task title *"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '16px',
              boxSizing: 'border-box',
            }}
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Task description (optional)"
            rows={3}
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '14px',
              resize: 'vertical',
              boxSizing: 'border-box',
            }}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !title.trim()}
          style={{
            padding: '12px 24px',
            background: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading || !title.trim() ? 'not-allowed' : 'pointer',
            fontSize: '16px',
            fontWeight: 600,
            opacity: isLoading || !title.trim() ? 0.6 : 1,
            width: '100%',
          }}
        >
          {isLoading ? 'Adding...' : '+ Add Task'}
        </button>
      </div>
    </form>
  );
};
