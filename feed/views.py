from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import NewCommentForm, NewPostForm
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Comments, Like
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from users.models import Profile,FriendRequest
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
import boto3
import random
from django.conf import settings
import re

import json

def replace(match):
    hashtag = match.group(1)
    return f'<a href = "/search/?p={hashtag}">{match.group(0)}</a>'

@method_decorator(login_required, name='dispatch')
class PostListView(ListView):
    model = Post
    template_name = 'feed/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    # paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            p = Profile.objects.get(user=self.request.user)
            p_friends = p.friends.all()
            context['friends'] = p_friends
            liked = [i for i in Post.objects.all() if Like.objects.filter(user = self.request.user, post=i)]
            context['liked_post'] = liked
            users = Profile.objects.exclude(user=self.request.user)
            sent_friend_requests = FriendRequest.objects.filter(from_user=self.request.user)
            rec_friend_requests = FriendRequest.objects.filter(to_user=self.request.user)
            my_friends = self.request.user.profile.friends.all()

            friends = []
            sent_to = []

            for user in my_friends:
                friends.extend(user.friends.all())

            friends = list(set(friends) - set(my_friends) - {self.request.user.profile})

            sent_to = [friend_request.to_user for friend_request in sent_friend_requests]

            suggestions=[]
            for user in users:
                mutual_friends = list(set(user.friends.all()) & set(my_friends))
                if user not in my_friends and user not in sent_to and user not in my_friends:
                    suggestions.append({
                        'user': user,
                        'mutual_friends': mutual_friends,
                    })

            context['users'] = friends
            context['sent'] = sent_to
            context['suggestions'] = suggestions
            hashtag_pattern = r'\#(\w+)'
            for i in context['posts']:
                desc = i.description
                link_desc = re.sub(hashtag_pattern, replace,desc)
                i.description = link_desc

        return context

class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'feed/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        liked = [i for i in Post.objects.filter(user_name=user) if Like.objects.filter(user = self.request.user, post=i)]
        context['liked_post'] = liked
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(user_name=user).order_by('-date_posted')


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    is_liked =  Like.objects.filter(user=user, post=post)
    if request.method == 'POST':
        form = NewCommentForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.post = post
            data.username = user
            data.save()
            return redirect('post-detail', pk=pk)
    else:
        form = NewCommentForm()
    return render(request, 'feed/post_detail.html', {'post':post, 'is_liked':is_liked, 'form':form})

@login_required
def create_post(request):
    user = request.user
    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.user_name = user
            data.save()
            messages.success(request, f'Posted Successfully')
            return redirect('home')
    else:
        form = NewPostForm()
    return render(request, 'feed/create_post.html', {'form':form})

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['description', 'pic', 'tags']
    template_name = 'feed/create_post.html'

    def form_valid(self, form):
        form.instance.user_name = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user_name:
            return True
        return False

@login_required
def post_delete(request, pk):
    post = Post.objects.get(pk=pk)
    if request.user== post.user_name:
        Post.objects.get(pk=pk).delete()
    return redirect('home')


@login_required
def search(request):
    query = "#" + request.GET.get('p')
    if(not query):
         return render(request, "feed/search.html")
    user_object_list = User.objects.filter(username__icontains=query)
    post_object_list = Post.objects.filter(description__icontains=query)
    liked = [i for i in post_object_list if Like.objects.filter(user = request.user, post=i)]
    context ={
        'posts': post_object_list,
        'liked_post': liked,
        'users': user_object_list
    }
    return render(request, "feed/search.html", context)


class explore_posts(ListView):
    model = Post
    template_name = 'feed/explore.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 10
    def get_context_data(self, **kwargs):
        context = super(explore_posts, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            p = Profile.objects.get(user=self.request.user)
            friends = p.friends.all()
            context['friends'] = friends
            liked = [i for i in Post.objects.all() if Like.objects.filter(user = self.request.user, post=i).exists()]
            context['liked_post'] = liked
        return context



@login_required
def like(request):
    post_id = request.GET.get("likeId", "")
    user = request.user
    post = Post.objects.get(pk=post_id)
    liked= False
    like = Like.objects.filter(user=user, post=post)
    if like:
        like.delete()
    else:
        liked = True
        Like.objects.create(user=user, post=post)
    resp = {
        'liked':liked
    }
    response = json.dumps(resp)
    return HttpResponse(response, content_type = "application/json")