"""
基于Token的认证系统 - 替代Session cookie方案
"""
import secrets
import time
from django.core.cache import cache
from django.conf import settings
from .models import User

class TokenAuthService:
    """Token认证服务"""
    
    TOKEN_PREFIX = "auth_token_"
    TOKEN_EXPIRE_TIME = 86400  # 24小时
    
    @classmethod
    def generate_token(cls, user):
        """为用户生成认证token"""
        # 生成随机token
        token = secrets.token_urlsafe(32)
        
        # 在缓存中存储token和用户信息
        cache_key = f"{cls.TOKEN_PREFIX}{token}"
        user_data = {
            'user_id': user.id,
            'user_name': user.userName,
            'login_time': time.time()
        }
        
        # 存储到缓存，过期时间24小时
        cache.set(cache_key, user_data, cls.TOKEN_EXPIRE_TIME)
        
        return token
    
    @classmethod
    def verify_token(cls, token):
        """验证token并返回用户信息"""
        if not token:
            return None
            
        cache_key = f"{cls.TOKEN_PREFIX}{token}"
        user_data = cache.get(cache_key)
        
        if not user_data:
            return None
            
        # 获取用户对象
        try:
            user = User.objects.get(id=user_data['user_id'])
            return user
        except User.DoesNotExist:
            # 如果用户不存在，删除token
            cache.delete(cache_key)
            return None
    
    @classmethod
    def refresh_token(cls, token):
        """刷新token的过期时间"""
        if not token:
            return False
            
        cache_key = f"{cls.TOKEN_PREFIX}{token}"
        user_data = cache.get(cache_key)
        
        if user_data:
            # 重新设置过期时间
            cache.set(cache_key, user_data, cls.TOKEN_EXPIRE_TIME)
            return True
        return False
    
    @classmethod
    def revoke_token(cls, token):
        """撤销token"""
        if not token:
            return False
            
        cache_key = f"{cls.TOKEN_PREFIX}{token}"
        cache.delete(cache_key)
        return True