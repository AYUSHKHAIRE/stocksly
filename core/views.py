from datetime import datetime, timedelta
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
