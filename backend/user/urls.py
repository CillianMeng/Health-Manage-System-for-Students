from django.urls import path
from .views import (
    LoginView, RegisterView, LogoutView, CheckLoginView,
    SleepRecordListView, SleepRecordCreateView, SleepRecordDetailView, SleepStatisticsView
)
from .admin_views import (
    admin_dashboard, admin_user_create, admin_user_edit, 
    admin_user_delete, admin_user_detail,
    admin_sleep_records, admin_sleep_record_create, admin_sleep_record_edit,
    admin_sleep_record_delete, admin_sleep_record_detail
)

urlpatterns = [
    # API 路由 - 用户认证
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('check-login/', CheckLoginView.as_view(), name='check_login'),
    
    # API 路由 - 睡眠记录
    path('sleep-records/', SleepRecordListView.as_view(), name='sleep_record_list'),
    path('sleep-records/create/', SleepRecordCreateView.as_view(), name='sleep_record_create'),
    path('sleep-records/<int:record_id>/', SleepRecordDetailView.as_view(), name='sleep_record_detail'),
    path('sleep-statistics/', SleepStatisticsView.as_view(), name='sleep_statistics'),
    
    # 后台管理路由 - 用户管理
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('admin/user/create/', admin_user_create, name='admin_user_create'),
    path('admin/user/<int:user_id>/edit/', admin_user_edit, name='admin_user_edit'),
    path('admin/user/<int:user_id>/delete/', admin_user_delete, name='admin_user_delete'),
    path('admin/user/<int:user_id>/', admin_user_detail, name='admin_user_detail'),
    
    # 后台管理路由 - 睡眠记录管理
    path('admin/sleep-records/', admin_sleep_records, name='admin_sleep_records'),
    path('admin/sleep-records/create/', admin_sleep_record_create, name='admin_sleep_record_create'),
    path('admin/sleep-records/<int:record_id>/edit/', admin_sleep_record_edit, name='admin_sleep_record_edit'),
    path('admin/sleep-records/<int:record_id>/delete/', admin_sleep_record_delete, name='admin_sleep_record_delete'),
    path('admin/sleep-records/<int:record_id>/', admin_sleep_record_detail, name='admin_sleep_record_detail'),
]