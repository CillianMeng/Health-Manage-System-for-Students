from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import User
from .utils import set_user_password
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def admin_dashboard(request):
    """后台管理首页"""
    total_users = User.objects.count()
    
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
    return render(request, 'admin/user_detail.html', {'user': user})
