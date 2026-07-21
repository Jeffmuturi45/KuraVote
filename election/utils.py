from django.core.cache import cache
from django.utils import timezone
import time


# ── Cache keys ─────────────────────────────────────────────
CACHE_STUDENTS_STATS = 'students_stats'
CACHE_ACTIVE_ELECTION = 'active_election'
CACHE_POSITIONS_PREFIX = 'positions_election_'
CACHE_RESULTS_PREFIX = 'results_election_'

CACHE_SHORT = 30    # 30 seconds — live data
CACHE_MEDIUM = 300   # 5 minutes  — semi-static
CACHE_LONG = 3600  # 1 hour     — rarely changes


def get_student_stats():
    """
    Cache student stats — recomputed every 5 minutes.
    Invalidated on student create/update/delete.
    """
    cached = cache.get(CACHE_STUDENTS_STATS)
    if cached:
        return cached

    from .models import Student
    stats = {
        'total':            Student.objects.filter(
            is_staff=False
        ).count(),
        'active':           Student.objects.filter(
            is_staff=False, is_active=True
        ).count(),
        'inactive':         Student.objects.filter(
            is_staff=False, is_active=False
        ).count(),
        'default_password': Student.objects.filter(
            is_staff=False,
            password_changed=False
        ).count(),
    }
    cache.set(CACHE_STUDENTS_STATS, stats, timeout=CACHE_MEDIUM)
    return stats


def invalidate_student_stats():
    """Call this whenever a student is created, updated, or deleted."""
    cache.delete(CACHE_STUDENTS_STATS)


def get_active_election():
    """
    Cache active election — recomputed every 30 seconds.
    Invalidated when election status changes.
    """
    cached = cache.get(CACHE_ACTIVE_ELECTION)
    if cached == 'NONE':
        return None
    if cached:
        return cached

    from .models import Election
    try:
        election = Election.objects.get(status=Election.STATUS_ACTIVE)
        cache.set(CACHE_ACTIVE_ELECTION, election, timeout=CACHE_SHORT)
        return election
    except Election.DoesNotExist:
        cache.set(CACHE_ACTIVE_ELECTION, 'NONE', timeout=CACHE_SHORT)
        return None


def invalidate_active_election():
    """Call this when election status changes."""
    cache.delete(CACHE_ACTIVE_ELECTION)
    # Also clear any results cache
    cache.delete_pattern = getattr(cache, 'delete_pattern', None)


def get_positions_for_election(election_id):
    """Cache positions per election — 5 minutes."""
    key = f'{CACHE_POSITIONS_PREFIX}{election_id}'
    cached = cache.get(key)
    if cached:
        return cached

    from .models import Position
    positions = list(
        Position.objects.filter(
            election_id=election_id
        ).prefetch_related('candidates__student')
    )
    cache.set(key, positions, timeout=CACHE_MEDIUM)
    return positions


def invalidate_election_positions(election_id):
    cache.delete(f'{CACHE_POSITIONS_PREFIX}{election_id}')


def get_active_users():
    active_ids = cache.get('active_user_ids', set())
    active_list = []
    now = time.time()
    stale = set()

    for user_id in list(active_ids):
        data = cache.get(f'active_user_{user_id}')
        if data and (now - data['last_seen']) < 300:
            active_list.append(data)
        else:
            stale.add(user_id)

    if stale:
        active_ids -= stale
        cache.set('active_user_ids', active_ids, timeout=300)

    return active_list


def active_election(request):
    from .models import Election, SystemSettings
    try:
        election = Election.objects.get(
            status=Election.STATUS_ACTIVE
        )
    except Election.DoesNotExist:
        election = None
    sys_settings = SystemSettings.get()
    return {
        'active_election':    election,
        'active_users_count': len(get_active_users()),
        'system_settings':    sys_settings,
        'system_name':        sys_settings.system_name,
    }


def create_notification(student, title, message,
                        notif_type='info'):
    from .models import Notification
    Notification.objects.create(
        student=student,
        title=title,
        message=message,
        notif_type=notif_type,
    )


def create_admin_notification(title, message, notif_type='info'):
    from .models import Notification
    Notification.objects.create(
        student=None,
        is_admin_notification=True,
        title=title,
        message=message,
        notif_type=notif_type,
    )


def create_bulk_notifications(students, title,
                              message, notif_type='info'):
    from .models import Notification
    Notification.objects.bulk_create([
        Notification(
            student=s,
            title=title,
            message=message,
            notif_type=notif_type,
        )
        for s in students
    ], batch_size=500)


def create_bulk_notifications(students, title,
                              message, notif_type='info'):
    from .models import Notification
    Notification.objects.bulk_create([
        Notification(
            student=s,
            title=title,
            message=message,
            notif_type=notif_type,
        )
        for s in students
    ], batch_size=500)


def detect_and_log_ties(election):
    """
    Run after election closes.
    Finds all positions with tied top vote counts.
    Creates TieResolution records for each.
    Returns list of TieResolution objects created.
    """
    from .models import Position, Vote, Candidate, TieResolution

    positions = Position.objects.filter(election=election)
    new_ties = []

    for position in positions:
        pos_total = Vote.objects.filter(position=position).count()
        if pos_total == 0:
            continue

        candidates = list(
            Candidate.objects.filter(
                position=position
            ).select_related('student')
        )

        if not candidates:
            continue

        # Sort by actual vote count — NOT by registration order
        candidates_with_votes = sorted(
            [(c, Vote.objects.filter(candidate=c).count())
             for c in candidates],
            key=lambda x: x[1],
            reverse=True
        )

        top_votes = candidates_with_votes[0][1]
        if top_votes == 0:
            continue

        # Find all candidates with top vote count
        tied = [
            c for c, votes in candidates_with_votes
            if votes == top_votes
        ]

        if len(tied) <= 1:
            continue  # Clear winner — no tie

        # Create or update tie resolution record
        tie_obj, created = TieResolution.objects.get_or_create(
            position=position,
            defaults={
                'election':        election,
                'tied_vote_count': top_votes,
                'status':          TieResolution.STATUS_PENDING,
            }
        )
        if created:
            tie_obj.tied_candidates.set(tied)
            tie_obj.save()
            new_ties.append(tie_obj)

            # Notify admins
            create_admin_notification(
                title=f'Vote Tie Detected — {position.position_name}',
                message=(
                    f'{len(tied)} candidates are tied at {top_votes} votes '
                    f'each in {position.position_name} for '
                    f'"{election.election_name}". '
                    f'A rerun election is required.'
                ),
                notif_type='warning',
            )

    return new_ties
