import pytest
from rest_framework.test import APIClient
from colleges.models import College
from accounts.models import User

@pytest.mark.django_db
class TestTenantIsolation:
    def setup_method(self):
        self.client = APIClient()

        # College Alpha
        self.college_alpha = College.objects.create(
            name="Alpha Engineering Institute",
            code="ALPHA-ENG",
            slug="alpha-eng",
            status="ACTIVE"
        )
        self.principal_alpha = User.objects.create_user(
            email="principal@alpha.edu",
            password="Password123!",
            first_name="Alpha",
            last_name="Principal",
            role="PRINCIPAL",
            college=self.college_alpha,
            status="ACTIVE"
        )
        self.student_alpha = User.objects.create_user(
            email="student@alpha.edu",
            password="Password123!",
            first_name="Alpha",
            last_name="Student",
            role="STUDENT",
            college=self.college_alpha,
            status="ACTIVE"
        )

        # College Beta
        self.college_beta = College.objects.create(
            name="Beta Science College",
            code="BETA-SCI",
            slug="beta-sci",
            status="ACTIVE"
        )
        self.student_beta = User.objects.create_user(
            email="student@beta.edu",
            password="Password123!",
            first_name="Beta",
            last_name="Student",
            role="STUDENT",
            college=self.college_beta,
            status="ACTIVE"
        )

        # Super Admin
        self.superadmin = User.objects.create_superuser(
            email="superadmin@campyteq.io",
            password="Password123!",
            first_name="Super",
            last_name="Admin"
        )

    def test_alpha_user_cannot_see_beta_records(self):
        """Alpha principal should ONLY see Alpha users, never Beta users."""
        self.client.force_authenticate(user=self.principal_alpha)
        response = self.client.get('/api/v1/users/')
        assert response.status_code == 200

        # Extract returned emails
        results = response.data.get('results', response.data)
        if isinstance(results, dict) and 'data' in results:
            results = results['data']
        emails = [u['email'] for u in (results.get('results', results) if isinstance(results, dict) else results)]

        assert "principal@alpha.edu" in emails
        assert "student@alpha.edu" in emails
        assert "student@beta.edu" not in emails

    def test_alpha_cannot_access_beta_user_by_direct_id(self):
        """Direct lookup of Beta user ID by Alpha principal must return 404."""
        self.client.force_authenticate(user=self.principal_alpha)
        response = self.client.get(f'/api/v1/users/{self.student_beta.id}/')
        assert response.status_code == 404

    def test_superadmin_can_access_all_colleges(self):
        """Super admin has global multi-tenant visibility."""
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get('/api/v1/users/')
        assert response.status_code == 200

        results = response.data.get('results', response.data)
        if isinstance(results, dict) and 'data' in results:
            results = results['data']
        emails = [u['email'] for u in (results.get('results', results) if isinstance(results, dict) else results)]

        assert "student@alpha.edu" in emails
        assert "student@beta.edu" in emails
