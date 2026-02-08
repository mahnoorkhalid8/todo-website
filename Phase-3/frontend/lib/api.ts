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
    // Explicitly use the environment variable which should be set to local backend for development
    // In production/deployment, this will use the production API
    let baseUrl = process.env.NEXT_PUBLIC_API_URL || '';

    // If no env var is set, fallback to local development URL
    if (!baseUrl) {
      // Check if we're in a development environment
      if (typeof window !== 'undefined') {
        // Browser environment - check if we're running locally
        const hostname = window.location.hostname;
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
          baseUrl = 'http://127.0.0.1:8000'; // Local backend
        } else {
          // In production environment, use production API
          baseUrl = 'https://mahnoorkhalid8-todo-bot.hf.space';
        }
      } else {
        // Server environment (Node.js)
        const isDev = process.env.NODE_ENV === 'development';
        baseUrl = isDev ? 'http://127.0.0.1:8000' : 'https://mahnoorkhalid8-todo-bot.hf.space';
      }
    }

    // Ensure we have a proper URL format
    if (!baseUrl.startsWith('http://') && !baseUrl.startsWith('https://')) {
      baseUrl = 'http://' + baseUrl;
    }

    // Remove any trailing slashes to ensure clean URL joining
    baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

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

    // Ensure Content-Type header is set properly
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    } as Record<string, string>;

    // Add authorization header if token exists
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Log the request for debugging with proper headers
    console.log('API Request:', {
      url,
      method: options.method || 'GET',
      headers: { 'Content-Type': 'application/json', 'Authorization': token ? '***' : 'none' }, // Don't log the actual token
      endpoint
    });

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Log response status for debugging
      console.log('API Response status:', response.status, 'for', url);

      // Handle response based on content type
      const contentType = response.headers.get('content-type');
      let data;

      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        // For non-JSON responses, return text or empty object
        const text = await response.text();
        try {
          data = JSON.parse(text);
        } catch {
          data = { message: text };
        }
      }

      if (!response.ok) {
        console.error('API Error Response:', {
          status: response.status,
          statusText: response.statusText,
          url,
          data
        });

        return {
          success: false,
          error: {
            code: `HTTP_${response.status}`,
            message: data.message || response.statusText,
            details: data.details || null,
          },
        };
      }

      console.log('API Success Response:', { url, data });
      return {
        success: true,
        data,
      };
    } catch (error: any) {
      console.error('API Network Error:', {
        error: error.message,
        url,
        endpoint
      });

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
    const response = await this.request(`/api/chat/${userId}/conversations`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

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
    const response = await this.request(`/api/chat/${userId}/conversation/${conversationId}/messages`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

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

    // Log the request for debugging
    console.log(`Sending chat message to: /api/chat/${userId}`, requestBody);

    try {
      const response = await this.request(`/api/chat/${userId}`, {
        method: 'POST',
        body: JSON.stringify(requestBody),
      });

      // Log the response for debugging
      if (!response.success) {
        console.error('Chat message API error:', response.error);
      }

      return response;
    } catch (err) {
      console.error('Chat message network error:', err);
      // Return a proper error response
      return {
        success: false,
        error: {
          code: 'NETWORK_ERROR',
          message: err instanceof Error ? err.message : 'Network error occurred',
        }
      };
    }
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






// // API client for the Todo Web Application
// // Centralized error handling and request management

// interface ApiResponse<T> {
//   success: boolean;
//   data?: T;
//   error?: {
//     code: string;
//     message: string;
//     details?: any;
//   };
// }

// class ApiClient {
//   private baseUrl: string;
//   private token: string | null;

//   constructor() {
//     let baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://mahnoorkhalid8-todo-bot.hf.space';

//     // Remove any trailing slashes to ensure clean URL joining
//     baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

//     // Always ensure HTTPS in production environments to prevent mixed content errors
//     // Check if we're in production (browser or server)
//     const isProduction = typeof process !== 'undefined' && process.env?.NODE_ENV === 'production';
//     const isBrowserAndHttps = typeof window !== 'undefined' && window.location?.protocol === 'https:';

//     // If in production, or if page is loaded over HTTPS, enforce HTTPS for API calls
//     if (isProduction || isBrowserAndHttps) {
//       if (baseUrl.startsWith('http://')) {
//         baseUrl = baseUrl.replace('http://', 'https://');
//       }
//       // If it doesn't start with https://, ensure it's a proper URL format
//       else if (!baseUrl.startsWith('https://')) {
//         // If it starts with http://, https://, or protocol-relative //, handle appropriately
//         if (baseUrl.startsWith('//')) {
//           baseUrl = 'https:' + baseUrl;
//         } else if (!baseUrl.startsWith('https://')) {
//           // If it's just a domain, prepend https://
//           baseUrl = 'https://' + baseUrl;
//         }
//       }
//     }

//     // Ensure no trailing slash after protocol change
//     baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

//     this.baseUrl = baseUrl;
//     this.token = null;
//   }

//   // Set authentication token
//   setToken(token: string) {
//     this.token = token;
//     if (typeof window !== 'undefined') {
//       localStorage.setItem('auth_token', token);
//     }
//   }

//   // Get authentication token
//   getToken(): string | null {
//     if (typeof window !== 'undefined') {
//       return localStorage.getItem('auth_token');
//     }
//     return this.token;
//   }

//   // Remove authentication token
//   removeToken() {
//     this.token = null;
//     if (typeof window !== 'undefined') {
//       localStorage.removeItem('auth_token');
//     }
//   }

//   // Helper method to properly join URL segments
//   private joinUrl(base: string, endpoint: string): string {
//     // Remove trailing slash from base if present
//     const normalizedBase = base.endsWith('/') ? base.slice(0, -1) : base;
//     // Remove leading slash from endpoint if present
//     const normalizedEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;

//     // Join with a single slash in between
//     return `${normalizedBase}/${normalizedEndpoint}`;
//   }

//   // Generic request method
//   private async request<T>(
//     endpoint: string,
//     options: RequestInit = {}
//   ): Promise<ApiResponse<T>> {
//     const url = this.joinUrl(this.baseUrl, endpoint);

//     const headers = {
//       'Content-Type': 'application/json',
//       ...(options.headers as Record<string, string>),
//     } as Record<string, string>;

//     // Add authorization header if token exists
//     const token = this.getToken();
//     if (token) {
//       headers['Authorization'] = `Bearer ${token}`;
//     }

//     try {
//       const response = await fetch(url, {
//         ...options,
//         headers,
//       });

//       const data = await response.json();

//       if (!response.ok) {
//         return {
//           success: false,
//           error: {
//             code: `HTTP_${response.status}`,
//             message: data.message || response.statusText,
//             details: data.details || null,
//           },
//         };
//       }

//       return {
//         success: true,
//         data,
//       };
//     } catch (error: any) {
//       return {
//         success: false,
//         error: {
//           code: 'NETWORK_ERROR',
//           message: error.message || 'Network error occurred',
//         },
//       };
//     }
//   }

//   // Authentication methods
//   async register(email: string, password: string, name?: string) {
//     return this.request('/api/auth/register', {
//       method: 'POST',
//       body: JSON.stringify({ email, password, name }),
//     });
//   }

//   async login(email: string, password: string) {
//     return this.request('/api/auth/login', {
//       method: 'POST',
//       body: JSON.stringify({ email, password }),
//     });
//   }

//   async logout() {
//     const result: ApiResponse<unknown> = await this.request('/api/auth/logout', {
//       method: 'POST',
//     });

//     if (result.success) {
//       this.removeToken();
//     }

//     return result;
//   }

//   // Task methods
//   async getTasks(status: string = 'all', sort: string = 'created', page: number = 1, limit: number = 10) {
//     const params = new URLSearchParams({
//       status,
//       sort,
//       page: page.toString(),
//       limit: limit.toString(),
//     });

//     return this.request(`/api/tasks?${params}`);
//   }

//   async createTask(title: string, description?: string, dueDate?: string) {
//     // Format due date to ISO 8601 if provided
//     let formattedDueDate: string | undefined;
//     if (dueDate) {
//       try {
//         // Convert to proper ISO format
//         const date = new Date(dueDate);
//         formattedDueDate = date.toISOString().split('T')[0] + 'T00:00:00';
//       } catch (error) {
//         console.error('Error formatting due date:', error);
//         // If formatting fails, send as is (backend will validate)
//         formattedDueDate = dueDate;
//       }
//     }

//     return this.request('/api/tasks', {
//       method: 'POST',
//       body: JSON.stringify({ title, description, due_date: formattedDueDate }),
//     });
//   }

//   async getTask(id: number) {
//     return this.request(`/api/tasks/${id}`);
//   }

//   async updateTask(id: number, title?: string, description?: string, dueDate?: string) {
//     // Format due date to ISO 8601 if provided
//     let formattedDueDate: string | undefined;
//     if (dueDate) {
//       try {
//         // Convert to proper ISO format
//         const date = new Date(dueDate);
//         formattedDueDate = date.toISOString().split('T')[0] + 'T00:00:00';
//       } catch (error) {
//         console.error('Error formatting due date:', error);
//         // If formatting fails, send as is (backend will validate)
//         formattedDueDate = dueDate;
//       }
//     }

//     return this.request(`/api/tasks/${id}`, {
//       method: 'PUT',
//       body: JSON.stringify({ title, description, due_date: formattedDueDate }),
//     });
//   }

//   async deleteTask(id: number) {
//     return this.request(`/api/tasks/${id}`, {
//       method: 'DELETE',
//     });
//   }

//   async toggleTaskCompletion(id: number, completed: boolean) {
//     return this.request(`/api/tasks/${id}/complete`, {
//       method: 'PATCH',
//       body: JSON.stringify({ completed }),
//     });
//   }

//   // Chat methods with proper return types
//   async getConversations(userId: string): Promise<ApiResponse<{ conversations: any[] }>> {
//     const response = await this.request(`/api/chat/${userId}/conversations`);

//     // If successful, return the conversations from the response data
//     if (response.success) {
//       const responseData = response.data as any;
//       // Assume the backend returns { conversations: [...] }
//       return {
//         success: true,
//         data: { conversations: responseData?.conversations || [] }
//       };
//     }
//     // Return the original error response
//     return response as ApiResponse<{ conversations: any[] }>;
//   }

//   async getConversationMessages(userId: string, conversationId: number): Promise<ApiResponse<{ messages: any[] }>> {
//     const response = await this.request(`/api/chat/${userId}/conversation/${conversationId}/messages`);

//     // If successful, return the messages from the response data
//     if (response.success) {
//       const responseData = response.data as any;
//       // Assume the backend returns { messages: [...] }
//       return {
//         success: true,
//         data: { messages: responseData?.messages || [] }
//       };
//     }
//     // Return the original error response
//     return response as ApiResponse<{ messages: any[] }>;
//   }

//   async sendMessage(userId: string, message: string, conversationId?: number): Promise<ApiResponse<any>> {
//     const requestBody: {
//       conversation_id?: number;
//       message: string;
//     } = {
//       message,
//     };

//     if (conversationId !== undefined) {
//       requestBody.conversation_id = conversationId;
//     }

//     return this.request(`/api/chat/${userId}`, {
//       method: 'POST',
//       body: JSON.stringify(requestBody),
//     });
//   }

//   async getChatHealth(): Promise<ApiResponse<any>> {
//     return this.request('/api/chat/health');
//   }
// }

// // Create a singleton instance using a factory pattern to avoid initialization issues
// let _apiInstance: ApiClient | null = null;

// function getApiClient(): ApiClient {
//   if (!_apiInstance) {
//     _apiInstance = new ApiClient();
//   }
//   return _apiInstance;
// }

// // Export the getter function instead of the instance directly
// export { getApiClient };

// // For backward compatibility, also export as default
// export default getApiClient;
