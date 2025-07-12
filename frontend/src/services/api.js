import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Replace with your backend URL
const API_BASE_URL = 'http://localhost:8080/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add JWT token
api.interceptors.request.use(
    async (config) => {
        try {
            const token = await AsyncStorage.getItem('userToken');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        } catch (error) {
            console.error('Error getting token:', error);
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle token expiration
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            await AsyncStorage.removeItem('userToken');
            await AsyncStorage.removeItem('userData');
            // Note: In a full app, you would redirect to login screen here
        }
        return Promise.reject(error);
    }
);

// Auth services
export const authService = {
    login: async (username, password) => {
        try {
            const response = await api.post('/auth/login', { username, password });
            const { token, user } = response.data;

            // Store token and user data
            await AsyncStorage.setItem('userToken', token);
            await AsyncStorage.setItem('userData', JSON.stringify(user));

            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || 'Login failed'
            };
        }
    },

    logout: async () => {
        try {
            await AsyncStorage.removeItem('userToken');
            await AsyncStorage.removeItem('userData');
            return { success: true };
        } catch (error) {
            return { success: false, error: 'Logout failed' };
        }
    },

    getStoredToken: async () => {
        try {
            return await AsyncStorage.getItem('userToken');
        } catch (error) {
            return null;
        }
    },

    getStoredUser: async () => {
        try {
            const userData = await AsyncStorage.getItem('userData');
            return userData ? JSON.parse(userData) : null;
        } catch (error) {
            return null;
        }
    },
};

// Meal services
export const mealService = {
    getMeals: async () => {
        try {
            const response = await api.get('/meals');
            return { success: true, data: response.data.meals };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || 'Failed to fetch meals'
            };
        }
    },

    getMeal: async (id) => {
        try {
            const response = await api.get(`/meals/${id}`);
            return { success: true, data: response.data.meal };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || 'Failed to fetch meal'
            };
        }
    },

    createMeal: async (mealData) => {
        try {
            const response = await api.post('/meals', mealData);
            return { success: true, data: response.data.meal };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || 'Failed to create meal'
            };
        }
    },

    updateMeal: async (id, mealData) => {
        try {
            const response = await api.put(`/meals/${id}`, mealData);
            return { success: true, data: response.data.meal };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || 'Failed to update meal'
            };
        }
    },

    deleteMeal: async (id) => {
        try {
            await api.delete(`/meals/${id}`);
            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.error || 'Failed to delete meal'
            };
        }
    },
};

export default api; 