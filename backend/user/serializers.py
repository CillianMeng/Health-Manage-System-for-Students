from .models import User, SleepRecord
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