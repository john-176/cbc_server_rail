from django.contrib import admin

from .models import VideoShowcase, Achiever, ShowcaseImage, YouTubeVideo
from django.utils.html import format_html  
#-----------------------------------------------------------
@admin.register(Achiever)  # Note: Just @admin.register without .site
class AchieverAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'created_at')
    search_fields = ('name', 'title')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

#-------------------Showcase Images-------------------------------------------------

@admin.register(ShowcaseImage)
class ShowcaseImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_preview', 'created_at', 'created_by')
    readonly_fields = ('image_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('id',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" />', obj.url)
        return "No Image"
    image_preview.short_description = 'Preview'
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

#--------------------Video Showcase------------------------------------------------

@admin.register(VideoShowcase)
class VideoShowcaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'video_preview', 'created_by')
    readonly_fields = ('created_by', 'video_preview')
    
    # Simple video preview
    def video_preview(self, obj):
        if obj.video:
            return format_html('<video width="300" controls><source src="{}"></video>', obj.video.url)
        return "No video"
    video_preview.short_description = "Preview"
    
    # Auto-set creator on save
    def save_model(self, request, obj, form, change):
        if not change:  # Only set creator on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    # Show only own videos to non-superusers
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)
    
    
#-------------------YouTube Videos-------------------------------------------------

admin.register(YouTubeVideo)
