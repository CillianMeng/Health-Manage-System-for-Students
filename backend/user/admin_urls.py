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
]
