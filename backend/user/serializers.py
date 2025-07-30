from .models import User
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