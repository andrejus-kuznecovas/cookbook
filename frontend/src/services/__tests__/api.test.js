import { authService, mealService } from '../api';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  setItem: jest.fn(),
  getItem: jest.fn(),
  removeItem: jest.fn(),
}));

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() },
    },
  })),
}));

describe('Auth Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getStoredToken', () => {
    it('should return token from AsyncStorage', async () => {
      const mockToken = 'mock-token';
      AsyncStorage.getItem.mockResolvedValue(mockToken);

      const result = await authService.getStoredToken();
      expect(result).toBe(mockToken);
      expect(AsyncStorage.getItem).toHaveBeenCalledWith('userToken');
    });

    it('should return null if no token exists', async () => {
      AsyncStorage.getItem.mockResolvedValue(null);

      const result = await authService.getStoredToken();
      expect(result).toBe(null);
    });

    it('should return null if AsyncStorage throws error', async () => {
      AsyncStorage.getItem.mockRejectedValue(new Error('Storage error'));

      const result = await authService.getStoredToken();
      expect(result).toBe(null);
    });
  });

  describe('getStoredUser', () => {
    it('should return parsed user data from AsyncStorage', async () => {
      const mockUser = { id: 1, username: 'testuser' };
      AsyncStorage.getItem.mockResolvedValue(JSON.stringify(mockUser));

      const result = await authService.getStoredUser();
      expect(result).toEqual(mockUser);
      expect(AsyncStorage.getItem).toHaveBeenCalledWith('userData');
    });

    it('should return null if no user data exists', async () => {
      AsyncStorage.getItem.mockResolvedValue(null);

      const result = await authService.getStoredUser();
      expect(result).toBe(null);
    });

    it('should return null if JSON parsing fails', async () => {
      AsyncStorage.getItem.mockResolvedValue('invalid-json');

      const result = await authService.getStoredUser();
      expect(result).toBe(null);
    });
  });

  describe('logout', () => {
    it('should remove token and user data from AsyncStorage', async () => {
      AsyncStorage.removeItem.mockResolvedValue(true);

      const result = await authService.logout();
      expect(result).toEqual({ success: true });
      expect(AsyncStorage.removeItem).toHaveBeenCalledWith('userToken');
      expect(AsyncStorage.removeItem).toHaveBeenCalledWith('userData');
    });

    it('should return error if AsyncStorage operation fails', async () => {
      AsyncStorage.removeItem.mockRejectedValue(new Error('Storage error'));

      const result = await authService.logout();
      expect(result).toEqual({ success: false, error: 'Logout failed' });
    });
  });
});

describe('Meal Service', () => {
  // Note: These tests would need proper mocking of the axios instance
  // For now, we'll just test the service structure
  it('should have all required methods', () => {
    expect(typeof mealService.getMeals).toBe('function');
    expect(typeof mealService.getMeal).toBe('function');
    expect(typeof mealService.createMeal).toBe('function');
    expect(typeof mealService.updateMeal).toBe('function');
    expect(typeof mealService.deleteMeal).toBe('function');
  });
}); 