from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login
from django.contrib import messages
# Create your views here.

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        print(user)

        if user is not None:
            if hasattr(user, "role") and user.role == "admin":
                print("ADMIN — redirecting now")
                login(request,user)
                return redirect("/core/dashboard/")
            else:
                messages.error(request, "Only admin users can log in here.")
        else:
            messages.error(request, "Invalid username or password.")

        return redirect("/core/login")

    return render(request,'admin/login.html')


def admin_dashboard(request):

    return render(request,'admin/admindashboard.html')