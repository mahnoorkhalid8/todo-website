'use client';

import { useState, useEffect } from 'react';
import { api } from '../../lib/api';

interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
}

interface TaskListProps {
  status?: 'all' | 'pending' | 'completed';
  onTaskUpdate?: () => void;
}

export default function TaskList({ status = 'all', onTaskUpdate }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTasks();
  }, [status]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await api.getTasks(status);
      if (response.success) {
        setTasks(response.data as Task[] || []);
      } else {
        setError(response.error?.message || 'Failed to load tasks');
      }
    } catch (err) {
      setError('An error occurred while loading tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = async (id: number, completed: boolean) => {
    try {
      const response = await api.toggleTaskCompletion(id, !completed);
      if (response.success) {
        if (onTaskUpdate) onTaskUpdate();
      } else {
        setError(response.error?.message || 'Failed to update task');
      }
    } catch (err) {
      setError('An error occurred while updating task');
      console.error(err);
    }
  };

  const handleDeleteTask = async (id: number) => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      const response = await api.deleteTask(id);
      if (response.success) {
        if (onTaskUpdate) onTaskUpdate();
      } else {
        setError(response.error?.message || 'Failed to delete task');
      }
    } catch (err) {
      setError('An error occurred while deleting task');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-2 text-gray-600">Loading tasks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-8">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by creating a new task.</p>
      </div>
    );
  }

  return (
    <ul className="bg-white shadow overflow-hidden rounded-md">
      {tasks.map((task) => (
        <li key={task.id} className="border-b border-gray-200 last:border-b-0">
          <div className="flex items-center justify-between p-4 hover:bg-gray-50">
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => handleToggleTask(task.id, task.completed)}
                className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <span
                className={`ml-3 text-sm font-medium ${task.completed ? 'text-gray-500 line-through' : 'text-gray-900'}`}
              >
                {task.title}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              {task.description && (
                <span className="text-sm text-gray-500 hidden md:inline">
                  {task.description.length > 50
                    ? `${task.description.substring(0, 50)}...`
                    : task.description}
                </span>
              )}
              <button
                onClick={() => handleDeleteTask(task.id)}
                className="text-red-600 hover:text-red-900 text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}