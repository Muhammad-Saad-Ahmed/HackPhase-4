'use client';

/**
 * TodoItem Component
 * Displays a single todo item with actions
 */
import React, { useState } from 'react';
import { Task } from '../../services/taskApi';

interface TodoItemProps {
  task: Task;
  onComplete: (taskId: number) => Promise<void>;
  onDelete: (taskId: number) => Promise<void>;
  onEdit: (taskId: number, title: string, description: string) => Promise<void>;
}

export const TodoItem: React.FC<TodoItemProps> = ({
  task,
  onComplete,
  onDelete,
  onEdit,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [isLoading, setIsLoading] = useState(false);

  const handleSaveEdit = async () => {
    setIsLoading(true);
    try {
      await onEdit(task.id, editTitle, editDescription);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleComplete = async () => {
    setIsLoading(true);
    try {
      await onComplete(task.id);
    } catch (error) {
      console.error('Failed to complete task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this task?')) {
      setIsLoading(true);
      try {
        await onDelete(task.id);
      } catch (error) {
        console.error('Failed to delete task:', error);
        setIsLoading(false);
      }
    }
  };

  if (isEditing) {
    return (
      <div
        style={{
          background: '#fff',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '12px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          border: '2px solid #007bff',
        }}
      >
        <input
          type="text"
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            marginBottom: '8px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '16px',
          }}
          disabled={isLoading}
        />
        <textarea
          value={editDescription}
          onChange={(e) => setEditDescription(e.target.value)}
          rows={3}
          style={{
            width: '100%',
            padding: '8px',
            marginBottom: '12px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '14px',
            resize: 'vertical',
          }}
          disabled={isLoading}
        />
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={handleSaveEdit}
            disabled={isLoading || !editTitle.trim()}
            style={{
              padding: '8px 16px',
              background: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              opacity: isLoading || !editTitle.trim() ? 0.6 : 1,
            }}
          >
            {isLoading ? 'Saving...' : 'Save'}
          </button>
          <button
            onClick={() => {
              setIsEditing(false);
              setEditTitle(task.title);
              setEditDescription(task.description || '');
            }}
            disabled={isLoading}
            style={{
              padding: '8px 16px',
              background: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              opacity: isLoading ? 0.6 : 1,
            }}
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        background: '#fff',
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '12px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        border: task.status === 'completed' ? '1px solid #28a745' : '1px solid #e0e0e0',
        opacity: task.status === 'completed' ? 0.7 : 1,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <h3
            style={{
              margin: '0 0 8px 0',
              fontSize: '18px',
              fontWeight: 600,
              textDecoration: task.status === 'completed' ? 'line-through' : 'none',
              color: task.status === 'completed' ? '#6c757d' : '#212529',
            }}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              style={{
                margin: '0 0 12px 0',
                fontSize: '14px',
                color: '#6c757d',
                lineHeight: 1.5,
              }}
            >
              {task.description}
            </p>
          )}
          <div style={{ fontSize: '12px', color: '#999' }}>
            Created: {new Date(task.created_at).toLocaleString()}
            {task.completed_at && (
              <span style={{ marginLeft: '12px' }}>
                | Completed: {new Date(task.completed_at).toLocaleString()}
              </span>
            )}
          </div>
        </div>

        {/* Status Badge */}
        <div
          style={{
            marginLeft: '12px',
            padding: '4px 12px',
            borderRadius: '12px',
            fontSize: '12px',
            fontWeight: 600,
            background: task.status === 'completed' ? '#d4edda' : '#fff3cd',
            color: task.status === 'completed' ? '#155724' : '#856404',
          }}
        >
          {task.status === 'completed' ? '✓ Completed' : '○ Pending'}
        </div>
      </div>

      {/* Action buttons */}
      <div style={{ marginTop: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {task.status === 'pending' && (
          <button
            onClick={handleComplete}
            disabled={isLoading}
            style={{
              padding: '6px 12px',
              background: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              fontSize: '13px',
              opacity: isLoading ? 0.6 : 1,
            }}
          >
            ✓ Complete
          </button>
        )}
        <button
          onClick={() => setIsEditing(true)}
          disabled={isLoading}
          style={{
            padding: '6px 12px',
            background: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontSize: '13px',
            opacity: isLoading ? 0.6 : 1,
          }}
        >
          ✎ Edit
        </button>
        <button
          onClick={handleDelete}
          disabled={isLoading}
          style={{
            padding: '6px 12px',
            background: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontSize: '13px',
            opacity: isLoading ? 0.6 : 1,
          }}
        >
          ✕ Delete
        </button>
      </div>
    </div>
  );
};
