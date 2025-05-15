from django.urls import path
from .views import OCRView

urlpatterns = [
    path('extract/', OCRView.as_view(), name='extract-text'),
]
