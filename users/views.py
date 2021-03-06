from gettext import install
from pydoc import describe
from tkinter import EW
from urllib import request
from django.shortcuts import redirect, render
from .models import Profile, Skill
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from django.contrib.auth.decorators import login_required
from .utils import searchHelper, paginatorHelper

# Create your views here.

def RegisterUser(request):
    form = CustomUserCreationForm()
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request,"User Account was created!")

            login(request,user)
            return redirect('edit-account')
        else:
            messages.error(request,"Error ha occured!")
    
    context = {"page":"register","form":form,}
    return render(request,"users/login_register.html",context)

def LoginUser(request):
    if request.user.is_authenticated:
        return redirect('profiles')
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,"Got Error")
            print("user does not exist")
        user = authenticate(request,username=username,password=password)
        
        if user is not None:
            login(request,user)
            messages.success(request,"User has successfully Login!")
            return redirect('profiles')
        else:
            messages.error(request,"Got Error")

    context = {"page":"login",}

    return render(request,'users/login_register.html',context)


def LogoutUser(request):
    logout(request)
    messages.success(request,"User has successfully Logout!")
    return redirect('login')

def profiles(request):
    profiles,search_query = searchHelper(request)
    profiles,paginator,custom_range = paginatorHelper(request,profiles,result=3)
    context = {"profiles":profiles,"search_query":search_query,"paginator":paginator,"custom_range":custom_range,}
    return render(request,"users/profiles.html",context)

def userprofile(request,pk):
    profile = Profile.objects.get(id=pk)
    context  = {"profile":profile,}
    return render(request,"users/user-profile.html",context)

@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile
    skills = profile.skill_set.all()
    otherskills = profile.skill_set.filter(description="")
    context = {"profile":profile,"skills":skills}
    return render(request,'users/account.html',context)


@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)
    if request.method=="POST":
        form = ProfileForm(request.POST,request.FILES,instance=profile)
        if form.is_valid:
            form.save()
            return redirect('account')
    context = {'form':form,}
    return render(request,'users/profile_form.html',context)

@login_required(login_url='login')
def createSkill(request):
    profile = request.user.profile
    form = SkillForm()
    if request.method=="POST":
        form = SkillForm(request.POST)
        if form.is_valid:
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request,"Skill Added Successfully!")
            return redirect('account')
    context = {"form":form,}
    return render(request,"users/skill_form.html",context)

@login_required(login_url='login')
def updateSkill(request,pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=profile)
    if request.method=="POST":
        form = SkillForm(request.POST,instance=skill)
        if form.is_valid:
            form.save()
            messages.success(request,"Profile successfully updated!")
            return redirect('account')
    context = {"form":form,}
    return render(request,"users/skill_form.html",context)


@login_required(login_url='login')
def deleteSkill(request,pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method=="POST":
            skill.delete()
            messages.success(request,"Profile successfully deleted!")
            return redirect('account')
    context = {"object":skill,}
    return render(request,"delete_template.html",context)


@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    context = {'messageRequests': messageRequests, 'unreadCount': unreadCount}
    return render(request, 'users/inbox.html', context)



@login_required(login_url='login')
def viewMessage(request,pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read=True
        message.save()

    context = {"message":message}
    return render(request,'users/message.html',context)



def createMessage(request,pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()
    try:
        sender = request.user.profile
    except:
        sender = None
    
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()
            
            messages.success(request,"Message sent successufully")
            return redirect('user-profile',pk=recipient.id)

    context = {"recipient":recipient,"form":form,}
    return render(request,'users/message_form.html',context)