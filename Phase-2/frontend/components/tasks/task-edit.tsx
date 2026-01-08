import { useState } from 'react';
import { api } from '../../lib/api';

interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
}

interface TaskEditProps {
  task: Task;
  onTaskUpdated: () => void;
  onCancel: () => void;
}

export default function TaskEdit({ task, onTaskUpdated, onCancel }: TaskEditProps) {
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || '');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.updateTask(task.id, title, description);
      if (response.success) {
        onTaskUpdated();
      } else {
        setError(response.error?.message || 'Failed to update task');
      }
    } catch (err) {
      setError('An error occurred while updating task');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div className="mb-3">
        <label htmlFor="edit-task-title" className="block text-sm font-medium text-gray-700 mb-1">
          Task Title *
        </label>
        <input
          type="text"
          id="edit-task-title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
          placeholder="What needs to be done?"
          required
        />
      </div>
      <div className="mb-3">
        <label htmlFor="edit-task-description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="edit-task-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
          placeholder="Add details..."
          rows={2}
        />
      </div>
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-3" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      <div className="flex space-x-2">
        <button
          type="submit"
          disabled={loading}
          className="px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Saving...' : 'Save'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}