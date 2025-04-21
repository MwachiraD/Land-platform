from functools import wraps
from django.shortcuts import redirect

def seller_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if hasattr(user, 'email') and user.is_authenticated and user.__class__.__name__ == 'Seller':
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/login/seller/?next=' + request.path)
    return wrapper