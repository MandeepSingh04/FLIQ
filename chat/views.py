from django.shortcuts import render, redirect
from chat.models import Room, Message
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User

# Create your views here.
def chat(request):
    p = request.user.profile
    friends = p.friends.all()
    context={
    'friends': friends
    }
    return render(request, 'chat.html', context)

def room(request, room):
    p = request.user.profile
    friends = p.friends.all()
    chat_user = request.user
    try:
        room_details = Room.objects.get(name=room)
    except Room.DoesNotExist:
         room_details = None
    return render(request, 'room.html', {
        'chat_user': chat_user,
        'room': room,
        'room_details': room_details,
        'friends': friends
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

    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages":list(messages.values())})