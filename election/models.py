from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import (
    MinValueValidator, MaxValueValidator, FileExtensionValidator, MinLengthValidator)
from django.utils import timezone
from django.db.models import Count
import uuid
import os


class StudentManager(BaseUserManager):

    def create_user(self, admission_number, password=None, **extra_fields):
        if not admission_number:
            raise ValueError('Admission number is required')
        user = self.model(admission_number=admission_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, admission_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(admission_number, password, **extra_fields)


class Student(AbstractBaseUser, PermissionsMixin):
    admission_number = models.IntegerField(unique=True,
                                           validators=[
                                               MinValueValidator(1),
                                               MaxValueValidator(999999)
                                           ])
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=254)

    password_changed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    has_seen_tour = models.BooleanField(default=False)

    objects = StudentManager()

    USERNAME_FIELD = 'admission_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    class Meta:
        db_table = 'students'
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        indexes = [
            models.Index(fields=['admission_number']),
            models.Index(fields=['email']),
            models.Index(fields=['first_name']),
            models.Index(fields=['last_name']),
            models.Index(fields=['first_name', 'last_name']),
        ]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_initials(self):
        return f"{self.first_name[0].upper()}{self.last_name[0].upper()}"

    AVATAR_COLORS = [
        '#1a3a5c', '#0f766e', '#7c3aed',
        '#b45309', '#0369a1', '#065f46',
        '#9f1239', '#1e40af', '#5b21b6',
    ]

    def get_avatar_color(self):
        return self.AVATAR_COLORS[self.admission_number % len(self.AVATAR_COLORS)]

    def __str__(self):
        return f"{self.get_full_name()} ({self.admission_number})"


class Admin(models.Model):
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)

    created_at = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'admins'
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_initials(self):
        return f"{self.first_name[0].upper()}{self.last_name[0].upper()}"

    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"


class Election(models.Model):
    STATUS_ACTIVE   = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_CLOSED   = 'closed'
    STATUS_RERUN    = 'rerun'   # tie-rerun in progress for selected positions

    announcement = models.TextField(
        blank=True, null=True,
        help_text='Optional message shown to students on their dashboard'
    )

    STATUS_CHOICES = [
        (STATUS_ACTIVE,   'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_CLOSED,   'Closed'),
        (STATUS_RERUN,    'Re-run (Tie Resolution)'),
    ]

    election_name = models.CharField(max_length=200)
    start_date    = models.DateTimeField()
    end_date      = models.DateTimeField()
    status        = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_INACTIVE)
    created_at    = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'elections'
        verbose_name = 'Election'
        verbose_name_plural = 'Elections'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status'])]

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    @property
    def is_closed(self):
        return self.status == self.STATUS_CLOSED

    @property
    def is_rerun(self):
        return self.status == self.STATUS_RERUN

    @property
    def total_votes(self):
        return Vote.objects.filter(election=self).count()

    def __str__(self):
        return f"{self.election_name} ({self.get_status_display()})"


class Position(models.Model):

    election = models.ForeignKey(
        Election, on_delete=models.CASCADE, related_name='positions')

    position_name = models.CharField(max_length=100)
    max_votes     = models.PositiveIntegerField(default=1)
    # True when this position has been flagged for a re-run due to a tie
    is_rerun      = models.BooleanField(default=False)
    created_at    = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'positions'
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        ordering = ['position_name']
        indexes = [
            models.Index(fields=['election']),
        ]
        # we prevent duplicate position names
        unique_together = ('election', 'position_name')

        # helper properties
    @property
    def total_votes(self):
        return Vote.objects.filter(position=self).count()

    @property
    def total_candidates(self):
        return self.candidates.count()

    def __str__(self):
        return f"{self.position_name} ({self.election.election_name})"


def candidate_photo_path(instance, filename):
    """Store as UUID to prevent filename-based attacks."""
    ext = os.path.splitext(filename)[1].lower()
    return f'candidates/{uuid.uuid4().hex}{ext}'


