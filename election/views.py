from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.utils import timezone
import csv
import io

from .models import Student, Election, Position, Candidate, Vote
from .forms import (
    StudentLoginForm, ForcePasswordChangeForm,
    CSVUploadForm, ElectionForm, PositionForm,
    CandidateForm, StudentPasswordChangeForm
)


# ═══════════════════════════════════════════════
# AUTH VIEWS
# ═══════════════════════════════════════════════
# ═══════════════════════════════════════════════
# AUTH VIEWS
# ═══════════════════════════════════════════════

def login_view(request):

    # Already logged in — redirect appropriately
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('student_dashboard')

    form = StudentLoginForm()

    if request.method == 'POST':
        form = StudentLoginForm(request.POST)

        if form.is_valid():
            admission_number = form.cleaned_data['admission_number']
            password = form.cleaned_data['password']

            # Try to authenticate using our custom backend
            user = authenticate(
                request,
                username=str(admission_number),
                password=password
            )

            if user is not None:
                # ── Valid credentials ─────────────────────
                login(request, user)
                messages.success(
                    request,
                    f'Welcome back, {user.first_name}!'
                )
                return redirect('student_dashboard')

            else:
                # ── Check why login failed ────────────────
                try:
                    student = Student.objects.get(
                        admission_number=admission_number
                    )
                    # Student exists but password is wrong
                    if not student.is_active:
                        messages.error(
                            request,
                            'Your account has been deactivated. '
                            'Please contact the administrator.'
                        )
                    else:
                        messages.error(
                            request,
                            'Incorrect password. Please try again.'
                        )
                except Student.DoesNotExist:
                    # Admission number not found in database
                    messages.error(
                        request,
                        'You are not a registered voter. '
                        'Please register with the admin.'
                    )

    return render(request, 'student/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def change_password_view(request):

    # Must be logged in to change password
    if not request.user.is_authenticated:
        return redirect('login')

    # Staff/admin don't use this view
    if request.user.is_staff:
        return redirect('admin_dashboard')

    form = ForcePasswordChangeForm()

    if request.method == 'POST':
        form = ForcePasswordChangeForm(request.POST)

        if form.is_valid():
            # Save the new password
            request.user.set_password(
                form.cleaned_data['new_password1']
            )
            # Mark password as changed — middleware will now let them through
            request.user.password_changed = True
            request.user.save()

            # Re-authenticate so session stays valid after password change
            user = authenticate(
                request,
                username=str(request.user.admission_number),
                password=form.cleaned_data['new_password1']
            )
            if user:
                login(request, user)

            messages.success(
                request,
                'Password changed successfully! Welcome to KuraVote.'
            )
            return redirect('student_dashboard')

    return render(request, 'student/change_password.html', {'form': form})
# ```

# ---

# **Three important things happening here:**

# **1. Login gives specific error messages per failure reason:**
# ```
# Admission number not in DB  → "You are not a registered voter..."
# Account deactivated         → "Your account has been deactivated..."
# Wrong password              → "Incorrect password. Please try again."

# ═══════════════════════════════════════════════
# STUDENT VIEWS
# ═══════════════════════════════════════════════


@login_required(login_url='login')
def student_dashboard(request):

    # Staff should not access student dashboard
    if request.user.is_staff:
        return redirect('admin_dashboard')

    # Get active election if any
    try:
        election = Election.objects.get(status=Election.STATUS_ACTIVE)
    except Election.DoesNotExist:
        election = None

    # Get positions student has already voted for
    voted_positions = []
    if election:
        voted_positions = Vote.objects.filter(
            student=request.user,
            election=election
        ).values_list('position_id', flat=True)

    context = {
        'election':        election,
        'voted_positions': list(voted_positions),
        'total_positions': election.positions.count() if election else 0,
        'votes_cast':      len(voted_positions),
    }
    return render(request, 'student/dashboard.html', context)


@login_required(login_url='login')
def ballot_view(request):

    if request.user.is_staff:
        return redirect('admin_dashboard')

    # Get active election
    try:
        election = Election.objects.get(status=Election.STATUS_ACTIVE)
    except Election.DoesNotExist:
        messages.error(request, 'No active election at the moment.')
        return redirect('student_dashboard')

    # Get all positions with their candidates
    positions = Position.objects.filter(
        election=election
    ).prefetch_related(
        'candidates__student'
    )

    # Get positions this student has already voted for
    voted_position_ids = Vote.objects.filter(
        student=request.user,
        election=election
    ).values_list('position_id', flat=True)

    # Get candidate IDs this student voted for
    voted_candidate_ids = Vote.objects.filter(
        student=request.user,
        election=election
    ).values_list('candidate_id', flat=True)

    context = {
        'election':           election,
        'positions':          positions,
        'voted_position_ids': list(voted_position_ids),
        'voted_candidate_ids': list(voted_candidate_ids),
    }
    return render(request, 'student/ballot.html', context)


@login_required(login_url='login')
def cast_vote(request):

    if request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method != 'POST':
        return redirect('ballot')

    # Get active election
    try:
        election = Election.objects.get(status=Election.STATUS_ACTIVE)
    except Election.DoesNotExist:
        messages.error(request, 'No active election at the moment.')
        return redirect('student_dashboard')

    candidate_id = request.POST.get('candidate_id')
    position_id = request.POST.get('position_id')

    if not candidate_id or not position_id:
        messages.error(request, 'Invalid vote submission.')
        return redirect('ballot')

    # Verify candidate and position exist
    candidate = get_object_or_404(Candidate, id=candidate_id)
    position = get_object_or_404(Position,  id=position_id)

    # Verify candidate belongs to this position
    if candidate.position != position:
        messages.error(request, 'Invalid vote submission.')
        return redirect('ballot')

    # Verify position belongs to active election
    if position.election != election:
        messages.error(request, 'Invalid vote submission.')
        return redirect('ballot')

    # ── Layer 1: Check if student already voted for this position ──
    already_voted = Vote.objects.filter(
        student=request.user,
        position=position,
        election=election
    ).exists()

    if already_voted:
        messages.error(
            request,
            f'You have already voted for {position.position_name}.'
        )
        return redirect('ballot')

    # ── Layer 2: Save the vote (Layer 3 is DB unique_together) ────
    try:
        Vote.objects.create(
            student=request.user,
            candidate=candidate,
            position=position,
            election=election
        )
        messages.success(
            request,
            f'Your vote for {position.position_name} has been '
            f'cast successfully!'
        )
    except Exception:
        messages.error(
            request,
            'Something went wrong. Your vote was not recorded. '
            'Please try again.'
        )

    return redirect('ballot')


@login_required(login_url='login')
def student_results(request):

    if request.user.is_staff:
        return redirect('admin_dashboard')

    # Show results only for closed or active elections
    elections = Election.objects.exclude(
        status=Election.STATUS_INACTIVE
    ).order_by('-created_at')

    # Get the most recent election to display by default
    selected_election = elections.first()

    results = []
    if selected_election:
        positions = Position.objects.filter(
            election=selected_election
        ).prefetch_related('candidates__student')

        for position in positions:
            candidates = Candidate.objects.filter(
                position=position
            ).annotate(
                total_votes=Count('votes')
            ).order_by('-total_votes')

            results.append({
                'position':   position,
                'candidates': candidates,
                'total_votes': position.total_votes,
            })

    context = {
        'elections':         elections,
        'selected_election': selected_election,
        'results':           results,
    }
    return render(request, 'student/results.html', context)


@login_required(login_url='login')
def student_profile(request):

    if request.user.is_staff:
        return redirect('admin_dashboard')

    form = StudentPasswordChangeForm(user=request.user)

    if request.method == 'POST':
        form = StudentPasswordChangeForm(
            user=request.user,
            data=request.POST
        )
        if form.is_valid():
            form.save()

            # Re-authenticate to keep session alive
            user = authenticate(
                request,
                username=str(request.user.admission_number),
                password=form.cleaned_data['new_password1']
            )
            if user:
                login(request, user)

            messages.success(
                request,
                'Password changed successfully!'
            )
            return redirect('student_profile')
        else:
            messages.error(
                request,
                'Please fix the errors below.'
            )

    context = {
        'form':    form,
        'student': request.user,
    }
    return render(request, 'student/profile.html', context)
# ```

# ---

# **Key decisions made in these views:**

# **`cast_vote` has four layers of validation before saving:**
# ```
# 1. Method must be POST         → prevents URL manipulation
# 2. Active election must exist  → prevents voting outside election period
# 3. Candidate belongs to position → prevents form tampering
# 4. Already voted check         → Layer 1 duplicate prevention
# 5. DB unique_together          → Layer 2 duplicate prevention (silent safety net)


def student_dashboard(request):
    pass


def ballot_view(request):
    pass


def cast_vote(request):
    pass


def student_results(request):
    pass


def student_profile(request):
    pass


# ═══════════════════════════════════════════════
# ADMIN VIEWS
# ═══════════════════════════════════════════════

@staff_member_required(login_url='login')
def admin_dashboard(request):

    # Summary stats for the dashboard
    total_students = Student.objects.filter(is_staff=False).count()
    total_elections = Election.objects.count()
    total_candidates = Candidate.objects.count()

    # Active election info
    try:
        active_election = Election.objects.get(status=Election.STATUS_ACTIVE)
        total_votes = Vote.objects.filter(election=active_election).count()
        voters_count = Vote.objects.filter(
            election=active_election
        ).values('student').distinct().count()
        turnout = round((voters_count / total_students) * 100, 1) \
            if total_students > 0 else 0
    except Election.DoesNotExist:
        active_election = None
        total_votes = 0
        voters_count = 0
        turnout = 0

    recent_elections = Election.objects.order_by('-created_at')[:5]

    context = {
        'total_students':   total_students,
        'total_elections':  total_elections,
        'total_candidates': total_candidates,
        'active_election':  active_election,
        'total_votes':      total_votes,
        'voters_count':     voters_count,
        'turnout':          turnout,
        'recent_elections': recent_elections,
    }
    return render(request, 'admin/dashboard.html', context)


# ── Elections ─────────────────────────────────────────────

@staff_member_required(login_url='login')
def admin_elections(request):
    elections = Election.objects.order_by('-created_at')
    return render(request, 'admin/elections.html', {
        'elections': elections
    })


@staff_member_required(login_url='login')
def admin_election_create(request):
    form = ElectionForm()
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Election created successfully.')
            return redirect('admin_elections')
        else:
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'admin/election_form.html', {
        'form': form, 'action': 'Create'
    })


