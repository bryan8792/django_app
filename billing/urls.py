from django.urls import path
from .views import DashboardView, SubscriberListView, SubscriberDetailView, InvoiceUpdateView, InvoicePreviewView, ImportExcelView, CampaignCreateView, CampaignListView, CampaignQueueView, WhatsAppQrView, UserListView, UserCreateView, UserUpdateView, UserToggleView
urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('abonados/', SubscriberListView.as_view(), name='subscribers'),
    path('abonados/<int:pk>/', SubscriberDetailView.as_view(), name='subscriber_detail'),
    path('facturas/<int:pk>/', InvoicePreviewView.as_view(), name='invoice_preview'),
    path('facturas/<int:pk>/editar/', InvoiceUpdateView.as_view(), name='invoice_edit'),
    path('importar/', ImportExcelView.as_view(), name='import_excel'),
    path('campanas/', CampaignListView.as_view(), name='campaigns'),
    path('campanas/nueva/', CampaignCreateView.as_view(), name='campaign_create'),
    path('whatsapp/qr/', WhatsAppQrView.as_view(), name='whatsapp_qr'),
    path('usuarios/', UserListView.as_view(), name='users'),
    path('usuarios/nuevo/', UserCreateView.as_view(), name='user_create'),
    path('usuarios/nueva/', UserCreateView.as_view(), name='user_create_alias'),
    path('usuarios/<int:pk>/editar/', UserUpdateView.as_view(), name='user_edit'),
    path('usuarios/<int:pk>/estado/', UserToggleView.as_view(), name='user_toggle'),
    path('campanas/<int:pk>/encolar/', CampaignQueueView.as_view(), name='campaign_queue'),
]
