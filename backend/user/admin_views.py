from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, date, timedelta
from .models import User, SleepRecord
from .utils import set_user_password
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def admin_dashboard(request):
    """后台管理首页"""
    total_users = User.objects.count()
    total_sleep_records = SleepRecord.objects.count()
    
    # 最近7天的睡眠记录数
    seven_days_ago = date.today() - timedelta(days=7)
    recent_sleep_records = SleepRecord.objects.filter(date__gte=seven_days_ago).count()
    
    # 搜索功能
    search_query = request.GET.get('search', '')
    if search_query:
        users = User.objects.filter(userName__icontains=search_query)
    else:
        users = User.objects.all()
    
    # 分页功能
    paginator = Paginator(users, 10)  # 每页显示10个用户
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'total_users': total_users,
        'total_sleep_records': total_sleep_records,
        'recent_sleep_records': recent_sleep_records,
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'admin/dashboard.html', context)

def admin_user_create(request):
    """创建用户页面"""
    if request.method == 'POST':
        userName = request.POST.get('userName')
        password = request.POST.get('password')
        
        # 验证数据
        if not userName or not password:
            messages.error(request, '用户名和密码不能为空')
            return render(request, 'admin/user_create.html')
        
        # 检查用户名是否已存在
        if User.objects.filter(userName=userName).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'admin/user_create.html')
        
        try:
            # 创建用户
            user = User(userName=userName)
            set_user_password(user, password)
            user.save()
            messages.success(request, f'用户 {userName} 创建成功')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'创建用户失败: {str(e)}')
    
    return render(request, 'admin/user_create.html')

