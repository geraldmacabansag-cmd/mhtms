from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.role not in roles and not request.user.is_staff:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

def doctor_required(view_func):
    return role_required('doctor', 'admin')(view_func)

def nurse_required(view_func):
    return role_required('nurse', 'doctor', 'admin')(view_func)

def admin_required(view_func):
    return role_required('admin')(view_func)
