"use client";

import { useState, useRef, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { getApiClient } from '../../lib/api';
const api = getApiClient();

interface Message {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  createdAt?: string;
}

interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: any[];
  timestamp: string;
}

const ChatPage = () => {
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const pathname = usePathname();

  // Check if user is authenticated
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      router.push('/login');
      return;
    }

    // Try to get user ID
    let userId = '';
    try {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        const user = JSON.parse(userStr);
        userId = user.id;
      } else {
        // If user data isn't stored, decode the token to get user ID
        const tokenParts = token.split('.');
        if (tokenParts.length === 3) {
          const payload = JSON.parse(atob(tokenParts[1]));
          userId = payload.sub;
        }
      }
    } catch (error) {
      console.error('Error getting user ID:', error);
      return;
    }

    // Load existing conversations for the user
    loadConversations(userId);
  }, [router]);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to load conversations
  const loadConversations = async (userId: string) => {
    try {
      // Use the API client which handles authentication automatically
      const response = await api.getConversations(userId);

      if (!response.success) {
        console.error('Failed to load conversations:', response.error?.message);
        return;
      }

      const conversations = response.data?.conversations || [];

      if (conversations && conversations.length > 0) {
        // Get the most recent conversation
        const mostRecentConversation = conversations.reduce((latest: any, current: any) =>
          new Date(current.updated_at) > new Date(latest.updated_at) ? current : latest
        );

        // Load messages from the most recent conversation
        loadConversationMessages(userId, mostRecentConversation.id);
        setConversationId(mostRecentConversation.id);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  // Function to load messages from a specific conversation
  const loadConversationMessages = async (userId: string, convId: number) => {
    try {
      // Use the API client which handles authentication automatically
      const response = await api.getConversationMessages(userId, convId);

      if (!response.success) {
        console.error('Failed to load conversation messages:', response.error?.message);
        return;
      }

      const messages = response.data?.messages || [];

      if (messages && messages.length > 0) {
        // Format messages to match our Message interface
        const formattedMessages: Message[] = messages.map((msg: any) => ({
          role: msg.role,
          content: msg.content,
          createdAt: msg.created_at,
        }));

        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error('Error loading conversation messages:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) return;

    // Add user message to the chat
    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      createdAt: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Get the JWT token
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Prepare the request payload
      const requestBody: {
        conversation_id?: number;
        message: string;
      } = {
        message: inputValue,
      };

      if (conversationId) {
        requestBody.conversation_id = conversationId;
      }

      // Get user ID from stored user data
      let userId = '';
      try {
        const userStr = localStorage.getItem('user');
        if (userStr) {
          const user = JSON.parse(userStr);
          userId = user.id;
        } else {
          // If user data isn't stored, decode the token to get user ID
          const tokenParts = token.split('.');
          if (tokenParts.length === 3) {
            const payload = JSON.parse(atob(tokenParts[1]));
            userId = payload.sub;
          }
        }
      } catch (error) {
        console.error('Error getting user ID:', error);
        throw new Error('Unable to retrieve user information');
      }

      // Use the API client to send the message
      const response = await api.sendMessage(userId, inputValue, conversationId ? conversationId : undefined);

      if (!response.success) {
        throw new Error(response.error?.message || 'Failed to get response from chat API');
      }

      const data: ChatResponse = response.data as ChatResponse;

      // Update conversation ID if this is the first message
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      // Add AI response to the chat
      const aiMessage: Message = {
        role: 'assistant',
        content: data.response,
        createdAt: data.timestamp,
      };

      setMessages(prev => [...prev, aiMessage]);

      // Check if the response indicates a task operation was performed
      // and notify other parts of the app to refresh tasks
      if (data.tool_calls && Array.isArray(data.tool_calls)) {
        const taskOperations = ['add_task', 'update_task', 'delete_task', 'complete_task'];
        const hasTaskOperation = data.tool_calls.some((call: any) =>
          taskOperations.includes(call.name)
        );

        if (hasTaskOperation) {
          // Dispatch a custom event to notify other components to refresh tasks
          window.dispatchEvent(new CustomEvent('tasksChanged', { detail: { action: 'refresh' } }));

          // Also update localStorage to signal other tabs/pages to refresh
          localStorage.setItem('tasksLastUpdated', new Date().toISOString());
          localStorage.setItem('tasksRefreshTrigger', Date.now().toString());
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to the chat
      const errorMessage: Message = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`,
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-600 to-purple-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-white flex items-center">
                  <svg className="w-8 h-8 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  Todo App
                </h1>
              </div>
              <div className="hidden md:ml-6 md:flex md:space-x-8">
                <a
                  href="/dashboard"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    pathname === '/dashboard'
                      ? 'border-white text-white'
                      : 'border-transparent text-indigo-200 hover:border-indigo-300 hover:text-white'
                  }`}
                >
                  Dashboard
                </a>
                <a
                  href="/chat"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    pathname === '/chat'
                      ? 'border-white text-white'
                      : 'border-transparent text-indigo-200 hover:border-indigo-300 hover:text-white'
                  }`}
                >
                  AI Assistant
                </a>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-white">
                {conversationId ? `Conv #${conversationId}` : 'New Chat'}
              </span>
              <button
                onClick={() => {
                  setMessages([]);
                  setConversationId(null);
                }}
                className="px-3 py-1 text-sm bg-white text-indigo-600 rounded-md hover:bg-gray-100 transition-colors"
              >
                New
              </button>
              <button
                onClick={() => {
                  localStorage.removeItem('auth_token');
                  localStorage.removeItem('user');
                  window.location.href = '/login';
                }}
                className="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-500 text-white font-medium rounded-lg hover:from-red-600 hover:to-pink-600 transform hover:scale-105 transition-all duration-200 shadow-md"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 pb-20">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <h2 className="text-2xl font-medium text-gray-700 mb-4">Welcome to AI Task Assistant!</h2>
              <p className="text-gray-500 max-w-md mx-auto">
                I can help you manage your tasks. Try saying something like "Add a task to buy groceries"
                or "Show me my tasks".
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  {message.createdAt && (
                    <div className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-200' : 'text-gray-500'}`}>
                      {new Date(message.createdAt).toLocaleString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true,
                        timeZone: 'Asia/Karachi'
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t py-4 px-6 sticky bottom-0">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex gap-3">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message here..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white"
            rows={Math.min(inputValue.split('\n').length, 5)}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className={`px-6 py-3 rounded-lg font-medium ${
              isLoading || !inputValue.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-500 text-white hover:bg-blue-600 transition-colors'
            }`}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
        <div className="max-w-4xl mx-auto mt-2 text-xs text-gray-500">
          Tip: Press Enter to send, Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default ChatPage;