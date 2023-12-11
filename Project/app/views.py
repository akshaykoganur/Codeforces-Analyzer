from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def home(request):
    return render(request, "home.html")

def analysis(request):
    #Fetch basic user info
    user_name = request.GET.get("user_name")
    user_info_url = 'https://codeforces.com/api/user.info?handles=' + user_name
    req = requests.get(user_info_url)
    data = req.json()
    u_data = data['result']
    user_data = u_data[0]

    #Fetch last 10 contests user has participated
    user_past_contests_url = 'https://codeforces.com/api/user.rating?handle=' + user_name
    req1 = requests.get(user_past_contests_url)
    data1 = req1.json()
    c_data = data1['result']
    c_data.reverse()
    past_10_contests = []
    for i in range(min(len(c_data),10)):
        cur_data = c_data[i]
        past_10_contests.append(cur_data['contestId'])

    #Check performance of past 10 contests
    past_contest_performance = [[0]*10]*len(past_10_contests)
    past_arr = [0]*len(past_10_contests)
    past_contest_problems_solved = [0]*len(past_10_contests)
    for i in range(len(past_10_contests)):
        for j in range(10):
            past_contest_performance[i][j] = 0
        contest_status_url = 'https://codeforces.com/api/contest.status?contestId='+ str(past_10_contests[i]) + '&from=1&count=100&handle=' + user_name
        req2 = requests.get(contest_status_url)
        data2 = req2.json()
        contest_status_data = data2['result']
        total_problem_rating = 0
        total_problems_solved = 0
        flag = 0
        if "rating" in contest_status_data[0]["problem"]:
            flag = 0
        else:
            continue
        for j in range(len(contest_status_data)):
            if(contest_status_data[j]['verdict']=="OK" and past_contest_performance[i][ord(contest_status_data[j]['problem']['index']) - 65]==0):
                past_contest_performance[i][ord(contest_status_data[j]['problem']['index']) - 65] = 1
                if(contest_status_data[j]["problem"]["rating"]):
                    total_problem_rating+=contest_status_data[j]["problem"]["rating"]
                total_problems_solved+=1
        past_arr[i] = total_problem_rating/total_problems_solved
        past_contest_problems_solved[i] = total_problems_solved
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(y=past_arr, name='Average Rating of Problems Solved'), secondary_y=False,)
    fig.add_trace(go.Scatter(y=past_contest_problems_solved, name='Total Problem Solved'), secondary_y=True,)
    chart = fig.to_html

    return render(request, 'analysis.html', context={'user_info': user_data, 'past_contests': past_10_contests, 'past': chart})
    #return HttpResponse(req)
