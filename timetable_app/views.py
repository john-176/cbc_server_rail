from django.shortcuts import render

# Timetable views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Timetable

class TimetableView(APIView):
    def get(self, request, category):
        try:
            obj, _ = Timetable.objects.get_or_create(category=category)
            return Response(obj.data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

    def put(self, request, category):
        try:
            obj, _ = Timetable.objects.get_or_create(category=category)
            obj.data = request.data
            obj.save()
            return Response({'status': 'updated'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class SubjectListView(APIView):
    def get(self, request):
        subjects = [
            "Math", "English", "Science", "Geography",
            "History", "ICT", "Art", "PE", "Kiswahili", "CRE"
        ]
        return Response(subjects)