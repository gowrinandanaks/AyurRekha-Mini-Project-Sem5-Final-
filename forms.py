from django import forms
from .models import CommunityBlog, BlogReview, PersonalHealthProfile, HealthDocument, UserProfile

class CommunityBlogForm(forms.ModelForm):
    class Meta:
        model = CommunityBlog
        fields = ['title', 'content', 'image_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter blog title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your content here...'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional image URL'})
        }

class BlogReviewForm(forms.ModelForm):
    class Meta:
        model = BlogReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, str(i)) for i in range(1, 6)], attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your review...'})
        }

class PersonalHealthProfileForm(forms.ModelForm):
    class Meta:
        model = PersonalHealthProfile
        exclude = ['user', 'updated_at']
        widgets = {
            'existing_diseases': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'current_medications': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'previous_surgeries': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'family_medical_history': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class HealthDocumentForm(forms.ModelForm):
    class Meta:
        model = HealthDocument
        fields = ['document_type', 'file', 'notes']
        widgets = {
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional notes'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PractitionerProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'qualification', 'specialization', 'bio', 'profile_photo', 'certificate', 
            'hospital_name', 'hospital_district', 'hospital_place', 'experience_years', 'contact_number',
            'gender', 'date_of_birth', 'gov_id_type', 'gov_id_file',
            'university_name', 'graduation_year', 'internship_certificate',
            'med_reg_number', 'med_council', 'reg_certificate', 'license_validity',
            'previous_hospitals', 'hospital_email', 'hospital_contact', 'consultation_type'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_place': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_district': forms.Select(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gov_id_type': forms.Select(attrs={'class': 'form-control'}),
            'gov_id_file': forms.FileInput(attrs={'class': 'form-control'}),
            
            'university_name': forms.TextInput(attrs={'class': 'form-control'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'internship_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            
            'med_reg_number': forms.TextInput(attrs={'class': 'form-control'}),
            'med_council': forms.TextInput(attrs={'class': 'form-control'}),
            'reg_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'license_validity': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            
            'previous_hospitals': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'hospital_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'hospital_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'consultation_type': forms.Select(attrs={'class': 'form-control'}),
        }
