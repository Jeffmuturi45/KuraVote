import re
import csv
import io

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinValueValidator, MaxValueValidator,
)

from .models import Student, Election, Position, Candidate


# ═══════════════════════════════════════════════
# REUSABLE WIDGET CLASS CONSTANTS
# ═══════════════════════════════════════════════

_INPUT_LG = 'form-control form-control-lg'
_INPUT = 'form-control'
_SELECT = 'form-select'
_SELECT_LG = 'form-select form-select-lg'
_FILE = 'form-control'
_CHECKBOX = 'form-check-input'


# ═══════════════════════════════════════════════
# 1. STUDENT LOGIN FORM
# ═══════════════════════════════════════════════

class StudentLoginForm(forms.Form):

    admission_number = forms.CharField(
        label='Admission Number',
        # No min_length / max_length here — Django attaches
        # MinLengthValidator / MaxLengthValidator which call len()
        # AFTER clean_admission_number() returns an int → TypeError.
        # All length and range checks live in clean_admission_number().
        widget=forms.TextInput(attrs={
            'class':        _INPUT_LG,
            'placeholder':  'Enter your admission number',
            'autofocus':    True,
            'inputmode':    'numeric',
            'pattern':      '[0-9]*',
            'autocomplete': 'off',
        }),
        error_messages={
            'required': 'Please enter your admission number.',
        }
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class':        _INPUT_LG,
            'placeholder':  'Enter your password',
            'autocomplete': 'current-password',
        }),
        error_messages={
            'required': 'Please enter your password.',
        }
    )

    def clean_admission_number(self):
        value = str(self.cleaned_data.get('admission_number', '')).strip()

        if not value:
            raise ValidationError('Please enter your admission number.')

        if not value.isdigit():
            raise ValidationError(
                'Admission number must contain digits only — '
                'no letters or spaces.'
            )

        if len(value) > 10:
            raise ValidationError(
                'Admission number cannot exceed 10 digits.'
            )

        val = int(value)

        if val <= 0:
            raise ValidationError(
                'Admission number must be a positive number.'
            )

        return val   # return int — views.py passes this to authenticate()

    def clean_password(self):
        value = self.cleaned_data.get('password', '')
        if len(value) > 128:
            raise ValidationError('Password is too long.')
        return value


# ═══════════════════════════════════════════════
# 2. FORCE PASSWORD CHANGE FORM (first login)
# ═══════════════════════════════════════════════

class ForcePasswordChangeForm(forms.Form):

    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class':        _INPUT_LG,
            'placeholder':  'Enter new password',
            'autocomplete': 'new-password',
        }),
        error_messages={
            'required': 'Please enter a new password.',
        }
    )

    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class':        _INPUT_LG,
            'placeholder':  'Confirm new password',
            'autocomplete': 'new-password',
        }),
        error_messages={
            'required': 'Please confirm your password.',
        }
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1', '')
        if len(password) < 6:
            raise ValidationError(
                'Password must be at least 6 characters long.'
            )
        if len(password) > 128:
            raise ValidationError('Password is too long.')
        return password

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get('new_password1')
        password2 = cleaned.get('new_password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    'Passwords do not match. Please try again.'
                )

        return cleaned


# ═══════════════════════════════════════════════
# 3. CSV UPLOAD FORM
# ═══════════════════════════════════════════════

