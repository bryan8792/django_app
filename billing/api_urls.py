from django.urls import path
from .api import bot_invoice, bot_invoice_message

app_name = 'bot_api'
urlpatterns = [
    path('factura/', bot_invoice, name='factura'),
    path('factura/mensaje/', bot_invoice_message, name='factura_mensaje'),
]
