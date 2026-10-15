from django.db import models
from django.contrib.auth.models import User
from .quiz_models import QuizQuestion, QuizAttempt


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('practitioner', 'Practitioner'),
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    PROFESSION_CHOICES = [
        ('student', 'Student'),
        ('professional', 'Working Professional'),
        ('homemaker', 'Homemaker'),
        ('retired', 'Retired'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    is_blocked = models.BooleanField(default=False)
    
    # Common profile fields
    age = models.IntegerField(null=True, blank=True)
    profession = models.CharField(max_length=50, choices=PROFESSION_CHOICES, default='other')
    
    # Practitioner specific fields (can be null for others)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False) # For practitioner approval
    
    wake_time_goal = models.TimeField(default="06:00:00")
    current_streak = models.IntegerField(default=0)
    last_processed_date = models.DateField(null=True, blank=True)

    # Kerala Districts
    KERALA_DISTRICTS = [
        ('thiruvananthapuram', 'Thiruvananthapuram'),
        ('kollam', 'Kollam'),
        ('pathanamthitta', 'Pathanamthitta'),
        ('alappuzha', 'Alappuzha'),
        ('kottayam', 'Kottayam'),
        ('idukki', 'Idukki'),
        ('ernakulam', 'Ernakulam'),
        ('thrissur', 'Thrissur'),
        ('palakkad', 'Palakkad'),
        ('malappuram', 'Malappuram'),
        ('kozhikode', 'Kozhikode'),
        ('wayanad', 'Wayanad'),
        ('kannur', 'Kannur'),
        ('kasaragod', 'Kasaragod'),
    ]

    # Additional Practitioner Details
    profile_photo = models.ImageField(upload_to='practitioner_photos/', null=True, blank=True)
    certificate = models.FileField(upload_to='practitioner_certificates/', null=True, blank=True)
    hospital_name = models.CharField(max_length=255, blank=True, null=True)
    hospital_district = models.CharField(max_length=50, choices=KERALA_DISTRICTS, blank=True, null=True)
    hospital_place = models.CharField(max_length=255, blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    
    # --- New Practitioner Fields ---
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    GOV_ID_CHOICES = [
        ('aadhaar', 'Aadhaar Card'),
        ('passport', 'Passport'),
        ('license', 'Driving License'),
    ]
    gov_id_type = models.CharField(max_length=20, choices=GOV_ID_CHOICES, null=True, blank=True)
    gov_id_file = models.FileField(upload_to='practitioner_ids/', null=True, blank=True)
    
    # Education
    university_name = models.CharField(max_length=255, blank=True, null=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    internship_certificate = models.FileField(upload_to='internship_certs/', null=True, blank=True)
    
    # Registration
    med_reg_number = models.CharField(max_length=50, blank=True, null=True)
    med_council = models.CharField(max_length=255, blank=True, null=True)
    reg_certificate = models.FileField(upload_to='reg_certificates/', null=True, blank=True)
    license_validity = models.DateField(null=True, blank=True)
    
    # Professional details
    previous_hospitals = models.TextField(blank=True, null=True, help_text="List previous hospitals/clinics with place and details")
    hospital_email = models.EmailField(blank=True, null=True)
    hospital_contact = models.CharField(max_length=20, blank=True, null=True)
    
    CONSULTATION_CHOICES = [
        ('online', 'Online'),
        ('in_person', 'In-person'),
        ('both', 'Both'),
    ]
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_CHOICES, default='both')
    # ------------------------------

    def __str__(self):
        return f"{self.user.username}'s ({self.role}) Profile"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_patient')
    practitioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_practitioner')
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appt: {self.patient.username} with {self.practitioner.username} on {self.date_time}"


class WellnessContent(models.Model):
    CATEGORY_CHOICES = [
        ('article', 'Article'),
        ('blog', 'Blog'),
        ('tip', 'Wellness Tip'),
        ('remedy', 'Ayurvedic Remedy'),
        ('yoga', 'Yoga & Asana'),
        ('panchakarma', 'Panchakarma'),
    ]
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_practitioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_inappropriate = models.BooleanField(default=False)

    def __str__(self):
        return f"Review by {self.user.username} - Rating: {self.rating}"


class HelpRequest(models.Model):
    programme = models.CharField(max_length=100)
    arrival_date = models.DateField()
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    subscribe = models.BooleanField(default=False)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('spam', 'Spam'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reply_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.surname} - {self.programme}"



class DoshaResult(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vata = models.IntegerField()
    pitta = models.IntegerField()
    kapha = models.IntegerField()
    dominant_dosha = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.dominant_dosha}"


class ChatMessage(models.Model):
    """Stores chat history in database (global storage) for DocAyu chatbot."""
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True)  # For anonymous users
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class DailyRoutine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    completed = models.BooleanField(default=False)
    tips = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    is_timed = models.BooleanField(default=False)
    timer_duration = models.IntegerField(default=0) # in minutes
    last_completed_at = models.DateTimeField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class BadgeRecord(models.Model):
    BADGE_TYPES = [
        ('early_riser', 'Early Riser'),
        ('routine_master', 'Routine Master'),
        ('routine_master_l2', 'Routine Master Level 2'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPES)
    date_earned = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.badge_type} ({self.date_earned})"


class CommunityBlog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_blogs')
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class BlogReview(models.Model):
    blog = models.ForeignKey(CommunityBlog, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.blog.title}"


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    username_attempted = models.CharField(max_length=150, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_successful = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Success" if self.is_successful else "Failed"
        user_str = self.user.username if self.user else self.username_attempted
        return f"{status} Login: {user_str} at {self.timestamp}"

class SystemSettings(models.Model):
    site_name = models.CharField(max_length=100, default='AyurWellness')
    contact_email = models.EmailField(default='admin@ayurwellness.com')
    enable_email_notifications = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"System Settings (Last Updated: {self.updated_at})"

class FAQItem(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    icon_color = models.CharField(max_length=20, default='gold') # gold, blue, red

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} by {self.user.username if self.user else 'System'} at {self.timestamp}"

class HealthRecord(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_records')
    practitioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_health_history')
    blood_pressure = models.CharField(max_length=20, help_text="e.g., 120/80")
    cholesterol = models.CharField(max_length=50, blank=True, null=True)
    physical_pain_details = models.TextField(blank=True, null=True)
    mental_health_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Health Record for {self.patient.username} by {self.practitioner.username}"

class TreatmentRecommendation(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    practitioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_recommendations')
    medicines = models.TextField(help_text="Recommended Ayurvedic medicines")
    therapies = models.TextField(help_text="Recommended Panchakarma therapies")
    yoga_pranayama = models.TextField(help_text="Yoga and pranayama suggestions")
    diet_plan = models.TextField(help_text="Diet plans based on dosha")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.patient.username} by {self.practitioner.username}"

class PatientNote(models.Model):
    practitioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_notes')
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note on {self.patient.username} by {self.practitioner.username}"
class ConsultationMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_consultation_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_consultation_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'Message from {self.sender.username} to {self.recipient.username} at {self.timestamp}'
class PersonalHealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personal_health')
    
    # 1. Basic Health Information
    height = models.FloatField(null=True, blank=True, help_text="in cm")
    weight = models.FloatField(null=True, blank=True, help_text="in kg")
    bmi = models.FloatField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)

    # 2. Vital Signs
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    blood_oxygen = models.IntegerField(null=True, blank=True, help_text="SpO2 %")
    body_temperature = models.FloatField(null=True, blank=True, help_text="in Fahrenheit")
    respiratory_rate = models.IntegerField(null=True, blank=True)

    # 3. Blood Test Reports
    blood_sugar_fasting = models.FloatField(null=True, blank=True)
    blood_sugar_pp = models.FloatField(null=True, blank=True)
    hba1c = models.FloatField(null=True, blank=True)
    total_cholesterol = models.FloatField(null=True, blank=True)
    ldl_cholesterol = models.FloatField(null=True, blank=True)
    hdl_cholesterol = models.FloatField(null=True, blank=True)
    triglycerides = models.FloatField(null=True, blank=True)
    hemoglobin = models.FloatField(null=True, blank=True)

    # 4. Lifestyle Details
    sleep_duration = models.FloatField(null=True, blank=True, help_text="hours per day")
    stress_level = models.IntegerField(null=True, blank=True, help_text="1 to 10 scale")
    physical_activity = models.CharField(max_length=100, blank=True, null=True)
    diet_type = models.CharField(max_length=50, choices=[('vegetarian', 'Vegetarian'), ('non-vegetarian', 'Non-Vegetarian')], blank=True, null=True)
    water_intake = models.FloatField(null=True, blank=True, help_text="liters per day")

    # 5. Medical Information
    existing_diseases = models.TextField(blank=True, null=True, help_text="Diabetes, Hypertension, etc.")
    allergies = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    previous_surgeries = models.TextField(blank=True, null=True)
    family_medical_history = models.TextField(blank=True, null=True)

    # 6. Ayurveda-Specific Details
    dominant_dosha = models.CharField(max_length=50, blank=True, null=True)
    digestion_type = models.CharField(max_length=50, choices=[('strong', 'Strong'), ('medium', 'Medium'), ('weak', 'Weak')], blank=True, null=True)
    body_constitution = models.CharField(max_length=100, blank=True, null=True, help_text="Prakriti")
    current_imbalance = models.CharField(max_length=100, blank=True, null=True, help_text="Vikriti")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Health Profile for {self.user.username}"

class HealthDocument(models.Model):
    DOCUMENT_TYPES = [
        ('lab_report', 'Lab Report'),
        ('prescription', 'Doctor Prescription'),
        ('scan_report', 'Scan Report (ECG, X-Ray etc.)'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='health_documents/')
    notes = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type} for {self.user.username} uploaded on {self.uploaded_at.date()}"
