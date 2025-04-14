from django.urls import path
from myapp import views

urlpatterns = [
    path('predict/', views.predictFailure, name='predict'), 
    path('chart-data/', views.chartData, name='chart-data'),
]
