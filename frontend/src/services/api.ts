import axios, { AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
    ApiResponse,
    AuthResponse,
    MealsResponse,
    MealResponse,
    User,
    Meal,
    MealFormData
} from '../types';

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
    login: async (username: string, password: string): Promise<ApiResponse<AuthResponse>> => {
        try {
            const response: AxiosResponse<AuthResponse> = await api.post('/auth/login', { username, password });
            const { token, user } = response.data;

            // Store token and user data
            await AsyncStorage.setItem('userToken', token);
            await AsyncStorage.setItem('userData', JSON.stringify(user));

            return { success: true, data: response.data };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.error || 'Login failed'
            };
        }
    },

    logout: async (): Promise<ApiResponse> => {
        try {
            await AsyncStorage.removeItem('userToken');
            await AsyncStorage.removeItem('userData');
            return { success: true };
        } catch (error) {
            return { success: false, error: 'Logout failed' };
        }
    },

    getStoredToken: async (): Promise<string | null> => {
        try {
            return await AsyncStorage.getItem('userToken');
        } catch (error) {
            return null;
        }
    },

    getStoredUser: async (): Promise<User | null> => {
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
    getMeals: async (): Promise<ApiResponse<Meal[]>> => {
        try {
            const response: AxiosResponse<MealsResponse> = await api.get('/meals');
            return { success: true, data: response.data.meals };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.error || 'Failed to fetch meals'
            };
        }
    },

    getMeal: async (id: number): Promise<ApiResponse<Meal>> => {
        try {
            const response: AxiosResponse<MealResponse> = await api.get(`/meals/${id}`);
            return { success: true, data: response.data.meal };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.error || 'Failed to fetch meal'
            };
        }
    },

    createMeal: async (mealData: MealFormData): Promise<ApiResponse<Meal>> => {
        try {
            const response: AxiosResponse<MealResponse> = await api.post('/meals', mealData);
            return { success: true, data: response.data.meal };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.error || 'Failed to create meal'
            };
        }
    },

    updateMeal: async (id: number, mealData: MealFormData): Promise<ApiResponse<Meal>> => {
        try {
            const response: AxiosResponse<MealResponse> = await api.put(`/meals/${id}`, mealData);
            return { success: true, data: response.data.meal };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.error || 'Failed to update meal'
            };
        }
    },

    deleteMeal: async (id: number): Promise<ApiResponse> => {
        try {
            await api.delete(`/meals/${id}`);
            return { success: true };
        } catch (error: any) {
            return {
                success: false,
                error: error.response?.data?.error || 'Failed to delete meal'
            };
        }
    },
};

export default api; 