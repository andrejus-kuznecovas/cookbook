import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext({});

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        checkAuthStatus();
    }, []);

    const checkAuthStatus = async () => {
        try {
            const token = await authService.getStoredToken();
            const userData = await authService.getStoredUser();

            if (token && userData) {
                setUser(userData);
                setIsAuthenticated(true);
            } else {
                setUser(null);
                setIsAuthenticated(false);
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            setUser(null);
            setIsAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    const login = async (username, password) => {
        try {
            const result = await authService.login(username, password);

            if (result.success) {
                setUser(result.data.user);
                setIsAuthenticated(true);
                return { success: true };
            } else {
                return { success: false, error: result.error };
            }
        } catch (error) {
            return { success: false, error: 'Login failed' };
        }
    };

    const logout = async () => {
        try {
            await authService.logout();
            setUser(null);
            setIsAuthenticated(false);
            return { success: true };
        } catch (error) {
            return { success: false, error: 'Logout failed' };
        }
    };

    const value = {
        user,
        loading,
        isAuthenticated,
        login,
        logout,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext; 