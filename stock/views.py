from django.shortcuts import render, redirect

# Create your views here.
def dashboard(request):
    return render(request, 'stock/dashboard.html')