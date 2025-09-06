from django.urls import path
from .views import SendEmailView, EmailLogListView

urlpatterns = [
    path('send/', SendEmailView.as_view(), name='emails-send'),
    path('logs/', EmailLogListView.as_view(), name='emails-logs'),
]