@staff_member_required(login_url='login')
def admin_election_edit(request, pk):
    election = get_object_or_404(Election, pk=pk)
    form = ElectionForm(instance=election)
    if request.method == 'POST':
        form = ElectionForm(request.POST, instance=election)
        if form.is_valid():
            form.save()
            messages.success(request, 'Election updated successfully.')
            return redirect('admin_elections')
        else:
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'admin/election_form.html', {
        'form': form, 'action': 'Edit', 'election': election
    })


@staff_member_required(login_url='login')
def admin_election_delete(request, pk):
    election = get_object_or_404(Election, pk=pk)
    if request.method == 'POST':
        election.delete()
        messages.success(request, 'Election deleted successfully.')
        return redirect('admin_elections')
    return render(request, 'admin/election_confirm_delete.html', {
        'election': election
    })


@staff_member_required(login_url='login')
def admin_election_activate(request, pk):
    election = get_object_or_404(Election, pk=pk)

    # Only one election can be active at a time
    if Election.objects.filter(status=Election.STATUS_ACTIVE).exists():
        messages.error(
            request,
            'Another election is already active. '
            'Please close it before activating a new one.'
        )
        return redirect('admin_elections')

    election.status = Election.STATUS_ACTIVE
    election.save()
    messages.success(
        request,
        f'"{election.election_name}" is now active. Voting has started.'
    )
    return redirect('admin_elections')


