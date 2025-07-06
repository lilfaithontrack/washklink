import axios from 'axios'

export const api = axios.create({
  baseURL: 'https://api.washlinnk.com',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API service functions
export const authService = {
  login: (email: string, password: string) =>
    api.post('/api/v1/auth/admin/login', { email, password }),
  
  getCurrentUser: () =>
    api.get('/api/v1/auth/me'),
  
  logout: () =>
    api.post('/api/v1/auth/logout'),
}

export const userService = {
  getUsers: (params?: any) =>
    api.get('/api/v1/users/', { params }),
  
  getUser: (id: number) =>
    api.get(`/api/v1/users/${id}`),
  
  updateUserRole: (id: number, role: string) =>
    api.put(`/api/v1/users/${id}/role`, { new_role: role }),
  
  deleteUser: (id: number) =>
    api.delete(`/api/v1/users/${id}`),
  
  getUserStats: () =>
    api.get('/api/v1/users/stats/summary'),
}

export const orderService = {
  getOrders: (params?: any) =>
    api.get('/api/v1/orders/', { params }),
  
  getOrder: (id: number) =>
    api.get(`/api/v1/orders/${id}`),
  
  updateOrderStatus: (id: number, status: string, notes?: string) =>
    api.put(`/api/v1/orders/${id}/status`, { status, notes }),
  
  assignProvider: (orderId: number, providerId: number) =>
    api.post(`/api/v1/orders/${orderId}/assign-provider`, { provider_id: providerId }),
  
  assignDriver: (orderId: number) =>
    api.post(`/api/v1/orders/${orderId}/assign-driver`),
  
  getOrderStats: () =>
    api.get('/api/v1/orders/stats/summary'),
}

export const providerService = {
  getProviders: () =>
    api.get('/api/v1/laundry-providers/'),
  
  getProvider: (id: number) =>
    api.get(`/api/v1/laundry-providers/${id}`),
  
  createProvider: (data: any) =>
    api.post('/api/v1/laundry-providers/', data),
}

export const driverService = {
  getDrivers: (params?: any) =>
    api.get('/api/v1/drivers/', { params }),
  
  getDriver: (id: number) =>
    api.get(`/api/v1/drivers/${id}`),
  
  createDriver: (data: any) =>
    api.post('/api/v1/drivers/', data),
  
  updateDriver: (id: number, data: any) =>
    api.put(`/api/v1/drivers/${id}`, data),
  
  updateDriverStatus: (id: number, status: string) =>
    api.put(`/api/v1/drivers/${id}/status`, { status }),
}

export const paymentService = {
  getPaymentMethods: () =>
    api.get('/api/v1/payments/methods'),
  
  initiatePayment: (data: any) =>
    api.post('/api/v1/payments/initiate', data),
  
  verifyPayment: (transactionId: string, method: string) =>
    api.get(`/api/v1/payments/verify/${transactionId}?payment_method=${method}`),
}

export const analyticsService = {
  getDashboardStats: () =>
    api.get('/api/v1/realtime/dashboard/live-data'),
  
  getActiveDeliveries: () =>
    api.get('/api/v1/realtime/orders/active-deliveries'),
  
  getAnalytics: () =>
    api.get('/api/v1/realtime/analytics/real-time'),
}