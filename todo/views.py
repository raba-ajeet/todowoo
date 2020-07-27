from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login,logout,authenticate
from .forms import TodoForm
from .models import Todo
from django.utils  import timezone
from django.contrib.auth.decorators import login_required
# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('currenttodos')
    else :
        return render(request,'todo/home1.html')
        

def signupuser(request):
    if request.method=='GET':
        return render(request,'todo/signup.html',{'form':UserCreationForm()})
    else:
        if request.POST['password1']==request.POST['password2']:
            try:
                user=User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request,user)
                return redirect('home')
            except IntegrityError:
                    return render(request,'todo/signup.html',{'form':UserCreationForm(),'warning':"username is already taken"})
            # return render(request,'todo/home.html')
        else:
            return render(request,'todo/signup.html',{'form':UserCreationForm(),'warning':"passwords didn't match"})

def loginuser(request):
    if request.method=='POST':
        user=authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request,'todo/login.html',{'form':AuthenticationForm(),'warning':"username and password didn't match"})
        else:
            login(request,user)
            return redirect('home')
    else:
        return render(request,'todo/login.html',{'form':AuthenticationForm()})

@login_required
def logoutuser(request):
    if request.method=='POST':
        logout(request)
        return redirect('home')

@login_required
def createtodo(request):
    if request.method=='GET':
        return render(request,'todo/createtodo.html',{'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            new_todo=form.save(commit=False)
            new_todo.user=request.user
            new_todo.save()
            return redirect('home')
        except ValueError:
            return render(request,'todo/createtodo.html',{'form':TodoForm(),'warning':'bad data passed '})
            
@login_required
def currenttodos(request):
    todos=Todo.objects.filter(user=request.user,date_completed__isnull=True)
    return render(request,'todo/currenttodos.html',{'todos':todos})

@login_required
def completed(request):
    todos=Todo.objects.filter(user=request.user,date_completed__isnull=False).order_by('-date_completed')
    return render(request,'todo/completed.html',{'todos':todos})

@login_required
def viewtodo(request,todo_pk):
    todo=get_object_or_404(Todo,pk=todo_pk)
    if request.method=='GET':
        form=TodoForm(instance=todo)
        return render(request,'todo/viewtodo.html',{'todo':todo,'form':form})
    else:
        try:
            form=TodoForm(request.POST,instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request,'todo/viewtodo.html',{'todo':todo,'form':form,'warning':'badinfo passed'})

@login_required
def completetodo(request,todo_pk):
    todo=get_object_or_404(Todo,pk=todo_pk)
    if request.method=='POST':
        todo.date_completed=timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required    
def deletetodo(request,todo_pk):
    todo=get_object_or_404(Todo,pk=todo_pk)
    if request.method=='POST':
        todo.delete() 
        return redirect('currenttodos')
        