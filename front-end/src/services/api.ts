"use client";

type ApiOptions = {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
  isFormData?: boolean;
};

export const apiService = {
    async fetch(url: string, options: ApiOptions = {}) {
      const { method = "GET", body, headers = {}, isFormData = false } = options;
      
      const finalHeaders: Record<string, string> = {
        ...(isFormData ? {} : { "Content-Type": "application/json" }),
        ...headers
      };
  
      try {
        const response = await fetch(url, {
          method,
          headers: finalHeaders,
          credentials: "include",
          body: isFormData ? body : (body ? JSON.stringify(body) : undefined),
        });
  
        // Handle non-2xx responses
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw {
            status: response.status,
            statusText: response.statusText,
            data: errorData
          };
        }
  
        const data = await response.json();
        return { data, status: response.status };
      } catch (error) {
        console.error("API request failed:", error);
        throw error;
      }
    },
  
    // Convenience methods
    get(url: string, options: Omit<ApiOptions, "method" | "body"> = {}) {
      return this.fetch(url, { ...options, method: "GET" });
    },
  
    post(url: string, body: any, options: Omit<ApiOptions, "method"> = {}) {
      return this.fetch(url, { ...options, method: "POST", body });
    },
  
    put(url: string, body: any, options: Omit<ApiOptions, "method"> = {}) {
      return this.fetch(url, { ...options, method: "PUT", body });
    },
  
    delete(url: string, options: Omit<ApiOptions, "method"> = {}) {
      return this.fetch(url, { ...options, method: "DELETE" });
    },
  
    // Special method for handling FormData uploads
    uploadFile(url: string, formData: FormData, method: string = "POST") {
      return this.fetch(url, {
        method,
        body: formData,
        isFormData: true
      });
    }
  };