// API client for the Todo Web Application
// Centralized error handling and request management

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

class ApiClient {
  private baseUrl: string;
  private token: string | null;

  constructor() {
    let baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://mahnoorkhalid8-todo-bot.hf.space';

    // Remove any trailing slashes to ensure clean URL joining
    baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

    // Ensure HTTPS in production environments to prevent mixed content errors
    if (typeof window !== 'undefined' && window.location?.protocol === 'https:') {
      try {
        const urlObj = new URL(baseUrl);
        urlObj.protocol = 'https:';
        baseUrl = urlObj.toString();
        // Ensure no trailing slash after protocol change
        baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
      } catch (e) {
        // If parsing fails, fall back to the default HTTPS URL
        baseUrl = 'https://mahnoorkhalid8-todo-bot.hf.space';
        // Ensure no trailing slash on fallback
        baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
      }
    } else if (!baseUrl.startsWith('https://') && process.env.NODE_ENV === 'production') {
      // If in production and URL doesn't start with https, force HTTPS
      if (baseUrl.startsWith('http://')) {
        baseUrl = baseUrl.replace('http://', 'https://');
      } else {
        baseUrl = 'https://' + baseUrl;
      }
      // Ensure no trailing slash after protocol change
      baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
    }

    this.baseUrl = baseUrl;
    this.token = null;
  }

  // Set authentication token
  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  // Get authentication token
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return this.token;
  }

  // Remove authentication token
  removeToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Helper method to properly join URL segments
  private joinUrl(base: string, endpoint: string): string {
    // Remove trailing slash from base if present
    const normalizedBase = base.endsWith('/') ? base.slice(0, -1) : base;
    // Remove leading slash from endpoint if present
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;

    // Join with a single slash in between
    return `${normalizedBase}/${normalizedEndpoint}`;
  }

  // Generic request method
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = this.joinUrl(this.baseUrl, endpoint);

    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    } as Record<string, string>;

    // Add authorization header if token exists
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: {
            code: `HTTP_${response.status}`,
            message: data.message || response.statusText,
            details: data.details || null,
          },
        };
      }

      return {
        success: true,
        data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: {
          code: 'NETWORK_ERROR',
          message: error.message || 'Network error occurred',
        },
      };
    }
  }

  // Authentication methods
  async register(email: string, password: string, name?: string) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
  }

  async login(email: string, password: string) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async logout() {
    const result: ApiResponse<unknown> = await this.request('/api/auth/logout', {
      method: 'POST',
    });

    if (result.success) {
      this.removeToken();
    }

    return result;
  }

  // Task methods
  async getTasks(status: string = 'all', sort: string = 'created', page: number = 1, limit: number = 10) {
    const params = new URLSearchParams({
      status,
      sort,
      page: page.toString(),
      limit: limit.toString(),
    });

    return this.request(`/api/tasks?${params}`);
  }

  async createTask(title: string, description?: string, dueDate?: string) {
    // Format due date to ISO 8601 if provided
    let formattedDueDate: string | undefined;
    if (dueDate) {
      try {
        // Convert to proper ISO format
        const date = new Date(dueDate);
        formattedDueDate = date.toISOString().split('T')[0] + 'T00:00:00';
      } catch (error) {
        console.error('Error formatting due date:', error);
        // If formatting fails, send as is (backend will validate)
        formattedDueDate = dueDate;
      }
    }

    return this.request('/api/tasks', {
      method: 'POST',
      body: JSON.stringify({ title, description, due_date: formattedDueDate }),
    });
  }

  async getTask(id: number) {
    return this.request(`/api/tasks/${id}`);
  }

  async updateTask(id: number, title?: string, description?: string, dueDate?: string) {
    // Format due date to ISO 8601 if provided
    let formattedDueDate: string | undefined;
    if (dueDate) {
      try {
        // Convert to proper ISO format
        const date = new Date(dueDate);
        formattedDueDate = date.toISOString().split('T')[0] + 'T00:00:00';
      } catch (error) {
        console.error('Error formatting due date:', error);
        // If formatting fails, send as is (backend will validate)
        formattedDueDate = dueDate;
      }
    }

    return this.request(`/api/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ title, description, due_date: formattedDueDate }),
    });
  }

  async deleteTask(id: number) {
    return this.request(`/api/tasks/${id}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskCompletion(id: number, completed: boolean) {
    return this.request(`/api/tasks/${id}/complete`, {
      method: 'PATCH',
      body: JSON.stringify({ completed }),
    });
  }

  // Chat methods with proper return types
  async getConversations(userId: string): Promise<ApiResponse<{ conversations: any[] }>> {
    const response = await this.request(`/api/chat/${userId}/conversations`);

    // If successful, return the conversations from the response data
    if (response.success) {
      const responseData = response.data as any;
      // Assume the backend returns { conversations: [...] }
      return {
        success: true,
        data: { conversations: responseData?.conversations || [] }
      };
    }
    // Return the original error response
    return response as ApiResponse<{ conversations: any[] }>;
  }

  async getConversationMessages(userId: string, conversationId: number): Promise<ApiResponse<{ messages: any[] }>> {
    const response = await this.request(`/api/chat/${userId}/conversation/${conversationId}/messages`);

    // If successful, return the messages from the response data
    if (response.success) {
      const responseData = response.data as any;
      // Assume the backend returns { messages: [...] }
      return {
        success: true,
        data: { messages: responseData?.messages || [] }
      };
    }
    // Return the original error response
    return response as ApiResponse<{ messages: any[] }>;
  }

  async sendMessage(userId: string, message: string, conversationId?: number): Promise<ApiResponse<any>> {
    const requestBody: {
      conversation_id?: number;
      message: string;
    } = {
      message,
    };

    if (conversationId !== undefined) {
      requestBody.conversation_id = conversationId;
    }

    return this.request(`/api/chat/${userId}`, {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
  }

  async getChatHealth(): Promise<ApiResponse<any>> {
    return this.request('/api/chat/health');
  }
}

// Create a singleton instance using a factory pattern to avoid initialization issues
let _apiInstance: ApiClient | null = null;

function getApiClient(): ApiClient {
  if (!_apiInstance) {
    _apiInstance = new ApiClient();
  }
  return _apiInstance;
}

// Export the getter function instead of the instance directly
export { getApiClient };

// For backward compatibility, also export as default
export default getApiClient;