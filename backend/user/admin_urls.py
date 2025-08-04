"""
后台管理系统URL配置
"""
from django.urls import path
from . import admin_views

app_name = 'admin_panel'

urlpatterns = [
    # 直接访问后台管理 - 跳过登录
    path('', admin_views.DashboardView.as_view(), name='dashboard'),
    
    # 保留登录相关路由（备用）
    path('login/', admin_views.AdminLoginView.as_view(), name='login'),
    path('logout/', admin_views.AdminLogoutView.as_view(), name='logout'),
    
    # 用户管理
    path('users/', admin_views.UserListView.as_view(), name='user_list'),
    path('users/add/', admin_views.UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', admin_views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', admin_views.UserDeleteView.as_view(), name='user_delete'),
    
    # 睡眠记录管理
    path('sleep-records/', admin_views.SleepRecordListView.as_view(), name='sleep_record_list'),
    path('sleep-records/add/', admin_views.SleepRecordCreateView.as_view(), name='sleep_record_add'),
    path('sleep-records/<int:pk>/edit/', admin_views.SleepRecordUpdateView.as_view(), name='sleep_record_edit'),
    path('sleep-records/<int:pk>/delete/', admin_views.SleepRecordDeleteView.as_view(), name='sleep_record_delete'),
    
    # 运动记录管理
    path('exercise-records/', admin_views.ExerciseRecordListView.as_view(), name='exercise_record_list'),
    path('exercise-records/add/', admin_views.ExerciseRecordCreateView.as_view(), name='exercise_record_add'),
    path('exercise-records/<int:pk>/edit/', admin_views.ExerciseRecordUpdateView.as_view(), name='exercise_record_edit'),
    path('exercise-records/<int:pk>/delete/', admin_views.ExerciseRecordDeleteView.as_view(), name='exercise_record_delete'),
    
    # 饮食记录管理
    path('diet-records/', admin_views.DietRecordListView.as_view(), name='diet_record_list'),
    path('diet-records/add/', admin_views.DietRecordCreateView.as_view(), name='diet_record_add'),
    path('diet-records/<int:pk>/edit/', admin_views.DietRecordUpdateView.as_view(), name='diet_record_edit'),
    path('diet-records/<int:pk>/delete/', admin_views.DietRecordDeleteView.as_view(), name='diet_record_delete'),
    
    # 食物卡路里参考管理
    path('food-calories/', admin_views.FoodCalorieReferenceListView.as_view(), name='food_calorie_reference_list'),
    path('food-calories/add/', admin_views.FoodCalorieReferenceCreateView.as_view(), name='food_calorie_reference_add'),
    path('food-calories/<int:pk>/edit/', admin_views.FoodCalorieReferenceUpdateView.as_view(), name='food_calorie_reference_edit'),
    path('food-calories/<int:pk>/delete/', admin_views.FoodCalorieReferenceDeleteView.as_view(), name='food_calorie_reference_delete'),
]
