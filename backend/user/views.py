from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import LoginSerializer
from .models import User
from .utils import (
    set_user_password, 
    create_user_session, 
    get_current_user, 
    is_user_authenticated, 
    logout_user,
    get_user_sessions,
    clear_user_sessions
)
from .token_auth import TokenAuthService
# Create your views here.

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # 生成认证token
            auth_token = TokenAuthService.generate_token(user)
            
            # 创建响应
            response = Response({
                "message": "登录成功",
                "user_id": str(user.id),
                "userName": user.userName,
                "auth_token": auth_token
            }, status=status.HTTP_200_OK)
            
            return response
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        # 检查用户是否已登录
        if is_user_authenticated(request):
            logout_user(request)
            return Response({"message": "登出成功"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "用户未登录"}, status=status.HTTP_400_BAD_REQUEST)

class CheckLoginStatusView(APIView):
    def get(self, request):
        # 从请求头中获取token
        auth_token = request.headers.get('Authorization')
        if auth_token and auth_token.startswith('Bearer '):
            auth_token = auth_token[7:]  # 移除 'Bearer ' 前缀
        
        # 验证token
        user = TokenAuthService.verify_token(auth_token)
        if user:
            # 刷新token过期时间
            TokenAuthService.refresh_token(auth_token)
            
            return Response({
                "is_authenticated": True,
                "user_id": user.id,
                "user_name": user.userName,
                "auth_token": auth_token
            }, status=status.HTTP_200_OK)
        
        return Response({
            "is_authenticated": False,
            "message": "用户未登录"
        }, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    def post(self, request):
        userName = request.data.get('userName')
        password = request.data.get('password')

        if User.objects.filter(userName=userName).exists():
            return Response({"error": "用户名已存在"}, status=400)

        user = User(userName=userName)
        set_user_password(user, password)
        user.save()
        
        return Response({"message": "注册成功"}, status=201)

# 登录装饰器类，用于需要登录验证的视图
class LoginRequiredMixin:
    """
    需要登录才能访问的视图混入类
    """
    def dispatch(self, request, *args, **kwargs):
        if not is_user_authenticated(request):
            return Response({
                "error": "请先登录",
                "code": "NOT_AUTHENTICATED"
            }, status=status.HTTP_401_UNAUTHORIZED)
        return super().dispatch(request, *args, **kwargs)

# 示例：需要登录才能访问的用户信息视图
class UserProfileView(LoginRequiredMixin, APIView):
    def get(self, request):
        user = get_current_user(request)
        if user:
            return Response({
                "user_id": user.id,
                "user_name": user.userName,
                "login_time": request.session.get('login_time')
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

class UserSessionsView(LoginRequiredMixin, APIView):
    """
    用户session管理视图
    """
    def get(self, request):
        """获取当前用户的所有活跃session"""
        user = get_current_user(request)
        if user:
            sessions = get_user_sessions(user.id)
            return Response({
                "sessions": sessions,
                "current_session": request.session.session_key
            }, status=status.HTTP_200_OK)
        return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request):
        """清除用户的所有session（强制登出所有设备）"""
        user = get_current_user(request)
        if user:
            count = clear_user_sessions(user.id)
            return Response({
                "message": f"已清除 {count} 个活跃会话",
                "cleared_sessions": count
            }, status=status.HTTP_200_OK)
        return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

class DebugSessionView(APIView):
    """
    调试session的视图
    """
    def get(self, request):
        """获取当前请求的session详细信息"""
        session_data = dict(request.session)
        
        # 获取所有cookies
        cookies = dict(request.COOKIES)
        
        # 尝试获取session对象更多信息
        session_exists = False
        if request.session.session_key:
            from django.contrib.sessions.models import Session
            try:
                session_obj = Session.objects.get(session_key=request.session.session_key)
                session_exists = True
            except Session.DoesNotExist:
                session_exists = False
        
        return Response({
            "session_key": request.session.session_key,
            "session_data": session_data,
            "session_exists": session_exists,
            "session_empty": request.session.is_empty(),
            "cookies": cookies,
            "is_authenticated": is_user_authenticated(request),
            "current_user": get_current_user(request).userName if get_current_user(request) else None,
            "request_session_test_key": request.session.get('test_key', 'not_found'),
            "session_modified": request.session.modified,
            "session_accessed": request.session.accessed,
        }, status=status.HTTP_200_OK)

class CSRFTokenView(APIView):
    """
    获取CSRF token的视图
    """
    def get(self, request):
        """返回CSRF token"""
        token = get_token(request)
        return Response({
            "csrftoken": token
        }, status=status.HTTP_200_OK)