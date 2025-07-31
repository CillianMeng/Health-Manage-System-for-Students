from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import LoginSerializer, SleepRecordSerializer, WeeklySleepStatsSerializer
from .models import User, SleepRecord
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
from datetime import datetime, date, timedelta
from django.db.models import Avg, Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication
from django.contrib.auth.models import AnonymousUser
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


class TokenAuthentication(BaseAuthentication):
    """
    自定义Token认证类，用于睡眠记录API
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        user_info = TokenAuthService.verify_token(token)
        
        if user_info:
            try:
                user = User.objects.get(id=user_info['user_id'])
                return (user, token)
            except User.DoesNotExist:
                return None
        
        return None


class SleepRecordView(APIView):
    """
    睡眠记录管理视图
    """
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        """获取用户的睡眠记录"""
        # 手动检查认证
        auth_result = self.authentication_classes[0]().authenticate(request)
        if not auth_result:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user, token = auth_result
        
        # 获取查询参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # 构建查询集
        queryset = SleepRecord.objects.filter(user=user)
        
        # 应用日期过滤
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(sleep_date__gte=start_date)
            except ValueError:
                return Response(
                    {"error": "start_date格式错误，应为YYYY-MM-DD"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(sleep_date__lte=end_date)
            except ValueError:
                return Response(
                    {"error": "end_date格式错误，应为YYYY-MM-DD"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 序列化并返回
        serializer = SleepRecordSerializer(queryset, many=True)
        return Response({
            "records": serializer.data,
            "total": queryset.count()
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """创建或更新睡眠记录"""
        # 手动检查认证  
        auth_result = self.authentication_classes[0]().authenticate(request)
        if not auth_result:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user, token = auth_result
        
        data = request.data.copy()
        
        # 如果没有提供睡眠日期，使用今天
        if 'sleep_date' not in data:
            data['sleep_date'] = date.today().strftime('%Y-%m-%d')
        
        # 检查是否已存在该日期的记录
        sleep_date = datetime.strptime(data['sleep_date'], '%Y-%m-%d').date()
        existing_record = SleepRecord.objects.filter(
            user=user, 
            sleep_date=sleep_date
        ).first()
        
        if existing_record:
            # 更新现有记录
            serializer = SleepRecordSerializer(existing_record, data=data, partial=True)
        else:
            # 创建新记录
            serializer = SleepRecordSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({
                "message": "睡眠记录保存成功",
                "record": serializer.data
            }, status=status.HTTP_201_CREATED if not existing_record else status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SleepRecordDetailView(APIView):
    """
    单个睡眠记录的详情、更新、删除视图
    """
    authentication_classes = [TokenAuthentication]
    
    def get_object(self, pk, user):
        """获取睡眠记录对象"""
        try:
            return SleepRecord.objects.get(pk=pk, user=user)
        except SleepRecord.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """获取单个睡眠记录"""
        # 手动检查认证
        auth_result = self.authentication_classes[0]().authenticate(request)
        if not auth_result:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user, token = auth_result
        
        record = self.get_object(pk, user)
        if not record:
            return Response(
                {"error": "睡眠记录不存在"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SleepRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        """更新睡眠记录"""
        # 手动检查认证
        auth_result = self.authentication_classes[0]().authenticate(request)
        if not auth_result:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user, token = auth_result
        
        record = self.get_object(pk, user)
        if not record:
            return Response(
                {"error": "睡眠记录不存在"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SleepRecordSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "睡眠记录更新成功",
                "record": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """删除睡眠记录"""
        # 手动检查认证
        auth_result = self.authentication_classes[0]().authenticate(request)
        if not auth_result:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user, token = auth_result
        
        record = self.get_object(pk, user)
        if not record:
            return Response(
                {"error": "睡眠记录不存在"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        record.delete()
        return Response({
            "message": "睡眠记录删除成功"
        }, status=status.HTTP_204_NO_CONTENT)


class WeeklySleepStatsView(APIView):
    """
    一周睡眠统计视图
    """
    authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        """获取最近一周的睡眠统计"""
        # 手动检查认证
        auth_result = self.authentication_classes[0]().authenticate(request)
        if not auth_result:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user, token = auth_result
        
        # 计算一周前的日期
        end_date = date.today()
        start_date = end_date - timedelta(days=6)  # 包含今天共7天
        
        # 获取一周内的睡眠记录
        records = SleepRecord.objects.filter(
            user=user,
            sleep_date__gte=start_date,
            sleep_date__lte=end_date
        ).order_by('sleep_date')
        
        # 计算统计数据
        if records.exists():
            avg_duration = records.aggregate(avg=Avg('sleep_duration'))['avg'] or 0
            avg_hours = avg_duration / 60 if avg_duration else 0
            
            # 计算平均睡眠质量评分
            quality_scores = [record.get_sleep_quality_score() for record in records]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # 睡眠规律性分析
            regularity = self._analyze_sleep_regularity(records)
            
            # 生成建议
            recommendations = self._generate_recommendations(avg_hours, avg_quality, len(records))
        else:
            avg_duration = 0
            avg_hours = 0
            avg_quality = 0
            regularity = "无数据"
            recommendations = ["开始记录您的睡眠数据以获得个性化建议"]
        
        # 构建响应数据
        stats_data = {
            'records': SleepRecordSerializer(records, many=True).data,
            'average_sleep_duration': round(avg_duration, 1),
            'average_sleep_hours': round(avg_hours, 1),
            'average_quality_score': round(avg_quality, 1),
            'total_records': records.count(),
            'sleep_regularity': regularity,
            'recommendations': recommendations
        }
        
        # 直接返回构建的数据，不使用序列化器
        return Response(stats_data, status=status.HTTP_200_OK)
    
    def _analyze_sleep_regularity(self, records):
        """分析睡眠规律性"""
        if len(records) < 3:
            return "数据不足"
        
        # 计算入睡时间的标准差
        bedtimes = []
        for record in records:
            # 将时间转换为分钟数便于计算
            bedtime_minutes = record.bedtime.hour * 60 + record.bedtime.minute
            bedtimes.append(bedtime_minutes)
        
        # 简单的标准差计算
        avg_bedtime = sum(bedtimes) / len(bedtimes)
        variance = sum((x - avg_bedtime) ** 2 for x in bedtimes) / len(bedtimes)
        std_dev = variance ** 0.5
        
        # 根据标准差判断规律性
        if std_dev < 30:  # 30分钟内
            return "非常规律"
        elif std_dev < 60:  # 1小时内
            return "比较规律"
        elif std_dev < 120:  # 2小时内
            return "一般规律"
        else:
            return "不规律"
    
    def _generate_recommendations(self, avg_hours, avg_quality, record_count):
        """生成睡眠建议"""
        recommendations = []
        
        # 基于睡眠时长的建议
        if avg_hours < 6:
            recommendations.append("您的平均睡眠时间不足6小时，建议增加睡眠时间")
        elif avg_hours > 10:
            recommendations.append("您的平均睡眠时间超过10小时，可能需要调整作息")
        elif 7 <= avg_hours <= 9:
            recommendations.append("您的睡眠时长很理想，继续保持")
        
        # 基于睡眠质量的建议
        if avg_quality < 60:
            recommendations.append("您的睡眠质量有待改善，建议保持规律作息")
        elif avg_quality >= 80:
            recommendations.append("您的睡眠质量很好，继续保持健康的睡眠习惯")
        
        # 基于记录频率的建议
        if record_count < 5:
            recommendations.append("建议坚持记录睡眠数据，以便更好地分析睡眠模式")
        
        return recommendations if recommendations else ["您的睡眠状况良好，继续保持"]