import React, { useState } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    StyleSheet,
    Alert,
    Share,
} from 'react-native';
import { mealService } from '../services/api';
import { Meal, ScreenProps } from '../types';

const MealDetailScreen: React.FC<ScreenProps<'MealDetail'>> = ({ route, navigation }) => {
    const { meal } = route.params;
    const [currentMeal, setCurrentMeal] = useState<Meal>(meal);

    const handleEdit = (): void => {
        navigation.navigate('EditMeal', { meal: currentMeal });
    };

    const handleDelete = (): void => {
        Alert.alert(
            'Delete Meal',
            'Are you sure you want to delete this meal?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Delete',
                    style: 'destructive',
                    onPress: deleteMeal
                }
            ]
        );
    };

    const deleteMeal = async (): Promise<void> => {
        try {
            const result = await mealService.deleteMeal(currentMeal.id);

            if (result.success) {
                Alert.alert('Success', 'Meal deleted successfully', [
                    { text: 'OK', onPress: () => navigation.goBack() }
                ]);
            } else {
                Alert.alert('Error', result.error || 'Failed to delete meal');
            }
        } catch (error) {
            Alert.alert('Error', 'Failed to delete meal');
        }
    };

    const handleShare = async (): Promise<void> => {
        try {
            const shareContent = `${currentMeal.name}\n\nIngredients:\n${currentMeal.ingredients}\n\nRecipe:\n${currentMeal.recipe}\n\nDifficulty: ${currentMeal.difficulty}`;

            await Share.share({
                message: shareContent,
                title: currentMeal.name,
            });
        } catch (error) {
            Alert.alert('Error', 'Failed to share meal');
        }
    };

    return (
        <ScrollView style={styles.container}>
            <View style={styles.header}>
                <View style={styles.headerLeft}>
                    <Text style={styles.title}>{currentMeal.name}</Text>
                    <Text style={styles.difficulty}>{currentMeal.difficulty}</Text>
                </View>
                <View style={styles.headerRight}>
                    <TouchableOpacity onPress={handleShare} style={styles.actionButton}>
                        <Text style={styles.actionButtonText}>Share</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={handleEdit} style={styles.actionButton}>
                        <Text style={styles.actionButtonText}>Edit</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={handleDelete} style={[styles.actionButton, styles.deleteButton]}>
                        <Text style={[styles.actionButtonText, styles.deleteButtonText]}>Delete</Text>
                    </TouchableOpacity>
                </View>
            </View>

            <View style={styles.content}>
                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Ingredients</Text>
                    <Text style={styles.sectionContent}>{currentMeal.ingredients}</Text>
                </View>

                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Recipe</Text>
                    <Text style={styles.sectionContent}>{currentMeal.recipe}</Text>
                </View>

                <View style={styles.footer}>
                    <Text style={styles.footerText}>
                        Created: {new Date(currentMeal.created_at).toLocaleDateString()}
                    </Text>
                    {currentMeal.updated_at !== currentMeal.created_at && (
                        <Text style={styles.footerText}>
                            Updated: {new Date(currentMeal.updated_at).toLocaleDateString()}
                        </Text>
                    )}
                </View>
            </View>
        </ScrollView>
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
        alignItems: 'flex-start',
        padding: 20,
        paddingTop: 50,
        backgroundColor: '#ffffff',
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    headerLeft: {
        flex: 1,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 5,
    },
    difficulty: {
        fontSize: 14,
        color: '#007AFF',
        fontWeight: 'bold',
        backgroundColor: '#e8f4fd',
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 15,
        alignSelf: 'flex-start',
    },
    headerRight: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'flex-end',
    },
    actionButton: {
        backgroundColor: '#007AFF',
        paddingHorizontal: 12,
        paddingVertical: 6,
        borderRadius: 15,
        marginLeft: 8,
        marginBottom: 5,
    },
    actionButtonText: {
        color: '#ffffff',
        fontSize: 12,
        fontWeight: 'bold',
    },
    deleteButton: {
        backgroundColor: '#FF3B30',
    },
    deleteButtonText: {
        color: '#ffffff',
    },
    content: {
        padding: 20,
    },
    section: {
        backgroundColor: '#ffffff',
        borderRadius: 10,
        padding: 20,
        marginBottom: 20,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 5,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 10,
    },
    sectionContent: {
        fontSize: 16,
        color: '#666',
        lineHeight: 24,
    },
    footer: {
        marginTop: 20,
        padding: 15,
        backgroundColor: '#f0f0f0',
        borderRadius: 10,
    },
    footerText: {
        fontSize: 12,
        color: '#999',
        marginBottom: 2,
    },
});

export default MealDetailScreen; 