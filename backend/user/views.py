from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import LoginSerializer, SleepRecordSerializer, WeeklySleepStatsSerializer, ExerciseRecordSerializer, WeeklyExerciseStatsSerializer, DietRecordSerializer, WeeklyDietStatsSerializer, FoodCalorieReferenceSerializer
from .models import User, SleepRecord, ExerciseRecord, DietRecord, FoodCalorieReference
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
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.authentication import BaseAuthentication
from django.contrib.auth.models import AnonymousUser


class TokenAuthentication(BaseAuthentication):
    """
    自定义Token认证类，用于API认证
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        user = TokenAuthService.verify_token(token)
        
        if user:
            return (user, token)
        
        return None


class IsTokenAuthenticated(BasePermission):
    """
    自定义权限类，确保用户通过Token认证
    """
    def has_permission(self, request, view):
        return bool(request.user and not isinstance(request.user, AnonymousUser))


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


class SleepRecordView(APIView):
    """
    睡眠记录管理视图
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsTokenAuthenticated]
    
    def get(self, request):
        """获取用户的睡眠记录"""
        user = request.user
        
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
        user = request.user
        
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
    permission_classes = [IsTokenAuthenticated]
    
    def get_object(self, pk, user):
        """获取睡眠记录对象"""
        try:
            return SleepRecord.objects.get(pk=pk, user=user)
        except SleepRecord.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """获取单个睡眠记录"""
        user = request.user
        
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
        user = request.user
        
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
        user = request.user
        
        record = self.get_object(pk, user)
        if not record:
            return Response(
                {"error": "睡眠记录不存在"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        record.delete()
        # HTTP 204 不应该有响应体
        return Response(status=status.HTTP_204_NO_CONTENT)


class WeeklySleepStatsView(APIView):
    """
    一周睡眠统计视图
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsTokenAuthenticated]
    
    def get(self, request):
        """获取最近一周的睡眠统计"""
        user = request.user
        
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


class ExerciseRecordView(APIView):
    """
    运动记录视图
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsTokenAuthenticated]
    
    def get(self, request):
        """获取用户的运动记录"""
        user = request.user
        
        # 获取查询参数
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        exercise_type = request.GET.get('exercise_type')
        
        # 构建查询条件
        queryset = ExerciseRecord.objects.filter(user=user)
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(exercise_date__gte=start_date)
            except ValueError:
                return Response(
                    {'error': '开始日期格式错误，请使用YYYY-MM-DD格式'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(exercise_date__lte=end_date)
            except ValueError:
                return Response(
                    {'error': '结束日期格式错误，请使用YYYY-MM-DD格式'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if exercise_type:
            queryset = queryset.filter(exercise_type=exercise_type)
        
        # 按日期倒序排列
        records = queryset.order_by('-exercise_date', '-created_at')
        
        # 序列化数据
        serializer = ExerciseRecordSerializer(records, many=True)
        
        return Response({
            'records': serializer.data,
            'total_count': records.count()
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """创建运动记录"""
        user = request.user
        
        # 准备数据，添加用户信息
        data = request.data.copy()
        
        # 创建序列化器实例
        serializer = ExerciseRecordSerializer(data=data)
        
        if serializer.is_valid():
            # 保存记录，关联到当前用户
            exercise_record = serializer.save(user=user)
            
            # 返回创建的记录
            response_serializer = ExerciseRecordSerializer(exercise_record)
            return Response({
                'message': '运动记录创建成功',
                'record': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': '数据验证失败',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ExerciseRecordDetailView(APIView):
    """
    运动记录详情视图（更新和删除）
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsTokenAuthenticated]
    
    def get_object(self, user, record_id):
        """获取指定的运动记录"""
        try:
            return ExerciseRecord.objects.get(id=record_id, user=user)
        except ExerciseRecord.DoesNotExist:
            return None
    
    def put(self, request, record_id):
        """更新运动记录"""
        user = request.user
        exercise_record = self.get_object(user, record_id)
        
        if not exercise_record:
            return Response({
                'error': '运动记录不存在或无权访问'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 更新记录
        serializer = ExerciseRecordSerializer(exercise_record, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_record = serializer.save()
            
            # 返回更新后的记录
            response_serializer = ExerciseRecordSerializer(updated_record)
            return Response({
                'message': '运动记录更新成功',
                'record': response_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': '数据验证失败',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, record_id):
        """删除运动记录"""
        user = request.user
        exercise_record = self.get_object(user, record_id)
        
        if not exercise_record:
            return Response({
                'error': '运动记录不存在或无权访问'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 删除记录
        exercise_record.delete()
        
        return Response({
            'message': '运动记录删除成功'
        }, status=status.HTTP_200_OK)


class WeeklyExerciseStatsView(APIView):
    """
    一周运动统计视图
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsTokenAuthenticated]
    
    def get(self, request):
        """获取最近一周的运动统计"""
        user = request.user
        
        # 计算一周前的日期
        end_date = date.today()
        start_date = end_date - timedelta(days=6)  # 包含今天共7天
        
        # 获取一周内的运动记录
        records = ExerciseRecord.objects.filter(
            user=user,
            exercise_date__gte=start_date,
            exercise_date__lte=end_date
        ).order_by('exercise_date')
        
        # 计算统计数据
        if records.exists():
            total_duration = sum(record.duration_minutes for record in records)
            total_calories = sum(record.calories_burned or 0 for record in records)
            
            # 计算平均值
            avg_daily_duration = total_duration / 7  # 按7天计算平均值
            avg_daily_calories = total_calories / 7
            
            # 统计最常做的运动
            exercise_counts = {}
            for record in records:
                exercise_type = record.get_exercise_type_display()
                exercise_counts[exercise_type] = exercise_counts.get(exercise_type, 0) + 1
            
            most_frequent = max(exercise_counts.items(), key=lambda x: x[1])[0] if exercise_counts else "无"
            
            # 计算健身评分
            fitness_score = self._calculate_fitness_score(total_duration, total_calories, len(records))
            
            # 生成建议
            recommendations = self._generate_exercise_recommendations(
                total_duration, total_calories, len(records), fitness_score
            )
        else:
            total_duration = 0
            total_calories = 0
            avg_daily_duration = 0
            avg_daily_calories = 0
            most_frequent = "无"
            fitness_score = 0
            recommendations = ["开始记录您的运动数据，保持健康的生活方式"]
        
        # 构建响应数据
        stats_data = {
            'records': ExerciseRecordSerializer(records, many=True).data,
            'total_duration_minutes': total_duration,
            'total_duration_hours': round(total_duration / 60, 1),
            'total_calories_burned': total_calories,
            'average_daily_duration': round(avg_daily_duration, 1),
            'average_daily_calories': round(avg_daily_calories, 1),
            'most_frequent_exercise': most_frequent,
            'exercise_frequency': records.count(),
            'fitness_score': fitness_score,
            'recommendations': recommendations
        }
        
        return Response(stats_data, status=status.HTTP_200_OK)
    
    def _calculate_fitness_score(self, total_duration, total_calories, frequency):
        """计算健身评分（0-100分）"""
        score = 0
        
        # 基于总运动时长评分（最多40分）
        if total_duration >= 150:  # WHO推荐每周150分钟
            score += 40
        else:
            score += (total_duration / 150) * 40
        
        # 基于运动频率评分（最多30分）
        if frequency >= 3:  # 建议每周至少3次
            score += 30
        else:
            score += (frequency / 3) * 30
        
        # 基于卡路里消耗评分（最多30分）
        target_calories = 500  # 每周目标消耗500卡路里
        if total_calories >= target_calories:
            score += 30
        else:
            score += (total_calories / target_calories) * 30
        
        return min(int(score), 100)
    
    def _generate_exercise_recommendations(self, total_duration, total_calories, frequency, score):
        """生成运动建议"""
        recommendations = []
        
        # 基于运动时长的建议
        if total_duration < 75:
            recommendations.append("建议增加运动时间，每周至少150分钟的中等强度运动")
        elif total_duration >= 300:
            recommendations.append("您的运动量很充足，注意适当休息和恢复")
        elif 150 <= total_duration < 300:
            recommendations.append("运动量达标，继续保持这个良好的习惯")
        
        # 基于运动频率的建议
        if frequency < 3:
            recommendations.append("建议增加运动频率，每周至少运动3次")
        elif frequency >= 5:
            recommendations.append("运动频率很好，记得安排充分的休息时间")
        
        # 基于健身评分的建议
        if score < 50:
            recommendations.append("您的整体运动水平有待提升，建议制定合理的运动计划")
        elif score >= 80:
            recommendations.append("您的运动表现很出色，继续保持健康的生活方式")
        
        return recommendations if recommendations else ["您的运动状况良好，继续保持"]


class FoodCalorieReferenceView(APIView):
    """食物卡路里参考API"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsTokenAuthenticated]
    
    def get(self, request):
        """获取食物卡路里参考列表"""
        try:
            # 获取查询参数
            search_query = request.GET.get('q', '').strip()  # 搜索关键词
            category = request.GET.get('category', '').strip()  # 食物分类
            
            # 构建查询条件
            queryset = FoodCalorieReference.objects.all()
            
            # 按分类筛选
            if category:
                queryset = queryset.filter(food_category=category)
            
            # 按关键词搜索
            if search_query:
                queryset = queryset.filter(food_name__icontains=search_query)
            
            # 限制返回数量（避免数据过多）
            queryset = queryset[:100]
            
            serializer = FoodCalorieReferenceSerializer(queryset, many=True)
            
            return Response({
                "foods": serializer.data,
                "total_count": queryset.count(),
                "search_query": search_query,
                "category": category
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"获取食物参考数据失败: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DietRecordView(APIView):
    """饮食记录API"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsTokenAuthenticated]
    
    def get(self, request):
        """获取用户饮食记录列表"""
        try:
            user = request.user
            
            # 获取查询参数
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            meal_type = request.GET.get('meal_type')
            
            # 构建查询条件
            queryset = DietRecord.objects.filter(user=user)
            
            # 日期范围筛选
            if start_date:
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    queryset = queryset.filter(diet_date__gte=start_date)
                except ValueError:
                    return Response(
                        {"error": "开始日期格式错误，请使用 YYYY-MM-DD 格式"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if end_date:
                try:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                    queryset = queryset.filter(diet_date__lte=end_date)
                except ValueError:
                    return Response(
                        {"error": "结束日期格式错误，请使用 YYYY-MM-DD 格式"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # 餐次筛选
            if meal_type:
                queryset = queryset.filter(meal_type=meal_type)
            
            # 按日期和餐次排序
            queryset = queryset.order_by('-diet_date', 'meal_type', '-created_at')
            
            # 限制返回数量（分页可以后续添加）
            queryset = queryset[:100]
            
            serializer = DietRecordSerializer(queryset, many=True)
            
            return Response({
                "records": serializer.data,
                "total_count": queryset.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"获取饮食记录失败: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """创建新的饮食记录"""
        try:
            user = request.user
            
            # 添加用户信息到数据中
            data = request.data.copy()
            
            serializer = DietRecordSerializer(data=data)
            if serializer.is_valid():
                # 保存记录，关联当前用户
                diet_record = serializer.save(user=user)
                
                # 返回创建的记录
                response_serializer = DietRecordSerializer(diet_record)
                return Response({
                    "message": "饮食记录创建成功",
                    "record": response_serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {"error": f"创建饮食记录失败: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DietRecordDetailView(APIView):
    """饮食记录详情API"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsTokenAuthenticated]
    
    def get_object(self, user, record_id):
        """获取指定用户的饮食记录"""
        try:
            return DietRecord.objects.get(id=record_id, user=user)
        except DietRecord.DoesNotExist:
            return None
    
    def get(self, request, record_id):
        """获取特定饮食记录详情"""
        try:
            user = request.user
            record = self.get_object(user, record_id)
            
            if not record:
                return Response(
                    {"error": "饮食记录不存在"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = DietRecordSerializer(record)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"获取饮食记录失败: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, record_id):
        """更新饮食记录"""
        try:
            user = request.user
            record = self.get_object(user, record_id)
            
            if not record:
                return Response(
                    {"error": "饮食记录不存在"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = DietRecordSerializer(record, data=request.data, partial=True)
            if serializer.is_valid():
                updated_record = serializer.save()
                
                response_serializer = DietRecordSerializer(updated_record)
                return Response({
                    "message": "饮食记录更新成功",
                    "record": response_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {"error": f"更新饮食记录失败: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, record_id):
        """删除饮食记录"""
        try:
            user = request.user
            record = self.get_object(user, record_id)
            
            if not record:
                return Response(
                    {"error": "饮食记录不存在"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            record.delete()
            return Response(
                {"message": "饮食记录删除成功"}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"error": f"删除饮食记录失败: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WeeklyDietStatsView(APIView):
    """一周饮食统计API"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsTokenAuthenticated]
    
    def get(self, request):
        """获取用户最近一周的饮食统计数据"""
        try:
            user = request.user
            
            # 计算最近一周的日期范围
            end_date = date.today()
            start_date = end_date - timedelta(days=6)  # 包括今天在内的7天
            
            # 获取一周内的饮食记录
            records = DietRecord.objects.filter(
                user=user,
                diet_date__range=[start_date, end_date]
            ).order_by('diet_date', 'meal_type', 'created_at')
            
            # 计算统计数据
            stats_data = self._calculate_diet_stats(records, start_date, end_date)
            
            # 序列化记录数据
            records_serializer = DietRecordSerializer(records, many=True)
            stats_data['records'] = records_serializer.data
            
            # 直接返回统计数据，不使用序列化器验证
            return Response(stats_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {"error": f"获取一周饮食统计失败: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _calculate_diet_stats(self, records, start_date, end_date):
        """计算饮食统计数据"""
        # 基础统计
        total_calories = sum(record.total_calories or 0 for record in records)
        total_days = (end_date - start_date).days + 1
        average_daily_calories = total_calories / total_days if total_days > 0 else 0
        
        # 餐次分布统计
        meal_distribution = {
            'breakfast': 0,
            'lunch': 0,
            'dinner': 0,
            'snack': 0
        }
        
        for record in records:
            if record.total_calories:
                meal_distribution[record.meal_type] += record.total_calories
        
        # 食物多样性评分（基于不同食物种类数量）
        unique_foods = set(record.food_name for record in records)
        food_variety_score = min(len(unique_foods) * 5, 100)  # 每种食物5分，最高100分
        
        # 营养均衡评分（基于餐次分布）
        nutrition_balance_score = self._calculate_nutrition_balance_score(meal_distribution, total_calories)
        
        # 每日推荐摄入量和达成率
        daily_calories_target = 2000  # 成年人建议每日摄入2000kcal
        target_achievement_rate = (average_daily_calories / daily_calories_target * 100) if daily_calories_target > 0 else 0
        
        # 生成建议
        recommendations = self._generate_diet_recommendations(
            average_daily_calories, meal_distribution, food_variety_score, 
            nutrition_balance_score, target_achievement_rate
        )
        
        return {
            'total_calories': total_calories,
            'average_daily_calories': round(average_daily_calories, 1),
            'meal_distribution': meal_distribution,
            'food_variety_score': food_variety_score,
            'nutrition_balance_score': nutrition_balance_score,
            'daily_calories_target': daily_calories_target,
            'target_achievement_rate': round(target_achievement_rate, 1),
            'recommendations': recommendations
        }
    
    def _calculate_nutrition_balance_score(self, meal_distribution, total_calories):
        """计算营养均衡评分"""
        if total_calories == 0:
            return 0
        
        # 理想餐次分配比例：早餐25%，午餐35%，晚餐30%，加餐10%
        ideal_ratios = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'dinner': 0.30,
            'snack': 0.10
        }
        
        score = 100
        for meal_type, ideal_ratio in ideal_ratios.items():
            actual_ratio = meal_distribution[meal_type] / total_calories if total_calories > 0 else 0
            # 计算与理想比例的偏差，偏差越大扣分越多
            deviation = abs(actual_ratio - ideal_ratio)
            score -= deviation * 200  # 每1%偏差扣2分
        
        return max(int(score), 0)
    
    def _generate_diet_recommendations(self, avg_calories, meal_dist, variety_score, balance_score, achievement_rate):
        """生成饮食建议"""
        recommendations = []
        
        # 基于卡路里摄入的建议
        if avg_calories < 1200:
            recommendations.append("您的每日卡路里摄入偏低，建议增加营养丰富的食物")
        elif avg_calories > 2500:
            recommendations.append("您的每日卡路里摄入偏高，建议适当控制饮食量")
        elif 1800 <= avg_calories <= 2200:
            recommendations.append("您的卡路里摄入量适中，继续保持均衡饮食")
        
        # 基于食物多样性的建议
        if variety_score < 30:
            recommendations.append("建议增加食物种类，丰富营养来源")
        elif variety_score >= 70:
            recommendations.append("您的饮食种类很丰富，营养均衡")
        
        # 基于营养均衡的建议
        if balance_score < 50:
            recommendations.append("建议调整三餐比例，早中晚餐合理分配")
        elif balance_score >= 80:
            recommendations.append("您的餐次分配很合理，营养摄入均衡")
        
        # 基于目标达成率的建议
        if achievement_rate < 80:
            recommendations.append("建议适当增加营养密度高的食物摄入")
        elif achievement_rate > 120:
            recommendations.append("注意控制食物分量，避免过量摄入")
        
        return recommendations if recommendations else ["您的饮食状况良好，继续保持健康的饮食习惯"]