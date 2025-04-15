from django.shortcuts import render
from rest_framework import generics
from myapp.models import Prediction
from .serializers import PredictionSerializer

# GET (list) and POST (create)
class PredictAPIView(generics.ListCreateAPIView):  
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer

# GET (retrieve), PUT/PATCH (update), DELETE (delete)
class PredictDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
