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
    WeeklySleepStatsView
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
]