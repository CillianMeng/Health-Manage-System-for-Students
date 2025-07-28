from .models import User, SleepRecord, ExerciseRecord
from rest_framework import serializers
from .utils import verify_user_password

class LoginSerializer(serializers.Serializer):
    userName = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, data):
        username = data.get('userName')
        password = data.get('password')
        
        try:
            user = User.objects.get(userName=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("用户名或密码错误")
            
        if not verify_user_password(user, password):
            raise serializers.ValidationError("用户名或密码错误")
            
        # 返回用户对象
        data['user'] = user
        return data

class SleepRecordSerializer(serializers.ModelSerializer):
    sleep_duration_hours = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.userName', read_only=True)
    
    class Meta:
        model = SleepRecord
        fields = ['id', 'user', 'user_name', 'date', 'sleep_time', 'wake_time', 
                 'sleep_duration', 'sleep_duration_hours', 'created_at', 'updated_at']
        read_only_fields = ['sleep_duration', 'created_at', 'updated_at']

    def validate(self, data):
        # 检查日期不能是未来
        from datetime import date
        if data.get('date') and data['date'] > date.today():
            raise serializers.ValidationError("不能记录未来的睡眠数据")
        
        return data

class SleepRecordCreateSerializer(serializers.ModelSerializer):
    """创建睡眠记录的序列化器（不需要传user_id，从session获取）"""
    
    class Meta:
        model = SleepRecord
        fields = ['date', 'sleep_time', 'wake_time']

    def validate(self, data):
        from datetime import date
        if data.get('date') and data['date'] > date.today():
            raise serializers.ValidationError("不能记录未来的睡眠数据")
        
        return data

class ExerciseRecordSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.userName', read_only=True)
    exercise_type_display = serializers.CharField(source='get_exercise_type_display', read_only=True)
    duration_hours = serializers.ReadOnlyField()
    intensity_level = serializers.CharField(source='get_intensity_level', read_only=True)
    
    class Meta:
        model = ExerciseRecord
        fields = ['id', 'user', 'user_name', 'date', 'exercise_type', 'exercise_type_display',
                 'duration_minutes', 'duration_hours', 'calories_burned', 'intensity_level',
                 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        # 检查日期不能是未来
        from datetime import date
        if data.get('date') and data['date'] > date.today():
            raise serializers.ValidationError("不能记录未来的运动数据")
        
        # 检查运动时长合理性
        if data.get('duration_minutes') and data['duration_minutes'] > 600:  # 10小时
            raise serializers.ValidationError("单次运动时长不能超过10小时")
        
        # 检查卡路里消耗合理性
        if data.get('calories_burned') and data['calories_burned'] > 3000:
            raise serializers.ValidationError("单次运动消耗卡路里不能超过3000")
        
        return data

class ExerciseRecordCreateSerializer(serializers.ModelSerializer):
    """创建运动记录的序列化器（不需要传user_id，从session获取）"""
    
    class Meta:
        model = ExerciseRecord
        fields = ['date', 'exercise_type', 'duration_minutes', 'calories_burned', 'notes']

    def validate(self, data):
        from datetime import date
        if data.get('date') and data['date'] > date.today():
            raise serializers.ValidationError("不能记录未来的运动数据")
        
        if data.get('duration_minutes') and data['duration_minutes'] > 600:
            raise serializers.ValidationError("单次运动时长不能超过10小时")
        
        if data.get('calories_burned') and data['calories_burned'] > 3000:
            raise serializers.ValidationError("单次运动消耗卡路里不能超过3000")
        
        return data