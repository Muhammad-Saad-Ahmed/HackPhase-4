/**
 * Task API Service
 * Handles all task-related API calls
 */

import { apiClient } from './api-client';

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: 'pending' | 'completed';
  created_at: string;
  completed_at: string | null;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
}

/**
 * Get list of tasks with optional filtering
 */
export async function getTasks(
  status: 'all' | 'pending' | 'completed' = 'all',
  limit: number = 50,
  offset: number = 0
): Promise<Task[]> {
  const params = new URLSearchParams({
    status,
    limit: limit.toString(),
    offset: offset.toString(),
  });

  const response = await apiClient.get<Task[]>(`/v1/tasks?${params.toString()}`);
  return response;
}

/**
 * Get a specific task by ID
 */
export async function getTask(taskId: number): Promise<Task> {
  const response = await apiClient.get<Task>(`/v1/tasks/${taskId}`);
  return response;
}

/**
 * Create a new task
 */
export async function createTask(taskData: CreateTaskRequest): Promise<Task> {
  const response = await apiClient.post<Task>('/v1/tasks', taskData);
  return response;
}

/**
 * Update an existing task
 */
export async function updateTask(
  taskId: number,
  taskData: UpdateTaskRequest
): Promise<Task> {
  const response = await apiClient.put<Task>(`/v1/tasks/${taskId}`, taskData);
  return response;
}

/**
 * Mark a task as completed
 */
export async function completeTask(taskId: number): Promise<Task> {
  const response = await apiClient.patch<Task>(`/v1/tasks/${taskId}/complete`);
  return response;
}

/**
 * Delete a task
 */
export async function deleteTask(taskId: number): Promise<void> {
  await apiClient.delete<void>(`/v1/tasks/${taskId}`);
}
