from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer
from .models import User
from .utils import set_user_password
# Create your views here.

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({
                "message": "登录成功",
                "user_id": str(user.id),
                "userName": user.username
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
        
        return Response({"message": "注册成功"}, status=201)