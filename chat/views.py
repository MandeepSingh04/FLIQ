from django.shortcuts import render, redirect
from chat.models import Room, Message
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User

# Create your views here.
def chat(request):
    p = request.user.profile
    friends = p.friends.all()
    chat_details=[]
    for friend in friends:
        room="";
        if(friend.user.username < request.user.username):
            room += friend.user.username + "-" + request.user.username;
        else:
            room += request.user.username + "-" + friend.user.username;
        try:
            room_details = Room.objects.get(name=room)
        except Room.DoesNotExist:
            room_details = None
        messages = Message.objects.filter(room=room_details.id,read=True)
        unread_messages = Message.objects.filter(room=room_details.id,read=False)
        num = unread_messages.count()
        if(num>0):
            recent = unread_messages[0].value
            time = unread_messages[0].date
        else:
            recent = messages[0].value
            time = messages[0].date
        chat = [num,recent,time]
        chat_details.append(chat)
    context={
    'friends': zip(friends,chat_details)
    }

    return render(request, 'chat.html', context)

def room(request, room):
    p = request.user.profile
    friends = p.friends.all()

    chat_details=[]
    for friend in friends:
        room_p="";
        if(friend.user.username < request.user.username):
            room_p += friend.user.username + "-" + request.user.username;
        else:
            room_p += request.user.username + "-" + friend.user.username;
        try:
            room_details = Room.objects.get(name=room_p)
        except Room.DoesNotExist:
            room_details = None
        messages = Message.objects.filter(room=room_details.id,read=True)
        unread_messages = Message.objects.filter(room=room_details.id,read=False)
        num = unread_messages.count()
        if(num>0):
            recent = unread_messages[0].value
            time = unread_messages[0].date
        else:
            recent = messages[0].value
            time = messages[0].date
        chat = [num,recent,time]
        chat_details.append(chat)

    name = room.replace(request.user.username, '').replace('-', '')
    chat_user = User.objects.get(username=name)
    try:
        room_details = Room.objects.get(name=room)
    except Room.DoesNotExist:
         room_details = None
    return render(request, 'room.html', {
        'chat_user': chat_user,
        'room': room,
        'room_details': room_details,
        'friends': zip(friends,chat_details)
    })

def checkview(request):
    room = request.POST.get('room_name', False)
    chat_user = request.user

    if Room.objects.filter(name=room).exists():
        return redirect(room)
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect(room)

def send(request):
    message = request.POST['message']
    user = request.user
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value=message, user=user, username=user.username, name= user.profile.name, image=user.profile.image.url, room=room_id)
    new_message.save()
    return HttpResponse('Message sent successfully')

def getMessages(request, room):
    room_details = Room.objects.get(name=room)

    messages = Message.objects.filter(room=room_details.id,read=True)
    unread_messages = Message.objects.filter(room=room_details.id,read=False)
    unread_message_list = list(unread_messages.values())
    return JsonResponse({"messages":list(messages.values()),"unread_messages": unread_message_list})