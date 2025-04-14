from myapp.models import Prediction
from rest_framework import serializers

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = '__all__'