from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta, date, datetime
import random
import json
import io
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa

from ayurwellness.models import (
    HelpRequest, DoshaResult, ChatMessage, QuizQuestion, 
    QuizAttempt, DailyRoutine, UserProfile, BadgeRecord, 
    Appointment, WellnessContent, Feedback, LoginHistory,
    CommunityBlog, BlogReview, SystemSettings, FAQItem, ActivityLog,
    HealthRecord, TreatmentRecommendation, PatientNote, ConsultationMessage,
    PersonalHealthProfile, HealthDocument
)
from ayurwellness.forms import CommunityBlogForm, BlogReviewForm, PersonalHealthProfileForm, HealthDocumentForm, PractitionerProfileForm
from ayurwellness.ayurveda_chatbot import get_ayurveda_response

# --- Helper Functions ---

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def is_admin(user):
    return user.is_superuser

def is_practitioner(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'practitioner'

# --- Core Authentication Views ---

def home(request):
    return render(request, 'ayu/home.html')

def therapies_view(request):
    return render(request, 'ayu/therapies.html')

def guide_view(request):
    return render(request, 'ayu/guide.html')

def herbs_view(request):
    return render(request, 'ayu/herbs.html')

def daily_routine_view(request):
    return render(request, 'ayu/daily-routine.html')

def diet_nutrition_view(request):
    return render(request, 'ayu/diet-and-nutrition.html')

def doshas_view(request):
    return render(request, 'ayu/doshas.html')

def six_tastes_view(request):
    return render(request, 'ayu/six-tastes.html')

def seasonal_guide_view(request):
    return render(request, 'ayu/seasonal-guide.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        role = request.POST.get('role', 'patient')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('home')

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Username or Email already exists!")
            return redirect('home')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            if role == 'admin':
                user.is_superuser = True
                user.is_staff = True
            user.save()

            # Create/Update UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            
            if role == 'practitioner':
                profile.qualification = request.POST.get('qualification')
                profile.specialization = request.POST.get('specialization')
                profile.hospital_name = request.POST.get('hospital_name')
                profile.hospital_district = request.POST.get('hospital_district')
                profile.hospital_place = request.POST.get('hospital_place')
                profile.experience_years = int(request.POST.get('experience') or 0)
                profile.contact_number = request.POST.get('contact_number')
                profile.bio = request.POST.get('bio')
                
                if 'profile_photo' in request.FILES:
                    profile.profile_photo = request.FILES['profile_photo']
                if 'certificates' in request.FILES:
                    profile.certificate = request.FILES['certificates']
                
                profile.is_approved = False  # Practitioners need admin approval
            
            profile.save()
            
            login(request, user)
            ActivityLog.objects.create(user=user, action=f"registered as a {role}", icon_color='blue')
            messages.success(request, f"Registration successful! Welcome, {username}.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error saving to database: {e}")
            return redirect('home')

    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                LoginHistory.objects.create(username_attempted=email, ip_address=get_client_ip(request), is_successful=False)
                messages.error(request, "This email is not registered.")
                return redirect('home')
            
            username = user_obj.username
        except Exception as e:
            messages.error(request, "An error occurred during login. Please try again.")
            return redirect('home')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            LoginHistory.objects.create(user=user, username_attempted=email, ip_address=get_client_ip(request), is_successful=True)
            ActivityLog.objects.create(user=user, action="logged in", icon_color='blue')
            login(request, user)
            
            if request.POST.get('remember_me'):
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)
                
            messages.success(request, f"Welcome back, {username}!")
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            if user.is_superuser:
                return redirect('admin_dashboard')
            if is_practitioner(user):
                return redirect('practitioner_dashboard')
            return redirect('dashboard')
        else:
            LoginHistory.objects.create(user=user_obj, username_attempted=email, ip_address=get_client_ip(request), is_successful=False)
            messages.error(request, "Incorrect password.")
            return redirect('home')

    next_param = request.GET.get('next', '')
    if next_param:
        return redirect(reverse('home') + f'?next={next_param}')
    return redirect('home')

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

def demo_password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            return redirect('demo_password_reset_confirm', user_id=user.id)
        else:
            messages.error(request, "This email is not associated with any account.")
    return render(request, 'ayu/demo_password_reset.html')

def demo_password_reset_confirm_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            user.set_password(password)
            user.save()
            messages.success(request, "Password has been reset successfully. You can now login.")
            return redirect('home')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'ayu/demo_password_reset_confirm.html', {'user_to_reset': user})

@login_required
def patient_recommendations_view(request):
    recommendations = TreatmentRecommendation.objects.filter(patient=request.user).order_by('-created_at')
    return render(request, 'ayu/user_recommendations.html', {'recommendations': recommendations})

@login_required
def practitioner_directory_view(request):
    # Only show practitioners who are approved
    practitioners = UserProfile.objects.filter(role='practitioner', is_approved=True).select_related('user')
    return render(request, 'ayu/practitioner_directory.html', {'practitioners': practitioners})

@login_required
def user_practitioner_detail_view(request, practitioner_id):
    practitioner_user = get_object_or_404(User, id=practitioner_id, profile__role='practitioner', profile__is_approved=True)
    return render(request, 'ayu/user_practitioner_detail.html', {'practitioner': practitioner_user})

