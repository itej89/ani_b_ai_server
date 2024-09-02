#from django.urls import path


from . import consumer

# ws_urlpatters = [
#     path('chat/', WSConsumer.as_asgi())
# ]

channel_routing = {
    # TODO: From the original examples, there is more (https://github.com/jacobian/channels-example/)
    'websocket.connect': consumer.ws_connect,
    'websocket.receive': consumer.ws_receive,
    'websocket.disconnect': consumer.ws_disconnect,
}
