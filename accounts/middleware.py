from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def business_verified_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and user.is_business:
            business_info = getattr(user, 'business_info', None)
            if not (business_info and business_info.is_admin_verified):
                messages.warning(
                    request,
                    'Your business account is under verification.'
                )
                return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def local_verified_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and user.is_local:
            business_info = getattr(user, 'business_info', None)
            if not (business_info and business_info.is_admin_verified):
                messages.warning(
                    request,
                    'Your business account is under verification.'
                )
                return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view