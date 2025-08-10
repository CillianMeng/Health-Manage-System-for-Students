from django.urls import path
from .views import (
    LoginView, 
    RegisterView, 
    LogoutView, 
    CheckLoginStatusView, 
    UserProfileView,
    UserSessionsView,
    DebugSessionView,
    CSRFTokenView,
    SleepRecordView,
    SleepRecordDetailView,
    WeeklySleepStatsView,
    ExerciseRecordView,
    ExerciseRecordDetailView,
    WeeklyExerciseStatsView,
    DietRecordView,
    DietRecordDetailView,
    WeeklyDietStatsView,
    FoodCalorieReferenceView,
    HealthReportGenerateView,
    HealthReportLatestView,
    HealthReportListView,
    HealthReportDetailView,
    HealthReportStatisticsView,
    HealthGoalView,
    HealthGoalDetailView,
    HealthGoalProgressView,
    HealthGoalStatsView
)

urlpatterns = [
    path('csrf-token/', CSRFTokenView.as_view(), name='csrf_token'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('check-login/', CheckLoginStatusView.as_view(), name='check_login'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('sessions/', UserSessionsView.as_view(), name='user_sessions'),
    path('debug-session/', DebugSessionView.as_view(), name='debug_session'),
    
    # 睡眠记录相关路由
    path('sleep-records/', SleepRecordView.as_view(), name='sleep_records'),
    path('sleep-records/<int:pk>/', SleepRecordDetailView.as_view(), name='sleep_record_detail'),
    path('sleep-records/weekly/', WeeklySleepStatsView.as_view(), name='weekly_sleep_stats'),
    
    # 运动记录相关路由
    path('exercise-records/', ExerciseRecordView.as_view(), name='exercise_records'),
    path('exercise-records/<int:record_id>/', ExerciseRecordDetailView.as_view(), name='exercise_record_detail'),
    path('exercise-records/weekly/', WeeklyExerciseStatsView.as_view(), name='weekly_exercise_stats'),
    
    # 饮食记录相关路由
    path('diet-records/', DietRecordView.as_view(), name='diet_records'),
    path('diet-records/<int:record_id>/', DietRecordDetailView.as_view(), name='diet_record_detail'),
    path('diet-records/weekly/', WeeklyDietStatsView.as_view(), name='weekly_diet_stats'),
    
    # 食物卡路里参考路由
    path('food-calories/', FoodCalorieReferenceView.as_view(), name='food_calories'),
    path('food-calories/search/', FoodCalorieReferenceView.as_view(), name='food_calories_search'),
    
    # 健康报告相关路由
    path('health-reports/generate/', HealthReportGenerateView.as_view(), name='health_report_generate'),
    path('health-reports/latest/', HealthReportLatestView.as_view(), name='health_report_latest'),
    path('health-reports/', HealthReportListView.as_view(), name='health_report_list'),
    path('health-reports/<int:report_id>/', HealthReportDetailView.as_view(), name='health_report_detail'),
    path('health-reports/statistics/', HealthReportStatisticsView.as_view(), name='health_report_statistics'),
    
    # 健康目标相关路由
    path('health-goals/', HealthGoalView.as_view(), name='health_goals'),
    path('health-goals/<int:pk>/', HealthGoalDetailView.as_view(), name='health_goal_detail'),
    path('health-goals/<int:goal_id>/progress/', HealthGoalProgressView.as_view(), name='health_goal_progress'),
    path('health-goals/stats/', HealthGoalStatsView.as_view(), name='health_goal_stats'),
]