@staff_member_required(login_url='login')
def admin_election_close(request, pk):
    election = get_object_or_404(Election, pk=pk)
    election.status = Election.STATUS_CLOSED
    election.save()
    messages.success(
        request,
        f'"{election.election_name}" has been closed. Voting has ended.'
    )
    return redirect('admin_elections')


# ── Positions ─────────────────────────────────────────────

@staff_member_required(login_url='login')
def admin_positions(request):
    positions = Position.objects.select_related(
        'election'
    ).order_by('election', 'position_name')
    return render(request, 'admin/positions.html', {
        'positions': positions
    })


@staff_member_required(login_url='login')
def admin_position_create(request):
    form = PositionForm()
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Position created successfully.')
            return redirect('admin_positions')
        else:
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'admin/position_form.html', {
        'form': form, 'action': 'Create'
    })


@staff_member_required(login_url='login')
def admin_position_edit(request, pk):
    position = get_object_or_404(Position, pk=pk)
    form = PositionForm(instance=position)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, 'Position updated successfully.')
            return redirect('admin_positions')
        else:
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'admin/position_form.html', {
        'form': form, 'action': 'Edit', 'position': position
    })


@staff_member_required(login_url='login')
def admin_position_delete(request, pk):
    position = get_object_or_404(Position, pk=pk)
    if request.method == 'POST':
        position.delete()
        messages.success(request, 'Position deleted successfully.')
        return redirect('admin_positions')
    return render(request, 'admin/position_confirm_delete.html', {
        'position': position
    })


