from django.shortcuts import render
from django.contrib.sessions.models import Session
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from datetime import datetime, date, timedelta
from .serializers import (
    LoginSerializer, SleepRecordSerializer, SleepRecordCreateSerializer,
    ExerciseRecordSerializer, ExerciseRecordCreateSerializer
)
from .models import User, SleepRecord, ExerciseRecord
from .utils import set_user_password
import json
# Create your views here.

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # 创建用户会话
            request.session['user_id'] = user.id
            request.session['user_name'] = user.userName
            request.session['login_time'] = timezone.now().isoformat()
            
            # 设置会话过期时间（可选，这里设置为7天）
            request.session.set_expiry(7 * 24 * 60 * 60)  # 7天
            
            return Response({
                "message": "登录成功",
                "user_id": str(user.id),
                "userName": user.userName,
                "session_key": request.session.session_key
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    def post(self, request):
        userName = request.data.get('userName')
        password = request.data.get('password')

        if User.objects.filter(userName=userName).exists():
            return Response({"error": "用户名已存在"}, status=400)

        user = User(userName=userName)
        set_user_password(user, password)
        user.save()
        
        # 注册成功后自动登录（创建会话）
        request.session['user_id'] = user.id
        request.session['user_name'] = user.userName
        request.session['login_time'] = timezone.now().isoformat()
        request.session.set_expiry(7 * 24 * 60 * 60)  # 7天
        
        return Response({
            "message": "注册成功",
            "user_id": str(user.id),
            "userName": user.userName,
            "session_key": request.session.session_key
        }, status=201)

class LogoutView(APIView):
    def post(self, request):
        """
        用户注销API
        清除服务器端的session数据和前端cookie
        """
        # 清除session数据
        if 'user_id' in request.session:
            del request.session['user_id']
        if 'user_name' in request.session:
            del request.session['user_name']
        if 'login_time' in request.session:
            del request.session['login_time']
        
        # 完全清除session
        request.session.flush()
        
        return Response({
            "message": "注销成功",
            "detail": "会话已清除，用户已注销"
        }, status=status.HTTP_200_OK)

class CheckLoginView(APIView):
    def get(self, request):
        """
        检查用户登录状态API
        用于前端页面检测用户是否已登录
        """
        user_id = request.session.get('user_id')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                return Response({
                    "is_logged_in": True,
                    "user_id": str(user.id),
                    "userName": user.userName,
                    "login_time": request.session.get('login_time'),
                    "session_key": request.session.session_key
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                # 用户不存在，清除session
                request.session.flush()
                return Response({
                    "is_logged_in": False,
                    "message": "用户不存在，会话已清除"
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                "is_logged_in": False,
                "message": "用户未登录"
            }, status=status.HTTP_200_OK)

class SleepRecordListView(APIView):
    def get(self, request):
        """获取当前用户的睡眠记录列表"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取查询参数
        days = request.GET.get('days', 30)  # 默认获取最近30天
        try:
            days = int(days)
        except ValueError:
            days = 30
        
        # 计算日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # 查询睡眠记录
        records = SleepRecord.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')
        
        # 分页
        page_size = request.GET.get('page_size', 10)
        try:
            page_size = int(page_size)
        except ValueError:
            page_size = 10
            
        paginator = Paginator(records, page_size)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        serializer = SleepRecordSerializer(page_obj, many=True)
        
        return Response({
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)

class SleepRecordCreateView(APIView):
    def post(self, request):
        """创建睡眠记录"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SleepRecordCreateSerializer(data=request.data)
        if serializer.is_valid():
            # 检查该日期是否已有记录
            record_date = serializer.validated_data['date']
            existing_record = SleepRecord.objects.filter(user=user, date=record_date).first()
            
            if existing_record:
                return Response({
                    "error": f"日期 {record_date} 的睡眠记录已存在，请使用更新接口"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建记录
            sleep_record = serializer.save(user=user)
            
            # 返回创建的记录
            return_serializer = SleepRecordSerializer(sleep_record)
            return Response({
                "message": "睡眠记录创建成功",
                "data": return_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SleepRecordDetailView(APIView):
    def get(self, request, record_id):
        """获取睡眠记录详情"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
            record = SleepRecord.objects.get(id=record_id, user=user)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        except SleepRecord.DoesNotExist:
            return Response({"error": "睡眠记录不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SleepRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, record_id):
        """更新睡眠记录"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
            record = SleepRecord.objects.get(id=record_id, user=user)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        except SleepRecord.DoesNotExist:
            return Response({"error": "睡眠记录不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SleepRecordCreateSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            sleep_record = serializer.save()
            return_serializer = SleepRecordSerializer(sleep_record)
            return Response({
                "message": "睡眠记录更新成功",
                "data": return_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, record_id):
        """删除睡眠记录"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
            record = SleepRecord.objects.get(id=record_id, user=user)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        except SleepRecord.DoesNotExist:
            return Response({"error": "睡眠记录不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        record.delete()
        return Response({
            "message": "睡眠记录删除成功"
        }, status=status.HTTP_200_OK)

class SleepStatisticsView(APIView):
    def get(self, request):
        """获取睡眠统计数据"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取统计天数参数
        days = request.GET.get('days', 7)  # 默认7天
        try:
            days = int(days)
        except ValueError:
            days = 7
        
        # 计算日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # 查询记录
        records = SleepRecord.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        if not records.exists():
            return Response({
                "message": "暂无睡眠记录",
                "statistics": {
                    "total_records": 0,
                    "average_sleep_hours": 0,
                    "total_sleep_hours": 0,
                    "date_range": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            }, status=status.HTTP_200_OK)
        
        # 计算统计数据
        total_sleep_seconds = sum(
            record.sleep_duration.total_seconds() 
            for record in records 
            if record.sleep_duration
        )
        total_sleep_hours = round(total_sleep_seconds / 3600, 2)
        average_sleep_hours = round(total_sleep_hours / len(records), 2) if records else 0
        
        # 找出最长和最短睡眠
        records_with_duration = [r for r in records if r.sleep_duration]
        longest_sleep = max(records_with_duration, key=lambda x: x.sleep_duration) if records_with_duration else None
        shortest_sleep = min(records_with_duration, key=lambda x: x.sleep_duration) if records_with_duration else None
        
        return Response({
            "statistics": {
                "total_records": len(records),
                "average_sleep_hours": average_sleep_hours,
                "total_sleep_hours": total_sleep_hours,
                "longest_sleep": {
                    "date": longest_sleep.date,
                    "hours": longest_sleep.sleep_duration_hours
                } if longest_sleep else None,
                "shortest_sleep": {
                    "date": shortest_sleep.date, 
                    "hours": shortest_sleep.sleep_duration_hours
                } if shortest_sleep else None,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "days": days
                }
            }
        }, status=status.HTTP_200_OK)


# 运动记录相关视图
class ExerciseRecordListView(APIView):
    def get(self, request):
        """获取当前用户的运动记录列表"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取查询参数
        days = request.GET.get('days', 30)  # 默认获取最近30天
        exercise_type = request.GET.get('exercise_type', '')  # 运动类型筛选
        
        try:
            days = int(days)
        except ValueError:
            days = 30
        
        # 计算日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # 查询运动记录
        records = ExerciseRecord.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # 按运动类型筛选
        if exercise_type:
            records = records.filter(exercise_type=exercise_type)
        
        records = records.order_by('-date', '-created_at')
        
        # 分页
        page_size = request.GET.get('page_size', 10)
        try:
            page_size = int(page_size)
        except ValueError:
            page_size = 10
        
        paginator = Paginator(records, page_size)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        serializer = ExerciseRecordSerializer(page_obj, many=True)
        
        return Response({
            "records": serializer.data,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_records": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            }
        }, status=status.HTTP_200_OK)

class ExerciseRecordCreateView(APIView):
    def post(self, request):
        """创建新的运动记录"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExerciseRecordCreateSerializer(data=request.data)
        if serializer.is_valid():
            # 保存运动记录，自动关联当前用户
            exercise_record = serializer.save(user=user)
            
            # 返回完整的运动记录信息
            response_serializer = ExerciseRecordSerializer(exercise_record)
            return Response({
                "message": "运动记录创建成功",
                "record": response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExerciseRecordDetailView(APIView):
    def get(self, request, record_id):
        """获取单个运动记录详情"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
            record = ExerciseRecord.objects.get(id=record_id, user=user)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        except ExerciseRecord.DoesNotExist:
            return Response({"error": "运动记录不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExerciseRecordSerializer(record)
        return Response({"record": serializer.data}, status=status.HTTP_200_OK)
    
    def put(self, request, record_id):
        """更新运动记录"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
            record = ExerciseRecord.objects.get(id=record_id, user=user)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        except ExerciseRecord.DoesNotExist:
            return Response({"error": "运动记录不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ExerciseRecordCreateSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            updated_record = serializer.save()
            
            response_serializer = ExerciseRecordSerializer(updated_record)
            return Response({
                "message": "运动记录更新成功",
                "record": response_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, record_id):
        """删除运动记录"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
            record = ExerciseRecord.objects.get(id=record_id, user=user)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        except ExerciseRecord.DoesNotExist:
            return Response({"error": "运动记录不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        record.delete()
        return Response({"message": "运动记录删除成功"}, status=status.HTTP_200_OK)

class ExerciseStatisticsView(APIView):
    def get(self, request):
        """获取用户运动统计信息"""
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "用户未登录"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取查询参数
        days = request.GET.get('days', 30)
        try:
            days = int(days)
        except ValueError:
            days = 30
        
        # 计算日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # 查询运动记录
        records = ExerciseRecord.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date')
        
        if not records:
            return Response({
                "statistics": {
                    "total_records": 0,
                    "total_duration_minutes": 0,
                    "total_calories_burned": 0,
                    "average_duration_minutes": 0,
                    "average_calories_per_session": 0,
                    "exercise_type_distribution": {},
                    "most_frequent_exercise": None,
                    "date_range": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "days": days
                    }
                }
            }, status=status.HTTP_200_OK)
        
        # 计算统计信息
        total_duration = sum(record.duration_minutes for record in records)
        total_calories = sum(record.calories_burned for record in records)
        
        # 运动类型分布
        exercise_type_stats = {}
        for record in records:
            exercise_type = record.get_exercise_type_display()
            if exercise_type not in exercise_type_stats:
                exercise_type_stats[exercise_type] = {
                    'count': 0,
                    'total_duration': 0,
                    'total_calories': 0
                }
            exercise_type_stats[exercise_type]['count'] += 1
            exercise_type_stats[exercise_type]['total_duration'] += record.duration_minutes
            exercise_type_stats[exercise_type]['total_calories'] += record.calories_burned
        
        # 最常进行的运动
        most_frequent_exercise = max(exercise_type_stats.items(), key=lambda x: x[1]['count']) if exercise_type_stats else None
        
        return Response({
            "statistics": {
                "total_records": len(records),
                "total_duration_minutes": total_duration,
                "total_calories_burned": total_calories,
                "average_duration_minutes": round(total_duration / len(records), 1) if records else 0,
                "average_calories_per_session": round(total_calories / len(records), 1) if records else 0,
                "exercise_type_distribution": exercise_type_stats,
                "most_frequent_exercise": {
                    "type": most_frequent_exercise[0],
                    "count": most_frequent_exercise[1]['count']
                } if most_frequent_exercise else None,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "days": days
                }
            }
        }, status=status.HTTP_200_OK)