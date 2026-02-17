from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Play(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    story_id = models.IntegerField()
    ending_label = models.CharField(max_length=255, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class StoryRating(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    story_id = models.IntegerField() 
    # Stars requirement
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        
        unique_together = ('user', 'story_id')

class StoryReport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    story_id = models.IntegerField()
    reason = models.CharField(max_length=255) 
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)