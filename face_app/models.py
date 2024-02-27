from django.db import models
from django.contrib import admin

class Student(models.Model):
    name = models.CharField(max_length=255)
    face_encoding = models.BinaryField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
from django.utils import timezone

class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.name} - {self.timestamp}"
admin.site.register(Student)
admin.site.register(AttendanceRecord)
