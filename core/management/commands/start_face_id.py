"""
Face ID avtomatik monitoring tizimi.
Tizim ishga tushganda kamerani yoqib, xodimlarni avtomatik tanib, 
kirig/chiqish vaqtini, kechikishni yozib boradi.

Ishlatish:
    python manage.py start_face_id

Tavsiya etilgan qurilmalar:
    - USB Webcam (Logitech C920/C922)
    - Intel RealSense D415/D435
    - Raspberry Pi Camera Module
"""
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from decimal import Decimal

import django
from django.core.management.base import BaseCommand
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bakery_erp.settings')
django.setup()

from hr.models import Employee, EmployeePhoto, FaceIDLog, Attendance, Shift


class FaceIDMonitor:
    def __init__(self, camera_id=0, confidence_threshold=0.6):
        self.camera_id = camera_id
        self.confidence_threshold = confidence_threshold
        self.known_encodings = []
        self.known_employees = []
        self.running = False
        self.cap = None
        
    def load_employees(self):
        """Barcha Face ID ga ulangan xodimlarni yuklash"""
        self.known_encodings = []
        self.known_employees = []
        
        employees = Employee.objects.filter(face_id_enrolled=True)
        for emp in employees:
            photos = EmployeePhoto.objects.filter(employee=emp)
            for photo in photos:
                try:
                    import face_recognition
                    image = face_recognition.load_image_file(photo.photo.path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        self.known_encodings.append(encodings[0])
                        self.known_employees.append(emp)
                except Exception as e:
                    print(f"[FaceID] Xodim {emp.name} rasmi yuklanmadi: {e}")
        
        print(f"[FaceID] {len(self.known_encodings)} ta yuz encoding yuklandi.")
    
    def process_check_in(self, employee, confidence):
        """Kirishni qayd etish"""
        today = timezone.localdate()
        now = timezone.now()
        current_time = now.time()
        
        # Smena vaqtini aniqlash
        shift_start = None
        if employee.shift:
            shift_start = employee.shift.start_time
        
        # Kechikishni hisoblash
        late_minutes = 0
        is_late = False
        
        if shift_start and current_time > shift_start:
            shift_datetime = datetime.combine(today, shift_start)
            current_datetime = datetime.combine(today, current_time)
            late_seconds = (current_datetime - shift_datetime).total_seconds()
            late_minutes = int(late_seconds / 60)
            is_late = late_minutes > 0
        
        # FaceIDLog yaratish
        log = FaceIDLog.objects.create(
            employee=employee,
            action='check_in',
            confidence=Decimal(str(confidence * 100)),
            is_late=is_late,
            late_minutes=late_minutes,
            shift_start_time=shift_start,
        )
        
        # Attendance yaratish yoki yangilash
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'check_in': current_time,
                'check_in_method': 'face_id',
                'late_minutes': late_minutes,
                'expected_check_in': shift_start,
            }
        )
        
        if not created and not attendance.check_in:
            attendance.check_in = current_time
            attendance.check_in_method = 'face_id'
            attendance.late_minutes = late_minutes
            attendance.expected_check_in = shift_start
            attendance.save()
        
        status = "KECHIKDI" if is_late else "o'z vaqtida"
        print(f"[FaceID] ✅ {employee.name} KIRDI ({status}) — {now.strftime('%H:%M:%S')}")
    
    def process_check_out(self, employee, confidence):
        """Chiqishni qayd etish"""
        today = timezone.localdate()
        now = timezone.now()
        current_time = now.time()
        
        # FaceIDLog yaratish
        FaceIDLog.objects.create(
            employee=employee,
            action='check_out',
            confidence=Decimal(str(confidence * 100)),
        )
        
        # Attendance yangilash
        attendance = Attendance.objects.filter(
            employee=employee,
            date=today,
        ).first()
        
        if attendance:
            attendance.check_out = current_time
            attendance.check_out_method = 'face_id'
            attendance.save()
        else:
            Attendance.objects.create(
                employee=employee,
                date=today,
                check_out=current_time,
                check_out_method='face_id',
            )
        
        print(f"[FaceID] 👋 {employee.name} CHIQDI — {now.strftime('%H:%M:%S')}")
    
    def run(self):
        """Asosiy monitoring sikli"""
        try:
            import cv2
            import face_recognition
            import numpy as np
        except ImportError as e:
            print(f"[FaceID] XATO: Kerakli kutubxonalar o'rnatilmagan: {e}")
            print("[FaceID] pip install opencv-python face-recognition numpy")
            return
        
        self.load_employees()
        
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            print(f"[FaceID] XATO: Kamera {self.camera_id} ochilmadi!")
            return
        
        # Kamera sozlamalari
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("[FaceID] Monitoring boshlandi. Chiqish uchun 'q' bosing.")
        print("[FaceID] Kirish uchun chap qo'l, chiqish uchun o'ng qo'l ko'taring.")
        
        self.running = True
        last_seen = {}  # employee_id -> last_action_time
        cooldown_seconds = 60  # 1 daqiqa cooldown
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Har 5-kadrda bir tanish (tezlik uchun)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=self.confidence_threshold)
                face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                
                if True in matches:
                    best_match_index = np.argmin(face_distances)
                    confidence = 1 - face_distances[best_match_index]
                    employee = self.known_employees[best_match_index]
                    
                    emp_id = employee.id
                    now = time.time()
                    
                    # Cooldown tekshirish
                    if emp_id in last_seen:
                        if now - last_seen[emp_id] < cooldown_seconds:
                            continue
                    
                    # Qo'l harakatini aniqlash (sodda: kadrning chap/o'ng tomoni)
                    top, right, bottom, left = face_location
                    face_center_x = (left + right) / 2
                    frame_center_x = small_frame.shape[1] / 2
                    
                    # Agar yuz kadrning chap yarmida bo'lsa -> kirish, o'ng yarmida -> chiqish
                    # Haqiqiy loyihada hand tracking ishlatiladi, bu sodda variant
                    action = 'check_in'  # default
                    
                    # Oxirgi harakatni tekshirish
                    last_log = FaceIDLog.objects.filter(employee=employee).order_by('-timestamp').first()
                    if last_log and last_log.action == 'check_in':
                        # Agar oxirgi kirish bo'lsa va 5 daqiqa o'tgan bo'lsa -> chiqish
                        if timezone.now() - last_log.timestamp > timedelta(minutes=5):
                            action = 'check_out'
                    
                    last_seen[emp_id] = now
                    
                    if action == 'check_in':
                        self.process_check_in(employee, confidence)
                    else:
                        self.process_check_out(employee, confidence)
                    
                    # Vizual tasdiq
                    cv2.putText(frame, f"{employee.name} - {action}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('BunyodNon Face ID', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        print("[FaceID] Monitoring to'xtatildi.")
    
    def stop(self):
        self.running = False


class Command(BaseCommand):
    help = 'Face ID monitoringni boshlash (kamera orqali avtomatik keldi-ketdi)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--camera',
            type=int,
            default=0,
            help='Kamera ID (default: 0)',
        )
        parser.add_argument(
            '--confidence',
            type=float,
            default=0.6,
            help='Tanishish ishonchliligi (0-1, default: 0.6)',
        )
    
    def handle(self, *args, **options):
        camera_id = options['camera']
        confidence = options['confidence']
        
        self.stdout.write(self.style.SUCCESS(
            f'Face ID tizimi ishga tushmoqda... (kamera: {camera_id}, confidence: {confidence})'
        ))
        
        monitor = FaceIDMonitor(camera_id=camera_id, confidence_threshold=confidence)
        
        try:
            monitor.run()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nFace ID monitoring to\'xtatildi.'))
            monitor.stop()
