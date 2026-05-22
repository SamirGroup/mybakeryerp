"""
Face ID monitoring daemon - doimiy ishlab turuvchi xizmat
Tizim avtomatik kamerani topib, xodimlarni tanib, keldi-ketdi qayd etadi.

Ishlatish:
    python manage.py face_id_daemon

Tavsiya:
    - Systemd yoki supervisor orqali doimiy ishga tushiring
    - Railway/Render'da background worker sifatida ishlatiladi
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
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bakery_erp.settings')
django.setup()

from hr.models import Employee, EmployeePhoto, FaceIDLog, Attendance, Shift
from core.models import CameraDevice, FaceIDSession


class FaceIDDaemon:
    """Face ID monitoring daemon - doimiy ishlaydigan xizmat"""
    
    def __init__(self, confidence_threshold=0.6):
        self.confidence_threshold = confidence_threshold
        self.known_encodings = []
        self.known_employees = []
        self.running = False
        self.current_session = None
        self.camera = None
        
    def load_employees(self):
        """Barcha Face ID ga ulangan xodimlarni yuklash"""
        self.known_encodings = []
        self.known_employees = []
        
        try:
            import face_recognition
        except ImportError:
            print("[FaceID] XATO: face_recognition kutubxonasi o'rnatilmagan")
            return False
            
        employees = Employee.objects.filter(face_id_enrolled=True)
        for emp in employees:
            photos = EmployeePhoto.objects.filter(employee=emp)
            for photo in photos:
                try:
                    image = face_recognition.load_image_file(photo.photo.path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        self.known_encodings.append(encodings[0])
                        self.known_employees.append(emp)
                except Exception as e:
                    print(f"[FaceID] Xodim {emp.name} rasmi yuklanmadi: {e}")
        
        print(f"[FaceID] {len(self.known_encodings)} ta yuz encoding yuklandi.")
        return True
    
    def start_session(self):
        """Yangi sessiyani boshlash"""
        # Asosiy kamerani topish
        self.camera = CameraDevice.objects.filter(is_default=True).first()
        if not self.camera:
            self.camera = CameraDevice.objects.filter(is_active=True).first()
        
        if not self.camera:
            print("[FaceID] XATO: Hech qanday faol kamera topilmadi")
            return False
        
        # Faol sessiya yo'qligini tekshirish
        existing = FaceIDSession.objects.filter(is_running=True).first()
        if existing:
            print(f"[FaceID] Boshqa sessiya allaqachon ishlayapti: ID {existing.id}")
            self.current_session = existing
            return True
        
        # Yangi sessiya yaratish
        self.current_session = FaceIDSession.objects.create(
            camera=self.camera,
            is_running=True,
            started_at=timezone.now(),
        )
        
        self.camera.last_used = timezone.now()
        self.camera.save()
        
        print(f"[FaceID] Sessiya boshlandi: ID {self.current_session.id}, Kamera: {self.camera.name}")
        return True
    
    def stop_session(self):
        """Sessiyani to'xtatish"""
        if self.current_session:
            self.current_session.is_running = False
            self.current_session.stopped_at = timezone.now()
            self.current_session.save()
            print(f"[FaceID] Sessiya to'xtatildi: ID {self.current_session.id}")
            self.current_session = None
    
    def process_check_in(self, employee, confidence):
        """Kirishni qayd etish"""
        today = timezone.localdate()
        now = timezone.now()
        current_time = now.time()
        
        with transaction.atomic():
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
                },
            )
            
            if not created and not attendance.check_in:
                attendance.check_in = current_time
                attendance.check_in_method = 'face_id'
                attendance.late_minutes = late_minutes
                attendance.expected_check_in = shift_start
                attendance.save()
            
            # Session statistikasini yangilash
            if self.current_session:
                FaceIDSession.objects.filter(id=self.current_session.id).update(
                    total_check_ins=self.current_session.total_check_ins + 1,
                    last_employee_seen=employee,
                )
                self.current_session.total_check_ins += 1
            
            status = "KECHIKDI" if is_late else "o'z vaqtida"
            print(f"[FaceID] ✅ {employee.name} KIRDI ({status}) — {now.strftime('%H:%M:%S')}")
    
    def process_check_out(self, employee, confidence):
        """Chiqishni qayd etish"""
        today = timezone.localdate()
        now = timezone.now()
        current_time = now.time()
        
        with transaction.atomic():
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
            
            # Session statistikasini yangilash
            if self.current_session:
                FaceIDSession.objects.filter(id=self.current_session.id).update(
                    total_check_outs=self.current_session.total_check_outs + 1,
                    last_employee_seen=employee,
                )
                self.current_session.total_check_outs += 1
            
            print(f"[FaceID] 👋 {employee.name} CHIQDI — {now.strftime('%H:%M:%S')}")
    
    def run(self):
        """Asosiy daemon sikli"""
        try:
            import cv2
            import face_recognition
            import numpy as np
        except ImportError as e:
            print(f"[FaceID] XATO: Kerakli kutubxonalar o'rnatilmagan: {e}")
            print("[FaceID] pip install opencv-python face-recognition numpy")
            return
        
        # Sessiyani boshlash
        if not self.start_session():
            return
        
        # Xodimlarni yuklash
        if not self.load_employees():
            return
        
        # Kamerani ochish
        self.cap = cv2.VideoCapture(self.camera.camera_id)
        if not self.cap.isOpened():
            print(f"[FaceID] XATO: Kamera {self.camera.camera_id} ochilmadi!")
            self.stop_session()
            return
        
        # Kamera sozlamalari
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("[FaceID] Monitoring boshlandi. Chiqish uchun Ctrl+C bosing.")
        print("[FaceID] Kirish uchun chap qo'l, chiqish uchun o'ng qo'l ko'taring.")
        
        self.running = True
        last_seen = {}  # employee_id -> last_action_time
        cooldown_seconds = 60  # 1 daqiqa cooldown
        
        try:
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
                    matches = face_recognition.compare_faces(
                        self.known_encodings, 
                        face_encoding, 
                        tolerance=self.confidence_threshold
                    )
                    face_distances = face_recognition.face_distance(
                        self.known_encodings, 
                        face_encoding
                    )
                    
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
                        
                        # Kirish/chiqish aniqlash
                        top, right, bottom, left = face_location
                        face_center_x = (left + right) / 2
                        frame_center_x = small_frame.shape[1] / 2
                        
                        # Oxirgi harakatni tekshirish
                        last_log = FaceIDLog.objects.filter(
                            employee=employee
                        ).order_by('-timestamp').first()
                        
                        action = 'check_in'
                        if last_log and last_log.action == 'check_in':
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
            
        except KeyboardInterrupt:
            print("\n[FaceID] Foydalanuvchi to'xtatdi")
        
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            self.stop_session()
            print("[FaceID] Monitoring to'xtatildi.")
    
    def stop(self):
        self.running = False


class Command(BaseCommand):
    help = 'Face ID daemonni ishga tushirish (doimiy monitoring)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--confidence',
            type=float,
            default=0.6,
            help='Tanishish ishonchliligi (0-1, default: 0.6)',
        )
    
    def handle(self, *args, **options):
        confidence = options['confidence']
        
        self.stdout.write(self.style.SUCCESS(
            f'Face ID daemon ishga tushmoqda... (confidence: {confidence})'
        ))
        
        daemon = FaceIDDaemon(confidence_threshold=confidence)
        
        try:
            daemon.run()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nFace ID daemon to\'xtatildi.'))
            daemon.stop()