# ── Candidates ────────────────────────────────────────────

@staff_member_required(login_url='login')
def admin_candidates(request):
    candidates = Candidate.objects.select_related(
        'student', 'position', 'position__election'
    ).order_by('position', 'student__last_name')
    return render(request, 'admin/candidates.html', {
        'candidates': candidates
    })


@staff_member_required(login_url='login')
def admin_candidate_create(request):
    form = CandidateForm()
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate registered successfully.')
            return redirect('admin_candidates')
        else:
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'admin/candidate_form.html', {
        'form': form, 'action': 'Register'
    })


@staff_member_required(login_url='login')
def admin_candidate_edit(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    form = CandidateForm(instance=candidate)
    if request.method == 'POST':
        form = CandidateForm(
            request.POST, request.FILES, instance=candidate
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate updated successfully.')
            return redirect('admin_candidates')
        else:
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'admin/candidate_form.html', {
        'form': form, 'action': 'Edit', 'candidate': candidate
    })


@staff_member_required(login_url='login')
def admin_candidate_delete(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        candidate.delete()
        messages.success(request, 'Candidate removed successfully.')
        return redirect('admin_candidates')
    return render(request, 'admin/candidate_confirm_delete.html', {
        'candidate': candidate
    })


# ── Students ──────────────────────────────────────────────

@staff_member_required(login_url='login')
def admin_students(request):
    students = Student.objects.filter(
        is_staff=False
    ).order_by('admission_number')

    # Search functionality
    query = request.GET.get('q', '')
    if query:
        students = students.filter(
            admission_number__icontains=query
        ) | students.filter(
            first_name__icontains=query
        ) | students.filter(
            last_name__icontains=query
        ) | students.filter(
            email__icontains=query
        )

    # Pagination — 25 students per page
    paginator = Paginator(students, 25)
    page = request.GET.get('page', 1)
    students = paginator.get_page(page)

    return render(request, 'admin/students.html', {
        'students': students,
        'query':    query,
    })


@staff_member_required(login_url='login')
def admin_upload_csv(request):
    form = CSVUploadForm()

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            # Read file
            decoded = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))

            created = 0
            skipped = 0
            errors = []

            for row_num, row in enumerate(reader, start=2):
                try:
                    admission_number = int(row['admission_number'].strip())
                    first_name = row['first_name'].strip()
                    last_name = row['last_name'].strip()
                    email = row['email'].strip()

                    # Skip if admission number already exists
                    if Student.objects.filter(
                        admission_number=admission_number
                    ).exists():
                        skipped += 1
                        continue

                    # Create student with default password
                    # = admission number
                    student = Student(
                        admission_number=admission_number,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password_changed=False,
                        is_active=True,
                    )
                    # Default password is the admission number
                    student.set_password(str(admission_number))
                    student.save()
                    created += 1

                except (KeyError, ValueError) as e:
                    errors.append(f'Row {row_num}: {str(e)}')
                except Exception as e:
                    errors.append(f'Row {row_num}: {str(e)}')

            # Summary message
            if created > 0:
                messages.success(
                    request,
                    f'Successfully imported {created} student(s).'
                )
            if skipped > 0:
                messages.warning(
                    request,
                    f'{skipped} student(s) skipped — '
                    f'admission numbers already exist.'
                )
            for error in errors:
                messages.error(request, error)

            return redirect('admin_students')

    return render(request, 'admin/upload_csv.html', {'form': form})


