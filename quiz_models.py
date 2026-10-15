from django.db import models
from django.contrib.auth.models import User

class QuizQuestion(models.Model):
    TOPIC_CHOICES = [
        ('medicine', 'Ayurvedic Medicines & Terms'),
        ('herbs', 'Ayurvedic Herbs & Plants'),
        ('history', 'History of Ayurveda & Vedas'),
        ('yoga', 'Yoga, Asanas, Meditation & Pranayama'),
    ]

    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    hint = models.TextField()
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES)

    def __str__(self):
        return f"[{self.topic}] {self.question_text[:50]}..."

class QuizAttempt(models.Model):
    user_id = models.IntegerField()  # Store User ID directly since it's a separate DB
    score = models.IntegerField()
    total_questions = models.IntegerField(default=5)
    badge_awarded = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} - Score {self.score}/5 at {self.timestamp}"
