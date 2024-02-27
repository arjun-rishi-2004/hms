import face_recognition
import cv2
import numpy as np
from django.shortcuts import render, redirect
from .models import Student,AttendanceRecord
from datetime import timedelta,datetime
import winsound

def home(r):
    return redirect('/')
def register_face(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        # Capture image from webcam
        video_capture = cv2.VideoCapture(0)
        ret, frame = video_capture.read()
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        if face_encodings:
            face_encoding = face_encodings[0]
            # Save face encoding to database
            student = Student.objects.create(name=name, face_encoding=face_encoding.tobytes())
            student.save()

        # Display the frame with face rectangle
        while True:
            cv2.imshow('Register Face', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Press 'q' to quit
                break
            elif key == ord('c'):  # Press 'c' to capture image
                break

        video_capture.release()
        cv2.destroyAllWindows()
        return render(request, 'register_face.html')
    return render(request, 'register_face.html')


from django.shortcuts import render
from django.utils import timezone


def start_face_recognition(request):
    video_capture = cv2.VideoCapture(0)
    recognized_students = {}
    while True:
        ret, frame = video_capture.read()
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            matched = False
            # Compare face encoding with registered face encodings
            students = Student.objects.all()
            for student in students:
                registered_face_encoding = np.frombuffer(student.face_encoding, dtype=np.float64)
                match = face_recognition.compare_faces([registered_face_encoding], face_encoding)
                if match[0]:
                    matched = True
                    # Check if student has already been recognized in the last 5 seconds
                    if student.id not in recognized_students or (datetime.now() - recognized_students[student.id]) > timedelta(seconds=5):
                        # Display name and timestamp
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.putText(frame, student.name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        # Store attendance record
                        AttendanceRecord.objects.create(student=student, timestamp=datetime.now())
                        recognized_students[student.id] = datetime.now()
                    break
            if not matched:
                # Display red box for unregistered face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                winsound.Beep(1000, 500)  # Play beep sound (1000 Hz for 500 ms)

        # Display the frame with recognized faces
        cv2.imshow('Video', frame)
        # Break the loop on key combination press (Ctrl + C)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv2.destroyAllWindows()
    return redirect('/')


from .models import Student, AttendanceRecord

def display_attendance(request):
    # Fetch attendance records
    attendance_records = AttendanceRecord.objects.all()
    # Fetch registered students
    registered_students = Student.objects.all()
    return render(request, 'display_attendance.html', {'attendance_records': attendance_records, 'registered_students': registered_students})

def welcome(request):
    return render(request, 'welcome.html')
def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Simple check for username and password
        if username == 'admin' and password == 'admin123':
            # Set a session variable to indicate the user is logged in
            request.session['admin_logged_in'] = True
            return redirect('admin_panel')
        else:
            # Add error message for incorrect login
            return render(request, 'welcome.html', {'error_message': 'Invalid username or password.'})
    return redirect('welcome')

def admin_panel(request):
    return render(request, 'admin_panel.html')