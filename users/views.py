from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from feed.models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponseRedirect
from .models import Profile, FriendRequest
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
import random
from chat.models import Room

User = get_user_model()

@login_required
def users_list(request):
    users = Profile.objects.exclude(user=request.user)
    sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
    rec_friend_requests = FriendRequest.objects.filter(to_user=request.user)
    my_friends = request.user.profile.friends.all()
    sent_to = []
    received = []
    friends = []

    for user in my_friends:
        friend = user.friends.all()
        for f in friend:
            if f in friends:
                friend = friend.exclude(user=f.user)
        friends += friend
    for i in my_friends:
        if i in friends:
            friends.remove(i)
    if request.user.profile in friends:
        friends.remove(request.user.profile)
    random_list = random.sample(list(users), min(len(list(users)), 10))
    for r in random_list:
        if r in friends:
            random_list.remove(r)
    friends += random_list
    for i in my_friends:
        if i in friends:
            friends.remove(i)
    for se in sent_friend_requests:
        sent_to.append(se.to_user)
    for se in rec_friend_requests:
        received.append(se.from_user)
    context = {
        'users': friends,
        'sent': sent_to
    }
    p = Profile.objects.filter(user=request.user).first()
    # is this user our friend
    button_status = 'none'
    if p not in request.user.profile.friends.all():
        button_status = 'not_friend'
        
        # if we have sent him a friend request
        if len(FriendRequest.objects.filter(
            from_user=request.user).filter(to_user=p.user)) == 1:
                button_status = 'friend_request_sent'

        # if we have recieved a friend request
        if len(FriendRequest.objects.filter(
            from_user=p.user).filter(to_user=request.user)) == 1:
                button_status = 'friend_request_received'

    context = {
        'users': friends,
        'sent': sent_to,
        'received': received,
        'button_status': button_status,
        'sent_friend_requests': sent_friend_requests,
        'rec_friend_requests': rec_friend_requests,
    }
    return render(request, "users/users_list.html", context)

def friend_list(request):
    p = request.user.profile
    friends = p.friends.all()
    context={
    'friends': friends
    }
    return render(request, "users/friend_list.html", context)

@login_required
def send_friend_request(request, id):
    user = get_object_or_404(User, id=id)
    frequest, created = FriendRequest.objects.get_or_create(
            from_user=request.user,
            to_user=user)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def cancel_friend_request(request, id):
    user = get_object_or_404(User, id=id)
    frequest = FriendRequest.objects.filter(
            from_user=request.user,
            to_user=user).first()
    frequest.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def accept_friend_request(request, id):
    from_user = get_object_or_404(User, id=id)
    frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
    user1 = frequest.to_user
    user2 = from_user
    user1.profile.friends.add(user2.profile)
    user2.profile.friends.add(user1.profile)
    #chat room
    room = user2.username + '&' + user1.username
    new_room = Room.objects.create(name=room)
    new_room.save()

    if(FriendRequest.objects.filter(from_user=request.user, to_user=from_user).first()):
        request_rev = FriendRequest.objects.filter(from_user=request.user, to_user=from_user).first()
        request_rev.delete()
    frequest.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def delete_friend_request(request, id):
    from_user = get_object_or_404(User, id=id)
    frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
    frequest.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

def delete_friend(request, id):
    user_profile = request.user.profile
    friend_profile = get_object_or_404(Profile, id=id)
    user_profile.friends.remove(friend_profile)
    friend_profile.friends.remove(user_profile)
    return HttpResponseRedirect('/users/{}'.format(friend_profile.slug))

@login_required
def profile_view(request, slug):
    p = Profile.objects.filter(slug=slug).first()
    u = p.user
    sent_friend_requests = FriendRequest.objects.filter(from_user=p.user)
    rec_friend_requests = FriendRequest.objects.filter(to_user=p.user)
    user_posts = Post.objects.filter(user_name=u).order_by('-date_posted')

    friends = p.friends.all().exclude(id=request.user.profile.id)
    mutual = request.user.profile.friends.all().exclude(id=request.user.profile.id)
    mutual_friends = friends.intersection(mutual)
    non_mutual_friends = friends.difference(mutual)


    # is this user our friend
    button_status = 'none'
    if p not in request.user.profile.friends.all():
        button_status = 'not_friend'

        # if we have sent him a friend request
        if len(FriendRequest.objects.filter(
            from_user=request.user).filter(to_user=p.user)) == 1:
                button_status = 'friend_request_sent'

        # if we have recieved a friend request
        if len(FriendRequest.objects.filter(
            from_user=p.user).filter(to_user=request.user)) == 1:
                button_status = 'friend_request_received'

    context = {
        'u': u,
        'button_status': button_status,
        'friends_list': friends,
        'mutual_friends': mutual_friends,
        'non_mutual_friends': non_mutual_friends,
        'sent_friend_requests': sent_friend_requests,
        'rec_friend_requests': rec_friend_requests,
        'post_count': user_posts.count,
        'posts': user_posts
    }

    return render(request, "users/profile.html", context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You can now login!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('my_profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context ={
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'users/edit_profile.html', context)

@login_required
def my_profile(request):
    p = request.user.profile
    you = p.user
    sent_friend_requests = FriendRequest.objects.filter(from_user=you)
    rec_friend_requests = FriendRequest.objects.filter(to_user=you)
    user_posts = Post.objects.filter(user_name=you).order_by('-date_posted')
    friends = p.friends.all()

    # is this user our friend
    button_status = 'none'
    if p not in request.user.profile.friends.all():
        button_status = 'not_friend'

        # if we have sent him a friend request
        if len(FriendRequest.objects.filter(
            from_user=request.user).filter(to_user=you)) == 1:
                button_status = 'friend_request_sent'

        if len(FriendRequest.objects.filter(
            from_user=p.user).filter(to_user=request.user)) == 1:
                button_status = 'friend_request_received'

    context = {
        'u': you,
        'button_status': button_status,
        'friends_list': friends,
        'sent_friend_requests': sent_friend_requests,
        'rec_friend_requests': rec_friend_requests,
        'post_count': user_posts.count,
        'posts': user_posts
    }

    return render(request, "users/profile.html", context)

@login_required
def search_users(request):
    query = request.GET.get('q')
    if(not query):
         return render(request, "users/search_users.html")
    object_list = User.objects.filter(username__icontains=query)
    context ={
        'users': object_list
    }
    return render(request, "users/search_users.html", context)
