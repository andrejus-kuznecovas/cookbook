import React, { useState, useEffect, useCallback } from 'react';
import {
    View,
    Text,
    FlatList,
    TouchableOpacity,
    StyleSheet,
    Alert,
    RefreshControl,
    ActivityIndicator,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { mealService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const MealsListScreen = ({ navigation }) => {
    const [meals, setMeals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const { logout } = useAuth();

    const fetchMeals = async () => {
        try {
            const result = await mealService.getMeals();

            if (result.success) {
                setMeals(result.data);
            } else {
                Alert.alert('Error', result.error);
            }
        } catch (error) {
            Alert.alert('Error', 'Failed to load meals');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useFocusEffect(
        useCallback(() => {
            fetchMeals();
        }, [])
    );

    const handleRefresh = () => {
        setRefreshing(true);
        fetchMeals();
    };

    const handleLogout = async () => {
        Alert.alert(
            'Logout',
            'Are you sure you want to logout?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Logout',
                    style: 'destructive',
                    onPress: async () => {
                        await logout();
                    }
                }
            ]
        );
    };

    const renderMealItem = ({ item }) => (
        <TouchableOpacity
            style={styles.mealCard}
            onPress={() => navigation.navigate('MealDetail', { meal: item })}
        >
            <View style={styles.mealHeader}>
                <Text style={styles.mealName}>{item.name}</Text>
                <Text style={styles.mealDifficulty}>{item.difficulty}</Text>
            </View>
            <Text style={styles.mealIngredients} numberOfLines={2}>
                {item.ingredients}
            </Text>
            <Text style={styles.mealDate}>
                {new Date(item.created_at).toLocaleDateString()}
            </Text>
        </TouchableOpacity>
    );

    const renderEmptyState = () => (
        <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No meals yet!</Text>
            <Text style={styles.emptyStateSubtext}>
                Tap the + button to add your first meal
            </Text>
        </View>
    );

    if (loading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#007AFF" />
                <Text style={styles.loadingText}>Loading meals...</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.headerTitle}>My Cookbook</Text>
                <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
                    <Text style={styles.logoutText}>Logout</Text>
                </TouchableOpacity>
            </View>

            <FlatList
                data={meals}
                renderItem={renderMealItem}
                keyExtractor={(item) => item.id.toString()}
                contentContainerStyle={styles.listContainer}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={handleRefresh}
                        colors={['#007AFF']}
                    />
                }
                ListEmptyComponent={renderEmptyState}
            />

            <TouchableOpacity
                style={styles.fab}
                onPress={() => navigation.navigate('AddMeal')}
            >
                <Text style={styles.fabText}>+</Text>
            </TouchableOpacity>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 20,
        paddingTop: 50,
        backgroundColor: '#ffffff',
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    headerTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
    },
    logoutButton: {
        padding: 8,
    },
    logoutText: {
        color: '#007AFF',
        fontSize: 16,
    },
    listContainer: {
        padding: 20,
        paddingBottom: 100,
    },
    mealCard: {
        backgroundColor: '#ffffff',
        borderRadius: 10,
        padding: 15,
        marginBottom: 15,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 5,
    },
    mealHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10,
    },
    mealName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        flex: 1,
    },
    mealDifficulty: {
        fontSize: 12,
        color: '#007AFF',
        fontWeight: 'bold',
        backgroundColor: '#e8f4fd',
        paddingHorizontal: 8,
        paddingVertical: 4,
        borderRadius: 12,
    },
    mealIngredients: {
        fontSize: 14,
        color: '#666',
        marginBottom: 8,
    },
    mealDate: {
        fontSize: 12,
        color: '#999',
    },
    emptyState: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        marginTop: 100,
    },
    emptyStateText: {
        fontSize: 18,
        color: '#666',
        marginBottom: 10,
    },
    emptyStateSubtext: {
        fontSize: 14,
        color: '#999',
        textAlign: 'center',
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    loadingText: {
        marginTop: 10,
        fontSize: 16,
        color: '#666',
    },
    fab: {
        position: 'absolute',
        bottom: 30,
        right: 30,
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: '#007AFF',
        justifyContent: 'center',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 4,
        },
        shadowOpacity: 0.3,
        shadowRadius: 4.65,
        elevation: 8,
    },
    fabText: {
        fontSize: 24,
        color: '#ffffff',
        fontWeight: 'bold',
    },
});

export default MealsListScreen; 