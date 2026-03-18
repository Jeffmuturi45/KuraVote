from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from .models import Election, Position, Candidate

Student = get_user_model()


# ── 1. Student Login Form ─────────────────────────────────
class StudentLoginForm(forms.Form):

    admission_number = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'Enter your admission number',
            'autofocus':   True,
        }),
        label='Admission Number'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'Enter your password',
        }),
        label='Password'
    )


# ── 2. Force Password Change Form ────────────────────────
class ForcePasswordChangeForm(forms.Form):

    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'Enter new password',
        })
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control form-control-lg',
            'placeholder': 'Confirm new password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')

        if p1 and p2:
            # Passwords must match
            if p1 != p2:
                raise forms.ValidationError(
                    'Passwords do not match. Please try again.'
                )
            # Minimum length
            if len(p1) < 6:
                raise forms.ValidationError(
                    'Password must be at least 6 characters long.'
                )
            # Cannot use admission number as password
        return cleaned_data


# ── 3. CSV Upload Form ────────────────────────────────────
class CSVUploadForm(forms.Form):

    csv_file = forms.FileField(
        label='Select CSV File',
        widget=forms.FileInput(attrs={
            'class':  'form-control',
            'accept': '.csv',
        })
    )

    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']

        # Must be a .csv file
        if not file.name.endswith('.csv'):
            raise forms.ValidationError(
                'Invalid file type. Please upload a .csv file only.'
            )
        # Max file size 5MB
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                'File too large. Maximum size is 5MB.'
            )
        return file


# ── 4. Election Form ──────────────────────────────────────
class ElectionForm(forms.ModelForm):

    class Meta:
        model = Election
        fields = ['election_name', 'start_date',
                  'end_date', 'status', 'announcement']
        widgets = {
            'election_name': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'e.g. Student Council Elections 2025',
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type':  'datetime-local',
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type':  'datetime-local',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'announcement': forms.Textarea(attrs={
                'class':       'form-control',
                'rows':        3,
                'placeholder': 'e.g. Voting closes at 5PM today. '
                'Make sure to cast your vote!',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')

        if start and end:
            if end <= start:
                raise forms.ValidationError(
                    'End date must be after the start date.'
                )
        return cleaned_data


# ── 5. Position Form ──────────────────────────────────────
class PositionForm(forms.ModelForm):

    class Meta:
        model = Position
        fields = ['election', 'position_name', 'max_votes']
        widgets = {
            'election': forms.Select(attrs={
                'class': 'form-select',
            }),
            'position_name': forms.TextInput(attrs={
                'class':       'form-control',
                'placeholder': 'e.g. President, Secretary, Treasurer',
            }),
            'max_votes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min':   '1',
            }),
        }


# ── 6. Candidate Form ─────────────────────────────────────
class CandidateForm(forms.ModelForm):

    class Meta:
        model = Candidate
        fields = ['student', 'position', 'manifesto', 'photo']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'form-select',
            }),
            'position': forms.Select(attrs={
                'class': 'form-select',
            }),
            'manifesto': forms.Textarea(attrs={
                'class':       'form-control',
                'rows':        4,
                'placeholder': 'Enter candidate manifesto (max 500 characters)',
                'maxlength':   500,
            }),
            'photo': forms.FileInput(attrs={
                'class':  'form-control',
                'accept': 'image/jpeg, image/png',
            }),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Max 2MB
            if photo.size > 2 * 1024 * 1024:
                raise forms.ValidationError(
                    'Photo too large. Maximum size is 2MB.'
                )
        return photo


# ── 7. Student Profile Password Change Form ───────────────
class StudentPasswordChangeForm(forms.Form):

    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Enter current password',
        })
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Enter new password',
        })
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class':       'form-control',
            'placeholder': 'Confirm new password',
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get('current_password')
        if not self.user.check_password(current):
            raise forms.ValidationError(
                'Current password is incorrect.'
            )
        return current

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')

        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError(
                    'New passwords do not match.'
                )
            if len(p1) < 6:
                raise forms.ValidationError(
                    'Password must be at least 6 characters.'
                )
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.password_changed = True
        self.user.save()


class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
