import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    TextInput,
    TouchableOpacity,
    StyleSheet,
    Alert,
    ScrollView,
    KeyboardAvoidingView,
    Platform,
    ActivityIndicator,
} from 'react-native';
import { mealService } from '../services/api';

const AddEditMealScreen = ({ route, navigation }) => {
    const { meal } = route.params || {};
    const isEditing = !!meal;

    const [formData, setFormData] = useState({
        name: '',
        ingredients: '',
        recipe: '',
        difficulty: 'Easy',
    });
    const [loading, setLoading] = useState(false);

    const difficulties = ['Easy', 'Medium', 'Hard'];

    useEffect(() => {
        if (isEditing && meal) {
            setFormData({
                name: meal.name,
                ingredients: meal.ingredients,
                recipe: meal.recipe,
                difficulty: meal.difficulty,
            });
        }
    }, [isEditing, meal]);

    const handleInputChange = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value,
        }));
    };

    const validateForm = () => {
        if (!formData.name.trim()) {
            Alert.alert('Error', 'Please enter a meal name');
            return false;
        }
        if (!formData.ingredients.trim()) {
            Alert.alert('Error', 'Please enter ingredients');
            return false;
        }
        if (!formData.recipe.trim()) {
            Alert.alert('Error', 'Please enter the recipe');
            return false;
        }
        return true;
    };

    const handleSave = async () => {
        if (!validateForm()) return;

        setLoading(true);
        try {
            const result = isEditing
                ? await mealService.updateMeal(meal.id, formData)
                : await mealService.createMeal(formData);

            if (result.success) {
                Alert.alert(
                    'Success',
                    `Meal ${isEditing ? 'updated' : 'created'} successfully!`,
                    [
                        {
                            text: 'OK',
                            onPress: () => {
                                navigation.goBack();
                            },
                        },
                    ]
                );
            } else {
                Alert.alert('Error', result.error);
            }
        } catch (error) {
            Alert.alert('Error', `Failed to ${isEditing ? 'update' : 'create'} meal`);
        } finally {
            setLoading(false);
        }
    };

    const renderDifficultySelector = () => (
        <View style={styles.difficultyContainer}>
            <Text style={styles.difficultyLabel}>Difficulty:</Text>
            <View style={styles.difficultyButtons}>
                {difficulties.map(difficulty => (
                    <TouchableOpacity
                        key={difficulty}
                        style={[
                            styles.difficultyButton,
                            formData.difficulty === difficulty && styles.difficultyButtonActive
                        ]}
                        onPress={() => handleInputChange('difficulty', difficulty)}
                    >
                        <Text style={[
                            styles.difficultyButtonText,
                            formData.difficulty === difficulty && styles.difficultyButtonTextActive
                        ]}>
                            {difficulty}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>
        </View>
    );

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
            <ScrollView style={styles.scrollView}>
                <View style={styles.header}>
                    <Text style={styles.title}>
                        {isEditing ? 'Edit Meal' : 'Add New Meal'}
                    </Text>
                </View>

                <View style={styles.form}>
                    <View style={styles.inputGroup}>
                        <Text style={styles.label}>Meal Name *</Text>
                        <TextInput
                            style={styles.input}
                            placeholder="Enter meal name"
                            placeholderTextColor="#999"
                            value={formData.name}
                            onChangeText={(value) => handleInputChange('name', value)}
                            autoCapitalize="words"
                        />
                    </View>

                    <View style={styles.inputGroup}>
                        <Text style={styles.label}>Ingredients *</Text>
                        <TextInput
                            style={[styles.input, styles.textArea]}
                            placeholder="List all ingredients..."
                            placeholderTextColor="#999"
                            value={formData.ingredients}
                            onChangeText={(value) => handleInputChange('ingredients', value)}
                            multiline
                            numberOfLines={4}
                            textAlignVertical="top"
                        />
                    </View>

                    <View style={styles.inputGroup}>
                        <Text style={styles.label}>Recipe *</Text>
                        <TextInput
                            style={[styles.input, styles.textArea]}
                            placeholder="Enter cooking instructions..."
                            placeholderTextColor="#999"
                            value={formData.recipe}
                            onChangeText={(value) => handleInputChange('recipe', value)}
                            multiline
                            numberOfLines={6}
                            textAlignVertical="top"
                        />
                    </View>

                    {renderDifficultySelector()}

                    <TouchableOpacity
                        style={[styles.saveButton, loading && styles.saveButtonDisabled]}
                        onPress={handleSave}
                        disabled={loading}
                    >
                        {loading ? (
                            <ActivityIndicator color="#ffffff" />
                        ) : (
                            <Text style={styles.saveButtonText}>
                                {isEditing ? 'Update Meal' : 'Add Meal'}
                            </Text>
                        )}
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    scrollView: {
        flex: 1,
    },
    header: {
        padding: 20,
        paddingTop: 50,
        backgroundColor: '#ffffff',
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
    },
    form: {
        padding: 20,
    },
    inputGroup: {
        marginBottom: 20,
    },
    label: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 8,
    },
    input: {
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 8,
        padding: 15,
        fontSize: 16,
        backgroundColor: '#ffffff',
    },
    textArea: {
        height: 100,
        textAlignVertical: 'top',
    },
    difficultyContainer: {
        marginBottom: 30,
    },
    difficultyLabel: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 10,
    },
    difficultyButtons: {
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    difficultyButton: {
        flex: 1,
        padding: 12,
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 8,
        alignItems: 'center',
        marginHorizontal: 5,
        backgroundColor: '#ffffff',
    },
    difficultyButtonActive: {
        backgroundColor: '#007AFF',
        borderColor: '#007AFF',
    },
    difficultyButtonText: {
        fontSize: 14,
        color: '#333',
        fontWeight: 'bold',
    },
    difficultyButtonTextActive: {
        color: '#ffffff',
    },
    saveButton: {
        backgroundColor: '#007AFF',
        borderRadius: 8,
        padding: 15,
        alignItems: 'center',
        marginTop: 20,
    },
    saveButtonDisabled: {
        backgroundColor: '#ccc',
    },
    saveButtonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: 'bold',
    },
});

export default AddEditMealScreen; 