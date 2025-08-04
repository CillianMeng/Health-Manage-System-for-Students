from django.contrib import admin
from .models import User, SleepRecord, ExerciseRecord, DietRecord, FoodCalorieReference

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'userName']
    search_fields = ['userName']
    ordering = ['id']

@admin.register(SleepRecord)
class SleepRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'sleep_date', 'bedtime', 'wake_time', 'sleep_duration']
    list_filter = ['sleep_date', 'user']
    search_fields = ['user__userName']
    ordering = ['-sleep_date']

@admin.register(ExerciseRecord)
class ExerciseRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise_date', 'exercise_type', 'duration_minutes', 'calories_burned']
    list_filter = ['exercise_date', 'exercise_type', 'user']
    search_fields = ['user__userName', 'exercise_type']
    ordering = ['-exercise_date']

@admin.register(DietRecord)
class DietRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'diet_date', 'meal_type', 'food_name', 'portion_size', 'total_calories']
    list_filter = ['diet_date', 'meal_type', 'user']
    search_fields = ['user__userName', 'food_name']
    ordering = ['-diet_date', 'meal_type']

@admin.register(FoodCalorieReference)
class FoodCalorieReferenceAdmin(admin.ModelAdmin):
    list_display = ['food_name', 'calories_per_100g', 'food_category']
    list_filter = ['food_category']
    search_fields = ['food_name']
    ordering = ['food_category', 'food_name']
