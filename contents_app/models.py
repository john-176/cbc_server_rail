from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

class Achiever(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    bio = models.TextField()
    image = CloudinaryField('image', folder='achievers/')
    years_active = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        
        
    
#-----------------Video upload---------------------------------------------------------

from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField

class VideoShowcase(models.Model):
    title = models.CharField(max_length=200)
    video = CloudinaryField(resource_type='video', folder='school_videos/')
    format = models.CharField(max_length=10, blank=True)
    duration = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Only try to get format if video exists and is already uploaded
        if self.video and hasattr(self.video, 'url'):
            self.format = self.video.url.split('.')[-1].lower()
            
        super().save(*args, **kwargs)
        
        


#-----------------Announcements--------------------------------------------------------- 

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title    
       
       
       
#-----------------Images-------------------------------------

class ShowcaseImage(models.Model):
    image = CloudinaryField('image', folder='showcase/')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Showcase Image {self.id}"

    @property
    def url(self):
        return self.image.url if self.image else None
    
    
#----------------------Youtube videos--------------------------------------------
class YouTubeVideo(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title