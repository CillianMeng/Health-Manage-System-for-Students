from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, date, timedelta
from .models import User, SleepRecord, ExerciseRecord, FoodItem, DietRecord
from .utils import set_user_password
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def admin_dashboard(request):
    """后台管理首页"""
    total_users = User.objects.count()
    total_sleep_records = SleepRecord.objects.count()
    total_exercise_records = ExerciseRecord.objects.count()
    total_diet_records = DietRecord.objects.count()
    
    # 最近7天的记录数
    seven_days_ago = date.today() - timedelta(days=7)
    recent_sleep_records = SleepRecord.objects.filter(date__gte=seven_days_ago).count()
    recent_exercise_records = ExerciseRecord.objects.filter(date__gte=seven_days_ago).count()
    recent_diet_records = DietRecord.objects.filter(date__gte=seven_days_ago).count()
    
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
        'total_exercise_records': total_exercise_records,
        'total_diet_records': total_diet_records,
        'recent_sleep_records': recent_sleep_records,
        'recent_exercise_records': recent_exercise_records,
        'recent_diet_records': recent_diet_records,
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
    
    # 获取用户的运动记录
    exercise_records = ExerciseRecord.objects.filter(user=user).order_by('-date', '-created_at')[:10]
    
    return render(request, 'admin/user_detail.html', {
        'user': user,
        'sleep_records': sleep_records,
        'exercise_records': exercise_records
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


# 运动记录管理视图
def admin_exercise_records(request):
    """运动记录管理页面"""
    # 获取查询参数
    user_search = request.GET.get('user_search', '')
    exercise_type = request.GET.get('exercise_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # 构建查询
    records = ExerciseRecord.objects.select_related('user').all()
    
    if user_search:
        records = records.filter(user__userName__icontains=user_search)
    
    if exercise_type:
        records = records.filter(exercise_type=exercise_type)
    
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
    total_duration = sum(record.duration_minutes for record in records)
    total_calories = sum(record.calories_burned for record in records)
    
    # 运动类型选项
    exercise_type_choices = ExerciseRecord.EXERCISE_TYPES
    
    context = {
        'page_obj': page_obj,
        'user_search': user_search,
        'exercise_type': exercise_type,
        'date_from': date_from,
        'date_to': date_to,
        'total_records': total_records,
        'total_duration': total_duration,
        'total_calories': total_calories,
        'exercise_type_choices': exercise_type_choices,
    }
    return render(request, 'admin/exercise_records.html', context)

def admin_exercise_record_create(request):
    """创建运动记录页面"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        record_date = request.POST.get('date')
        exercise_type = request.POST.get('exercise_type')
        duration_minutes = request.POST.get('duration_minutes')
        calories_burned = request.POST.get('calories_burned')
        notes = request.POST.get('notes', '')
        
        # 验证数据
        if not all([user_id, record_date, exercise_type, duration_minutes, calories_burned]):
            messages.error(request, '除备注外的所有字段都是必填的')
            users = User.objects.all().order_by('userName')
            preselected_user_id = request.GET.get('user_id')
            today = datetime.now().date()
            return render(request, 'admin/exercise_record_create.html', {
                'users': users,
                'preselected_user_id': preselected_user_id,
                'today': today,
                'exercise_type_choices': ExerciseRecord.EXERCISE_TYPES
            })
        
        try:
            user = User.objects.get(id=user_id)
            record_date_obj = datetime.strptime(record_date, '%Y-%m-%d').date()
            duration_minutes = int(duration_minutes)
            calories_burned = int(calories_burned)
        except (User.DoesNotExist, ValueError) as e:
            messages.error(request, f'数据格式错误: {str(e)}')
            users = User.objects.all().order_by('userName')
            preselected_user_id = request.GET.get('user_id')
            today = datetime.now().date()
            return render(request, 'admin/exercise_record_create.html', {
                'users': users,
                'preselected_user_id': preselected_user_id,
                'today': today,
                'exercise_type_choices': ExerciseRecord.EXERCISE_TYPES
            })
        
        # 验证数据范围
        if duration_minutes <= 0 or duration_minutes > 600:
            messages.error(request, '运动时长必须在1-600分钟之间')
            users = User.objects.all().order_by('userName')
            preselected_user_id = request.GET.get('user_id')
            today = datetime.now().date()
            return render(request, 'admin/exercise_record_create.html', {
                'users': users,
                'preselected_user_id': preselected_user_id,
                'today': today,
                'exercise_type_choices': ExerciseRecord.EXERCISE_TYPES
            })
        
        if calories_burned <= 0 or calories_burned > 3000:
            messages.error(request, '消耗卡路里必须在1-3000之间')
            users = User.objects.all().order_by('userName')
            preselected_user_id = request.GET.get('user_id')
            today = datetime.now().date()
            return render(request, 'admin/exercise_record_create.html', {
                'users': users,
                'preselected_user_id': preselected_user_id,
                'today': today,
                'exercise_type_choices': ExerciseRecord.EXERCISE_TYPES
            })
        
        try:
            # 创建运动记录
            exercise_record = ExerciseRecord.objects.create(
                user=user,
                date=record_date_obj,
                exercise_type=exercise_type,
                duration_minutes=duration_minutes,
                calories_burned=calories_burned,
                notes=notes
            )
            messages.success(request, f'成功为 {user.userName} 创建运动记录')
            return redirect('admin_exercise_records')
        except Exception as e:
            messages.error(request, f'创建运动记录失败: {str(e)}')
    
    # GET 请求
    users = User.objects.all().order_by('userName')
    preselected_user_id = request.GET.get('user_id')
    today = datetime.now().date()
    return render(request, 'admin/exercise_record_create.html', {
        'users': users,
        'preselected_user_id': preselected_user_id,
        'today': today,
        'exercise_type_choices': ExerciseRecord.EXERCISE_TYPES
    })

def admin_exercise_record_edit(request, record_id):
    """编辑运动记录页面"""
    record = get_object_or_404(ExerciseRecord, id=record_id)
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        record_date = request.POST.get('date')
        exercise_type = request.POST.get('exercise_type')
        duration_minutes = request.POST.get('duration_minutes')
        calories_burned = request.POST.get('calories_burned')
        notes = request.POST.get('notes', '')
        
        # 验证数据
        if not all([user_id, record_date, exercise_type, duration_minutes, calories_burned]):
            messages.error(request, '除备注外的所有字段都是必填的')
            users = User.objects.all().order_by('userName')
            today = datetime.now().date()
            return render(request, 'admin/exercise_record_edit.html', {
                'record': record,
                'users': users,
                'today': today,
                'exercise_type_choices': ExerciseRecord.EXERCISE_TYPES
            })
        
        try:
            user = User.objects.get(id=user_id)
            record_date_obj = datetime.strptime(record_date, '%Y-%m-%d').date()
            duration_minutes = int(duration_minutes)
            calories_burned = int(calories_burned)
        except (User.DoesNotExist, ValueError) as e:
            messages.error(request, f'数据格式错误: {str(e)}')
            users = User.objects.all().order_by('userName')
            today = datetime.now().date()
            return render(request, 'admin/exercise_record_edit.html', {
                'record': record,
                'users': users,
                'today': today,
                'exercise_type_choices': ExerciseRecord.EXERCISE_TYPES
            })
        
        # 验证数据范围
        if duration_minutes <= 0 or duration_minutes > 600:
            messages.error(request, '运动时长必须在1-600分钟之间')
            users = User.objects.all().order_by('userName')
            today = datetime.now().date()
            return render(request, 'admin/exercise_record_edit.html', {
                'record': record,
                'users': users,
                'today': today,
                'exercise_type_choices': ExerciseRecord.EXERCISE_TYPES
            })
        
        if calories_burned <= 0 or calories_burned > 3000:
            messages.error(request, '消耗卡路里必须在1-3000之间')
            users = User.objects.all().order_by('userName')
            today = datetime.now().date()
            return render(request, 'admin/exercise_record_edit.html', {
                'record': record,
                'users': users,
                'today': today,
                'exercise_type_choices': ExerciseRecord.EXERCISE_TYPES
            })
        
        try:
            # 更新运动记录
            record.user = user
            record.date = record_date_obj
            record.exercise_type = exercise_type
            record.duration_minutes = duration_minutes
            record.calories_burned = calories_burned
            record.notes = notes
            record.save()
            
            messages.success(request, f'成功更新 {user.userName} 的运动记录')
            return redirect('admin_exercise_records')
        except Exception as e:
            messages.error(request, f'更新运动记录失败: {str(e)}')
    
    # GET 请求
    users = User.objects.all().order_by('userName')
    today = datetime.now().date()
    return render(request, 'admin/exercise_record_edit.html', {
        'record': record,
        'users': users,
        'today': today,
        'exercise_type_choices': ExerciseRecord.EXERCISE_TYPES
    })

@csrf_exempt
@require_http_methods(["DELETE"])
def admin_exercise_record_delete(request, record_id):
    """删除运动记录 (AJAX)"""
    try:
        record = get_object_or_404(ExerciseRecord, id=record_id)
        user_name = record.user.userName
        exercise_type = record.get_exercise_type_display()
        record_date = record.date
        
        record.delete()
        return JsonResponse({
            'success': True, 
            'message': f'成功删除 {user_name} 在 {record_date} 的{exercise_type}记录'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'删除运动记录失败: {str(e)}'
        }, status=400)

def admin_exercise_record_detail(request, record_id):
    """运动记录详情页面"""
    record = get_object_or_404(ExerciseRecord, id=record_id)
    return render(request, 'admin/exercise_record_detail.html', {'record': record})


# 饮食记录管理相关视图

def admin_diet_records(request):
    """饮食记录管理页面"""
    search_query = request.GET.get('search', '')
    meal_type_filter = request.GET.get('meal_type', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    records = DietRecord.objects.all()
    
    # 搜索功能
    if search_query:
        records = records.filter(
            Q(user__userName__icontains=search_query) |
            Q(food_name__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # 餐次筛选
    if meal_type_filter:
        records = records.filter(meal_type=meal_type_filter)
    
    # 日期筛选
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            records = records.filter(date__gte=start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            records = records.filter(date__lte=end_date_obj)
        except ValueError:
            pass
    
    # 按日期倒序排列
    records = records.order_by('-date', '-created_at')
    
    # 分页功能
    paginator = Paginator(records, 20)  # 每页显示20条记录
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 餐次选择
    meal_choices = DietRecord.MEAL_CHOICES
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'meal_type_filter': meal_type_filter,
        'start_date': start_date,
        'end_date': end_date,
        'meal_choices': meal_choices,
    }
    return render(request, 'admin/diet_records.html', context)

def admin_diet_record_create(request):
    """创建饮食记录页面"""
    if request.method == 'POST':
        try:
            # 获取表单数据
            user_id = request.POST.get('user_id')
            date_str = request.POST.get('date')
            meal_type = request.POST.get('meal_type')
            food_item_id = request.POST.get('food_item')
            food_name = request.POST.get('food_name')
            serving_size = request.POST.get('serving_size')
            serving_weight_grams = request.POST.get('serving_weight_grams')
            calories = request.POST.get('calories')
            notes = request.POST.get('notes', '')
            
            # 验证必填字段
            if not all([user_id, date_str, meal_type]):
                messages.error(request, '用户、日期和餐次为必填项')
                return redirect('admin_diet_record_create')
            
            # 获取用户
            user = get_object_or_404(User, id=user_id)
            
            # 转换日期
            record_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # 获取食物项目（如果选择了）
            food_item = None
            if food_item_id:
                food_item = get_object_or_404(FoodItem, id=food_item_id)
                # 如果没有提供食物名称，使用数据库中的名称
                if not food_name:
                    food_name = food_item.name
            
            # 验证至少有食物名称
            if not food_name:
                messages.error(request, '必须提供食物名称或选择食物数据库中的食物')
                return redirect('admin_diet_record_create')
            
            # 创建饮食记录
            diet_record = DietRecord.objects.create(
                user=user,
                date=record_date,
                meal_type=meal_type,
                food_item=food_item,
                food_name=food_name,
                serving_size=serving_size if serving_size else None,
                serving_weight_grams=float(serving_weight_grams) if serving_weight_grams else None,
                calories=float(calories) if calories else None,
                notes=notes
            )
            
            messages.success(request, f'饮食记录创建成功！记录ID: {diet_record.id}')
            return redirect('admin_diet_records')
            
        except ValueError as e:
            messages.error(request, f'数据格式错误: {str(e)}')
        except Exception as e:
            messages.error(request, f'创建失败: {str(e)}')
        
        return redirect('admin_diet_record_create')
    
    # GET请求：显示创建表单
    users = User.objects.all().order_by('userName')
    foods = FoodItem.objects.all().order_by('category', 'name')
    meal_choices = DietRecord.MEAL_CHOICES
    
    context = {
        'users': users,
        'foods': foods,
        'meal_choices': meal_choices,
    }
    return render(request, 'admin/diet_record_create.html', context)

def admin_diet_record_edit(request, record_id):
    """编辑饮食记录页面"""
    record = get_object_or_404(DietRecord, id=record_id)
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            user_id = request.POST.get('user_id')
            date_str = request.POST.get('date')
            meal_type = request.POST.get('meal_type')
            food_item_id = request.POST.get('food_item')
            food_name = request.POST.get('food_name')
            serving_size = request.POST.get('serving_size')
            serving_weight_grams = request.POST.get('serving_weight_grams')
            calories = request.POST.get('calories')
            notes = request.POST.get('notes', '')
            
            # 验证必填字段
            if not all([user_id, date_str, meal_type]):
                messages.error(request, '用户、日期和餐次为必填项')
                return redirect('admin_diet_record_edit', record_id=record_id)
            
            # 获取用户
            user = get_object_or_404(User, id=user_id)
            
            # 转换日期
            record_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # 获取食物项目（如果选择了）
            food_item = None
            if food_item_id:
                food_item = get_object_or_404(FoodItem, id=food_item_id)
                # 如果没有提供食物名称，使用数据库中的名称
                if not food_name:
                    food_name = food_item.name
            
            # 验证至少有食物名称
            if not food_name:
                messages.error(request, '必须提供食物名称或选择食物数据库中的食物')
                return redirect('admin_diet_record_edit', record_id=record_id)
            
            # 更新饮食记录
            record.user = user
            record.date = record_date
            record.meal_type = meal_type
            record.food_item = food_item
            record.food_name = food_name
            record.serving_size = serving_size if serving_size else None
            record.serving_weight_grams = float(serving_weight_grams) if serving_weight_grams else None
            record.calories = float(calories) if calories else None
            record.notes = notes
            record.save()
            
            messages.success(request, '饮食记录更新成功！')
            return redirect('admin_diet_record_detail', record_id=record.id)
            
        except ValueError as e:
            messages.error(request, f'数据格式错误: {str(e)}')
        except Exception as e:
            messages.error(request, f'更新失败: {str(e)}')
    
    # GET请求：显示编辑表单
    users = User.objects.all().order_by('userName')
    foods = FoodItem.objects.all().order_by('category', 'name')
    meal_choices = DietRecord.MEAL_CHOICES
    
    context = {
        'record': record,
        'users': users,
        'foods': foods,
        'meal_choices': meal_choices,
    }
    return render(request, 'admin/diet_record_edit.html', context)

@csrf_exempt
@require_http_methods(["DELETE"])
def admin_diet_record_delete(request, record_id):
    """删除饮食记录"""
    try:
        record = get_object_or_404(DietRecord, id=record_id)
        record_info = f"{record.user.userName}的{record.get_meal_type_display()}记录"
        record.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'饮食记录 "{record_info}" 删除成功'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }, status=500)

def admin_diet_record_detail(request, record_id):
    """饮食记录详情页面"""
    record = get_object_or_404(DietRecord, id=record_id)
    return render(request, 'admin/diet_record_detail.html', {'record': record})
