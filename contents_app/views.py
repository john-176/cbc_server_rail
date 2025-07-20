from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, AllowAny
from .models import Achiever, Announcement, VideoShowcase, ShowcaseImage
from .serializers import (AchieverSerializer, 
                          AnnouncementSerializer,
                          VideoShowcaseSerializer,
                          ShowcaseImageSerializer,
                          YouTubeVideoSerializer,
                          YouTubeVideo
                          )
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .models import ShowcaseImage
from .serializers import ShowcaseImageSerializer
from rest_framework.parsers import MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators to edit their achievers
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user

class AchieverListCreateView(generics.ListCreateAPIView):
    queryset = Achiever.objects.all()
    serializer_class = AchieverSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    pagination_class = StandardResultsSetPagination
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class AchieverRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Achiever.objects.all()
    serializer_class = AchieverSerializer
    permission_classes = [IsCreatorOrReadOnly | IsAdminUser]
    
    
#--------------------video upload---------------------------------------------------------------

from rest_framework import generics, permissions
from .models import VideoShowcase
from .serializers import VideoShowcaseSerializer
from rest_framework.parsers import MultiPartParser
from django.http import JsonResponse
from rest_framework.views import APIView

class VideoShowcaseListCreateView(generics.ListCreateAPIView):
    queryset = VideoShowcase.objects.all()
    serializer_class = VideoShowcaseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class VideoUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        video_file = request.FILES.get('video_file')
        if not video_file:
            return JsonResponse({'error': 'No video file provided'}, status=400)
        
        # Create a temporary VideoShowcase instance
        video = VideoShowcase(
            title=request.POST.get('title', 'Untitled'),
            video=video_file,
            created_by=request.user
        )
        video.save()
        
        return JsonResponse({
            'id': video.id,
            'title': video.title,
            'url': video.video.url,
            'format': video.format
        })
        
from .serializers import VideoShowcaseSerializer
from django.core.exceptions import PermissionDenied
from cloudinary import uploader

class VideoShowcaseRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = VideoShowcase.objects.all()
    serializer_class = VideoShowcaseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAdminUser()]  # Only admin can delete
        return super().get_permissions()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Add additional video data for frontend
        data = serializer.data
        data['is_staff'] = request.user.is_staff or request.user.is_superuser
        data['can_delete'] = self.can_delete_video(request.user, instance)
        
        return Response(data)
    
    def can_delete_video(self, user, video):
        """Check if user has permission to delete this video"""
        return user.is_staff or user.is_superuser or video.created_by == user
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if not self.can_delete_video(request.user, instance):
            raise PermissionDenied("You don't have permission to delete this video")
        
        try:
            # Delete from Cloudinary first
            if hasattr(instance.video, 'public_id'):
                uploader.destroy(instance.video.public_id, resource_type='video')
            
            # Then delete from database
            self.perform_destroy(instance)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to delete video: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        
            
#---------------------Announcements--------------------------------------------------------------    

class AnnouncementListCreateView(generics.ListCreateAPIView):
    queryset = Announcement.objects.order_by('-date')
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            serializer.save()
        else:
            raise PermissionDenied("Only staff or superusers can add announcements.")


class AnnouncementDeleteView(generics.DestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            instance.delete()
        else:
            raise PermissionDenied("Only staff or superusers can delete announcements.")   
        
        
#---------------------------Images---------------------------------------------------------------


class ShowcaseImageListCreateView(generics.ListCreateAPIView):
    queryset = ShowcaseImage.objects.all()
    serializer_class = ShowcaseImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser]
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ShowcaseImageRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = ShowcaseImage.objects.all()
    serializer_class = ShowcaseImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_destroy(self, instance):
        if not (self.request.user.is_staff or 
                self.request.user.is_superuser or
                instance.created_by == self.request.user):
            raise PermissionDenied("You don't have permission to delete this image")
        instance.delete()         
        
        
#---------------------------Youtube Videos---------------------------------------------------------------

# Public can view; only staff/superuser can create
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class YouTubeVideoListCreateView(generics.ListCreateAPIView):
    queryset = YouTubeVideo.objects.all().order_by('-created_at')
    serializer_class = YouTubeVideoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if not self.request.user.is_staff and not self.request.user.is_superuser:
            raise PermissionDenied("Only staff or superusers can create YouTube videos.")
        serializer.save()


# Public can retrieve; only staff/superuser can update/delete
class YouTubeVideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = YouTubeVideo.objects.all()
    serializer_class = YouTubeVideoSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
