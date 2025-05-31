from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Tweet, Like

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'dwitter/register.html', {'form': form})


@login_required
def delete_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id, user=request.user)
    tweet.delete()
    return redirect('dashboard')


@login_required
def like_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    like, created = Like.objects.get_or_create(user=request.user, tweet=tweet)
    if not created:
        like.delete() 
    return redirect('dashboard')


@login_required
def dashboard(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content and len(content) <= 280:
            Tweet.objects.create(user=request.user, content=content)
            return redirect('dashboard')

    all_tweets = Tweet.objects.select_related('user').order_by('-created_at')

    tweet_count = Tweet.objects.filter(user=request.user).count()
    like_count = request.user.like_set.count()

    return render(request, 'dwitter/dashboard.html', {
        'tweets': all_tweets,
        'tweet_count': tweet_count,
        'like_count': like_count,
    })

@login_required
def user_profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    tweets = Tweet.objects.filter(user=user_profile).order_by('-created_at')
    return render(request, 'dwitter/user_profile.html', {
        'profile_user': user_profile,
        'tweets': tweets
    })

@login_required
def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    return render(request, 'dwitter/tweet_detail.html', {'tweet': tweet})

