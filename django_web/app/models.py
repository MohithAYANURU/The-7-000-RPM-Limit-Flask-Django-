from django.db import models
from django.conf import settings

class Play(models.Model):
    # Level 16: Link to User
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    story_id = models.IntegerField()
    # Level 13: Stats and Labels
    ending_label = models.CharField(max_length=255, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)