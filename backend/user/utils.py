from django.contrib.auth.hashers import make_password, check_password
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import User

def set_user_password(user, password):
    """
    Set the user's password after hashing it.
    """
    user.password = make_password(password)
    user.save()

def verify_user_password(user, password):
    """
    Verify the user's password against the stored hashed password.
    """
    return check_password(password, user.password)

def create_user_session(request, user):
    """
    为用户创建session
    """
    # 确保session存在
    if not request.session.session_key:
        request.session.create()
    
    request.session['user_id'] = user.id
    request.session['user_name'] = user.userName
    request.session['is_authenticated'] = True
    request.session['login_time'] = timezone.now().timestamp()
    
    # 强制保存session
    request.session.save()
    
    # 设置session过期时间
    request.session.set_expiry(86400)  # 24小时
    
    return request.session.session_key

def get_current_user(request):
    """
    从session中获取当前用户
    """
    if request.session.get('is_authenticated'):
        user_id = request.session.get('user_id')
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            # 如果用户不存在，清除session
            request.session.flush()
            return None
    return None

def is_user_authenticated(request):
    """
    检查用户是否已认证
    """
    return request.session.get('is_authenticated', False)

def logout_user(request):
    """
    用户登出，清除session
    """
    request.session.flush()

def get_user_sessions(user_id):
    """
    获取用户的所有有效session
    """
    sessions = []
    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        session_data = session.get_decoded()
        if session_data.get('user_id') == user_id:
            sessions.append({
                'session_key': session.session_key,
                'login_time': session_data.get('login_time'),
                'expire_date': session.expire_date
            })
    return sessions

def clear_user_sessions(user_id):
    """
    清除用户的所有session（强制登出所有设备）
    """
    count = 0
    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        session_data = session.get_decoded()
        if session_data.get('user_id') == user_id:
            session.delete()
            count += 1
    return count