from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('send-otp/', views.send_otp, name='send_otp'),
    path('help/', views.help_view, name='help'),
    path('doshatest/', views.doshatest_view, name='doshatest'),
    path('history/', views.history_view, name='history'),
    path('nature/', views.nature_view, name='nature'),
    path('yoga/', views.yoga_view, name='yoga'),
    path('yogasana/', views.yogasana_view, name='yogasana'),
    path('therapies/', views.therapies_view, name='therapies'),
    path('guide/', views.guide_view, name='guide'),
    path('guide/herbs/', views.herbs_view, name='guide_herbs'),
    path('guide/daily-routine/', views.daily_routine_view, name='guide_routine'),
    path('guide/diet-nutrition/', views.diet_nutrition_view, name='guide_diet'),
    path('guide/doshas/', views.doshas_view, name='guide_doshas'),
    path('guide/six-tastes/', views.six_tastes_view, name='guide_tastes'),
    path('guide/seasonal/', views.seasonal_guide_view, name='guide_seasonal'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('save-dosha/', views.save_dosha_result, name='save_dosha'),
    path('chat/', views.chat_api, name='chat'),
    path('chat/history/', views.chat_history_api, name='chat_history'),
    path('quiz/check/', views.check_quiz_eligibility, name='quiz_check'),
    path('quiz/questions/', views.get_quiz_questions, name='quiz_questions'),
    path('quiz/submit/', views.submit_quiz, name='quiz_submit'),
    path('routine/', views.get_routines, name='get_routines'),
    path('routine/save/', views.save_routine, name='save_routine'),
    path('routine/toggle/<int:routine_id>/', views.toggle_routine, name='toggle_routine'),
    path('routine/delete/<int:routine_id>/', views.delete_routine, name='delete_routine'),
    path('routine/update-time/', views.update_routine_time, name='update_routine_time'),
    path('profile/', views.get_profile, name='get_profile'),
    path('demo-password-reset/', views.demo_password_reset_view, name='demo_password_reset'),
    path('demo-password-reset-confirm/<int:user_id>/', views.demo_password_reset_confirm_view, name='demo_password_reset_confirm'),
    path('wellness-consultation/', views.wellness_consultation_view, name='wellness_consultation'),
    path('routine/achievements/', views.get_achievements, name='get_achievements'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='ayu/password_reset_form.html',
            email_template_name='ayu/password_reset_email.txt',
            subject_template_name='ayu/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='ayu/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='ayu/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path('reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='ayu/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),

    # Admin Portal URLs
    path('admin-portal/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-portal/login-history/', views.admin_login_history_view, name='admin_login_history'),
    path('admin-portal/users/', views.admin_user_list_view, name='admin_user_list'),
    path('admin-portal/practitioners/', views.admin_practitioner_list_view, name='admin_practitioner_list'),
    path('admin-portal/user/add/', views.admin_add_user_view, name='admin_add_user'),
    path('admin-portal/user/update/<int:user_id>/', views.admin_update_user_view, name='admin_update_user'),
    path('admin-portal/user/delete/<int:user_id>/', views.admin_delete_user_view, name='admin_delete_user'),
    path('admin-portal/user/toggle-block/<int:user_id>/', views.admin_toggle_block_view, name='admin_toggle_block_user'),
    path('admin-portal/practitioner/approve/<int:user_id>/', views.admin_approve_practitioner_view, name='admin_approve_practitioner'),
    path('admin-portal/practitioner/<int:user_id>/', views.admin_practitioner_detail_view, name='admin_practitioner_detail'),
    path('admin-portal/appointments/', views.admin_appointment_list_view, name='admin_appointment_list'),
    path('admin-portal/appointment/add/', views.admin_add_appointment_view, name='admin_add_appointment'),
    path('admin-portal/appointment/update-status/<int:appt_id>/<str:status>/', views.admin_update_appointment_status_view, name='admin_update_appointment_status'),
    path('admin-portal/health-analysis/', views.admin_dosha_analysis_view, name='admin_dosha_analysis'),
    path('admin-portal/content/', views.admin_content_list_view, name='admin_content_list'),
    path('admin-portal/content/add/', views.admin_add_content_view, name='admin_add_content'),
    path('admin-portal/content/edit/<int:content_id>/', views.admin_edit_content_view, name='admin_edit_content'),
    path('admin-portal/content/delete/<int:content_id>/', views.admin_delete_content_view, name='admin_delete_content'),
    path('admin-portal/blog/delete/<int:blog_id>/', views.admin_delete_blog_view, name='admin_delete_blog'),
    path('admin-portal/feedback/', views.admin_feedback_list_view, name='admin_feedback_list'),
    path('admin-portal/help/', views.admin_help_requests_view, name='admin_help_list'),
    path('admin-portal/help/reply/<int:req_id>/', views.admin_reply_help_view, name='admin_reply_help'),
    path('admin-portal/help/resolve/<int:req_id>/', views.admin_resolve_help_view, name='admin_resolve_help'),
    path('admin-portal/help/spam/<int:req_id>/', views.admin_spam_help_view, name='admin_spam_help'),
    path('admin-portal/settings/', views.admin_settings_view, name='admin_settings'),
    
    # Practitioner Portal URLs
    path('practitioner/', views.practitioner_dashboard_view, name='practitioner_dashboard'),
    path('practitioner/patients/', views.practitioner_patient_list_view, name='practitioner_patient_list'),
    path('practitioner/patients/<int:patient_id>/', views.practitioner_patient_detail_view, name='practitioner_patient_detail'),
    path('practitioner/consultations/', views.practitioner_consultations_view, name='practitioner_consultations'),
    path('practitioner/analytics/', views.practitioner_analytics_view, name='practitioner_analytics'),
    path('practitioner/settings/', views.practitioner_settings_view, name='practitioner_settings'),
    path('my-recommendations/', views.patient_recommendations_view, name='my_recommendations'),
    path('practitioners/', views.practitioner_directory_view, name='practitioner_directory'),
    path('practitioner/<int:practitioner_id>/', views.user_practitioner_detail_view, name='user_practitioner_detail'),
    path('book-appointment/<int:practitioner_id>/', views.book_appointment_view, name='book_appointment'),
    path('my-appointments/', views.patient_appointments_view, name='patient_appointments'),
    path('practitioner/appointments/', views.practitioner_appointments_view, name='practitioner_appointments'),
    path('practitioner/appointments/<int:appointment_id>/status/', views.update_appointment_status_view, name='update_appointment_status'),
    path('consultation-chat/<int:other_user_id>/', views.consultation_chat_view, name='consultation_chat'),
    path('api/send-consultation-message/<int:recipient_id>/', views.send_consultation_message_api, name='send_consultation_message_api'),
    path('export-report/<int:patient_id>/', views.export_health_report_view, name='export_health_report'),

    # Health Tracking System URLs
    path('health/profile/update/', views.update_health_profile_view, name='update_health_profile'),
    path('health/document/upload/', views.upload_health_document_view, name='upload_health_document'),
    path('health/document/delete/<int:doc_id>/', views.delete_health_document_view, name='delete_health_document'),

    # Community Blogs URLs
    path('community-blogs/', views.community_blogs_view, name='community_blogs'),
    path('community-blogs/create/', views.create_blog_view, name='create_blog'),
    path('community-blogs/<int:blog_id>/', views.blog_detail_view, name='blog_detail'),

    # Profile Update URL
    path('update-profile/', views.update_profile_api, name='update_profile'),
]




