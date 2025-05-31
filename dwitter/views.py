import time

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Q
from django.middleware.csrf import get_token

from .models import Tweet, Like, Follow
from .forms import ProfileForm, UserForm


CACHE_SECONDS = 30

def invalidate_dashboard_cache(user):
    cache_key = f'dashboard_data_{user.id}'
    cache.delete(cache_key)
 

#################
# AUTH & PROFILE
#################

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

#################
# DASHBOARD
#################

@login_required
def dashboard(request):
    start = time.perf_counter()

    if request.method == 'POST':
        content = request.POST.get('content')
        if content and len(content) <= 280:
            Tweet.objects.create(user=request.user, content=content)
            invalidate_dashboard_cache(request.user)
            return redirect('dashboard')

    cache_key = f'dashboard_data_{request.user.id}'
    data = cache.get(cache_key)

    if not data:
        print("⚠️ Cache MISS")
        all_tweets = Tweet.get_feed_for_user(request.user)
        tweet_count = Tweet.objects.filter(user=request.user).count()

        data = {
            'tweets': all_tweets,
            'tweet_count': tweet_count,
        }
        cache.set(cache_key, data, timeout=CACHE_SECONDS)
    else:
        print("✅ Cache HIT")

    like_count = request.user.like_set.count()  # SIEMPRE en tiempo real

    follower_count = Follow.objects.filter(following=request.user).count()
    following_count = Follow.objects.filter(follower=request.user).count()

    elapsed = time.perf_counter() - start
    print(f"⏱ Dashboard view took: {elapsed:.4f} seconds")

    return render(request, 'dwitter/dashboard.html', {
        **data,
        'like_count': like_count,
        'follower_count': follower_count,
        'following_count': following_count,
    })

#################
# TWEET
#################

@login_required
def delete_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id, user=request.user)
    tweet.delete()
    invalidate_dashboard_cache(request.user)
    return redirect('dashboard')


@login_required
def like_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    like, created = Like.objects.get_or_create(user=request.user, tweet=tweet)
    if not created:
        like.delete()
    return redirect('dashboard')


@login_required
def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    profile = tweet.user.profile
    return render(request, 'dwitter/tweet_detail.html', {'tweet': tweet, 'profile': profile})

#################
# PROFILES
#################

@login_required
def explore_users(request):
    users = User.objects.exclude(id=request.user.id).select_related('profile')
    following = set(request.user.following_set.values_list('following_id', flat=True))

    users_with_following_status = []
    for user in users:
        users_with_following_status.append({
            'user': user,
            'is_following': user.id in following
        })

    return render(request, 'dwitter/explore_users.html', {
        'users_with_status': users_with_following_status,
        'csrf_token': get_token(request),  # aquí lo incluyes
    })



@login_required
def user_profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    tweets = Tweet.objects.filter(user=user_profile).order_by('-created_at')
    profile = user_profile.profile
    profile_user = get_object_or_404(User, username=username)
    tweets = Tweet.objects.filter(user=profile_user)
    like_count = Like.objects.filter(tweet__user=profile_user).count()
    follower_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    is_following = request.user.following_set.filter(following=user_profile).exists()

    return render(request, 'dwitter/user_profile.html', {
        'profile_user': user_profile,
        'profile': profile,
        'tweets': tweets,
        'is_following': is_following,
        'tweet_count': tweets.count(),
        'like_count': like_count,
        'follower_count': follower_count,
        'following_count': following_count,
    })

@login_required
def toggle_follow_ajax(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        target = get_object_or_404(User, username=username)

        if request.user == target:
            return JsonResponse({'error': 'No puedes seguirte a ti mismo.'}, status=400)

        is_following = Follow.objects.filter(follower=request.user, following=target).exists()

        if is_following:
            Follow.objects.filter(follower=request.user, following=target).delete()
            invalidate_dashboard_cache(request.user)
            return JsonResponse({'status': 'unfollowed'})
        else:
            Follow.objects.create(follower=request.user, following=target)
            invalidate_dashboard_cache(request.user)
            return JsonResponse({'status': 'followed'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

###############
# TWEET SEARCH
###############

@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    tweets = Tweet.objects.none()

    if query:
        tweets = Tweet.objects.filter(
            Q(content__icontains=query) |
            Q(user__username__icontains=query)
        ).select_related('user').order_by('-created_at')

    return render(request, 'dwitter/search_results.html', {
        'query': query,
        'tweets': tweets
    })