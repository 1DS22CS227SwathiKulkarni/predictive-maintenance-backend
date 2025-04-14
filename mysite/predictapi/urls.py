from django.urls import path
from .views import PredictAPIView, PredictDetail

urlpatterns = [
    path('', PredictAPIView.as_view(), name='predict-list'),
    path('<int:pk>/', PredictDetail.as_view(), name='predict-detail'),
]