@staff_member_required(login_url='login')
def admin_reset_password(request, pk):
    student = get_object_or_404(Student, pk=pk, is_staff=False)
    if request.method == 'POST':
        # Reset to admission number as default password
        student.set_password(str(student.admission_number))
        student.password_changed = False
        student.save()
        messages.success(
            request,
            f'Password for {student.get_full_name()} reset to '
            f'their admission number.'
        )
        return redirect('admin_students')
    return render(request, 'admin/student_reset_password.html', {
        'student': student
    })


@staff_member_required(login_url='login')
def admin_toggle_student(request, pk):
    student = get_object_or_404(Student, pk=pk, is_staff=False)
    if request.method == 'POST':
        student.is_active = not student.is_active
        student.save()
        status = 'activated' if student.is_active else 'deactivated'
        messages.success(
            request,
            f'{student.get_full_name()} has been {status}.'
        )
    return redirect('admin_students')


# ── Live Results ──────────────────────────────────────────

@staff_member_required(login_url='login')
def admin_live_results(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    positions = Position.objects.filter(
        election=election
    ).prefetch_related('candidates__student')

    total_students = Student.objects.filter(is_staff=False).count()
    voters_count = Vote.objects.filter(
        election=election
    ).values('student').distinct().count()
    turnout = round((voters_count / total_students) * 100, 1) \
        if total_students > 0 else 0

    context = {
        'election':      election,
        'positions':     positions,
        'total_students': total_students,
        'voters_count':  voters_count,
        'turnout':       turnout,
    }
    return render(request, 'admin/live_results.html', context)


@staff_member_required(login_url='login')
def admin_results_api(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    positions = Position.objects.filter(election=election)

    data = []
    for position in positions:
        candidates = Candidate.objects.filter(
            position=position
        ).annotate(
            vote_count=Count('votes')
        ).select_related('student').order_by('-vote_count')

        data.append({
            'position_id':   position.id,
            'position_name': position.position_name,
            'total_votes':   position.total_votes,
            'candidates': [
                {
                    'id':         c.id,
                    'name':       c.student.get_full_name(),
                    'initials':   c.get_initials(),
                    'color':      c.get_avatar_color(),
                    'votes':      c.vote_count,
                    'percentage': c.vote_percentage,
                }
                for c in candidates
            ]
        })

    # Overall turnout
    total_students = Student.objects.filter(is_staff=False).count()
    voters_count = Vote.objects.filter(
        election=election
    ).values('student').distinct().count()
    turnout = round((voters_count / total_students) * 100, 1) \
        if total_students > 0 else 0

    return JsonResponse({
        'election_name': election.election_name,
        'total_votes':   election.total_votes,
        'voters_count':  voters_count,
        'total_students': total_students,
        'turnout':       turnout,
        'positions':     data,
    })


# ── Reports ───────────────────────────────────────────────

@staff_member_required(login_url='login')
def admin_reports(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    positions = Position.objects.filter(election=election)

    results = []
    for position in positions:
        candidates = Candidate.objects.filter(
            position=position
        ).annotate(
            vote_count=Count('votes')
        ).select_related('student').order_by('-vote_count')

        winner = candidates.first() if candidates.exists() else None
        results.append({
            'position':   position,
            'candidates': candidates,
            'winner':     winner,
        })

    total_students = Student.objects.filter(is_staff=False).count()
    voters_count = Vote.objects.filter(
        election=election
    ).values('student').distinct().count()
    turnout = round((voters_count / total_students) * 100, 1) \
        if total_students > 0 else 0

    context = {
        'election':       election,
        'results':        results,
        'total_students': total_students,
        'voters_count':   voters_count,
        'turnout':        turnout,
    }
    return render(request, 'admin/reports.html', context)


@staff_member_required(login_url='login')
def export_pdf(request, election_id):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from django.http import HttpResponse
    import io

    election = get_object_or_404(Election, pk=election_id)
    positions = Position.objects.filter(election=election)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(
        Paragraph(f'KuraVote — Election Results', styles['Title'])
    )
    elements.append(
        Paragraph(election.election_name, styles['Heading2'])
    )
    elements.append(Spacer(1, 20))

    for position in positions:
        elements.append(
            Paragraph(position.position_name, styles['Heading3'])
        )
        candidates = Candidate.objects.filter(
            position=position
        ).annotate(
            vote_count=Count('votes')
        ).select_related('student').order_by('-vote_count')

        table_data = [['Candidate', 'Admission No', 'Votes', '%']]
        for c in candidates:
            table_data.append([
                c.student.get_full_name(),
                str(c.student.admission_number),
                str(c.vote_count),
                f'{c.vote_percentage}%',
            ])

        table = Table(table_data, colWidths=[200, 100, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
            ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
            ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.HexColor('#f0f4f8')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 16))

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="kuravote_results_{election_id}.pdf"'
    )
    return response


@staff_member_required(login_url='login')
def export_excel(request, election_id):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from django.http import HttpResponse
    import io

    election = get_object_or_404(Election, pk=election_id)
    positions = Position.objects.filter(election=election)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Election Results'

    # Header row style
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill(
        start_color='166534',
        end_color='166534',
        fill_type='solid'
    )

    # Write headers
    headers = ['Position', 'Candidate', 'Admission No', 'Votes', 'Percentage']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    row_num = 2
    for position in positions:
        candidates = Candidate.objects.filter(
            position=position
        ).annotate(
            vote_count=Count('votes')
        ).select_related('student').order_by('-vote_count')

        for c in candidates:
            ws.cell(row=row_num, column=1, value=position.position_name)
            ws.cell(row=row_num, column=2, value=c.student.get_full_name())
            ws.cell(row=row_num, column=3, value=c.student.admission_number)
            ws.cell(row=row_num, column=4, value=c.vote_count)
            ws.cell(row=row_num, column=5, value=f'{c.vote_percentage}%')
            row_num += 1

    # Auto-size columns
    for col in ws.columns:
        max_length = max(
            len(str(cell.value or '')) for cell in col
        )
        ws.column_dimensions[col[0].column_letter].width = max_length + 4

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument'
                     '.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = (
        f'attachment; filename="kuravote_results_{election_id}.xlsx"'
    )
    return response


# ── Audit Log ─────────────────────────────────────────────

@staff_member_required(login_url='login')
def admin_audit_log(request):
    # Use Django's built-in admin log
    from django.contrib.admin.models import LogEntry
    logs = LogEntry.objects.select_related(
        'user', 'content_type'
    ).order_by('-action_time')
    paginator = Paginator(logs, 50)
    page = request.GET.get('page', 1)
    logs = paginator.get_page(page)
    return render(request, 'admin/audit_log.html', {'logs': logs})


# ── Settings ──────────────────────────────────────────────

@staff_member_required(login_url='login')
def admin_settings(request):
    return render(request, 'admin/settings.html')
