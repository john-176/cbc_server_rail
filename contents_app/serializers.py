from .models import Achiever, VideoShowcase, Announcement, YouTubeVideo
from cloudinary.models import CloudinaryField
from rest_framework import serializers, generics, permissions, status
from rest_framework.exceptions import PermissionDenied
import re

#---------------AchieverSerializer-----------------------------------

class AchieverSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    is_editable = serializers.SerializerMethodField()
    
    class Meta:
        model = Achiever
        fields = ['id', 'name', 'title', 'bio', 'image', 'years_active', 
                 'created_at', 'is_editable']
        read_only_fields = ['id', 'created_at', 'is_editable']
    
    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    def get_is_editable(self, obj):
        request = self.context.get('request')
        if request:
            return obj.created_by == request.user or request.user.is_staff
        return False
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
#-------------------video upload-----------------------------------------------------

class VideoShowcaseSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    is_editable = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = VideoShowcase
        fields = [
            'id', 'title', 'url', 'format', 'duration', 
            'created_at', 'is_editable', 'can_delete'
        ]
        read_only_fields = fields

    def get_url(self, obj):
        if hasattr(obj.video, 'url'):
            return obj.video.url
        return None

    def get_is_editable(self, obj):
        request = self.context.get('request')
        if request:
            return request.user.is_staff or request.user.is_superuser
        return False

    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request:
            return (request.user.is_staff or 
                    request.user.is_superuser or 
                    obj.created_by == request.user)
        return False
    
    
#--------------------AnnouncementSerializer-----------------------------------------------

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'message', 'date'] 
        
#--------------------Images----------------------------------------------------

from rest_framework import serializers
from .models import ShowcaseImage

class ShowcaseImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    is_editable = serializers.SerializerMethodField()

    class Meta:
        model = ShowcaseImage
        fields = ['id', 'url', 'created_at', 'is_editable']
        read_only_fields = ['id', 'created_at', 'is_editable']

    def get_url(self, obj):
        return obj.url

    def get_is_editable(self, obj):
        request = self.context.get('request')
        if request:
            return request.user.is_staff or request.user.is_superuser
        return False

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)        
    
    
#--------------------------Youtube videos--------------------------------------------

class YouTubeVideoSerializer(serializers.ModelSerializer):
    def validate_url(self, value):
        # Accept watch, youtu.be, embed, shorts
        pattern = re.compile(
            r'^(https?://)?(www\.)?(youtube\.com/(watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})'
        )
        if not pattern.match(value):
            raise serializers.ValidationError("Invalid YouTube URL format.")
        return value

    class Meta:
        model = YouTubeVideo
        fields = ['id', 'title', 'url', 'is_active', 'created_at']
        
        
#--------------------------Youtube videos--------------------------------------------


class YouTubeVideoSerializer(serializers.ModelSerializer):
    def validate_url(self, value):
        # Accept watch, youtu.be, embed, shorts
        pattern = re.compile(
            r'^(https?://)?(www\.)?(youtube\.com/(watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})'
        )
        if not pattern.match(value):
            raise serializers.ValidationError("Invalid YouTube URL format.")
        return value

    class Meta:
        model = YouTubeVideo
        fields = ['id', 'title', 'url', 'is_active', 'created_at']
        