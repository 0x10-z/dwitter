from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.core.cache import cache
import time
from .models import Tweet, Like
from .forms import ProfileForm, UserForm

CACHE_SECONDS = 30


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
    start = time.perf_counter()

    if request.method == 'POST':
        content = request.POST.get('content')
        if content and len(content) <= 280:
            Tweet.objects.create(user=request.user, content=content)
            return redirect('dashboard')

    cache_key = f'dashboard_data_{request.user.id}'
    data = cache.get(cache_key)

    if not data:
        print("⚠️ Cache MISS")
        all_tweets = Tweet.objects.select_related('user').order_by('-created_at')
        tweet_count = Tweet.objects.filter(user=request.user).count()

        data = {
            'tweets': all_tweets,
            'tweet_count': tweet_count,
        }
        cache.set(cache_key, data, timeout=CACHE_SECONDS)
    else:
        print("✅ Cache HIT")

    like_count = request.user.like_set.count()  # SIEMPRE en tiempo real

    elapsed = time.perf_counter() - start
    print(f"⏱ Dashboard view took: {elapsed:.4f} seconds")

    return render(request, 'dwitter/dashboard.html', {
        **data,
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

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        u_form = UserForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('dashboard')
    else:
        u_form = UserForm(instance=request.user)
        p_form = ProfileForm(instance=profile)
    return render(request, 'dwitter/edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })


@login_required
def upload_avatar(request):
    if request.method == 'POST' and request.FILES.get('file'):
        profile = request.user.profile
        profile.avatar = request.FILES['file']
        profile.save()
        return JsonResponse({'success': True, 'url': profile.avatar.url})
    return JsonResponse({'success': False}, status=400)
