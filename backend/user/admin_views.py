"""
后台管理系统视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from .models import User, SleepRecord, ExerciseRecord
from .forms import AdminUserForm, AdminSleepRecordForm, AdminExerciseRecordForm


class AdminRequiredMixin:
    """管理员权限验证混入类 - 本地开发版本，跳过登录验证"""
    pass  # 移除所有权限检查，允许直接访问


class AdminLoginView(View):
    """管理员登录视图"""
    
    def get(self, request):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return redirect('admin_panel:dashboard')
        return render(request, 'admin/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user and (user.is_staff or user.is_superuser):
                login(request, user)
                return redirect('admin_panel:dashboard')
            else:
                messages.error(request, '用户名或密码错误，或者您没有管理员权限')
        else:
            messages.error(request, '请输入用户名和密码')
        
        return render(request, 'admin/login.html')


class AdminLogoutView(View):
    """管理员登出视图"""
    
    def get(self, request):
        logout(request)
        return redirect('admin_panel:login')


class DashboardView(AdminRequiredMixin, TemplateView):
    """管理主页"""
    template_name = 'custom_admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 统计数据
        context['user_count'] = User.objects.count()
        context['sleep_record_count'] = SleepRecord.objects.count()
        context['exercise_record_count'] = ExerciseRecord.objects.count()
        context['today_records'] = SleepRecord.objects.filter(
            sleep_date=datetime.now().date()
        ).count()
        context['today_exercise_records'] = ExerciseRecord.objects.filter(
            exercise_date=datetime.now().date()
        ).count()
        
        # 最近7天的记录数量
        week_ago = datetime.now().date() - timedelta(days=7)
        context['week_records'] = SleepRecord.objects.filter(
            sleep_date__gte=week_ago
        ).count()
        context['week_exercise_records'] = ExerciseRecord.objects.filter(
            exercise_date__gte=week_ago
        ).count()
        
        return context


class UserListView(AdminRequiredMixin, ListView):
    """用户列表视图"""
    model = User
    template_name = 'custom_admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-id')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(userName__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class UserCreateView(AdminRequiredMixin, CreateView):
    """用户创建视图"""
    model = User
    form_class = AdminUserForm
    template_name = 'custom_admin/user_form.html'
    success_url = reverse_lazy('admin_panel:user_list')
    
    def form_valid(self, form):
        messages.success(self.request, '用户创建成功')
        return super().form_valid(form)


class UserUpdateView(AdminRequiredMixin, UpdateView):
    """用户更新视图"""
    model = User
    form_class = AdminUserForm
    template_name = 'custom_admin/user_form.html'
    success_url = reverse_lazy('admin_panel:user_list')
    
    def form_valid(self, form):
        messages.success(self.request, '用户信息更新成功')
        return super().form_valid(form)


class UserDeleteView(AdminRequiredMixin, DeleteView):
    """用户删除视图"""
    model = User
    template_name = 'custom_admin/user_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:user_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '用户删除成功')
        return super().delete(request, *args, **kwargs)


class SleepRecordListView(AdminRequiredMixin, ListView):
    """睡眠记录列表视图"""
    model = SleepRecord
    template_name = 'custom_admin/sleep_record_list.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = SleepRecord.objects.select_related('user').order_by('-sleep_date')
        
        # 用户筛选
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # 日期筛选
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(sleep_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(sleep_date__lte=end_date)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        context['selected_user'] = self.request.GET.get('user', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        return context


class SleepRecordCreateView(AdminRequiredMixin, CreateView):
    """睡眠记录创建视图"""
    model = SleepRecord
    form_class = AdminSleepRecordForm
    template_name = 'custom_admin/sleep_record_form.html'
    success_url = reverse_lazy('admin_panel:sleep_record_list')
    
    def form_valid(self, form):
        messages.success(self.request, '睡眠记录创建成功')
        return super().form_valid(form)


class SleepRecordUpdateView(AdminRequiredMixin, UpdateView):
    """睡眠记录更新视图"""
    model = SleepRecord
    form_class = AdminSleepRecordForm
    template_name = 'custom_admin/sleep_record_form.html'
    success_url = reverse_lazy('admin_panel:sleep_record_list')
    
    def form_valid(self, form):
        messages.success(self.request, '睡眠记录更新成功')
        return super().form_valid(form)


class SleepRecordDeleteView(AdminRequiredMixin, DeleteView):
    """睡眠记录删除视图"""
    model = SleepRecord
    template_name = 'custom_admin/sleep_record_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:sleep_record_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '睡眠记录删除成功')
        return super().delete(request, *args, **kwargs)


class ExerciseRecordListView(AdminRequiredMixin, ListView):
    """运动记录列表视图"""
    model = ExerciseRecord
    template_name = 'custom_admin/exercise_record_list.html'
    context_object_name = 'records'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ExerciseRecord.objects.select_related('user').order_by('-exercise_date', '-created_at')
        
        # 用户筛选
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # 运动类型筛选
        exercise_type = self.request.GET.get('exercise_type')
        if exercise_type:
            queryset = queryset.filter(exercise_type=exercise_type)
        
        # 日期筛选
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(exercise_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(exercise_date__lte=end_date)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        context['exercise_types'] = ExerciseRecord.EXERCISE_TYPES
        context['selected_user'] = self.request.GET.get('user', '')
        context['selected_exercise_type'] = self.request.GET.get('exercise_type', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        return context


class ExerciseRecordCreateView(AdminRequiredMixin, CreateView):
    """运动记录创建视图"""
    model = ExerciseRecord
    form_class = AdminExerciseRecordForm
    template_name = 'custom_admin/exercise_record_form.html'
    success_url = reverse_lazy('admin_panel:exercise_record_list')
    
    def form_valid(self, form):
        messages.success(self.request, '运动记录创建成功')
        return super().form_valid(form)


class ExerciseRecordUpdateView(AdminRequiredMixin, UpdateView):
    """运动记录更新视图"""
    model = ExerciseRecord
    form_class = AdminExerciseRecordForm
    template_name = 'custom_admin/exercise_record_form.html'
    success_url = reverse_lazy('admin_panel:exercise_record_list')
    
    def form_valid(self, form):
        messages.success(self.request, '运动记录更新成功')
        return super().form_valid(form)


class ExerciseRecordDeleteView(AdminRequiredMixin, DeleteView):
    """运动记录删除视图"""
    model = ExerciseRecord
    template_name = 'custom_admin/exercise_record_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:exercise_record_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '运动记录删除成功')
        return super().delete(request, *args, **kwargs)
