from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Student, Election, Position, Candidate, Vote

# student admin


@admin.register(Student)
class StudentAdmin(UserAdmin):
    list_display = [
        'admission_number', 'get_full_name', 'email',
        'password_changed', 'is_active', 'date_joined'
    ]
    list_filter = ['is_active', 'password_changed', 'date_joined']
    search_fields = ['admission_number', 'first_name', 'last_name', 'email']
    ordering = ['admission_number']
    list_per_page = 25

    # fields to be shown when editing a student
    fieldsets = (
        ('Login Info', {
            'fields': ('admission_number', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Account Status', {
            'fields': ('is_active', 'password_changed', 'is_staff')
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login')
        }),
    )

    # fields to be shown when creating new student
    add_fieldsets = (
        ('Create Student', {
            'classes': ('wide',),
            'fields': ('admission_number', 'first_name', 'last_name',
                       'email', 'password1', 'password2'),
        }),
    )

    # required fields by userAdmin
    filter_horizontal = ()
    list_filter = ['is_active', 'password_changed']

    # election admin


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):

    list_filter = ['status']
    search_fields = ['election_name']
    ordering = ['-created_at']
    list_per_page = 10

    def status_badge(self, obj):
        colors = {
            'inactive': '#6b7280',
            'active':   '#059669',
            'closed':   '#dc2626',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 10px; '
            'border-radius:10px; font-size:11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    list_display = [
        'election_name', 'status_badge',
        'start_date', 'end_date',
        'total_votes', 'created_at'
    ]


# position admin
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['position_name', 'election',
                    'total_candidates', 'total_votes', 'max_votes'
                    ]
    list_filter = ['election']
    search_fields = ['position_name']
    ordering = ['election', 'position_name']
    list_per_page = 20

# candidate admin


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):

    list_filter = ['position__election', 'position']
    search_fields = [
        'student__first_name', 'student__last_name',
        'student__admission_number'
    ]
    ordering = ['position', 'student__last_name']
    list_per_page = 20

    def get_full_name(self, obj):
        return obj.student.get_full_name()
    get_full_name.short_description = 'Candidate Name'

    def get_election(self, obj):
        return obj.position.election.election_name
    get_election.short_description = 'Election'

    def photo_preview(self, obj):
        if obj.has_photo():
            return format_html(
                '<img src="{}" style="width:36px; height:36px; '
                'border-radius:8px; object-fit:cover;">',
                obj.photo.url
            )
        return format_html(
            '<div style="width:36px; height:36px; border-radius:8px; '
            'background:{}; display:flex; align-items:center; '
            'justify-content:center; color:#fff; font-size:12px; '
            'font-weight:700;">{}</div>',
            obj.get_avatar_color(),
            obj.get_initials()
        )
    photo_preview.short_description = 'Photo'

    list_display = [
        'get_full_name', 'position', 'get_election',
        'photo_preview', 'vote_count', 'created_at'
    ]


# vote admin
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = [
        'get_student', 'get_candidate',
        'position', 'election', 'voted_at'
    ]
    list_filter = ['election', 'position']
    search_fields = [
        'student__admission_number',
        'student__first_name',
        'student__last_name'
    ]
    ordering = ['-voted_at']
    list_per_page = 50

    # votes should never be editale - read only
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_student(self, obj):
        return f"{obj.student.get_full_name()} ({obj.student.admission_number})"
    get_student.short_description = 'Student'

    def get_candidate(self, obj):
        return obj.candidate.student.get_full_name()
    get_candidate.short_description = 'Voted For'
