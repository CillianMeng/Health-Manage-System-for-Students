from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import json

class SessionAuthMiddleware(MiddlewareMixin):
    """
    Session认证中间件
    为需要登录验证的API端点提供自动验证
    """
    
    # 需要登录验证的URL路径前缀
    PROTECTED_PATHS = [
        '/api/user/profile/',
        '/api/user/sessions/',
        # 在这里添加其他需要登录验证的路径
        # 例如：'/api/health/', '/api/records/' 等
    ]
    
    # 不需要验证的路径（即使在PROTECTED_PATHS中也豁免）
    EXEMPT_PATHS = [
        '/api/user/login/',
        '/api/user/register/',
        '/api/user/check-login/',
        '/api/user/logout/',
        # 添加其他不需要验证的路径
    ]
    
    def process_request(self, request):
        """
        处理请求前的认证检查
        """
        path = request.path
        
        # 如果路径在豁免列表中，直接放行
        if any(path.startswith(exempt_path) for exempt_path in self.EXEMPT_PATHS):
            return None
            
        # 如果路径需要保护且用户未登录
        if any(path.startswith(protected_path) for protected_path in self.PROTECTED_PATHS):
            if not self._is_authenticated(request):
                return JsonResponse({
                    'error': '请先登录',
                    'code': 'NOT_AUTHENTICATED',
                    'redirect': '/api/user/login/'
                }, status=401)
        
        return None
    
    def _is_authenticated(self, request):
        """
        检查用户是否已认证
        """
        return request.session.get('is_authenticated', False)
    
    def process_response(self, request, response):
        """
        处理响应（可选）
        在这里可以添加一些响应后的处理逻辑
        """
        # 为所有API响应添加一些通用头部
        if request.path.startswith('/api/'):
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            
        return response
