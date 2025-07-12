// User related types
export interface User {
    id: number;
    username: string;
    email?: string;
    created_at: string;
    updated_at: string;
}

// Meal related types
export interface Meal {
    id: number;
    name: string;
    ingredients: string;
    recipe: string;
    difficulty: 'Easy' | 'Medium' | 'Hard';
    created_at: string;
    updated_at: string;
}

export interface MealFormData {
    name: string;
    ingredients: string;
    recipe: string;
    difficulty: 'Easy' | 'Medium' | 'Hard';
}

// API response types
export interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    error?: string;
}

export interface AuthResponse {
    token: string;
    user: User;
}

export interface MealsResponse {
    meals: Meal[];
}

export interface MealResponse {
    meal: Meal;
}

// Auth context types
export interface AuthContextType {
    user: User | null;
    loading: boolean;
    isAuthenticated: boolean;
    login: (username: string, password: string) => Promise<ApiResponse>;
    logout: () => Promise<ApiResponse>;
}

// Navigation types
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { RouteProp } from '@react-navigation/native';

export type RootStackParamList = {
    Login: undefined;
    MealsList: undefined;
    MealDetail: { meal: Meal };
    AddMeal: undefined;
    EditMeal: { meal: Meal };
};

// Screen props types
export interface ScreenProps<T extends keyof RootStackParamList> {
    navigation: NativeStackNavigationProp<RootStackParamList, T>;
    route: RouteProp<RootStackParamList, T>;
}

// Component props types
export interface AuthProviderProps {
    children: React.ReactNode;
} 