class CSVUploadForm(forms.Form):

    csv_file = forms.FileField(
        label='Select CSV File',
        widget=forms.FileInput(attrs={
            'class':  _FILE,
            'accept': '.csv',
        }),
        error_messages={
            'required': 'Please select a CSV file to upload.',
        }
    )

    def clean_csv_file(self):
        file = self.cleaned_data.get('csv_file')

        if not file:
            raise ValidationError('No file was uploaded.')

        # Extension check
        if not file.name.lower().endswith('.csv'):
            raise ValidationError(
                'Invalid file type. Please upload a .csv file only.'
            )

        # Max 20 MB
        if file.size > 20 * 1024 * 1024:
            raise ValidationError(
                'File is too large. Maximum size is 20MB. '
                'Split your CSV into smaller files.'
            )

        # Minimum — catch empty uploads
        if file.size < 10:
            raise ValidationError('File appears to be empty.')

        # Peek at headers before the view processes rows
        try:
            content = file.read(1024).decode('utf-8')
            file.seek(0)
            first_line = content.split('\n')[0].strip().lower()
            required = {
                'admission_number', 'first_name', 'last_name', 'email'
            }
            found = {h.strip() for h in first_line.split(',')}
            missing = required - found
            if missing:
                raise ValidationError(
                    f'Missing required columns: '
                    f'{", ".join(sorted(missing))}. '
                    f'Expected: admission_number, first_name, '
                    f'last_name, email'
                )
        except UnicodeDecodeError:
            raise ValidationError(
                'File encoding error. Please save your CSV '
                'as UTF-8 and try again.'
            )

        return file


# ═══════════════════════════════════════════════
# 4. ELECTION FORM
# ═══════════════════════════════════════════════

