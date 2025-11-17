from django.shortcuts import redirect
from django.contrib import messages

def customer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login first")
            return redirect('login')

        if request.user.role != 'customer':
            messages.error(request, "You are not authorized to access this page")
            return redirect('login')

        return view_func(request, *args, **kwargs)
    return wrapper
