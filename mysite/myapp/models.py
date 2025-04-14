from django.db import models

# Create your models here.
class Prediction(models.Model):
    def __str__(self):
        return f"{self.pk}"

    mach_type = models.CharField(max_length=1) 
    air_temp = models.FloatField()
    process_temp = models.FloatField()
    rot_speed = models.IntegerField()
    torque = models.FloatField()
    tool_wear = models.IntegerField()
    failure_risk = models.FloatField()
    failure_type = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
