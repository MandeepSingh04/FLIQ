from django.shortcuts import render, redirect
from chat.models import Room, Message
from django.http import HttpResponse, JsonResponse

# Create your views here.
def chat(request):
    return render(request, 'chat.html')

def room(request, room):
    chat_user = request.GET.get('chat_user')
    try:
        room_details = Room.objects.get(name=room)
    except Room.DoesNotExist:
         room_details = None
    return render(request, 'room.html', {
        'chat_user': chat_user,
        'room': room,
        'room_details': room_details
    })

def checkview(request):
    room = request.POST['room_name']
    chat_user = request.POST['chat_user']

    if Room.objects.filter(name=room).exists():
        return redirect('/'+room+'/?chat_user='+chat_user)
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect('/'+room+'/?chat_user='+chat_user)

def send(request):
    message = request.POST['message']
    chat_user = request.POST['chat_user']
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value=message, user=chat_user, room=room_id)
    new_message.save()
    return HttpResponse('Message sent successfully')

def getMessages(request, room):
    room_details = Room.objects.get(name=room)

    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages":list(messages.values())})