from .models import Election


def active_election(request):
    try:
        election = Election.objects.get(status=Election.STATUS_ACTIVE)
    except Election.DoesNotExist:
        election = None
    return {'active_election': election}
