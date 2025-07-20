from django.contrib import admin, auth
from django.urls import path

# urls.py
from django.urls import path
from .views import TimetableView, SubjectListView

urlpatterns = [
    path('timetable/<str:category>/', TimetableView.as_view(), name='timetable'),
    path('timetable/subjects/', SubjectListView.as_view(), name='subject-list'),
    
   # path('whoami/', views.whoami_view, name='api-whoami'),
    ]
