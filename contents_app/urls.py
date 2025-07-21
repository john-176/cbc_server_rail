from .views import (
    AchieverListCreateView,
    AchieverRetrieveUpdateDestroyView,
    VideoShowcaseListCreateView, 
    VideoShowcaseRetrieveDestroyView,
    VideoUploadView,
    ShowcaseImageListCreateView,
    ShowcaseImageRetrieveDestroyView,
    YouTubeVideoListCreateView,
    YouTubeVideoDetailView,
    AnnouncementDeleteView,
    AnnouncementListCreateView,
    )

from django.urls import path


urlpatterns = [
    path('achievers/', AchieverListCreateView.as_view(), name='achiever-list'),
    path('achievers/<int:pk>/', AchieverRetrieveUpdateDestroyView.as_view(), name='achiever-detail'),
    
    path('videos/', VideoShowcaseListCreateView.as_view(), name='video-list'),
    path('videos/<int:pk>/', VideoShowcaseRetrieveDestroyView.as_view(), name='video-detail'),
    path('videos/upload/', VideoUploadView.as_view(), name='video-upload'),
    
    path('showcase-images/', ShowcaseImageListCreateView.as_view(), name='showcase-image-list'),
    path('showcase-images/<int:pk>/', ShowcaseImageRetrieveDestroyView.as_view(), name='showcase-image-detail'),
    
    path("youtube/", YouTubeVideoListCreateView.as_view(), name="youtube-list"),
    path("youtube/<int:pk>/", YouTubeVideoDetailView.as_view(), name="youtube-detail"),
    
    path('announcements/', AnnouncementListCreateView.as_view(), name='announcement-list'),
    path('announcements/<int:pk>/', AnnouncementDeleteView.as_view(), name='announcement-delete'),
       
]