@login_required
def book_appointment_view(request, practitioner_id):
    practitioner_user = get_object_or_404(User, id=practitioner_id, profile__role='practitioner')
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        notes = request.POST.get('notes')
        
        try:
            # Combine date and time
            dt_str = f"{date_str} {time_str}"
            appointment_dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
            
            Appointment.objects.create(
                patient=request.user,
                practitioner=practitioner_user,
                date_time=appointment_dt,
                notes=notes,
                status='pending'
            )
            messages.success(request, f"Appointment request sent to Dr. {practitioner_user.username}. Please wait for approval.")
            return redirect('patient_appointments')
        except Exception as e:
            messages.error(request, f"Error booking appointment: {e}")
            
    return render(request, 'ayu/book_appointment.html', {'practitioner': practitioner_user})

@login_required
def patient_appointments_view(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-date_time')
    return render(request, 'ayu/patient_appointments.html', {'appointments': appointments})

@login_required
@user_passes_test(is_practitioner)
def practitioner_appointments_view(request):
    appointments = Appointment.objects.filter(practitioner=request.user).order_by('-date_time')
    return render(request, 'ayu/practitioner_appointments.html', {'appointments': appointments})

@login_required
@user_passes_test(is_practitioner)
def update_appointment_status_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, practitioner=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['approved', 'cancelled']:
            appointment.status = new_status
            appointment.save()
            messages.success(request, f"Appointment status updated to {new_status}.")
            
            # Log activity
            ActivityLog.objects.create(
                user=request.user,
                action=f"{new_status} an appointment",
                details=f"Patient: {appointment.patient.username} on {appointment.date_time}",
                icon_color='green' if new_status == 'approved' else 'red'
            )
            
    return redirect('practitioner_appointments')

@login_required
def export_health_report_view(request, patient_id):
    patient = get_object_or_404(User, id=patient_id)
    
    # Check permissions: only the patient themselves or an approved practitioner can export
    is_patient = request.user == patient
    is_doc = UserProfile.objects.filter(user=request.user, role='practitioner', is_approved=True).exists()
    
    if not (is_patient or is_doc):
        messages.error(request, "You do not have permission to export this report.")
        return redirect('dashboard')

    # Fetch data
    dosha = DoshaResult.objects.filter(user=patient).first()
    records = HealthRecord.objects.filter(patient=patient).order_by('-created_at')[:10]
    recommendations = TreatmentRecommendation.objects.filter(patient=patient).order_by('-created_at')[:5]
    
    # Render template to HTML
    template = get_template('ayu/report_template.html')
    context = {
        'patient': patient,
        'practitioner': request.user if is_doc else None, # Simplified
        'dosha': dosha,
        'records': records,
        'recommendations': recommendations,
        'today': timezone.now(),
    }
    html = template.render(context)
    
    # Create PDF
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="AyurRekha_Report_{patient.username}.pdf"'
        return response
        
    return HttpResponse("Error generating PDF", status=500)

@login_required
def consultation_chat_view(request, other_user_id):
    other_user = get_object_or_404(User, id=other_user_id)
    
    # Check if a chat is allowed (e.g., they have/had an appointment)
    # For now, let's keep it simple and allow any patient-practitioner pair
    
    messages_qs = ConsultationMessage.objects.filter(
        (models.Q(sender=request.user) & models.Q(recipient=other_user)) |
        (models.Q(sender=other_user) & models.Q(recipient=request.user))
    ).order_by('timestamp')
    
    # Mark incoming messages as read
    ConsultationMessage.objects.filter(sender=other_user, recipient=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'ayu/consultation_chat.html', {
        'other_user': other_user,
        'chat_messages': messages_qs
    })

@login_required
def send_consultation_message_api(request, recipient_id):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            content = body.get('content', '').strip()
            if not content:
                return JsonResponse({'error': 'Message content is required'}, status=400)
            
            recipient = get_object_or_404(User, id=recipient_id)
            
            msg = ConsultationMessage.objects.create(
                sender=request.user,
                recipient=recipient,
                content=content
            )
            
            return JsonResponse({
                'id': msg.id,
                'content': msg.content,
                'timestamp': msg.timestamp.strftime('%H:%M'),
                'sender': msg.sender.username
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# --- Basic Website Views ---

def help_view(request):
    if request.method == 'POST':
        try:
            HelpRequest.objects.create(
                programme=request.POST.get('programme'),
                arrival_date=request.POST.get('arrival'),
                first_name=request.POST.get('firstname'),
                surname=request.POST.get('surname'),
                email=request.POST.get('email'),
                telephone=request.POST.get('telephone'),
                country=request.POST.get('country'),
                message=request.POST.get('message'),
                subscribe=request.POST.get('subscribe') == 'on'
            )
            messages.success(request, "Your help request has been sent successfully!")
            return redirect('help')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('help')
    return render(request, 'ayu/help.html')

def doshatest_view(request): return render(request, 'ayu/doshatest.html')
def nature_view(request): return render(request, 'ayu/nature.html')
def yoga_view(request): return render(request, 'ayu/yoga.html')
def yogasana_view(request): return render(request, 'ayu/yogasana.html')
def history_view(request): return render(request, 'ayu/history.html')

@login_required
def wellness_consultation_view(request):
    """View to display the comprehensive wellness consultation page for patients."""
    if is_practitioner(request.user):
        return redirect('practitioner_dashboard')
        
    result = DoshaResult.objects.filter(user=request.user).first()
    health_profile, _ = PersonalHealthProfile.objects.get_or_create(user=request.user)
    health_documents = HealthDocument.objects.filter(user=request.user).order_by('-uploaded_at')
    
    # Get latest health record and recommendation
    latest_record = HealthRecord.objects.filter(patient=request.user).order_by('-created_at').first()
    latest_recommendation = TreatmentRecommendation.objects.filter(patient=request.user).order_by('-created_at').first()
    
    context = {
        'result': result,
        'health_profile': health_profile,
        'health_documents': health_documents,
        'latest_record': latest_record,
        'latest_recommendation': latest_recommendation,
        'today': timezone.now().date(),
    }
    return render(request, 'ayu/wellness_consultation.html', context)

@login_required
@require_POST
def update_profile_api(request):
    try:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        
        # Handle both JSON and Form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        # Handle field updates
        if 'age' in data:
            profile.age = int(data.get('age')) if data.get('age') else None
        if 'profession' in data:
            profile.profession = data.get('profession')
        if 'wake_time_goal' in data:
            profile.wake_time_goal = data.get('wake_time_goal')
            
        # Handle photo upload
        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']
            
        # Handle photo deletion
        if data.get('delete_photo') == 'true':
            if profile.profile_photo:
                profile.profile_photo.delete(save=False)
                profile.profile_photo = None
                
        profile.save()

        # Seed routines if this is a new profile completion
        if not DailyRoutine.objects.filter(user=request.user).exists():
            seed_personalized_routines(request.user, profile.profession)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Profile updated successfully',
            'age': profile.age,
            'profession': profile.get_profession_display() if hasattr(profile, 'get_profession_display') else profile.profession,
            'photo_url': profile.profile_photo.url if profile.profile_photo else None
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def dashboard_view(request):
    if is_practitioner(request.user):
        return redirect('practitioner_dashboard')
    
    # Process streak and routine resets
    process_eod_logic(request.user)
    
    result = DoshaResult.objects.filter(user=request.user).first()
    quiz_attempts = QuizAttempt.objects.filter(user_id=request.user.id).order_by('-timestamp')
    help_requests = HelpRequest.objects.filter(email=request.user.email).order_by('-created_at')
    
    # Health Tracking System Data
    health_profile, _ = PersonalHealthProfile.objects.get_or_create(user=request.user)
    health_documents = HealthDocument.objects.filter(user=request.user).order_by('-uploaded_at')
    
    context = {
        "result": result, 
        "quiz_attempts": quiz_attempts,
        "help_requests": help_requests,
        "health_profile": health_profile,
        "health_documents": health_documents,
        "health_form": PersonalHealthProfileForm(instance=health_profile),
        "doc_form": HealthDocumentForm(),
        "profile": UserProfile.objects.filter(user=request.user).first(),
    }
    return render(request, "ayu/dashboard.html", context)

@login_required
@csrf_exempt
def save_dosha_result(request):
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    if request.method == "POST":
        try:
            scores = {"Vata": int(request.POST.get("vata")), "Pitta": int(request.POST.get("pitta")), "Kapha": int(request.POST.get("kapha"))}
            dominant = max(scores, key=scores.get)
            DoshaResult.objects.update_or_create(user=request.user, defaults={**{k.lower(): v for k, v in scores.items()}, "dominant_dosha": dominant})
            if is_ajax: return JsonResponse({"success": True})
        except:
            if is_ajax: return JsonResponse({"success": False}, status=400)
    return redirect("dashboard")

# --- Health Tracking Views ---

@login_required
def update_health_profile_view(request):
    if request.method == 'POST':
        profile, _ = PersonalHealthProfile.objects.get_or_create(user=request.user)
        form = PersonalHealthProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Health profile updated successfully.")
        else:
            messages.error(request, "Error updating health profile.")
    return redirect('dashboard')

@login_required
def upload_health_document_view(request):
    if request.method == 'POST':
        form = HealthDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()
            messages.success(request, "Document uploaded successfully.")
        else:
            messages.error(request, "Error uploading document.")
    return redirect('dashboard')

@login_required
def delete_health_document_view(request, doc_id):
    doc = get_object_or_404(HealthDocument, id=doc_id, user=request.user)
    doc.delete()
    messages.success(request, "Document deleted.")
    return redirect('dashboard')

# --- API & Chat Views ---

def _get_chat_identifier(request):
    if request.user.is_authenticated: return ('user', request.user)
    # Create session if it doesn't exist
    if not request.session.session_key:
        request.session.create()
    return ('session', request.session.session_key)

@login_required
def chat_history_api(request):
    id_type, identifier = _get_chat_identifier(request)
    messages_qs = ChatMessage.objects.filter(user=identifier if id_type == 'user' else None, session_key='' if id_type == 'user' else identifier).order_by('created_at')[:50]
    return JsonResponse({'messages': [{'role': m.role, 'content': m.content, 'created_at': m.created_at.isoformat()} for m in messages_qs]})

@login_required
def chat_api(request):
    if request.method != 'POST': return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        body = json.loads(request.body)
        user_message = body.get('message', '').strip()
        if not user_message: return JsonResponse({'error': 'Message required'}, status=400)
        id_type, identifier = _get_chat_identifier(request)
        user_obj = identifier if id_type == 'user' else None
        session_key = identifier if id_type == 'session' else ''
        ChatMessage.objects.create(user=user_obj, session_key=session_key, role='user', content=user_message)
        recent = ChatMessage.objects.filter(user=user_obj, session_key=session_key).order_by('-created_at')[:10]
        response_content = get_ayurveda_response(user_message, [{'role': m.role, 'content': m.content} for m in reversed(list(recent))])
        ChatMessage.objects.create(user=user_obj, session_key=session_key, role='assistant', content=response_content)
        return JsonResponse({'message': response_content})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def check_quiz_eligibility(request):
    last = QuizAttempt.objects.filter(user_id=request.user.id).order_by('-timestamp').first()
    if last and timezone.now() < last.timestamp + timedelta(days=3):
        return JsonResponse({'eligible': False, 'message': "Available in 3 days."})
    return JsonResponse({'eligible': True})

@login_required
def get_quiz_questions(request):
    questions = list(QuizQuestion.objects.all())
    if len(questions) < 5: return JsonResponse({'error': 'Not enough questions'}, status=500)
    data = [{'id': q.id, 'question': q.question_text, 'options': {'A': q.option_a, 'B': q.option_b, 'C': q.option_c, 'D': q.option_d}, 'hint': q.hint} for q in random.sample(questions, 5)]
    return JsonResponse({'questions': data})

@login_required
@csrf_exempt
def submit_quiz(request):
    if request.method != 'POST': return JsonResponse({'error': 'Method not allowed'}, status=405)
    answers = json.loads(request.body).get('answers', {})
    score = sum(1 for q_id, ans in answers.items() if QuizQuestion.objects.filter(id=q_id, correct_answer=ans).exists())
    badge = "Golden" if score == 5 else "Blue" if score == 4 else "Green" if score == 3 else None
    QuizAttempt.objects.create(user_id=request.user.id, score=score, total_questions=5, badge_awarded=badge)
    return JsonResponse({'score': score, 'badge': badge})

# --- Routine & Profile Views ---

@login_required
def get_routines(request):
    routines = DailyRoutine.objects.filter(user=request.user).order_by('created_at')
    return JsonResponse({'routines': [{
        'id': r.id, 
        'title': r.title, 
        'icon': r.icon, 
        'completed': r.completed, 
        'tips': r.tips, 
        'instructions': r.instructions, 
        'is_timed': r.is_timed, 
        'timer_duration': r.timer_duration,
        'scheduled_time': r.scheduled_time.strftime("%H:%M") if r.scheduled_time else None
    } for r in routines]})

@login_required
@csrf_exempt
def save_routine(request):
    data = json.loads(request.body)
    routine_id = data.get('id')
    if routine_id:
        r = get_object_or_404(DailyRoutine, id=routine_id, user=request.user)
        r.title = data.get('title', r.title); r.icon = data.get('icon', r.icon); r.tips = data.get('tips', r.tips); r.instructions = data.get('instructions', r.instructions)
        r.is_timed = data.get('is_timed', r.is_timed); r.timer_duration = data.get('timer_duration', r.timer_duration)
        if 'scheduled_time' in data: r.scheduled_time = data.get('scheduled_time') if data.get('scheduled_time') else None
        r.save()
    else:
        r = DailyRoutine.objects.create(user=request.user, title=data.get('title'), icon=data.get('icon'), tips=data.get('tips', ''), instructions=data.get('instructions', ''), is_timed=data.get('is_timed', False), timer_duration=data.get('timer_duration', 0), scheduled_time=data.get('scheduled_time') if data.get('scheduled_time') else None)
    return JsonResponse({'status': 'success', 'id': r.id})

@login_required
@csrf_exempt
def update_routine_time(request):
    data = json.loads(request.body)
    r = get_object_or_404(DailyRoutine, id=data.get('id'), user=request.user)
    r.scheduled_time = data.get('scheduled_time') if data.get('scheduled_time') else None
    r.save()
    return JsonResponse({'status': 'success'})

@login_required
@csrf_exempt
def toggle_routine(request, routine_id):
    r = get_object_or_404(DailyRoutine, id=routine_id, user=request.user)
    r.completed = not r.completed
    if r.completed:
        r.last_completed_at = timezone.now()
    r.save()
    return JsonResponse({'status': 'success', 'completed': r.completed})

@login_required
@csrf_exempt
def delete_routine(request, routine_id):
    get_object_or_404(DailyRoutine, id=routine_id, user=request.user).delete()
    return JsonResponse({'status': 'success'})

@login_required
def get_profile(request):
    p, _ = UserProfile.objects.get_or_create(user=request.user)
    return JsonResponse({'age': p.age, 'profession': p.profession, 'wake_time_goal': p.wake_time_goal.strftime("%H:%M") if p.wake_time_goal else "06:00", 'streak': p.current_streak})


def seed_personalized_routines(user, profession):
    for r in [{"title": "Morning Flow", "icon": "fa-sun"}, {"title": "Herbal Tea", "icon": "fa-mug-hot"}]: 
        DailyRoutine.objects.get_or_create(user=user, title=r['title'], defaults={'icon': r['icon']})

def process_eod_logic(user):
    """
    Main logic for streak calculation and daily routine resets.
    Ensures that streaks are handled based on consecutive days and
    routines are reset only for a new calendar day.
    """
    p, _ = UserProfile.objects.get_or_create(user=user)
    today = date.today()
    
    # If we've already processed for today, skip
    if p.last_processed_date == today:
        return
    
    # If this is the first time processing, just set the date
    if p.last_processed_date is None:
        p.last_processed_date = today
        p.save()
        return

    yesterday = today - timedelta(days=1)
    routines = DailyRoutine.objects.filter(user=user)
    
    # If the user logged in yesterday, we are processing work done on that day
    if p.last_processed_date == yesterday:
        # Check if the goals were met yesterday (5+ routines completed)
        if routines.filter(completed=True).count() >= 5:
            p.current_streak += 1
        else:
            p.current_streak = 0
    else:
        # More than one day has passed (gap), so the streak is broken
        p.current_streak = 0
    
    # Update baseline for the new day
    p.last_processed_date = today
    p.save()
    
    # Reset routine completion status for the new day
    routines.update(completed=False)

@login_required
def get_achievements(request):
    p, _ = UserProfile.objects.get_or_create(user=request.user); process_eod_logic(request.user)
    return JsonResponse({'streak': p.current_streak, 'badges': list(BadgeRecord.objects.filter(user=request.user).values('badge_type', 'date_earned'))})

# --- Community Blog Views ---

def community_blogs_view(request):
    blogs = CommunityBlog.objects.all().order_by('-created_at')
    return render(request, 'ayu/community_blogs.html', {'blogs': blogs})

@login_required
def create_blog_view(request):
    if request.method == 'POST':
        f = CommunityBlogForm(request.POST)
        if f.is_valid():
            b = f.save(commit=False); b.author = request.user; b.save()
            ActivityLog.objects.create(user=request.user, action="published a new blog", details=f"Title: {b.title}", icon_color='gold')
            messages.success(request, "Blog published."); return redirect('community_blogs')
    return render(request, 'ayu/create_blog.html', {'form': CommunityBlogForm()})

def blog_detail_view(request, blog_id):
    b = get_object_or_404(CommunityBlog, id=blog_id)
    if request.method == 'POST':
        if not request.user.is_authenticated: return redirect('login')
        f = BlogReviewForm(request.POST)
        if f.is_valid():
            r = f.save(commit=False); r.blog = b; r.user = request.user; r.save()
            messages.success(request, "Review added."); return redirect('blog_detail', blog_id=b.id)
    return render(request, 'ayu/blog_detail.html', {'blog': b, 'reviews': b.reviews.all().order_by('-created_at'), 'review_form': BlogReviewForm()})

# --- Admin Portal Views ---

@user_passes_test(is_admin)
def admin_dashboard_view(request):
    context = {
        'total_users': User.objects.count(),
        'total_practitioners': UserProfile.objects.filter(role='practitioner').count(),
        'pending_approvals': UserProfile.objects.filter(role='practitioner', is_approved=False).count(),
        'appointments_today': Appointment.objects.filter(date_time__date=date.today()).count(),
        'recent_users': User.objects.all().order_by('-date_joined')[:10],
        'activity_logs': ActivityLog.objects.all().order_by('-timestamp')[:5]
    }
    return render(request, 'ayu/admin_dashboard.html', context)

@login_required
@user_passes_test(is_practitioner)
def practitioner_dashboard_view(request):
    # Fetch stats for the practitioner
    appointments = Appointment.objects.filter(practitioner=request.user).order_by('-date_time')
    # Get distinct patients who have appointments with this practitioner
    patients_count = User.objects.filter(appointments_as_patient__practitioner=request.user).distinct().count()
    
    context = {
        'total_appointments': appointments.count(),
        'total_patients': patients_count,
        'upcoming_appointments': appointments.filter(date_time__gte=timezone.now(), status='approved')[:5],
        'recent_appointments': appointments[:10],
    }
    return render(request, 'ayu/practitioner_dashboard.html', context)

@login_required
@user_passes_test(is_practitioner)
def practitioner_consultations_view(request):
    # Get patients who have chat messages with this practitioner
    messages_sent = ConsultationMessage.objects.filter(sender=request.user).values_list('recipient', flat=True)
    messages_received = ConsultationMessage.objects.filter(recipient=request.user).values_list('sender', flat=True)
    patient_ids = set(list(messages_sent) + list(messages_received))
    
    patients = User.objects.filter(id__in=patient_ids, profile__role='patient').distinct()
    
    # Also include patients who have appointments but no chat yet
    appointment_patients = User.objects.filter(appointments_as_patient__practitioner=request.user).distinct()
    
    all_patients = (patients | appointment_patients).distinct()

    return render(request, 'ayu/practitioner_consultations.html', {'patients': all_patients})

@login_required
@user_passes_test(is_practitioner)
def practitioner_analytics_view(request):
    appointments = Appointment.objects.filter(practitioner=request.user)
    total_appointments = appointments.count()
    completed_appointments = appointments.filter(status='completed').count()
    pending_appointments = appointments.filter(status='pending').count()
    cancelled_appointments = appointments.filter(status='cancelled').count()
    
    # Get patient count per district (for patients linked to this practitioner)
    patient_ids = appointments.values_list('patient', flat=True).distinct()
    # Note: UserProfile doesn't have district, but UserProfile of practitioners does. 
    # Let's just do appointment status split for now.
    
    context = {
        'total_appointments': total_appointments,
        'completed': completed_appointments,
        'pending': pending_appointments,
        'cancelled': cancelled_appointments,
    }
    return render(request, 'ayu/practitioner_analytics.html', context)

@login_required
@user_passes_test(is_practitioner)
def practitioner_settings_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = PractitionerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Professional profile updated successfully.")
            return redirect('practitioner_dashboard')
    else:
        form = PractitionerProfileForm(instance=profile)
    
    return render(request, 'ayu/practitioner_settings.html', {'form': form})

@login_required
@user_passes_test(is_practitioner)
def practitioner_patient_list_view(request):
    query = request.GET.get('q', '')
    if query:
        patients = User.objects.filter(
            models.Q(username__icontains=query) | 
            models.Q(email__icontains=query) |
            models.Q(id__icontains=query),
            profile__role__in=['patient', 'user']
        ).distinct()
    else:
        patients = User.objects.filter(
            appointments_as_patient__practitioner=request.user,
            profile__role__in=['patient', 'user']
        ).distinct()
        
    return render(request, 'ayu/patient_list.html', {'patients': patients, 'query': query})

@login_required
@user_passes_test(is_practitioner)
def practitioner_patient_detail_view(request, patient_id):
    patient = get_object_or_404(User, id=patient_id, profile__role__in=['patient', 'user'])
    
    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        if action_type == 'add_record':
            HealthRecord.objects.create(
                patient=patient,
                practitioner=request.user,
                blood_pressure=request.POST.get('blood_pressure'),
                cholesterol=request.POST.get('cholesterol'),
                physical_pain_details=request.POST.get('physical_pain'),
                mental_health_notes=request.POST.get('mental_health')
            )
            messages.success(request, "Health record added.")
        elif action_type == 'add_note':
            PatientNote.objects.create(
                practitioner=request.user,
                patient=patient,
                note=request.POST.get('note')
            )
            messages.success(request, "Clinician note saved.")
        elif action_type == 'add_recommendation':
            TreatmentRecommendation.objects.create(
                patient=patient,
                practitioner=request.user,
                medicines=request.POST.get('medicines'),
                therapies=request.POST.get('therapies'),
                yoga_pranayama=request.POST.get('yoga'),
                diet_plan=request.POST.get('diet')
            )
            messages.success(request, "Treatment recommendation updated.")
        return redirect('practitioner_patient_detail', patient_id=patient.id)

    appointments = Appointment.objects.filter(patient=patient, practitioner=request.user).order_by('-date_time')
    health_records = HealthRecord.objects.filter(patient=patient, practitioner=request.user).order_by('-created_at')
    dosha_result = DoshaResult.objects.filter(user=patient).first()
    notes = PatientNote.objects.filter(patient=patient, practitioner=request.user).order_by('-created_at')
    recommendations = TreatmentRecommendation.objects.filter(patient=patient, practitioner=request.user).order_by('-created_at')
    
    # Patient-reported data
    health_profile, _ = PersonalHealthProfile.objects.get_or_create(user=patient)
    health_documents = HealthDocument.objects.filter(user=patient).order_by('-uploaded_at')

    context = {
        'patient': patient,
        'appointments': appointments,
        'health_records': health_records,
        'dosha_result': dosha_result,
        'notes': notes,
        'recommendations': recommendations,
        'health_profile': health_profile,
        'health_documents': health_documents,
    }
    return render(request, 'ayu/patient_detail.html', context)

@user_passes_test(is_admin)
def admin_practitioner_detail_view(request, user_id):
    """View full biodata of a practitioner and allow admin updates."""
    practitioner_user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=practitioner_user, role='practitioner')
    
    if request.method == 'POST' and 'update_profile' in request.POST:
        form = PractitionerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action=f"updated practitioner profile for {practitioner_user.username}",
                details="Admin directly modified practitioner details.",
                icon_color='blue'
            )
            messages.success(request, f"Practitioner details for {practitioner_user.username} have been updated successfully.")
            return redirect('admin_practitioner_detail', user_id=user_id)
        else:
            messages.error(request, "There was an error updating the profile. Please check the form.")
    else:
        form = PractitionerProfileForm(instance=profile)

    appointments = Appointment.objects.filter(practitioner=practitioner_user).order_by('-date_time')
    return render(request, 'ayu/admin_practitioner_detail.html', {
        'practitioner': practitioner_user,
        'profile': profile,
        'form': form,
        'appointments': appointments,
        'total_appointments': appointments.count(),
        'total_patients': User.objects.filter(appointments_as_patient__practitioner=practitioner_user).distinct().count(),
    })

@user_passes_test(is_admin)
def admin_approve_practitioner_view(request, user_id):
    """Approve or reject a practitioner application."""
    profile = get_object_or_404(UserProfile, user_id=user_id, role='practitioner')
    action = request.POST.get('action', 'approve') if request.method == 'POST' else request.GET.get('action', 'approve')
    
    if action == 'reject':
        profile.is_approved = False
        profile.save()
        ActivityLog.objects.create(
            user=request.user,
            action=f"rejected practitioner application for {profile.user.username}",
            icon_color='red'
        )
        messages.warning(request, f"Practitioner {profile.user.username} has been rejected.")
    else:
        profile.is_approved = True
        profile.save()
        ActivityLog.objects.create(
            user=request.user,
            action=f"approved practitioner {profile.user.username}",
            details=f"Specialization: {profile.specialization or 'N/A'}",
            icon_color='green'
        )
        messages.success(request, f"Practitioner {profile.user.username} is now approved and active!")

    return redirect('admin_practitioner_detail', user_id=user_id)

@user_passes_test(is_admin)
def admin_login_history_view(request):
    return render(request, 'ayu/admin_login_history.html', {'logs': LoginHistory.objects.all().order_by('-timestamp').select_related('user')})

@user_passes_test(is_admin)
def admin_user_list_view(request):
    return render(request, 'ayu/admin_user_list.html', {'users': User.objects.all().order_by('-date_joined')})

@user_passes_test(is_admin)
def admin_add_user_view(request):
    r = request.GET.get('role', 'patient')
    if request.method == 'POST':
        try:
            u = User.objects.create_user(username=request.POST.get('username'), email=request.POST.get('email'), password=request.POST.get('password'))
            p, _ = UserProfile.objects.get_or_create(user=u)
            p.role = request.POST.get('role', 'patient'); p.age = int(request.POST.get('age') or 0); p.profession = request.POST.get('profession')
            if p.role == 'practitioner':
                p.qualification = request.POST.get('qualification')
                p.specialization = request.POST.get('specialization')
                p.is_approved = request.POST.get('is_approved') == 'on'
                p.hospital_name = request.POST.get('hospital_name')
                p.hospital_district = request.POST.get('hospital_district')
                p.hospital_place = request.POST.get('hospital_place')
                try:
                    p.experience_years = int(request.POST.get('experience_years') or 0)
                except ValueError:
                    p.experience_years = 0
                if 'profile_photo' in request.FILES:
                    p.profile_photo = request.FILES['profile_photo']
                if 'certificate' in request.FILES:
                    p.certificate = request.FILES['certificate']
            p.save()
            if p.role == 'patient': seed_personalized_routines(u, p.profession)
            messages.success(request, f"User {u.username} added."); return redirect('admin_practitioner_list' if p.role == 'practitioner' else 'admin_user_list')
        except Exception as e: messages.error(request, f"Error: {e}")
    return render(request, 'ayu/admin_user_form.html', {'action': 'Add', 'role': r})

@user_passes_test(is_admin)
def admin_content_list_view(request):
    contents = list(WellnessContent.objects.all())
    blogs = list(CommunityBlog.objects.all())
    all_content = sorted(contents + blogs, key=lambda x: x.created_at, reverse=True)
    return render(request, 'ayu/admin_content_list.html', {'contents': all_content})

@user_passes_test(is_admin)
def admin_add_content_view(request):
    if request.method == 'POST':
        c = WellnessContent.objects.create(title=request.POST.get('title'), category=request.POST.get('category'), content=request.POST.get('content'), author=request.user, is_published=request.POST.get('is_published') == 'on')
        ActivityLog.objects.create(user=request.user, action="added a new article", details=f"Title: {c.title}", icon_color='gold')
        messages.success(request, "Content added."); return redirect('admin_content_list')
    return render(request, 'ayu/admin_content_form.html', {'action': 'Add'})

@user_passes_test(is_admin)
def admin_edit_content_view(request, content_id):
    c = get_object_or_404(WellnessContent, id=content_id)
    if request.method == 'POST':
        c.title = request.POST.get('title'); c.category = request.POST.get('category'); c.content = request.POST.get('content'); c.is_published = request.POST.get('is_published') == 'on'; c.save()
        ActivityLog.objects.create(user=request.user, action="updated an article", details=f"Title: {c.title}", icon_color='blue')
        messages.success(request, "Content updated."); return redirect('admin_content_list')
    return render(request, 'ayu/admin_content_form.html', {'action': 'Edit', 'content_obj': c})

@user_passes_test(is_admin)
def admin_delete_content_view(request, content_id):
    c = get_object_or_404(WellnessContent, id=content_id)
    ActivityLog.objects.create(user=request.user, action="deleted an article", details=f"Title: {c.title}", icon_color='red')
    c.delete()
    messages.success(request, "Content deleted."); return redirect('admin_content_list')

@user_passes_test(is_admin)
def admin_delete_blog_view(request, blog_id):
    b = get_object_or_404(CommunityBlog, id=blog_id)
    ActivityLog.objects.create(user=request.user, action="deleted a community blog", details=f"Title: {b.title}", icon_color='red')
    b.delete()
    messages.success(request, "Blog deleted."); return redirect('admin_content_list')

@user_passes_test(is_admin)
def admin_feedback_list_view(request):
    return render(request, 'ayu/admin_feedback_list.html', {'feedbacks': Feedback.objects.all().order_by('-created_at').select_related('user', 'target_practitioner')})

@user_passes_test(is_admin)
def admin_help_requests_view(request):
    return render(request, 'ayu/admin_help_list.html', {'requests': HelpRequest.objects.all().order_by('-created_at')})

@user_passes_test(is_admin)
def admin_reply_help_view(request, req_id):
    r = get_object_or_404(HelpRequest, id=req_id)
    if request.method == 'POST':
        r.reply_message = request.POST.get('reply_message'); r.status = 'resolved'; r.save()
        messages.success(request, f"Replied to {r.first_name}."); return redirect('admin_help_list')
    return redirect('admin_help_list')

@user_passes_test(is_admin)
def admin_resolve_help_view(request, req_id):
    r = get_object_or_404(HelpRequest, id=req_id); r.status = 'resolved'; r.save()
    messages.success(request, "Resolved."); return redirect('admin_help_list')

@user_passes_test(is_admin)
def admin_spam_help_view(request, req_id):
    r = get_object_or_404(HelpRequest, id=req_id); r.status = 'spam'; r.save()
    messages.success(request, "Marked as spam."); return redirect('admin_help_list')

@user_passes_test(is_admin)
def admin_settings_view(request):
    s, _ = SystemSettings.objects.get_or_create(id=1); f = FAQItem.objects.all()
    if request.method == 'POST':
        if 'update_settings' in request.POST:
            s.site_name = request.POST.get('site_name'); s.contact_email = request.POST.get('contact_email'); s.enable_email_notifications = request.POST.get('enable_notifications') == 'on'; s.maintenance_mode = request.POST.get('maintenance_mode') == 'on'; s.save()
            messages.success(request, "Settings updated.")
        elif 'add_faq' in request.POST:
            q = request.POST.get('question'); a = request.POST.get('answer')
            if q and a: FAQItem.objects.create(question=q, answer=a); messages.success(request, "FAQ added.")
        return redirect('admin_settings')
    return render(request, 'ayu/admin_settings.html', {'settings': s, 'faqs': f})

@user_passes_test(is_admin)
def admin_update_user_view(request, user_id):
    u = get_object_or_404(User, id=user_id); p, _ = UserProfile.objects.get_or_create(user=u)
    if request.method == 'POST':
        u.username = request.POST.get('username'); u.email = request.POST.get('email'); u.save()
        p.age = int(request.POST.get('age') or p.age); p.profession = request.POST.get('profession', p.profession)
        if p.role == 'practitioner':
            p.qualification = request.POST.get('qualification')
            p.specialization = request.POST.get('specialization')
            p.is_approved = request.POST.get('is_approved') == 'on'
            p.hospital_name = request.POST.get('hospital_name')
            p.hospital_district = request.POST.get('hospital_district')
            p.hospital_place = request.POST.get('hospital_place')
            try:
                p.experience_years = int(request.POST.get('experience_years') or 0)
            except ValueError:
                p.experience_years = 0
            if 'profile_photo' in request.FILES:
                p.profile_photo = request.FILES['profile_photo']
            if 'certificate' in request.FILES:
                p.certificate = request.FILES['certificate']
        p.save(); messages.success(request, "User updated."); return redirect('admin_practitioner_list' if p.role == 'practitioner' else 'admin_user_list')
    return render(request, 'ayu/admin_user_form.html', {'action': 'Update', 'user_obj': u, 'role': p.role})

@user_passes_test(is_admin)
def admin_delete_user_view(request, user_id):
    u = get_object_or_404(User, id=user_id)
    if not u.is_superuser: u.delete(); messages.success(request, "User deleted.")
    else: messages.error(request, "Cannot delete superuser.")
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def admin_practitioner_list_view(request):
    status_filter = request.GET.get('status', 'all')
    practitioners = UserProfile.objects.filter(role='practitioner').select_related('user')
    
    if status_filter == 'pending':
        practitioners = practitioners.filter(is_approved=False)
    elif status_filter == 'approved':
        practitioners = practitioners.filter(is_approved=True)
    
    return render(request, 'ayu/admin_practitioner_list.html', {
        'practitioners': practitioners,
        'status_filter': status_filter,
    })


@user_passes_test(is_admin)
def admin_toggle_block_view(request, user_id):
    p = get_object_or_404(UserProfile, user_id=user_id); p.is_blocked = not p.is_blocked; p.save()
    ActivityLog.objects.create(user=request.user, action=f"{'blocked' if p.is_blocked else 'unblocked'} user", details=f"Username: {p.user.username}", icon_color='red' if p.is_blocked else 'blue')
    messages.success(request, f"User {'blocked' if p.is_blocked else 'unblocked'}."); return redirect('admin_user_list')


@user_passes_test(is_admin)
def admin_appointment_list_view(request):
    return render(request, 'ayu/admin_appointment_list.html', {'appointments': Appointment.objects.all().order_by('-date_time').select_related('patient', 'practitioner')})

@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    if request.method == 'POST':
        try:
            pt = User.objects.get(id=request.POST.get('patient')); pr = User.objects.get(id=request.POST.get('practitioner'))
            a = Appointment.objects.create(patient=pt, practitioner=pr, date_time=datetime.fromisoformat(request.POST.get('date_time').replace("T", " ")), status=request.POST.get('status', 'pending'), notes=request.POST.get('notes', ''))
            ActivityLog.objects.create(user=request.user, action="created a new appointment", details=f"Patient: {pt.username}, Practitioner: {pr.username}", icon_color='gold')
            messages.success(request, "Appointment created."); return redirect('admin_appointment_list')
        except Exception as e: messages.error(request, f"Error: {e}")
    return render(request, 'ayu/admin_appointment_form.html', {'patients': User.objects.filter(profile__role='patient'), 'practitioners': User.objects.filter(profile__role='practitioner')})

@user_passes_test(is_admin)
def admin_update_appointment_status_view(request, appt_id, status):
    a = get_object_or_404(Appointment, id=appt_id); a.status = status; a.save()
    ActivityLog.objects.create(user=request.user, action=f"updated appointment status to {status}", details=f"Appt ID: {a.id}, Patient: {a.patient.username}", icon_color='blue' if status != 'cancelled' else 'red')
    messages.success(request, f"Status updated to {status}."); return redirect('admin_appointment_list')

@user_passes_test(is_admin)
def admin_dosha_analysis_view(request):
    rs = DoshaResult.objects.all()
    return render(request, 'ayu/admin_dosha_analysis.html', {'results': rs[:20], 'chart_data': {'Vata': sum(r.vata for r in rs), 'Pitta': sum(r.pitta for r in rs), 'Kapha': sum(r.kapha for r in rs)}, 'total_assessments': rs.count()})
