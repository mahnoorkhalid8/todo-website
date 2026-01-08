import { useState } from 'react';
import { api } from '../../lib/api';

interface TaskDeleteProps {
  taskId: number;
  onTaskDeleted: () => void;
  onCancel: () => void;
}

export default function TaskDelete({ taskId, onTaskDeleted, onCancel }: TaskDeleteProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDelete = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await api.deleteTask(taskId);
      if (response.success) {
        onTaskDeleted();
      } else {
        setError(response.error?.message || 'Failed to delete task');
      }
    } catch (err) {
      setError('An error occurred while deleting task');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
      <h3 className="text-lg font-medium text-red-800">Confirm Deletion</h3>
      <p className="mt-1 text-sm text-red-600">
        Are you sure you want to delete this task? This action cannot be undone.
      </p>
      {error && (
        <div className="mt-2 bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      <div className="mt-3 flex space-x-2">
        <button
          type="button"
          onClick={handleDelete}
          disabled={loading}
          className="px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 disabled:opacity-50"
        >
          {loading ? 'Deleting...' : 'Delete'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}