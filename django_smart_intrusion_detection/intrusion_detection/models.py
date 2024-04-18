from django.db import models
from token_authentication import models as ta_model
# Create your models here.
class HomeSettings(models.Model):
    user = models.ForeignKey(ta_model.UserAuthentication, on_delete=models.DO_NOTHING)
    video_file = models.CharField(max_length=200, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    threshold = models.FloatField(default=0.5, null=True, blank=True)
    segmentation_orientation = models.CharField(max_length=1, null=True, blank=True, default='h')
    point1X = models.IntegerField(default=0)
    point1Y = models.IntegerField(default=0)
    area_flipped = models.BooleanField(default=False)

class InferenceSettings(models.Model):
    user = models.ForeignKey(ta_model.UserAuthentication, on_delete=models.DO_NOTHING)
    model_name = models.CharField(max_length=100, default='rtdetr_yolov9bb_ep27.onnx')
    overlay_line = models.CharField(max_length=100, default='h_0_450_640_450_0')
    objects_to_warn = models.CharField(max_length=300, default='person,bicycle')
    size = models.IntegerField(default=640)
