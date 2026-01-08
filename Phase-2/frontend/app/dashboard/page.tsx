'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '../../lib/auth';
import { api } from '../../lib/api';

interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
  due_date: string | null;  // New field for due date
  user_id: string;
}

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [newTaskDueDate, setNewTaskDueDate] = useState<string>(''); // New state for due date
  const [showForm, setShowForm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null); // Track which task ID is being confirmed for deletion
  const [toast, setToast] = useState<{message: string, type: 'success' | 'error' | 'info'} | null>(null);
  const router = useRouter();

  // Check authentication on page load
  useEffect(() => {
    const checkAuth = async () => {
      if (!auth.isAuthenticated()) {
        router.push('/login');
        return;
      }

      // Try to fetch user info to verify token is still valid
      const user = auth.getUser();
      if (!user) {
        // Token exists but user info is missing, try to refresh or re-authenticate
        router.push('/login');
        return;
      }

      fetchTasks();
    };

    checkAuth();
  }, []);

  // Show toast notification
  const showToast = (message: string, type: 'success' | 'error' | 'info') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 3000); // Auto-hide after 3 seconds
  };

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await api.getTasks();
      if (response.success) {
        setTasks(response.data || []);
      } else {
        // Check if it's an unauthorized error
        if (response.error?.code === 'HTTP_401' || response.error?.message?.includes('Unauthorized')) {
          auth.logout(); // Clear invalid token
          router.push('/login');
          return;
        }
        setError(response.error?.message || 'Failed to load tasks');
      }
    } catch (err) {
      setError('An error occurred while loading tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;

    try {
      const response = await api.createTask(newTaskTitle, newTaskDescription, newTaskDueDate);
      if (response.success) {
        setNewTaskTitle('');
        setNewTaskDescription('');
        setNewTaskDueDate(''); // Reset due date
        setShowForm(false);
        fetchTasks(); // Refresh the task list
        showToast('Task created successfully!', 'success');
      } else {
        // Check if it's an unauthorized error
        if (response.error?.code === 'HTTP_401' || response.error?.message?.includes('Unauthorized')) {
          auth.logout(); // Clear invalid token
          router.push('/login');
          return;
        }
        const errorMessage = response.error?.message || 'Failed to create task';
        setError(errorMessage);
        showToast(errorMessage, 'error');
      }
    } catch (err) {
      const errorMessage = 'An error occurred while creating task';
      setError(errorMessage);
      showToast(errorMessage, 'error');
      console.error(err);
    }
  };

  // State for editing tasks
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [editingDescription, setEditingDescription] = useState('');
  const [editingDueDate, setEditingDueDate] = useState<string>(''); // New state for editing due date

  const handleToggleTask = async (id: number, completed: boolean) => {
    try {
      const response = await api.toggleTaskCompletion(id, !completed);
      if (response.success) {
        fetchTasks(); // Refresh the task list
        const message = completed ? 'Task marked as incomplete!' : 'Task marked as complete!';
        showToast(message, 'success');
      } else {
        // Check if it's an unauthorized error
        if (response.error?.code === 'HTTP_401' || response.error?.message?.includes('Unauthorized')) {
          auth.logout(); // Clear invalid token
          router.push('/login');
          return;
        }
        const errorMessage = response.error?.message || 'Failed to update task';
        setError(errorMessage);
        showToast(errorMessage, 'error');
      }
    } catch (err) {
      const errorMessage = 'An error occurred while updating task';
      setError(errorMessage);
      showToast(errorMessage, 'error');
      console.error(err);
    }
  };

  const startEditingTask = (task: Task) => {
    setEditingTaskId(task.id);
    setEditingTitle(task.title);
    setEditingDescription(task.description || '');
    setEditingDueDate(task.due_date || ''); // Set the due date for editing
  };

  const cancelEditingTask = () => {
    setEditingTaskId(null);
    setEditingTitle('');
    setEditingDescription('');
    setEditingDueDate(''); // Reset due date
  };

  const saveEditedTask = async (id: number) => {
    try {
      const response = await api.updateTask(id, editingTitle, editingDescription, editingDueDate);
      if (response.success) {
        setEditingTaskId(null);
        setEditingTitle('');
        setEditingDescription('');
        setEditingDueDate(''); // Reset due date
        fetchTasks(); // Refresh the task list
        showToast('Task updated successfully!', 'success');
      } else {
        // Check if it's an unauthorized error
        if (response.error?.code === 'HTTP_401' || response.error?.message?.includes('Unauthorized')) {
          auth.logout(); // Clear invalid token
          router.push('/login');
          return;
        }
        const errorMessage = response.error?.message || 'Failed to update task';
        setError(errorMessage);
        showToast(errorMessage, 'error');
      }
    } catch (err) {
      const errorMessage = 'An error occurred while updating task';
      setError(errorMessage);
      showToast(errorMessage, 'error');
      console.error(err);
    }
  };

  const handleDeleteTask = async (id: number) => {
    setShowDeleteConfirm(id); // Show the confirmation modal
  };

  const confirmDeleteTask = async (id: number) => {
    try {
      const response = await api.deleteTask(id);
      if (response.success) {
        fetchTasks(); // Refresh the task list
        setShowDeleteConfirm(null); // Hide the confirmation modal
        showToast('Task deleted successfully!', 'success');
      } else {
        // Check if it's an unauthorized error
        if (response.error?.code === 'HTTP_401' || response.error?.message?.includes('Unauthorized')) {
          auth.logout(); // Clear invalid token
          router.push('/login');
          return;
        }
        const errorMessage = response.error?.message || 'Failed to delete task';
        setError(errorMessage);
        showToast(errorMessage, 'error');
        setShowDeleteConfirm(null); // Hide the confirmation modal
      }
    } catch (err) {
      const errorMessage = 'An error occurred while deleting task';
      setError(errorMessage);
      showToast(errorMessage, 'error');
      console.error(err);
      setShowDeleteConfirm(null); // Hide the confirmation modal
    }
  };

  const cancelDeleteTask = () => {
    setShowDeleteConfirm(null); // Hide the confirmation modal
  };

  const handleLogout = () => {
    auth.logout();
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <nav className="bg-gradient-to-r from-indigo-600 to-purple-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-white flex items-center">
                  <svg className="w-8 h-8 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  Todo Dashboard
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-500 text-white font-medium rounded-lg hover:from-red-600 hover:to-pink-600 transform hover:scale-105 transition-all duration-200 shadow-md"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Toast Notification */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-xl shadow-xl transition-all duration-300 transform transition-transform ${
          toast.type === 'success' ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white' :
          toast.type === 'error' ? 'bg-gradient-to-r from-red-500 to-pink-500 text-white' :
          'bg-gradient-to-r from-blue-500 to-indigo-500 text-white'
        } animate-in slide-in-from-top-4 duration-300`}>
          <div className="flex items-center">
            {toast.type === 'success' && (
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
            {toast.type === 'error' && (
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
            {toast.type === 'info' && (
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
            {toast.message}
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl transform transition-all duration-300 scale-95 animate-in fade-in-90 zoom-in-90">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mt-4">Confirm Deletion</h3>
              <p className="text-gray-600 mt-2">Are you sure you want to delete this task? This action cannot be undone.</p>
            </div>
            <div className="mt-6 flex justify-center space-x-4">
              <button
                onClick={cancelDeleteTask}
                className="px-5 py-2.5 border-2 border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-all duration-200"
              >
                Cancel
              </button>
              <button
                onClick={() => confirmDeleteTask(showDeleteConfirm)}
                className="px-5 py-2.5 bg-gradient-to-r from-red-500 to-pink-500 text-white font-medium rounded-lg hover:from-red-600 hover:to-pink-600 transform hover:scale-105 transition-all duration-200"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-800">Your Tasks</h2>
              <p className="text-gray-600 mt-1">Manage your tasks and stay organized</p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl shadow-lg hover:from-indigo-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200 flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              {showForm ? 'Cancel' : '+ Add Task'}
            </button>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
              <span className="block sm:inline">{error}</span>
            </div>
          )}

          {showForm && (
            <form onSubmit={handleAddTask} className="mb-8 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-6 shadow-lg border border-indigo-100">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="space-y-2">
                  <label htmlFor="task-title" className="block text-sm font-semibold text-indigo-800">
                    Task Title *
                  </label>
                  <input
                    type="text"
                    id="task-title"
                    value={newTaskTitle}
                    onChange={(e) => setNewTaskTitle(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-indigo-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 text-gray-800 bg-white shadow-sm"
                    placeholder="What needs to be done?"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <label htmlFor="task-due-date" className="block text-sm font-semibold text-indigo-800">
                    Due Date
                  </label>
                  <input
                    type="date"
                    id="task-due-date"
                    value={newTaskDueDate}
                    onChange={(e) => setNewTaskDueDate(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-indigo-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 text-gray-800 bg-white shadow-sm"
                  />
                </div>
              </div>
              <div className="mb-6">
                <label htmlFor="task-description" className="block text-sm font-semibold text-indigo-800 mb-2">
                  Description
                </label>
                <textarea
                  id="task-description"
                  value={newTaskDescription}
                  onChange={(e) => setNewTaskDescription(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-indigo-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 text-gray-800 bg-white shadow-sm"
                  placeholder="Add details..."
                  rows={3}
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg shadow-md hover:from-indigo-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200"
                >
                  Add Task
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    setNewTaskTitle('');
                    setNewTaskDescription('');
                    setNewTaskDueDate('');
                  }}
                  className="px-6 py-3 border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-all duration-200"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {tasks.length === 0 ? (
            <div className="text-center py-16">
              <div className="bg-gradient-to-br from-indigo-100 to-purple-100 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg
                  className="h-12 w-12 text-indigo-500"
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
              </div>
              <h3 className="mt-2 text-xl font-semibold text-gray-800">No tasks yet</h3>
              <p className="mt-1 text-gray-600">Get started by creating your first task.</p>
              <div className="mt-8">
                <button
                  onClick={() => setShowForm(true)}
                  className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl shadow-lg hover:from-indigo-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200"
                >
                  Create your first task
                </button>
              </div>
            </div>
          ) : (
            <ul className="space-y-4">
              {tasks.map((task) => (
                <li key={task.id} className="transition-all duration-200">
                  {editingTaskId === task.id ? (
                    // Edit mode
                    <div className="p-5 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border border-blue-200">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div className="space-y-1">
                          <input
                            type="text"
                            value={editingTitle}
                            onChange={(e) => setEditingTitle(e.target.value)}
                            className="w-full px-4 py-2 border-2 border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-gray-800 bg-white"
                            placeholder="Task title"
                          />
                        </div>
                        <div className="space-y-1">
                          <input
                            type="date"
                            value={editingDueDate}
                            onChange={(e) => setEditingDueDate(e.target.value)}
                            className="w-full px-4 py-2 border-2 border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-gray-800 bg-white"
                          />
                        </div>
                      </div>
                      <div className="mb-4">
                        <textarea
                          value={editingDescription}
                          onChange={(e) => setEditingDescription(e.target.value)}
                          className="w-full px-4 py-2 border-2 border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-gray-800 bg-white"
                          placeholder="Task description"
                          rows={3}
                        />
                      </div>
                      <div className="flex space-x-3">
                        <button
                          onClick={() => saveEditedTask(task.id)}
                          className="flex-1 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-medium rounded-lg hover:from-green-600 hover:to-emerald-600 transform hover:scale-105 transition-all duration-200"
                        >
                          Save
                        </button>
                        <button
                          onClick={cancelEditingTask}
                          className="px-4 py-2 bg-gradient-to-r from-gray-500 to-slate-500 text-white font-medium rounded-lg hover:from-gray-600 hover:to-slate-600 transform hover:scale-105 transition-all duration-200"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    // View mode
                    <div className={`p-5 rounded-xl border transition-all duration-200 ${
                      task.completed
                        ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200'
                        : 'bg-gradient-to-r from-white to-gray-50 border-gray-200 hover:shadow-md hover:border-indigo-300'
                    }`}>
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3 flex-1">
                          <input
                            type="checkbox"
                            checked={task.completed}
                            onChange={() => handleToggleTask(task.id, task.completed)}
                            className="mt-1 h-5 w-5 text-indigo-600 border-2 border-indigo-300 rounded focus:ring-indigo-500 focus:ring-2 focus:ring-offset-1 transition-all duration-200"
                          />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2">
                              <span
                                className={`font-semibold ${
                                  task.completed
                                    ? 'text-gray-500 line-through'
                                    : 'text-gray-800'
                                }`}
                              >
                                {task.title}
                              </span>
                              {task.due_date && (
                                <span className={`text-xs px-2 py-1 rounded-full ${
                                  new Date(task.due_date) < new Date() && !task.completed
                                    ? 'bg-red-100 text-red-800'
                                    : 'bg-blue-100 text-blue-800'
                                }`}>
                                  {new Date(task.due_date) < new Date() && !task.completed
                                    ? 'Overdue'
                                    : 'Due Soon'}
                                </span>
                              )}
                            </div>
                            {task.due_date && (
                              <div className="text-sm text-gray-600 mt-1">
                                📅 Due: {new Date(task.due_date).toLocaleDateString()}
                              </div>
                            )}
                            {task.description && (
                              <div className="text-sm text-gray-600 mt-1">
                                📝 {task.description.length > 100
                                  ? `${task.description.substring(0, 100)}...`
                                  : task.description}
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <button
                            onClick={() => startEditingTask(task)}
                            className="p-2 text-indigo-600 hover:text-indigo-800 hover:bg-indigo-100 rounded-full transition-all duration-200"
                            title="Edit task"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                          <button
                            onClick={() => handleDeleteTask(task.id)}
                            className="p-2 text-red-600 hover:text-red-800 hover:bg-red-100 rounded-full transition-all duration-200"
                            title="Delete task"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  );
}