class Candidate(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='candidatures'
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='candidates'
    )
    manifesto = models.TextField(
        max_length=500,
        blank=True,
        validators=[MinLengthValidator(0)],
    )
    photo = models.ImageField(
        upload_to=candidate_photo_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png']
            )
        ]
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'candidates'
        verbose_name = 'Candidate'
        verbose_name_plural = 'Candidates'
        ordering = ['position', 'student__last_name']
        indexes = [
            models.Index(fields=['position']),
            models.Index(fields=['student']),
        ]
        unique_together = ('student', 'position')

    def has_photo(self):
        return bool(self.photo and self.photo.name)

    def get_initials(self):
        return self.student.get_initials()

    def get_avatar_color(self):
        return self.student.get_avatar_color()

    @property
    def vote_count(self):
        return Vote.objects.filter(candidate=self).count()

    @property
    def vote_percentage(self):
        total = Vote.objects.filter(position=self.position).count()
        if total == 0:
            return 0
        return round((self.vote_count / total) * 100, 1)

    def __str__(self):
        return (
            f"{self.student.get_full_name()} "
            f"→ {self.position.position_name}"
        )


class Vote(models.Model):
    # FKs
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='votes')

    candidate = models.ForeignKey(
        Candidate, on_delete=models.CASCADE, related_name='votes')

    position = models.ForeignKey(
        Position, on_delete=models.CASCADE, related_name='votes')

    election = models.ForeignKey(
        Election, on_delete=models.CASCADE, related_name='votes')

    voted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'votes'
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'
        ordering = ['-voted_at']

        # prevents double voting for same position in same election
        unique_together = ('student', 'position', 'election')

        indexes = [
            # live results uses this
            models.Index(fields=['election', 'position', 'candidate']),
            # has_voted check
            models.Index(fields=['student', 'election']),
            # how many students have voted
            models.Index(fields=['election']),
        ]

    def __str__(self):
        return (
            f"{self.student.get_full_name()} voted for "
            f"{self.candidate.student.get_full_name()} "
            f"({self.position.position_name})"
        )


class SystemSettings(models.Model):
    """Single-row settings table for the institution."""

    # ── Identity ──────────────────────────────────────────
    system_name      = models.CharField(max_length=100, default='KuraVote')
    institution_name = models.CharField(max_length=200, default='')

    # ── Security ──────────────────────────────────────────
    two_fa_enabled   = models.BooleanField(default=True)

    # ── Appearance / Theme ────────────────────────────────
    # theme: 'green' | 'blue' | 'purple' | 'dark' | 'custom'
    theme            = models.CharField(max_length=20, default='green')
    # font_family: 'dmsans' | 'inter' | 'poppins' | 'roboto' | 'system'
    font_family      = models.CharField(max_length=20, default='dmsans')
    # font sizes for admin and student panels
    admin_font_size   = models.CharField(max_length=5, default='md')
    student_font_size = models.CharField(max_length=5, default='md')
    # custom theme colours (used when theme='custom')
    primary_color    = models.CharField(max_length=7, default='#16a34a')
    sidebar_color    = models.CharField(max_length=7, default='#14532d')
    accent_color     = models.CharField(max_length=7, default='#eab308')
    # extra CSS injected into every page (power-user customisation)
    custom_css       = models.TextField(blank=True, default='')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Settings'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f'Settings — {self.system_name}'


class TiebreakLog(models.Model):
    """Auditable record of every tiebreak decision made by the system."""
    position = models.ForeignKey(
        'Position', on_delete=models.CASCADE, related_name='tiebreak_logs'
    )
    election = models.ForeignKey(
        'Election', on_delete=models.CASCADE, related_name='tiebreak_logs'
    )
    tied_candidates = models.JSONField()        # list of {id, name, votes}
    winner_candidate_id = models.IntegerField()
    winner_name = models.CharField(max_length=200)
    method = models.CharField(max_length=50, default='earliest_vote')
    resolved_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'tiebreak_logs'
        ordering = ['-resolved_at']

    def __str__(self):
        return f'Tiebreak: {self.position} → {self.winner_name}'


class Notification(models.Model):

    TYPE_INFO = 'info'
    TYPE_SUCCESS = 'success'
    TYPE_WARNING = 'warning'

    TYPE_CHOICES = [
        (TYPE_INFO,    'Info'),
        (TYPE_SUCCESS, 'Success'),
        (TYPE_WARNING, 'Warning'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
    )
    is_admin_notification = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    message = models.TextField()
    notif_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=TYPE_INFO
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'is_read']),
            models.Index(fields=['is_admin_notification', 'is_read']),
        ]

    def __str__(self):
        if self.is_admin_notification:
            return f'[ADMIN] {self.title}'
        return f'{self.student.get_full_name()} — {self.title}'