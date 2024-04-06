"""
ASGI config for FLIQ project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

# import os
# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application
# import chat.routing



# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FLIQ.settings')

# application = ProtocolTypeRouter( 
#     {
#         "http":get_asgi_application(),
#         "websocket": AuthMiddlewareStack(
#             URLRouter(
#                chat.routing.websocket_urlpatterns
#             )
#         ),
#     }
# )

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FLIQ.settings')

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter , URLRouter
from chat import routing

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter(
	{
		"http" : get_asgi_application() , 
		"websocket" : AuthMiddlewareStack(
			URLRouter(
				routing.websocket_urlpatterns
			) 
		)
	}
)