class ElectionForm(forms.ModelForm):

    class Meta:
        model = Election
        fields = [
            'election_name', 'start_date',
            'end_date', 'status', 'announcement'
        ]
        widgets = {
            'election_name': forms.TextInput(attrs={
                'class':       _INPUT,
                'placeholder': 'e.g. Student Council Elections 2025',
            }),
            'start_date': forms.DateTimeInput(
                attrs={'class': _INPUT, 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_date': forms.DateTimeInput(
                attrs={'class': _INPUT, 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'status': forms.Select(attrs={
                'class': _SELECT,
            }),
            'announcement': forms.Textarea(attrs={
                'class':       _INPUT,
                'rows':        3,
                'placeholder': 'e.g. Voting closes at 5PM today. '
                               'Make sure to cast your vote!',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_date'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean_election_name(self):
        name = self.cleaned_data.get('election_name', '').strip()
        if len(name) < 5:
            raise ValidationError(
                'Election name must be at least 5 characters.'
            )
        if re.search(r'[<>{}]', name):
            raise ValidationError(
                'Election name contains invalid characters.'
            )
        return name

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get('start_date')
        end_date = cleaned.get('end_date')

        if start_date and end_date:
            if end_date <= start_date:
                raise ValidationError(
                    'End date must be after the start date.'
                )
            if (end_date - start_date).days > 30:
                raise ValidationError(
                    'Election cannot last longer than 30 days.'
                )

        return cleaned


# ═══════════════════════════════════════════════
# 5. POSITION FORM
# ═══════════════════════════════════════════════

class PositionForm(forms.ModelForm):

    class Meta:
        model = Position
        fields = ['election', 'position_name', 'max_votes']
        widgets = {
            'election': forms.Select(attrs={
                'class': _SELECT,
            }),
            'position_name': forms.TextInput(attrs={
                'class':       _INPUT,
                'placeholder': 'e.g. President, Secretary, Treasurer',
            }),
            'max_votes': forms.NumberInput(attrs={
                'class': _INPUT,
                'min':   '1',
                'max':   '10',
            }),
        }

    def clean_position_name(self):
        name = self.cleaned_data.get('position_name', '').strip()
        if len(name) < 3:
            raise ValidationError(
                'Position name must be at least 3 characters.'
            )
        if re.search(r'[<>{}]', name):
            raise ValidationError(
                'Position name contains invalid characters.'
            )
        return name

    def clean_max_votes(self):
        max_votes = self.cleaned_data.get('max_votes', 1)
        if max_votes < 1:
            raise ValidationError('Max votes must be at least 1.')
        if max_votes > 10:
            raise ValidationError('Max votes cannot exceed 10.')
        return max_votes


# ═══════════════════════════════════════════════
# 6. CANDIDATE FORM
# ═══════════════════════════════════════════════

class CandidateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ['student', 'position', 'manifesto', 'photo']
        widgets = {
            'student': forms.Select(attrs={
                'class': _SELECT,
            }),
            'position': forms.Select(attrs={
                'class': _SELECT,
            }),
            'manifesto': forms.Textarea(attrs={
                'class':       _INPUT,
                'rows':        4,
                'placeholder': 'Enter candidate manifesto '
                               '(max 500 characters)',
                'maxlength':   500,
            }),
            'photo': forms.FileInput(attrs={
                'class':  _FILE,
                'accept': 'image/jpeg,image/png',
            }),
        }

    def clean_manifesto(self):
        manifesto = self.cleaned_data.get('manifesto', '').strip()
        if len(manifesto) > 500:
            raise ValidationError(
                'Manifesto cannot exceed 500 characters.'
            )
        if re.search(
            r'<script|javascript:|on\w+=', manifesto, re.IGNORECASE
        ):
            raise ValidationError(
                'Manifesto contains invalid content.'
            )
        return manifesto

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 2 * 1024 * 1024:
                raise ValidationError(
                    'Photo too large. Maximum size is 2MB.'
                )
            ext = photo.name.rsplit('.', 1)[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                raise ValidationError(
                    'Only JPG and PNG photos are allowed.'
                )
            if hasattr(photo, 'content_type'):
                if photo.content_type not in (
                    'image/jpeg', 'image/png'
                ):
                    raise ValidationError(
                        'Invalid image format. '
                        'Only JPG and PNG are accepted.'
                    )
        return photo

    def clean(self):
        cleaned = super().clean()
        student = cleaned.get('student')
        position = cleaned.get('position')

        if student and position:
            qs = Candidate.objects.filter(
                student=student, position=position
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    f'{student.get_full_name()} is already registered '
                    f'as a candidate for {position.position_name}.'
                )
            if not student.is_active:
                raise ValidationError(
                    f'{student.get_full_name()} is deactivated and '
                    f'cannot be registered as a candidate.'
                )

        return cleaned


# ═══════════════════════════════════════════════
# 7. STUDENT PROFILE PASSWORD CHANGE FORM
# ═══════════════════════════════════════════════

class StudentPasswordChangeForm(forms.Form):

    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class':        _INPUT,
            'placeholder':  'Enter current password',
            'autocomplete': 'current-password',
        }),
        error_messages={
            'required': 'Please enter your current password.',
        }
    )

    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class':        _INPUT,
            'placeholder':  'Enter new password',
            'autocomplete': 'new-password',
        }),
        error_messages={
            'required': 'Please enter a new password.',
        }
    )

    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class':        _INPUT,
            'placeholder':  'Confirm new password',
            'autocomplete': 'new-password',
        }),
        error_messages={
            'required': 'Please confirm your new password.',
        }
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get('current_password')
        if not self.user.check_password(current):
            raise ValidationError('Current password is incorrect.')
        return current

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get('new_password1')
        password2 = cleaned.get('new_password2')

        if password1 and password2:
            if password1 != password2:
                raise ValidationError('New passwords do not match.')
            if len(password1) < 6:
                raise ValidationError(
                    'Password must be at least 6 characters.'
                )

        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.password_changed = True
        self.user.save()


# ═══════════════════════════════════════════════
# 8. STUDENT EDIT FORM (admin)
# ═══════════════════════════════════════════════

class StudentEditForm(forms.ModelForm):

    class Meta:
        model = Student
        # NEVER include is_staff / is_superuser / password
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': _INPUT}),
            'last_name':  forms.TextInput(attrs={'class': _INPUT}),
            'email':      forms.EmailInput(attrs={'class': _INPUT}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        qs = Student.objects.filter(email=email).exclude(
            pk=self.instance.pk
        )
        if qs.exists():
            raise ValidationError(
                'That email is already used by another student.'
            )
        return email
