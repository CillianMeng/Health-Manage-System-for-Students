from django.contrib.auth.hashers import make_password, check_password

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