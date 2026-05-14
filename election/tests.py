from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta

from .models import (
    Student, Election, Position,
    Candidate, Vote, Notification
)


# ═══════════════════════════════════════════════
# MODEL TESTS
# ═══════════════════════════════════════════════

class StudentModelTest(TestCase):

    def setUp(self):
        self.student = Student.objects.create(
            admission_number=43861,
            first_name='Jeff',
            last_name='Muturi',
            email='jeff@school.ac.ke',
            is_active=True,
            password_changed=False,
        )
        self.student.set_password('43861')
        self.student.save()

    def test_student_creation(self):
        self.assertEqual(
            self.student.get_full_name(), 'Jeff Muturi'
        )

    def test_student_initials(self):
        self.assertEqual(self.student.get_initials(), 'JM')

    def test_student_avatar_color(self):
        color = self.student.get_avatar_color()
        self.assertTrue(color.startswith('#'))

    def test_default_password_is_admission_number(self):
        self.assertTrue(
            self.student.check_password('43861')
        )

    def test_student_str(self):
        self.assertIn('Jeff Muturi', str(self.student))
        self.assertIn('43861', str(self.student))


class ElectionModelTest(TestCase):

    def setUp(self):
        self.election = Election.objects.create(
            election_name='Student Council 2025',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=2),
            status=Election.STATUS_ACTIVE,
        )

    def test_election_is_active(self):
        self.assertTrue(self.election.is_active)

    def test_election_is_not_closed(self):
        self.assertFalse(self.election.is_closed)

    def test_election_str(self):
        self.assertIn('Student Council 2025', str(self.election))

    def test_total_votes_starts_zero(self):
        self.assertEqual(self.election.total_votes, 0)


class PositionModelTest(TestCase):

    def setUp(self):
        self.election = Election.objects.create(
            election_name='Test Election',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=2),
            status=Election.STATUS_ACTIVE,
        )
        self.position = Position.objects.create(
            election=self.election,
            position_name='President',
            max_votes=1,
        )

    def test_position_str(self):
        self.assertIn('President', str(self.position))

    def test_position_linked_to_election(self):
        self.assertEqual(
            self.position.election, self.election
        )

    def test_total_candidates_starts_zero(self):
        self.assertEqual(self.position.total_candidates, 0)


class CandidateModelTest(TestCase):

    def setUp(self):
        self.student = Student.objects.create(
            admission_number=43862,
            first_name='Jane',
            last_name='Wanjiku',
            email='jane@school.ac.ke',
        )
        self.student.set_password('43862')
        self.student.save()

        self.election = Election.objects.create(
            election_name='Test Election',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=2),
            status=Election.STATUS_ACTIVE,
        )
        self.position = Position.objects.create(
            election=self.election,
            position_name='President',
            max_votes=1,
        )
        self.candidate = Candidate.objects.create(
            student=self.student,
            position=self.position,
            manifesto='I will serve with dedication.',
        )

    def test_candidate_str(self):
        self.assertIn('Jane Wanjiku', str(self.candidate))

    def test_candidate_initials(self):
        self.assertEqual(self.candidate.get_initials(), 'JW')

    def test_vote_count_starts_zero(self):
        self.assertEqual(self.candidate.vote_count, 0)

    def test_vote_percentage_zero_when_no_votes(self):
        self.assertEqual(self.candidate.vote_percentage, 0)

    def test_has_no_photo_by_default(self):
        self.assertFalse(self.candidate.has_photo())


# ═══════════════════════════════════════════════
# AUTH TESTS
# ═══════════════════════════════════════════════

class AuthTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            admission_number=43863,
            first_name='Brian',
            last_name='Otieno',
            email='brian@school.ac.ke',
            is_active=True,
            password_changed=True,
        )
        self.student.set_password('newpassword123')
        self.student.save()

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_correct_credentials(self):
        response = self.client.post(reverse('login'), {
            'admission_number': 43863,
            'password':         'newpassword123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_with_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'admission_number': 43863,
            'password':         'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_login_with_unregistered_admission(self):
        response = self.client.post(reverse('login'), {
            'admission_number': 99999,
            'password':         '99999',
        })
        self.assertEqual(response.status_code, 200)

    def test_deactivated_student_cannot_login(self):
        self.student.is_active = False
        self.student.save()
        response = self.client.post(reverse('login'), {
            'admission_number': 43863,
            'password':         'newpassword123',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


# ═══════════════════════════════════════════════
# VOTE INTEGRITY TESTS
# ═══════════════════════════════════════════════

class VoteIntegrityTest(TestCase):

    def setUp(self):
        self.client = Client()

        # Create voter
        self.student = Student.objects.create(
            admission_number=43864,
            first_name='Carol',
            last_name='Kamau',
            email='carol@school.ac.ke',
            is_active=True,
            password_changed=True,
        )
        self.student.set_password('password123')
        self.student.save()

        # Create candidate student
        self.cand_student = Student.objects.create(
            admission_number=43865,
            first_name='David',
            last_name='Mwangi',
            email='david@school.ac.ke',
            is_active=True,
            password_changed=True,
        )
        self.cand_student.set_password('password123')
        self.cand_student.save()

        # Create election
        self.election = Election.objects.create(
            election_name='Integrity Test Election',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=2),
            status=Election.STATUS_ACTIVE,
        )

        # Create position
        self.position = Position.objects.create(
            election=self.election,
            position_name='President',
            max_votes=1,
        )

        # Create candidate
        self.candidate = Candidate.objects.create(
            student=self.cand_student,
            position=self.position,
            manifesto='Test manifesto',
        )

    def test_student_can_vote(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse('cast_vote'),
            {f'vote_{self.position.id}': self.candidate.id},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Vote.objects.filter(
                student=self.student,
                election=self.election
            ).count(), 1
        )

    def test_student_cannot_vote_twice(self):
        # Cast first vote
        Vote.objects.create(
            student=self.student,
            candidate=self.candidate,
            position=self.position,
            election=self.election,
        )

        # Try to vote again
        self.client.force_login(self.student)
        self.client.post(
            reverse('cast_vote'),
            {f'vote_{self.position.id}': self.candidate.id},
            follow=True
        )

        # Should still be only 1 vote
        self.assertEqual(
            Vote.objects.filter(
                student=self.student,
                position=self.position,
                election=self.election
            ).count(), 1
        )

    def test_deactivated_student_cannot_vote(self):
        self.student.is_active = False
        self.student.save()

        self.client.force_login(self.student)
        response = self.client.post(
            reverse('cast_vote'),
            {f'vote_{self.position.id}': self.candidate.id},
            follow=True
        )
        self.assertEqual(
            Vote.objects.filter(
                student=self.student
            ).count(), 0
        )

    def test_vote_count_updates_correctly(self):
        Vote.objects.create(
            student=self.student,
            candidate=self.candidate,
            position=self.position,
            election=self.election,
        )
        self.assertEqual(self.candidate.vote_count, 1)
        self.assertEqual(self.candidate.vote_percentage, 100.0)

    def test_vote_invalidates_results_cache(self):
        cache_key = f'results_api_{self.election.id}'
        cache.set(cache_key, {'stale': True}, timeout=30)

        self.client.force_login(self.student)
        self.client.post(
            reverse('cast_vote'),
            {f'vote_{self.position.id}': self.candidate.id},
            follow=True
        )

        self.assertIsNone(cache.get(cache_key))

    def test_results_api_uses_fresh_annotated_totals(self):
        admin = Student.objects.create(
            admission_number=100001,
            first_name='Admin',
            last_name='Tester',
            email='admin-results@school.ac.ke',
            is_staff=True,
            is_superuser=True,
            password_changed=True,
        )
        admin.set_password('adminpass')
        admin.save()
        Vote.objects.create(
            student=self.student,
            candidate=self.candidate,
            position=self.position,
            election=self.election,
        )

        self.client.force_login(admin)
        response = self.client.get(
            reverse('admin_results_api', args=[self.election.id])
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['positions'][0]['total_votes'], 1)
        self.assertEqual(data['positions'][0]['candidates'][0]['votes'], 1)
        self.assertEqual(
            data['positions'][0]['candidates'][0]['percentage'],
            100.0
        )

    def test_unique_together_constraint(self):
        from django.db import IntegrityError
        Vote.objects.create(
            student=self.student,
            candidate=self.candidate,
            position=self.position,
            election=self.election,
        )
        with self.assertRaises(IntegrityError):
            Vote.objects.create(
                student=self.student,
                candidate=self.candidate,
                position=self.position,
                election=self.election,
            )


# ═══════════════════════════════════════════════
# CSV UPLOAD TESTS
# ═══════════════════════════════════════════════

class CSVUploadTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Create admin user
        from django.contrib.auth.models import User
        self.admin = Student.objects.create(
            admission_number=100000,
            first_name='Admin',
            last_name='User',
            email='admin@school.ac.ke',
            is_staff=True,
            is_superuser=True,
            password_changed=True,
        )
        self.admin.set_password('adminpass')
        self.admin.save()

    def test_csv_upload_creates_students(self):
        import io
        self.client.force_login(self.admin)

        csv_content = (
            'admission_number,first_name,last_name,email\n'
            '55001,Alice,Mwangi,alice@school.ac.ke\n'
            '55002,Bob,Otieno,bob@school.ac.ke\n'
            '55003,Carol,Kamau,carol@school.ac.ke\n'
        )
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test.csv'

        response = self.client.post(
            reverse('admin_upload_csv'),
            {'csv_file': csv_file},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Student.objects.filter(
                admission_number__in=[55001, 55002, 55003]
            ).count(), 3
        )

    def test_csv_skips_duplicates(self):
        import io
        Student.objects.create(
            admission_number=55004,
            first_name='Existing',
            last_name='Student',
            email='existing@school.ac.ke',
        )

        self.client.force_login(self.admin)
        csv_content = (
            'admission_number,first_name,last_name,email\n'
            '55004,Existing,Student,existing@school.ac.ke\n'
            '55005,New,Student,new@school.ac.ke\n'
        )
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test.csv'

        self.client.post(
            reverse('admin_upload_csv'),
            {'csv_file': csv_file},
            follow=True
        )
        self.assertEqual(
            Student.objects.filter(
                admission_number=55004
            ).count(), 1
        )


# ═══════════════════════════════════════════════
# NOTIFICATION TESTS
# ═══════════════════════════════════════════════

class NotificationTest(TestCase):

    def setUp(self):
        self.student = Student.objects.create(
            admission_number=43870,
            first_name='Eve',
            last_name='Njoroge',
            email='eve@school.ac.ke',
            is_active=True,
            password_changed=True,
        )
        self.student.set_password('password123')
        self.student.save()

    def test_notification_created(self):
        from .utils import create_notification
        create_notification(
            student=self.student,
            title='Test',
            message='Test message',
            notif_type='info',
        )
        self.assertEqual(
            self.student.notifications.count(), 1
        )

    def test_notification_marked_as_read(self):
        from .utils import create_notification
        create_notification(
            student=self.student,
            title='Test',
            message='Test message',
            notif_type='info',
        )
        self.student.notifications.filter(
            is_read=False
        ).update(is_read=True)
        self.assertEqual(
            self.student.notifications.filter(
                is_read=False
            ).count(), 0
        )
