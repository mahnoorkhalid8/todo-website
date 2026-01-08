import { useState } from 'react';
import { api } from '../../lib/api';

interface TaskToggleProps {
  taskId: number;
  currentStatus: boolean;
  onStatusChanged: () => void;
}

export default function TaskToggle({ taskId, currentStatus, onStatusChanged }: TaskToggleProps) {
  const [status, setStatus] = useState(currentStatus);
  const [loading, setLoading] = useState(false);

  const toggleStatus = async () => {
    setLoading(true);
    try {
      const response = await api.toggleTaskCompletion(taskId, !status);
      if (response.success) {
        setStatus(!status);
        onStatusChanged();
      }
    } catch (err) {
      console.error('Error toggling task completion:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={toggleStatus}
      disabled={loading}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
        status ? 'bg-green-600' : 'bg-gray-300'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          status ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  );
}