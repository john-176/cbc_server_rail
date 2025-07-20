from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Timetable

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['id', 'category']  # you can add more fields if needed