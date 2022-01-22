from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import requests

def signin(request):
    userName = request.POST.get('username')
    passWord = request.POST.get('password')

    user = authenticate(username=userName, password=passWord)

    if user is not None:
        if user.is_active:
            if user.is_superuser:
                login(request, user)

                request.session['usertype'] = 'admin'
                
                return JsonResponse({'ret' : 0})
            else:
                return JsonResponse({'ret' : 1, 'msg': 'Use the admin account to login'})
        else:
            return JsonResponse({'ret' : 0, 'msg': 'User has benn banned/deleted'})
    else:
        return JsonResponse({'ret' : 1, 'msg': 'Wrong user name or password'})
