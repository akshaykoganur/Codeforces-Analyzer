from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
import requests

def home(request):
    return render(request, "home.html")

def analysis(request):
    user_name = request.GET.get("user_name")
    url = 'https://codeforces.com/api/user.info?handles=' + user_name
    req = requests.get(url)
    data = req.json()
    u_data = data['result']
    user_data = u_data[0]
    return render(request, 'analysis.html', context={'user_info': user_data})
    #return HttpResponse(req)