def admin_user_edit(request, user_id):
    """编辑用户页面"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        userName = request.POST.get('userName')
        password = request.POST.get('password')
        
        # 验证数据
        if not userName:
            messages.error(request, '用户名不能为空')
            return render(request, 'admin/user_edit.html', {'user': user})
        
        # 检查用户名是否已被其他用户使用
        if User.objects.filter(userName=userName).exclude(id=user_id).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'admin/user_edit.html', {'user': user})
        
        try:
            # 更新用户信息
            user.userName = userName
            if password:  # 如果提供了新密码，则更新密码
                set_user_password(user, password)
            user.save()
            messages.success(request, f'用户 {userName} 更新成功')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'更新用户失败: {str(e)}')
    
    return render(request, 'admin/user_edit.html', {'user': user})

@csrf_exempt
@require_http_methods(["DELETE"])
def admin_user_delete(request, user_id):
    """删除用户 (AJAX)"""
    try:
        user = get_object_or_404(User, id=user_id)
        userName = user.userName
        user.delete()
        return JsonResponse({
            'success': True, 
            'message': f'用户 {userName} 删除成功'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'删除用户失败: {str(e)}'
        }, status=400)

def admin_user_detail(request, user_id):
    """用户详情页面"""
    user = get_object_or_404(User, id=user_id)
    
    # 获取用户的睡眠记录
    sleep_records = SleepRecord.objects.filter(user=user).order_by('-date')[:10]
    
    return render(request, 'admin/user_detail.html', {
        'user': user,
        'sleep_records': sleep_records
    })

# 睡眠记录管理视图
def admin_sleep_records(request):
    """睡眠记录管理页面"""
    # 获取查询参数
    user_search = request.GET.get('user_search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # 构建查询
    records = SleepRecord.objects.select_related('user').all()
    
    if user_search:
        records = records.filter(user__userName__icontains=user_search)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            records = records.filter(date__gte=date_from_obj)
        except ValueError:
            messages.error(request, '开始日期格式错误')
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            records = records.filter(date__lte=date_to_obj)
        except ValueError:
            messages.error(request, '结束日期格式错误')
    
    records = records.order_by('-date', '-created_at')
    
    # 分页
    paginator = Paginator(records, 15)  # 每页显示15条记录
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 统计信息
    total_records = records.count()
    if records.exists():
        avg_sleep_duration = sum(
            record.sleep_duration.total_seconds() / 3600 
            for record in records 
            if record.sleep_duration
        ) / len([r for r in records if r.sleep_duration])
        avg_sleep_duration = round(avg_sleep_duration, 2)
    else:
        avg_sleep_duration = 0
    
    context = {
        'page_obj': page_obj,
        'user_search': user_search,
        'date_from': date_from,
        'date_to': date_to,
        'total_records': total_records,
        'avg_sleep_duration': avg_sleep_duration,
    }
    return render(request, 'admin/sleep_records.html', context)

def admin_sleep_record_create(request):
    """创建睡眠记录页面"""
    # 获取可能的预选用户ID
    preselected_user_id = request.GET.get('user_id', '')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        record_date = request.POST.get('date')
        sleep_time = request.POST.get('sleep_time')
        wake_time = request.POST.get('wake_time')
        
        # 验证数据
        if not all([user_id, record_date, sleep_time, wake_time]):
            messages.error(request, '所有字段都是必填的')
            users = User.objects.all().order_by('userName')
            return render(request, 'admin/sleep_record_create.html', {
                'users': users,
                'preselected_user_id': preselected_user_id
            })
        
        try:
            user = User.objects.get(id=user_id)
            record_date_obj = datetime.strptime(record_date, '%Y-%m-%d').date()
            sleep_time_obj = datetime.strptime(sleep_time, '%H:%M').time()
            wake_time_obj = datetime.strptime(wake_time, '%H:%M').time()
        except (User.DoesNotExist, ValueError) as e:
            messages.error(request, f'数据格式错误: {str(e)}')
            users = User.objects.all().order_by('userName')
            return render(request, 'admin/sleep_record_create.html', {
                'users': users,
                'preselected_user_id': preselected_user_id
            })
        
        # 检查是否已存在记录
        if SleepRecord.objects.filter(user=user, date=record_date_obj).exists():
            messages.error(request, f'用户 {user.userName} 在 {record_date} 的睡眠记录已存在')
            users = User.objects.all().order_by('userName')
            return render(request, 'admin/sleep_record_create.html', {
                'users': users,
                'preselected_user_id': preselected_user_id
            })
        
        try:
            # 创建睡眠记录
            sleep_record = SleepRecord.objects.create(
                user=user,
                date=record_date_obj,
                sleep_time=sleep_time_obj,
                wake_time=wake_time_obj
            )
            messages.success(request, f'成功为 {user.userName} 创建睡眠记录')
            return redirect('admin_sleep_records')
        except Exception as e:
            messages.error(request, f'创建睡眠记录失败: {str(e)}')
    
    users = User.objects.all().order_by('userName')
    today = datetime.now().date()
    return render(request, 'admin/sleep_record_create.html', {
        'users': users,
        'preselected_user_id': preselected_user_id,
        'today': today
    })

def admin_sleep_record_edit(request, record_id):
    """编辑睡眠记录页面"""
    record = get_object_or_404(SleepRecord, id=record_id)
    
    if request.method == 'POST':
        record_date = request.POST.get('date')
        sleep_time = request.POST.get('sleep_time')
        wake_time = request.POST.get('wake_time')
        
        # 验证数据
        if not all([record_date, sleep_time, wake_time]):
            messages.error(request, '所有字段都是必填的')
            return render(request, 'admin/sleep_record_edit.html', {'record': record})
        
        try:
            record_date_obj = datetime.strptime(record_date, '%Y-%m-%d').date()
            sleep_time_obj = datetime.strptime(sleep_time, '%H:%M').time()
            wake_time_obj = datetime.strptime(wake_time, '%H:%M').time()
        except ValueError as e:
            messages.error(request, f'数据格式错误: {str(e)}')
            return render(request, 'admin/sleep_record_edit.html', {'record': record})
        
        # 检查日期是否与其他记录冲突（排除自己）
        existing_record = SleepRecord.objects.filter(
            user=record.user, 
            date=record_date_obj
        ).exclude(id=record.id).first()
        
        if existing_record:
            messages.error(request, f'用户 {record.user.userName} 在 {record_date} 已有其他睡眠记录')
            return render(request, 'admin/sleep_record_edit.html', {'record': record})
        
        try:
            # 更新睡眠记录
            record.date = record_date_obj
            record.sleep_time = sleep_time_obj
            record.wake_time = wake_time_obj
            record.save()
            messages.success(request, f'成功更新 {record.user.userName} 的睡眠记录')
            return redirect('admin_sleep_records')
        except Exception as e:
            messages.error(request, f'更新睡眠记录失败: {str(e)}')
    
    return render(request, 'admin/sleep_record_edit.html', {'record': record})

@csrf_exempt
@require_http_methods(["DELETE"])
def admin_sleep_record_delete(request, record_id):
    """删除睡眠记录 (AJAX)"""
    try:
        record = get_object_or_404(SleepRecord, id=record_id)
        user_name = record.user.userName
        record_date = record.date
        record.delete()
        return JsonResponse({
            'success': True, 
            'message': f'成功删除 {user_name} 在 {record_date} 的睡眠记录'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'删除睡眠记录失败: {str(e)}'
        }, status=400)

def admin_sleep_record_detail(request, record_id):
    """睡眠记录详情页面"""
    record = get_object_or_404(SleepRecord, id=record_id)
    return render(request, 'admin/sleep_record_detail.html', {'record': record})
