from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Welcome {username}.\nYour account has been created successfully.')
            return redirect('login')
    else:
        form = RegisterForm()
    
    context = {'form': form}

    return render(request, 'users/register.html', context)