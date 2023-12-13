from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

def home(request):
    return render(request, "home.html")

def analysis(request):
    #Fetch basic user info
    user_name = request.GET.get("user_name")
    user_info_url = 'https://codeforces.com/api/user.info?handles=' + user_name
    req = requests.get(user_info_url)
    time.sleep(2)
    data = req.json()
    u_data = data['result']
    user_data = u_data[0]

    #Fetch last 10 contests user has participated
    user_past_contests_url = 'https://codeforces.com/api/user.rating?handle=' + user_name
    req1 = requests.get(user_past_contests_url)
    time.sleep(2)
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
        time.sleep(2)
        data2 = req2.json()
        contest_status_data = data2['result']
        total_problem_rating = 0
        total_problems_solved = 0
        flag = 0
        if "rating" in contest_status_data[0]["problem"]:
            fla = 0
        else:
           flag+=1
        for j in range(len(contest_status_data)):
            if(contest_status_data[j]['verdict']=="OK" and past_contest_performance[i][ord(contest_status_data[j]['problem']['index']) - 65]==0):
                past_contest_performance[i][ord(contest_status_data[j]['problem']['index']) - 65] = 1
                if(flag==0 and contest_status_data[j]["problem"]["rating"]):
                    total_problem_rating+=contest_status_data[j]["problem"]["rating"]
                total_problems_solved+=1
        past_arr[i] = total_problem_rating/total_problems_solved
        past_contest_problems_solved[i] = total_problems_solved
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(y=past_arr, name='Average Rating of Problems Solved'), secondary_y=False,)
    fig.add_trace(go.Scatter(y=past_contest_problems_solved, name='Total Problem Solved'), secondary_y=True,)
    chart = fig.to_html


    #Past Contests Submission
    past_contests = []
    for i in range(len(c_data)):
        cur_data = c_data[i]
        past_contests.append(cur_data['contestId'])
    past_contests_problems_attempted_by_rating = [0]*27
    past_contests_problems_accepted_by_rating = [0]*27
    ma = 0
    for i in range(len(past_contests)):
        contest_status_url = 'https://codeforces.com/api/contest.status?contestId='+ str(past_contests[i]) + '&from=1&count=100&handle=' + user_name
        req2 = requests.get(contest_status_url)
        time.sleep(2)
        data2 = req2.json()
        contest_status_data = data2['result']
        flag = 0
        if "rating" in contest_status_data[0]["problem"]:
            fla = 0
        else:
           flag+=1
        for j in range(len(contest_status_data)):
            if(contest_status_data[j]['verdict']=="OK"):
                if(flag==0 and contest_status_data[j]["problem"]["rating"]):
                    past_contests_problems_accepted_by_rating[(contest_status_data[j]["problem"]["rating"]-800)//100]+=1
            if(flag==0):
                ma = max(ma, (contest_status_data[j]["problem"]["rating"]-800)//100)
                past_contests_problems_attempted_by_rating[(contest_status_data[j]["problem"]["rating"]-800)//100]+=1
    ma+=1
    ratings = ['800','900','1000','1100','1200','1300','1400','1500','1600','1700','1800','1900','2000','2100','2200','2300','2400','2500','2600','2700','2800','2900','3000','3100','3200','3300','3400','3500']
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=ratings[:ma],y=past_contests_problems_accepted_by_rating[:ma], name='Accepted Submissions in Contest'))
    fig1.add_trace(go.Bar(x=ratings[:ma],y=past_contests_problems_attempted_by_rating[:ma], name='Total Submissions in Contest'))
    chart1 = fig1.to_html

    return render(request, 'analysis.html', context={'user_info': user_data, 'past_c': chart1, 'past': chart})
    #return HttpResponse(req)