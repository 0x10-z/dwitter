from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Tweet

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
def dashboard(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content and len(content) <= 280:
            Tweet.objects.create(user=request.user, content=content)
            return redirect('dashboard')
    tweets = Tweet.objects.select_related('user').order_by('-created_at')
    return render(request, 'dwitter/dashboard.html', {'tweets': tweets})
